# pylint: disable=W0212

"""
Tests for Optimize.run, the entry point that dispatches to the solver classes.

The first half exercises the orchestrator directly: how it reads the budget off a case, how it
names the decision-maker option it writes back to, how settings reach one solver or all of
them, and what happens when a method or a setting is addressed that is not running. The second
half goes through TheResponsibleBusinessSimulator, the way a user reaches it.

optimize_single_scenario is covered here as well: it is the same run behind the frozen
contract an external front end calls.
"""

import numpy as np
import pytest

from vlinder.optimize import GridSearch, Optimize, SLSQPSolver, score_allocation
from vlinder.utils import suppress_print
from .conftest import BEERWISER_BUDGET, BEERWISER_OPTIMUM


@pytest.fixture(name="orchestrator")
def fixture_orchestrator(beerwiser_dicts):
    """An Optimize bound to a private copy of Beerwiser."""
    return Optimize(*beerwiser_dicts)


def test_budget_is_inferred_from_the_case(orchestrator):
    """The orchestrator reads the budget off the case when the caller does not supply one."""
    assert orchestrator.budget == BEERWISER_BUDGET


def test_unsupported_method_raises(orchestrator):
    """An unknown method is a typo, and the error says which methods do exist."""
    with pytest.raises(NotImplementedError, match="basin_hopping"):
        orchestrator.run("Base case", method="simulated_annealing")


def test_the_option_name_records_the_scenario(orchestrator):
    """An allocation is only optimal for the scenario it was optimized under, so the name says so."""
    result = orchestrator.run("Base case", method="slsqp", n_starts=2, seed=1, dmo_name="My DMO")

    assert result.dmo_name == "My DMO (SLSQP) (Base case)"
    assert "My DMO (SLSQP) (Base case)" in orchestrator.input_dict["decision_makers_options"]


@suppress_print
def test_optimizing_two_scenarios_keeps_them_apart(orchestrator):
    """Optimizing the same case twice must produce two options, not overwrite one."""
    orchestrator.run("Base case", method="slsqp", n_starts=2, seed=1)
    orchestrator.run("Optimistic", method="slsqp", n_starts=2, seed=1)

    names = list(orchestrator.input_dict["decision_makers_options"])
    assert SLSQPSolver.default_dmo_name + " (Base case)" in names
    assert SLSQPSolver.default_dmo_name + " (Optimistic)" in names


def test_a_list_of_methods_prints_each_and_keeps_the_best(orchestrator, capsys):
    """Every method reports, one winner is written back."""
    n_before = orchestrator.input_dict["decision_makers_options"].size

    result = orchestrator.run("Base case", method=["grid", "slsqp"], seed=42)
    printed = capsys.readouterr().out

    assert "[grid]" in printed
    assert "[slsqp]" in printed
    assert result.method in ("grid", "slsqp")

    # Only the winner reaches the case, not one option per method.
    assert orchestrator.input_dict["decision_makers_options"].size == n_before + 1
    names = list(orchestrator.input_dict["decision_makers_options"])
    candidates = [
        f"{GridSearch.default_dmo_name} (Base case)",
        f"{SLSQPSolver.default_dmo_name} (Base case)",
    ]
    present = [name for name in candidates if name in names]
    assert len(present) == 1


@suppress_print
def test_shared_settings_reach_every_method(orchestrator):
    """A setting passed directly applies to each method that runs.

    Both solvers report the number of starts they used, and both have a different default
    (100 for SLSQP, 1 for basin-hopping), so whichever one wins proves the setting arrived.
    """
    result = orchestrator.run("Base case", method=["slsqp", "basin_hopping"], n_starts=3, n_hops=2, seed=1)

    assert result.n_starts == 3


def test_method_kwargs_give_each_method_its_own_settings(orchestrator, capsys):
    """Two methods with parameters the other one does not have can run in one call."""
    orchestrator.run(
        "Base case",
        method=["grid", "slsqp"],
        method_kwargs={"grid": {"max_combinations": 1000}, "slsqp": {"n_starts": 4, "seed": 1}},
    )
    printed = capsys.readouterr().out

    assert "[grid]" in printed
    assert "[slsqp]" in printed


@suppress_print
def test_method_kwargs_win_over_the_shared_settings(orchestrator):
    """A per-method setting overrides the same setting passed for everyone."""
    result = orchestrator.run(
        "Base case", method="slsqp", n_starts=25, seed=1, method_kwargs={"slsqp": {"n_starts": 3}}
    )

    assert result.n_starts == 3
    assert len(result.per_start_results) == 3


def test_method_kwargs_for_a_method_that_is_not_running_raises(orchestrator):
    """Settings addressed to a method that is not running are a typo, not a silent no-op."""
    with pytest.raises(NotImplementedError, match="grid"):
        orchestrator.run("Base case", method="slsqp", method_kwargs={"grid": {"max_combinations": 10}})


@suppress_print
def test_without_a_configured_name_the_solver_default_applies(orchestrator):
    """The test fixtures carry no Optimize_DMO_name, so the solver default names the option."""
    result = orchestrator.run("Base case", method="slsqp", n_starts=2, seed=1)

    assert result.dmo_name == f"{SLSQPSolver.default_dmo_name} (Base case)"


@suppress_print
def test_optimize_single_scenario_keeps_the_papilio_contract(orchestrator):
    """The front end calls this positionally and reads only the returned input dict.

    The call mirrors Papilio's own line: Optimize(...).optimize_single_scenario(scenario,
    "Optimized DMO", 10000). Whatever the solver does, the return value must be the updated
    input dictionary, with the optimized option on it.
    """
    returned = orchestrator.optimize_single_scenario("Base case", "Optimized DMO", 10000, n_hops=2, n_starts=1, seed=1)

    assert returned is orchestrator.input_dict
    assert "Optimized DMO (basin-hopping) (Base case)" in returned["decision_makers_options"]


@suppress_print
def test_optimize_single_scenario_is_method_agnostic(orchestrator):
    """The frozen contract runs the package default, and a caller can still name the method."""
    orchestrator.optimize_single_scenario(
        "Base case", "Optimized DMO", 10000, method="grid", max_calculation_time=None
    )

    assert "Optimized DMO (grid) (Base case)" in orchestrator.input_dict["decision_makers_options"]


# ======================================================================
# Through the case: TheResponsibleBusinessSimulator.optimize()
# ======================================================================
@suppress_print
def test_case_optimize_defaults(beerwiser_appreciated):
    """No method means basin-hopping, spending the whole budget, under a 60-second limit."""
    original_name = beerwiser_appreciated.name
    beerwiser_appreciated.optimize("Base case", n_hops=3, n_starts=1, seed=42)
    result = beerwiser_appreciated.optimization_result

    assert result.method == "basin_hopping"
    assert result.budget_spent == pytest.approx(result.budget)
    assert result.calculation_time <= 60
    assert "Optimized_DMO (basin-hopping) (Base case)" in beerwiser_appreciated.input_dict["decision_makers_options"]
    assert beerwiser_appreciated.name == f"{original_name} - Optimized (basin_hopping) (Base case)"


@suppress_print
def test_configured_name_is_extended_with_method_and_scenario(beerwiser_appreciated):
    """A configured Optimize_DMO_name is the base; the method and scenario are appended."""
    beerwiser_appreciated.optimize("Base case", method="grid", max_calculation_time=None)
    result = beerwiser_appreciated.optimization_result

    assert result.dmo_name == "Optimized_DMO (grid) (Base case)"
    assert result.dmo_name in beerwiser_appreciated.input_dict["decision_makers_options"]


@suppress_print
def test_an_explicit_name_overrides_the_configured_one(beerwiser_appreciated):
    """A caller-supplied name wins over the configuration sheet; method and scenario are added."""
    beerwiser_appreciated.optimize("Base case", method="grid", dmo_name="My Grid Run", max_calculation_time=None)

    names = list(beerwiser_appreciated.input_dict["decision_makers_options"])
    assert "My Grid Run (grid) (Base case)" in names
    assert not any(str(name).startswith("Optimized_DMO (") for name in names)


@suppress_print
def test_case_optimize_returns_the_input_dict(beerwiser_appreciated):
    """optimize() hands back the updated input dictionary, as the other case steps do."""
    returned = beerwiser_appreciated.optimize("Base case", method="grid", max_calculation_time=None)

    assert returned is beerwiser_appreciated.input_dict
    assert 3 in beerwiser_appreciated.status


@suppress_print
def test_case_optimize_records_the_result(beerwiser_appreciated):
    """The full result of the run is kept on the case."""
    beerwiser_appreciated.optimize("Base case", method="grid", max_calculation_time=None)
    result = beerwiser_appreciated.optimization_result

    assert result.method == "grid"
    assert result.scenario == "Base case"
    assert result.appreciation == pytest.approx(BEERWISER_OPTIMUM, abs=1e-6)
    assert result.budget_spent <= result.budget + 1e-6


@suppress_print
def test_continuous_matches_or_beats_the_grid_baseline(beerwiser_appreciated):
    """The whole point of the continuous solvers: at least as good as enumerating the grid."""
    case_grid = beerwiser_appreciated.copy()
    case_grid.optimize(
        "Base case", method="grid", dmo_name="Grid Baseline", max_combinations=60000, max_calculation_time=None
    )
    grid_appreciation = case_grid.optimization_result.appreciation

    case_bh = beerwiser_appreciated.copy()
    case_bh.optimize("Base case", method="basin_hopping", n_hops=10, n_starts=2, seed=42, dmo_name="BH DMO")
    result = case_bh.optimization_result

    assert (
        result.appreciation >= grid_appreciation - 0.5
    ), f"basin-hopping appreciation {result.appreciation:.4f} trails grid {grid_appreciation:.4f} by more than 0.5"
    assert "BH DMO (basin-hopping) (Base case)" in case_bh.input_dict["decision_makers_options"]


@suppress_print
def test_the_written_back_allocation_scores_what_the_result_claims(beerwiser_appreciated):
    """The allocation stored on the case must reproduce the reported appreciation."""
    beerwiser_appreciated.optimize("Base case", method="slsqp", n_starts=5, seed=7, dmo_name="Check")
    result = beerwiser_appreciated.optimization_result

    input_dict = beerwiser_appreciated.input_dict
    name = "Check (SLSQP) (Base case)"
    idx = np.where(input_dict["decision_makers_options"] == name)[0][0]
    stored = input_dict["decision_makers_option_value"][idx]

    assert score_allocation(input_dict, stored, "Base case", name) == pytest.approx(result.appreciation, abs=1e-9)
