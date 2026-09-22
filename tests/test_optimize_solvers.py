# pylint: disable=W0212

"""
Tests for the solver classes in vlinder.optimize, one section per solver.

Each section checks the same three things for its solver: that it returns a well-formed result,
that the allocation it hands back is feasible, and that it finds what it is supposed to find on
Beerwiser, whose optimum is known exactly. Beerwiser has two optima 0.01 appreciation points
apart: an interior one at roughly [123000, 177000] and the global one at the clip kink
[25000, 275000]. Which of the two a solver reaches is the interesting part.
"""

import copy

import numpy as np
import pytest

from vlinder.optimize import (
    BasinHoppingSolver,
    GridSearch,
    OptimizationResult,
    SLSQPSolver,
    score_allocation,
)
from vlinder.utils import get_values_from_target, suppress_print
from .conftest import BEERWISER_BUDGET, BEERWISER_EQUAL_SPREAD, BEERWISER_OPTIMUM


def assert_feasible(allocation, budget):
    """Assert an allocation lies in the capped simplex {x >= 0, sum(x) <= budget}."""
    assert float(np.sum(allocation)) <= budget + 1e-3, "allocation overspends the budget"
    assert (np.asarray(allocation) >= -1e-6).all(), "allocation has a negative component"


# ======================================================================
# BaseSolver: what every solver inherits
# ======================================================================
def test_budget_is_the_largest_spend_across_options(prepared_solver):
    """The budget is the most any option spends, not whatever the first option happens to spend.

    Reading the first option would report a "do nothing" option as a zero budget and leave the
    continuous solvers with nothing to allocate.
    """
    values = prepared_solver.input_dict["decision_makers_option_value"]
    values[0] = np.zeros_like(values[0])

    assert prepared_solver.budget == BEERWISER_BUDGET


def test_prepare_input_dict_is_idempotent(prepared_solver):
    """Preparing twice must not add the option twice."""
    before = list(prepared_solver.input_dict["decision_makers_options"])
    prepared_solver._prepare_input_dict("Test DMO", [150000, 150000])

    assert list(prepared_solver.input_dict["decision_makers_options"]) == before


def test_write_back_result_lands_on_the_option(prepared_solver):
    """The winning allocation must be readable from the case, not only from the result."""
    prepared_solver._write_back_result("Test DMO", [25000.0, 275000.0])

    idx = np.where(prepared_solver.input_dict["decision_makers_options"] == "Test DMO")[0][0]
    assert np.array_equal(prepared_solver.input_dict["decision_makers_option_value"][idx], [25000.0, 275000.0])


def test_project_capped_simplex_restores_feasibility():
    """Solver tolerance dust is clipped and rescaled back into the feasible set."""
    projected = SLSQPSolver._project_capped_simplex(np.array([-1e-9, 200.0, 200.0]), 300.0)

    assert_feasible(projected, 300.0)
    assert float(np.sum(projected)) == pytest.approx(300.0)


def test_base_solver_has_no_solve(prepared_solver):
    """BaseSolver is scaffolding; only the concrete solvers can run."""
    with pytest.raises(NotImplementedError):
        prepared_solver.solve("Base case", "Test DMO", BEERWISER_BUDGET)


# ======================================================================
# GridSearch
# ======================================================================
@pytest.mark.parametrize(
    "max_investment, expected_result",
    [(1000, 1000), (15700, 1500), (999999, 10000), (1234567, 1200), (499999, 5000)],
)
def test_scale_max_investment(max_investment, expected_result):
    """The investment is scaled down to a size the combinatorics can handle."""
    assert GridSearch.scale_max_investment(max_investment) == expected_result


@pytest.mark.parametrize(
    "max_investment, scaled, num_inputs, max_combinations, expected_result",
    [
        (1000, 1000, 2, 60000, 1),
        (1000, 1000, 3, 60000, 4),
        (1000, 1000, 2, 100, 20),
        (15700, 15000, 2, 60000, 1.0466666666666666),
    ],
)
def test_calculate_step_size(max_investment, scaled, num_inputs, max_combinations, expected_result):
    """The step size is coarsened until the number of combinations fits the budget."""
    assert GridSearch.calculate_step_size(max_investment, scaled, num_inputs, max_combinations) == expected_result


@pytest.mark.parametrize(
    "max_investment, step_size, num_inputs, expected_result",
    [
        (10, 5, 2, [(5, 5), (10, 0), (0, 10)]),
        (10, 10, 2, [(0, 10), (10, 0)]),
        (10, 5, 3, [(0, 5, 5), (5, 5, 0), (5, 0, 5), (10, 0, 0), (0, 10, 0), (0, 0, 10)]),
    ],
)
def test_generate_combinations(max_investment, step_size, num_inputs, expected_result):
    """Every generated combination spends the budget exactly: grid works on the budget face."""
    combinations = GridSearch.generate_combinations(max_investment, step_size, num_inputs)

    assert sorted(combinations) == sorted(expected_result)
    for combination in combinations:
        assert sum(combination) == max_investment


def test_refinement_points_cover_the_face_and_skip_the_previous_round():
    """The first round is the whole lattice; later rounds yield only the new points."""
    first = list(GridSearch.refinement_points(2, 2, include_all=True))
    assert sorted(first) == [(0, 2), (1, 1), (2, 0)]

    second = list(GridSearch.refinement_points(4, 2, include_all=False))
    assert sorted(second) == [(1, 3), (3, 1)]

    # Together the two rounds cover the finer lattice exactly, with nothing evaluated twice.
    doubled = {tuple(2 * count for count in point) for point in first}
    assert sorted(doubled | set(second)) == sorted(GridSearch._face_compositions(4, 2))


@suppress_print
def test_grid_time_budget_starts_at_half_the_budget_and_refines(beerwiser_dicts):
    """Under a time budget the grid halves its step, round after round, until time runs out."""
    input_dict, output_dict = beerwiser_dicts
    solver = GridSearch(input_dict, output_dict)
    result = solver.solve("Base case", "Test DMO", max_calculation_time=1.5)

    steps = [level["step_size"] for level in result.per_start_results]
    assert steps[0] == pytest.approx(BEERWISER_BUDGET / 2)
    for coarse, fine in zip(steps, steps[1:]):
        assert fine == pytest.approx(coarse / 2)
    # Every evaluation is a new lattice point, and the equal split of the first round
    # guarantees the answer is at least as good as that split.
    assert result.n_function_evals == sum(level["new_points"] for level in result.per_start_results)
    assert result.appreciation >= 65.4


@suppress_print
def test_grid_without_spend_all_covers_under_spending_points(beerwiser_dicts):
    """With spend_all=False the lattice covers sum(x) <= B, so it holds under-spending points."""
    combos = GridSearch.generate_combinations(10, 5, 2, spend_all=False)
    assert sorted(combos) == [(0, 0), (0, 5), (0, 10), (5, 0), (5, 5), (10, 0)]

    input_dict, output_dict = beerwiser_dicts
    solver = GridSearch(input_dict, output_dict)
    result = solver.solve("Base case", "Capped DMO", max_combinations=300, spend_all=False)
    assert result.method == "grid"
    assert_feasible(result.allocation, BEERWISER_BUDGET)


def test_grid_find_dict_values(prepared_solver):
    """Grid search starts from the best-performing option already in the case."""
    grid = GridSearch(prepared_solver.input_dict, prepared_solver.output_dict)
    best_dmo_data, max_investment = grid.find_dict_values("Base case")

    assert best_dmo_data["dmo_name"] == "Equal spread"
    assert np.array_equal(best_dmo_data["decision_maker_options"], [150000, 150000])
    assert best_dmo_data["max_appreciated_value"] == BEERWISER_EQUAL_SPREAD
    assert max_investment == BEERWISER_BUDGET


def test_grid_search_finds_the_beerwiser_optimum(beerwiser_dicts):
    """Enumerating the budget face reaches Beerwiser's global optimum."""
    input_dict, output_dict = beerwiser_dicts
    result = GridSearch(input_dict, output_dict).solve("Base case", "Optimized DMO", max_combinations=60000)

    assert isinstance(result, OptimizationResult)
    assert result.method == "grid"
    assert result.scenario == "Base case"
    assert result.appreciation == pytest.approx(BEERWISER_OPTIMUM, abs=1e-6)
    assert get_values_from_target(input_dict, "decision_makers_options")[0].size == 4


def test_grid_search_can_rerun_under_the_same_name(beerwiser_dicts):
    """Running twice with one name must optimize twice, not refuse the second run."""
    input_dict, output_dict = beerwiser_dicts
    first = GridSearch(input_dict, output_dict).solve("Base case", "Optimized DMO", max_combinations=60000)
    second = GridSearch(input_dict, output_dict).solve("Base case", "Optimized DMO", max_combinations=60000)

    assert second.appreciation == pytest.approx(first.appreciation, abs=1e-9)
    assert get_values_from_target(input_dict, "decision_makers_options")[0].size == 4


def test_grid_search_keeps_an_already_optimal_option(beerwiser_dicts):
    """When nothing on the grid beats an existing option, that option stays the answer."""
    input_dict, output_dict = beerwiser_dicts
    output_dict["Base case"]["highest_weighted_dmo"] = "Equal spread"
    output_dict["Base case"]["Equal spread"]["decision_makers_option_appreciation"] = 100

    result = GridSearch(input_dict, output_dict).solve("Base case", "Optimized DMO", max_combinations=60000)

    idx = np.where(input_dict["decision_makers_options"] == "Optimized DMO")[0][0]
    assert np.array_equal(input_dict["decision_makers_option_value"][idx], [150000, 150000])
    assert result.dmo_name == "Equal spread"
    assert result.appreciation == 100


# ======================================================================
# SLSQPSolver
# ======================================================================
def test_slsqp_returns_a_structured_result(prepared_solver):
    """A multi-start run reports its starts, its cost and a feasible winner."""
    solver = SLSQPSolver(prepared_solver.input_dict, prepared_solver.output_dict)
    result = solver.solve("Base case", "Test DMO", BEERWISER_BUDGET, n_starts=20, seed=42)

    assert isinstance(result, OptimizationResult)
    assert result.method == "slsqp"
    assert result.n_starts == 20
    assert result.n_converged >= 10
    assert len(result.per_start_results) == 20
    assert result.n_function_evals > 20
    assert result.calculation_time > 0
    assert result.budget_spent == pytest.approx(BEERWISER_BUDGET, abs=1e-3)
    assert_feasible(result.allocation, BEERWISER_BUDGET)


def test_slsqp_moves_away_from_its_starting_point(prepared_solver):
    """A solve must actually travel, not report success while standing still.

    Two earlier defects both showed up this way: a float allocation written into a whole-number
    table, and an unnormalised budget scale that made the first trial step vanish. From
    [60000, 240000] a working solver reaches the interior optimum.
    """
    solver = SLSQPSolver(prepared_solver.input_dict, prepared_solver.output_dict)
    x0 = np.array([60000.0, 240000.0])
    start_appreciation = score_allocation(solver.input_dict, x0, "Base case", "Test DMO")

    res = solver._slsqp_from_start(x0, "Base case", "Test DMO", BEERWISER_BUDGET, [0])

    assert res.success, f"SLSQP did not converge: {res.message}"
    assert abs(res.x[0] - x0[0]) > 10000, f"solver stalled at its start point: x={res.x}"
    assert -res.fun > start_appreciation + 0.5


def test_slsqp_beats_an_even_split(prepared_solver):
    """From an even split the solver can only improve."""
    solver = SLSQPSolver(prepared_solver.input_dict, prepared_solver.output_dict)
    uniform = np.array([BEERWISER_BUDGET / 2, BEERWISER_BUDGET / 2])
    uniform_appreciation = score_allocation(solver.input_dict, uniform, "Base case", "Test DMO")

    res = solver._slsqp_from_start(uniform, "Base case", "Test DMO", BEERWISER_BUDGET, [0])

    assert res.success
    assert -float(res.fun) >= uniform_appreciation - 1e-3
    assert_feasible(res.x, BEERWISER_BUDGET)


# ======================================================================
# BasinHoppingSolver
# ======================================================================
def test_basin_hopping_returns_a_structured_result(prepared_solver):
    """A hopping run reports one entry per chain and a feasible winner."""
    solver = BasinHoppingSolver(prepared_solver.input_dict, prepared_solver.output_dict)
    result = solver.solve("Base case", "Test DMO", BEERWISER_BUDGET, n_hops=5, n_starts=2, seed=42)

    assert result.method == "basin_hopping"
    assert result.n_starts == 2
    assert len(result.per_start_results) == 2
    assert result.n_function_evals > 10
    assert result.calculation_time > 0
    assert_feasible(result.allocation, BEERWISER_BUDGET)


def test_basin_hopping_finds_the_global_kink(prepared_solver):
    """The escape loop reaches the clip kink that a single local solve can miss."""
    solver = BasinHoppingSolver(prepared_solver.input_dict, prepared_solver.output_dict)
    result = solver.solve("Base case", "Test DMO", BEERWISER_BUDGET, n_hops=25, n_starts=1, seed=1)

    assert result.appreciation == pytest.approx(BEERWISER_OPTIMUM, abs=1e-3)
    assert result.allocation[0] == pytest.approx(25000.0, abs=500.0)


def test_random_feasible_hop_stays_in_the_feasible_set():
    """Every jump lands somewhere the solver is allowed to start from."""
    hop = BasinHoppingSolver._RandomFeasibleHop(1.0, 2, np.random.default_rng(0), step_frac=0.9)

    for _ in range(50):
        assert_feasible(hop(np.array([0.5, 0.5])), 1.0)


# ======================================================================
# Shared contract: every solver behaves the same way from the outside
# ======================================================================
SOLVER_SETTINGS = [
    (GridSearch, {"max_combinations": 60000}),
    (SLSQPSolver, {"n_starts": 4, "seed": 1}),
    (BasinHoppingSolver, {"n_starts": 1, "n_hops": 3, "seed": 1}),
]


@suppress_print
@pytest.mark.parametrize("solver_class, settings", SOLVER_SETTINGS)
def test_every_solver_reports_the_shared_fields(beerwiser_dicts, solver_class, settings):
    """Whatever the solver, the result carries the run's context and a feasible allocation."""
    input_dict, output_dict = beerwiser_dicts
    solver = solver_class(input_dict, output_dict)
    result = solver.solve("Base case", "Solver DMO", BEERWISER_BUDGET, **settings)

    assert result.method == solver_class.method_name
    assert result.scenario == "Base case"
    assert result.appreciation > 0
    assert result.calculation_time > 0
    assert result.timestamp
    assert result.budget_spent == pytest.approx(float(np.sum(result.allocation)))
    assert_feasible(result.allocation, BEERWISER_BUDGET)


@suppress_print
@pytest.mark.parametrize("solver_class, settings", SOLVER_SETTINGS)
def test_every_solver_leaves_its_answer_on_the_case(beerwiser_dicts, solver_class, settings):
    """The optimized allocation has to be readable from the case itself."""
    input_dict, output_dict = beerwiser_dicts
    solver = solver_class(input_dict, output_dict)
    solver.solve("Base case", "Solver DMO", BEERWISER_BUDGET, **settings)

    assert "Solver DMO" in input_dict["decision_makers_options"]


@suppress_print
@pytest.mark.parametrize("solver_class, settings", SOLVER_SETTINGS)
def test_every_solver_is_reproducible(beerwiser_dicts, solver_class, settings):
    """The same case and the same seed must give the same answer twice."""
    first = solver_class(*copy.deepcopy(beerwiser_dicts)).solve("Base case", "A", BEERWISER_BUDGET, **settings)
    second = solver_class(*copy.deepcopy(beerwiser_dicts)).solve("Base case", "B", BEERWISER_BUDGET, **settings)

    assert first.appreciation == second.appreciation
    assert np.array_equal(first.allocation, second.allocation)


# ======================================================================
# spend_all: the budget as an equality instead of an upper bound
# ======================================================================
def test_project_budget_face_restores_the_face():
    """Solver tolerance dust is clipped and the sum is rescaled to the budget, in either direction."""
    projected = SLSQPSolver._project_budget_face(np.array([-1e-9, 100.0, 100.0]), 300.0)
    assert float(np.sum(projected)) == pytest.approx(300.0)
    assert (projected >= 0.0).all()

    all_clipped = SLSQPSolver._project_budget_face(np.array([-1.0, -2.0]), 300.0)
    assert float(np.sum(all_clipped)) == pytest.approx(300.0)


@suppress_print
@pytest.mark.parametrize(
    "solver_class, settings",
    [
        (SLSQPSolver, {"n_starts": 10_000, "seed": 1}),
        (BasinHoppingSolver, {"n_starts": 1, "n_hops": 1_000_000, "seed": 1}),
    ],
)
def test_every_continuous_solver_stops_at_its_time_limit(beerwiser_dicts, solver_class, settings):
    """With the unit knob out of reach, the clock is what ends the run, close to the limit."""
    input_dict, output_dict = beerwiser_dicts
    solver = solver_class(input_dict, output_dict)
    result = solver.solve("Base case", "Solver DMO", BEERWISER_BUDGET, max_calculation_time=1.0, **settings)

    assert result.calculation_time < 3.0, "the solver ran far past its time limit"
    assert result.appreciation > 0
    assert_feasible(result.allocation, BEERWISER_BUDGET)


@suppress_print
@pytest.mark.parametrize("solver_class, settings", SOLVER_SETTINGS[1:])
def test_spend_all_answers_on_the_budget_face(beerwiser_dicts, solver_class, settings):
    """With ``spend_all`` every continuous solver spends the budget exactly, like grid search."""
    input_dict, output_dict = beerwiser_dicts
    solver = solver_class(input_dict, output_dict)
    result = solver.solve("Base case", "Solver DMO", BEERWISER_BUDGET, spend_all=True, **settings)

    assert float(np.sum(result.allocation)) == pytest.approx(BEERWISER_BUDGET)
    assert (np.asarray(result.allocation) >= -1e-6).all()
    assert result.appreciation > 0
