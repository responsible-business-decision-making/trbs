# pylint: disable=W0212,R0913,R0917,R0914,too-many-lines

"""
This module is the single home for tRBS optimization.

``Optimize.run`` is the entry point. It dispatches to a named solver class, each of which
shares one contract (:class:`BaseSolver`) and returns an :class:`OptimizationResult`. Three
solvers are available: ``"grid"`` (a grid search over a lattice of allocations),
``"slsqp"`` (continuous multi-start sequential least-squares programming) and
``"basin_hopping"`` (SLSQP wrapped in an escape loop, for appreciation surfaces with more
than one optimum). Basin-hopping is the default.

``Optimize.optimize_single_scenario`` is the same run behind a frozen contract: it takes its
arguments positionally, runs the package defaults whatever the method, and returns only the
updated input dictionary. External front ends call it that way.

The feasible set for the continuous solvers is the capped simplex, ``{x : x >= 0, sum(x) <= B}``:
spending less than the whole budget is allowed. Every solver also accepts ``spend_all=True``,
which turns the budget into an equality so that every solution spends it exactly.

The module also exposes two pure functions, ``evaluate_and_appreciate`` and
``score_allocation``, shared by all solvers. Both take a case dictionary and leave it
untouched, so the hundreds of objective evaluations a continuous optimizer makes cannot
corrupt shared state.
"""

import copy
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import comb
from itertools import combinations_with_replacement, permutations
from typing import List, Optional

import numpy as np
from scipy.optimize import basinhopping, minimize

from vlinder.appreciate import Appreciate
from vlinder.evaluate import Evaluate


def evaluate_and_appreciate(input_dict, x, scenario, dmo_name, start_and_end_points=None):
    """
    Evaluate allocation ``x`` and appreciate the result: the full tRBS output for a given
    decision-maker option under a given scenario, without mutating ``input_dict``.

    Preconditions (caller's responsibility, typically done once per optimizer run):
      - ``dmo_name`` must already exist in ``input_dict["decision_makers_options"]``
      - ``input_dict["decision_makers_option_value"]`` must already have a row for
        ``dmo_name`` (any feasible allocation is fine; it will be overwritten by ``x``)
      - ``input_dict["key_output_automatic"]``, ``key_output_start``, ``key_output_end``
        must be initialised (Appreciate uses these to fix the boundary points)

    :param input_dict: tRBS case input dictionary (NOT mutated)
    :param x: 1-D array-like of length ``len(input_dict["internal_variable_inputs"])``,
              the allocation to evaluate
    :param scenario: scenario name (str), must be in ``input_dict["scenarios"]``
    :param dmo_name: decision-maker option name (str) the allocation belongs to
    :param start_and_end_points: precomputed appreciation boundaries (see
        :meth:`BaseSolver._freeze_boundaries`). Optional; derived per call when omitted.
    :return: the output dictionary of this DMO, holding ``key_outputs``,
             ``appreciations``, ``weighted_appreciations`` and
             ``decision_makers_option_appreciation``
    """
    # DMO values that are whole numbers get imported as int64. Writing a float allocation into
    # an int row rounds it silently, which breaks gradient-based solvers. Cast to float to
    # avoid this. Copying that one table (the only one written here) is enough to leave the
    # caller's dictionary untouched, because Evaluate and Appreciate only read the rest.
    values = np.array(input_dict["decision_makers_option_value"], dtype=float)
    idx = np.where(input_dict["decision_makers_options"] == dmo_name)[0][0]
    values[idx] = np.asarray(x, dtype=float)
    local = {**input_dict, "decision_makers_option_value": values}

    # One decision-maker option, not all of them: evaluating the whole scenario would compute
    # every other option as well and throw those results away.
    output = Evaluate(local).evaluate_all_dependencies(scenario, dmo_name)
    Appreciate(local, output, start_and_end_points).appreciate_single_decision_maker_option(output)
    return output


def score_allocation(input_dict, x, scenario, dmo_name, start_and_end_points=None):
    """
    Weighted appreciation of allocation ``x``: :func:`evaluate_and_appreciate` reduced to
    the single number every optimizer maximises. Same preconditions.

    :param input_dict: tRBS case input dictionary (NOT mutated)
    :param x: 1-D array-like of length ``len(input_dict["internal_variable_inputs"])``,
              the allocation to evaluate
    :param scenario: scenario name (str), must be in ``input_dict["scenarios"]``
    :param dmo_name: decision-maker option name (str) the allocation belongs to
    :param start_and_end_points: precomputed appreciation boundaries. Optional.
    :return: float, the value of ``output["decision_makers_option_appreciation"]``
    """
    return float(
        evaluate_and_appreciate(input_dict, x, scenario, dmo_name, start_and_end_points)[
            "decision_makers_option_appreciation"
        ]
    )


@dataclass
class OptimizationResult:  # pylint: disable=too-many-instance-attributes
    """Result of an optimization run, for any method.

    ``method`` through ``timestamp`` are filled by every solver. The solver diagnostics
    below them are filled where they mean something: grid search, for instance, has no
    starts to converge, so it leaves ``n_converged`` unset.
    """

    method: str
    dmo_name: str
    scenario: str
    allocation: np.ndarray
    appreciation: float
    budget: float
    budget_spent: float
    calculation_time: float
    timestamp: str
    n_starts: Optional[int] = None
    n_converged: Optional[int] = None
    n_function_evals: Optional[int] = None
    per_start_results: List[dict] = field(default_factory=list)

    def summary(self) -> str:
        """A readable one-block summary, for notebooks and logs."""
        spent = f"{self.budget_spent:,.2f} of {self.budget:,.2f}"
        share = f"{self.budget_spent / self.budget:.1%}" if self.budget else "n/a"
        lines = [
            f"method          {self.method}",
            f"scenario        {self.scenario}",
            f"DMO             {self.dmo_name}",
            f"appreciation    {self.appreciation:.4f}",
            f"budget spent    {spent} ({share})",
            f"allocation      {np.round(np.asarray(self.allocation, dtype=float), 2).tolist()}",
            f"calc. time      {self.calculation_time:.2f} s",
            f"evaluations     {self.n_function_evals if self.n_function_evals is not None else 'n/a'}",
            f"run at          {self.timestamp}",
        ]
        return "\n".join(lines)


class BaseSolver:
    """What every solver needs: a budget, its own decision-maker option, and a feasible answer.

    A solver is constructed on a case (``input_dict`` + ``output_dict``) and run through
    :meth:`solve`. Solvers mutate ``input_dict`` in exactly two places: registering their
    decision-maker option (:meth:`_prepare_input_dict`) and writing the winning allocation back
    to it (:meth:`_write_back_result`). Everything in between goes through the free functions at
    the top of this module, which never mutate the case.
    """

    #: Name of the decision-maker option this solver writes its answer to.
    default_dmo_name = "Optimized"
    #: Name of the method as reported on :class:`OptimizationResult`.
    method_name = "base_solver"
    #: Short label used when a configured base name is extended with the method.
    method_label = "base_solver"

    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self._k = len(input_dict["internal_variable_inputs"])
        # Appreciation boundaries once frozen; see _freeze_boundaries.
        self._frozen_boundaries = None

    @property
    def budget(self):
        """Total budget available to allocate.

        The largest amount any decision-maker option spends. Taking the first option instead
        would read a "do nothing" option (all zeros) as a zero budget.
        """
        values = np.asarray(self.input_dict["decision_makers_option_value"], dtype=float)
        return float(max(np.sum(row) for row in values))

    def solve(self, scenario, dmo_name, budget, **kwargs):
        """Run the solver and return an :class:`OptimizationResult`. Implemented per solver."""
        raise NotImplementedError(f"{type(self).__name__} does not implement solve()")

    def _prepare_input_dict(self, dmo_name, reference_allocation=None):
        """Register the solver's decision-maker option and fix the appreciation boundaries.

        The free evaluation functions need ``dmo_name`` to exist with a feasible row, and the
        appreciation boundaries to be fixed, so that the appreciation curve is identical across
        every evaluation instead of drifting with whichever allocation is on the table.
        Idempotent, so it is safe to call repeatedly with the same name.
        """
        if reference_allocation is None:
            reference_allocation = self.input_dict["decision_makers_option_value"][0].copy()
        if dmo_name not in self.input_dict["decision_makers_options"]:
            self.input_dict["decision_makers_options"] = np.array(
                np.append(self.input_dict["decision_makers_options"], dmo_name), dtype=object
            )
            self.input_dict["decision_makers_option_value"] = np.vstack(
                [self.input_dict["decision_makers_option_value"], np.asarray(reference_allocation)]
            )
        # Float dtype so the winning (generally non-integer) allocation is written back exactly.
        self.input_dict["decision_makers_option_value"] = np.asarray(
            self.input_dict["decision_makers_option_value"], dtype=float
        )

        boundaries = Appreciate(self.input_dict, self.output_dict)._get_start_and_end_points()
        self.input_dict["key_output_automatic"] = np.zeros(len(self.input_dict["key_output_automatic"]), dtype=int)
        self.input_dict["key_output_start"] = np.array([v[0] for v in boundaries.values()])
        self.input_dict["key_output_end"] = np.array([v[1] for v in boundaries.values()])
        self._freeze_boundaries()

    def _freeze_boundaries(self):
        """Cache the appreciation boundaries for the evaluations to come.

        Once ``key_output_automatic`` is zero everywhere the boundaries no longer depend on the
        allocation, yet Appreciate would rebuild them (through a pandas DataFrame) on every
        single evaluation. Recomputed once here, on the already-frozen dictionary, so it is by
        construction the same result every evaluation would have derived.
        """
        self._frozen_boundaries = Appreciate(self.input_dict, self.output_dict)._get_start_and_end_points()

    def _write_back_result(self, dmo_name, allocation):
        """Store the winning allocation on its decision-maker option.

        Downstream consumers (visuals, reports, the front end) read the case, not the result
        object, so the answer has to land in ``input_dict`` as a regular option.
        """
        idx = np.where(self.input_dict["decision_makers_options"] == dmo_name)[0][0]
        self.input_dict["decision_makers_option_value"][idx] = np.asarray(allocation, dtype=float)

    def _build_result(self, dmo_name, scenario, allocation, appreciation, budget, started_at, **diagnostics):
        """Assemble an :class:`OptimizationResult` with the fields every solver reports."""
        allocation = np.asarray(allocation, dtype=float)
        return OptimizationResult(
            method=self.method_name,
            dmo_name=dmo_name,
            scenario=scenario,
            allocation=allocation,
            appreciation=float(appreciation),
            budget=float(budget),
            budget_spent=float(np.sum(allocation)) if np.all(np.isfinite(allocation)) else float("nan"),
            calculation_time=time.perf_counter() - started_at,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **diagnostics,
        )

    def _objective(self, x, scenario, dmo_name, eval_counter):
        """Negated appreciation (scipy minimizes); ``eval_counter`` counts calls."""
        eval_counter[0] += 1
        return -score_allocation(self.input_dict, x, scenario, dmo_name, self._frozen_boundaries)

    def find_dict_values(self, scenario):
        """
        This function retrieves values based on the input and output dictionaries.
        """
        # Identify the decision-maker's option (DMO) with the highest appreciation in the given scenario
        dmo_name = self.output_dict[scenario]["highest_weighted_dmo"]

        # Identify the highest appreciation of that DMO
        max_appreciated_value = self.output_dict[scenario][dmo_name]["decision_makers_option_appreciation"]

        # Identify the distibution of that DMO
        decision_maker_options = self.input_dict["decision_makers_option_value"][
            np.where(self.input_dict["decision_makers_options"] == dmo_name)[0][0]
        ]

        best_dmo_data = {
            "dmo_name": dmo_name,
            "decision_maker_options": decision_maker_options,
            "max_appreciated_value": max_appreciated_value,
        }

        # Sum the values for this DMO (this represents the total investment)
        max_investment = sum(decision_maker_options)

        return best_dmo_data, max_investment

    def _settle_incumbent(self, dmo_name, scenario, allocation, appreciation):
        """
        This function applies the rule every solver shares: an optimizer may not
        report an answer worse than a decision-maker option the case already has.

        If nothing the solver found beats the best-performing existing option,
        that option is the answer and the optimizer's own option mirrors it.
        :param dmo_name: the solver's own decision-maker option name
        :param scenario: the scenario being solved
        :param allocation: the best allocation the solver found
        :param appreciation: the appreciation of that allocation
        :return: the winning option name, allocation and appreciation
        """
        best_dmo_data, _ = self.find_dict_values(scenario)
        incumbent_value = float(best_dmo_data["max_appreciated_value"])
        if not np.isfinite(appreciation) or appreciation <= incumbent_value:
            allocation = np.asarray(best_dmo_data["decision_maker_options"], dtype=float)
            self._write_back_result(dmo_name, allocation)
            return best_dmo_data["dmo_name"], allocation, incumbent_value
        return dmo_name, np.asarray(allocation, dtype=float), float(appreciation)

    @staticmethod
    def _project_capped_simplex(x, budget):
        """Pull a point back into ``{x >= 0, sum(x) <= budget}``.

        Solvers satisfy their constraints only to their own tolerance, while everything
        downstream assumes a strictly feasible allocation. Clip negatives and rescale an
        over-budget sum; on a converged solution this is a correction of order 1e-8.
        """
        x = np.clip(np.asarray(x, dtype=float), 0.0, None)
        total = float(np.sum(x))
        if total > budget:
            x = x * (budget / total)
        return x

    @staticmethod
    def _project_budget_face(x, budget):
        """Pull a point back onto the budget face ``{x >= 0, sum(x) = budget}``.

        The equality-mode counterpart of :meth:`_project_capped_simplex`, used when a solver
        runs with ``spend_all=True``: negatives are clipped and the sum is rescaled to the
        budget exactly, in either direction. A point that clips to all zeros carries no
        direction to rescale, so it falls back to the equal split.
        """
        x = np.clip(np.asarray(x, dtype=float), 0.0, None)
        total = float(np.sum(x))
        if total <= 0.0:
            return np.full(x.size, budget / x.size)
        return x * (budget / total)


class GridSearch(BaseSolver):
    """Enumerate a lattice of allocations and keep the best combination.

    With ``spend_all=True`` (the default) the lattice covers the budget face ``sum(x) = B``:
    only combinations that spend the budget exactly. With ``spend_all=False`` it covers the
    capped simplex ``sum(x) <= B``, so an optimum that leaves part of the budget unspent is
    inside the search space.

    The solver has two modes. Under ``max_combinations`` the step size is coarsened until the
    number of combinations stays under that ceiling and the whole lattice is evaluated once; on
    the budget face the true cost is higher than the ceiling, because every combination is
    expanded into all its distinct permutations. Under ``max_calculation_time`` the ceiling is
    ignored: the solver evaluates ever finer lattices, halving the step each round and skipping
    points it already evaluated, until the time runs out.
    """

    default_dmo_name = "Optimized (grid)"
    method_name = "grid"
    method_label = "grid"

    def solve(
        self,
        scenario,
        dmo_name,
        budget=None,
        *,
        max_combinations=60000,
        max_calculation_time=None,
        spend_all=True,
        **_ignored,
    ):
        """Enumerate the lattice for ``scenario`` and write back the best allocation.

        :param scenario: scenario name (must be in input_dict["scenarios"]).
        :param dmo_name: name under which the winning allocation is written back.
        :param budget: accepted for a uniform solver signature but unused. Grid search derives
            its own total from the best-performing decision-maker option.
        :param max_combinations: upper bound on the number of combinations to build. Only used
            when no ``max_calculation_time`` is given.
        :param max_calculation_time: seconds the run may take. When given, ``max_combinations``
            is ignored: the solver evaluates ever finer lattices, halving the step each round,
            until the time runs out. See :meth:`_refine_within_time`.
        :param spend_all: when True (the default), the lattice covers the budget face
            ``sum(x) = B``; when False, the capped simplex ``sum(x) <= B``.
        :return: an :class:`OptimizationResult`.
        """
        started_at = time.perf_counter()
        best_dmo_data, max_investment = self.find_dict_values(scenario)
        self._prepare_input_dict(dmo_name, best_dmo_data["decision_maker_options"])

        if max_investment <= 0:
            # A zero budget leaves nothing to allocate; the incumbent rule answers directly.
            winning_dmo, best_allocation, best_appreciation = self._settle_incumbent(
                dmo_name, scenario, np.zeros(self._k), float("nan")
            )
            return self._build_result(
                dmo_name=winning_dmo,
                scenario=scenario,
                allocation=best_allocation,
                appreciation=best_appreciation,
                budget=max_investment,
                started_at=started_at,
                n_function_evals=0,
            )

        if max_calculation_time is not None:
            best_allocation, best_appreciation, n_evals, levels = self._refine_within_time(
                scenario, dmo_name, max_investment, started_at, max_calculation_time, spend_all=spend_all
            )
        else:
            scaled_max_investment = self.scale_max_investment(max_investment)
            step_size = self.calculate_step_size(
                max_investment, scaled_max_investment, self._k, max_combinations, spend_all=spend_all
            )
            combinations = self.generate_combinations(max_investment, step_size, self._k, spend_all=spend_all)

            # Evaluate and appreciate without changing self.input_dict during the loop. Only the
            # best result is written back after the loop finishes.
            best_allocation = None
            best_appreciation = -np.inf
            for combination in combinations:
                allocation = np.array(combination)
                if len(allocation) != self._k:
                    continue
                appreciation = score_allocation(
                    self.input_dict, allocation, scenario, dmo_name, self._frozen_boundaries
                )
                if appreciation > best_appreciation:
                    best_appreciation = appreciation
                    best_allocation = allocation
            n_evals, levels = len(combinations), []

        if best_allocation is not None:
            self._write_back_result(dmo_name, best_allocation)
        winning_dmo, best_allocation, best_appreciation = self._settle_incumbent(
            dmo_name, scenario, best_allocation, best_appreciation
        )

        return self._build_result(
            dmo_name=winning_dmo,
            scenario=scenario,
            allocation=best_allocation,
            appreciation=best_appreciation,
            budget=max_investment,
            started_at=started_at,
            n_function_evals=n_evals,
            per_start_results=levels,
        )

    def _refine_within_time(
        self, scenario, dmo_name, max_investment, started_at, max_calculation_time, spend_all=True
    ):
        """
        This function evaluates ever finer lattices until the time budget runs out.

        The first round uses a step of half the budget, and every next round halves the
        step again, so the answer is available at any moment and only sharpens with time.
        Halving nests the lattices: every point of a round is also a point of the next,
        finer round, and :meth:`refinement_points` skips those so no allocation is ever
        evaluated twice. The clock is checked before every evaluation, and the incumbent
        so far is the answer when it runs out.
        :param scenario: the scenario being solved
        :param dmo_name: the solver's own decision-maker option name
        :param max_investment: the budget being allocated
        :param started_at: the ``time.perf_counter()`` the run started at
        :param max_calculation_time: the seconds available to the run
        :return: the best allocation, its appreciation, the evaluation count and a
            per-round trace of step size, new points and incumbent
        """
        deadline = started_at + float(max_calculation_time)
        best_allocation, best_appreciation = None, -np.inf
        n_evals, levels, units = 0, [], 2

        while time.perf_counter() < deadline:
            step_size = max_investment / units
            new_points = 0
            first_round = units == 2
            for point in self.refinement_points(units, self._k, include_all=first_round, spend_all=spend_all):
                if time.perf_counter() >= deadline:
                    break
                allocation = np.array(point, dtype=float) * step_size
                appreciation = score_allocation(
                    self.input_dict, allocation, scenario, dmo_name, self._frozen_boundaries
                )
                n_evals += 1
                new_points += 1
                if appreciation > best_appreciation:
                    best_appreciation = appreciation
                    best_allocation = allocation
            levels.append({"step_size": step_size, "new_points": new_points, "best": float(best_appreciation)})
            units *= 2

        return best_allocation, best_appreciation, n_evals, levels

    @staticmethod
    def refinement_points(units, parts, include_all, spend_all=True):
        """
        This function yields the lattice points of one refinement round, in units of the step.

        The lattice at ``units`` steps is every tuple of ``parts`` non-negative integers
        summing to ``units`` (``spend_all=True``) or to at most ``units``
        (``spend_all=False``). When ``include_all`` is False the all-even tuples are
        skipped: halving the step doubles every count, so a point whose counts are all
        even is a point of the previous, coarser round and has already been evaluated. On
        the capped lattice the same rule holds, because the implicit slack count is even
        whenever the spent counts are (the total is a power of two).
        :param units: the resolution, in steps, of the budget
        :param parts: the number of internal variable inputs
        :param include_all: whether this is the first round, which has no previous round
        :param spend_all: whether the lattice covers the budget face or the capped simplex
        :return: a generator of integer tuples of length ``parts``
        """
        compositions = GridSearch._face_compositions if spend_all else GridSearch._bounded_compositions
        for point in compositions(units, parts):
            if include_all or any(count % 2 for count in point):
                yield point

    @staticmethod
    def _face_compositions(units, parts):
        """
        This function yields every tuple of ``parts`` non-negative integers summing to
        exactly ``units``: the lattice points of the budget face, generated directly.
        :param units: the resolution, in steps, of the budget
        :param parts: the number of internal variable inputs
        :return: a generator of integer tuples of length ``parts``
        """
        if parts == 1:
            yield (units,)
            return
        for head in range(units + 1):
            for tail in GridSearch._face_compositions(units - head, parts - 1):
                yield (head,) + tail

    @staticmethod
    def _bounded_compositions(units, parts):
        """
        This function yields every tuple of ``parts`` non-negative integers summing to at
        most ``units``: the lattice points of the capped simplex.
        :param units: the resolution, in steps, of the budget
        :param parts: the number of internal variable inputs
        :return: a generator of integer tuples of length ``parts``
        """
        if parts == 0:
            yield ()
            return
        for head in range(units + 1):
            for tail in GridSearch._bounded_compositions(units - head, parts - 1):
                yield (head,) + tail

    @staticmethod
    def scale_max_investment(max_investment):
        """
        This function scales down the maximum investment value to make it more manageable for combinatorial purposes.
        It rounds the investment down to the nearest hundred, taking into account the order of magnitude.
        """
        # Determine the order of magnitude of the investment (in thousands)
        order_of_magnitude = math.floor(math.log10(abs(max_investment))) - 3

        # Normalize the value to thousands
        normalized_max_investment = max_investment / (10**order_of_magnitude)

        # Round the value to the nearest hundred
        scaled_max_investment = math.floor(round(normalized_max_investment, 1) / 100) * 100

        return scaled_max_investment

    @staticmethod
    def calculate_step_size(
        max_investment, scaled_max_investment, num_internal_inputs, max_combinations, spend_all=True
    ):
        """
        This function calculates the optimal step size to reduce the number of combinations.
        The goal is to stay under the maximum allowable number of combinations for efficiency.
        The capped lattice holds ``comb(units + k, k)`` points against the face's
        ``comb(units + k - 1, k - 1)``, so the same ceiling yields a slightly coarser step.
        """
        step_size_tmp = 1

        while True:
            # Calculate the number of units with the current step size
            units = scaled_max_investment // step_size_tmp

            # Calculate the number of combinations using binomial coefficient
            if spend_all:
                combinations = comb(units + num_internal_inputs - 1, num_internal_inputs - 1)
            else:
                combinations = comb(units + num_internal_inputs, num_internal_inputs)

            if combinations <= max_combinations and scaled_max_investment % step_size_tmp == 0:
                # If the number of combinations is within the constraints, use this step size
                break

            # Increase the step size if the number of combinations exceeds the limit
            step_size_tmp += 1

        # Scale the step size based on the original max investment
        step_size = max_investment / (scaled_max_investment / step_size_tmp)

        return step_size

    @staticmethod
    def generate_combinations(max_investment, step_size, num_internal_inputs, spend_all=True):
        """
        This function generates the lattice of allocations at the given step: every combination
        whose sum equals ``max_investment`` (``spend_all=True``), or every combination whose sum
        stays at or under it (``spend_all=False``, generated directly).
        """
        if not spend_all:
            units = int(round(max_investment / step_size))
            return [
                tuple(count * step_size for count in point)
                for point in GridSearch._bounded_compositions(units, num_internal_inputs)
            ]

        base_combinations = np.arange(0, max_investment + step_size, step_size)
        valid_combinations = []

        # Generate combinations and filter those that sum to the max investment
        for combination in combinations_with_replacement(base_combinations, num_internal_inputs):
            if sum(combination) == max_investment:
                # Add all unique permutations of the combination
                for perm in set(permutations(combination)):
                    valid_combinations.append(perm)

        return valid_combinations


class SLSQPSolver(BaseSolver):
    """Multi-start sequential least-squares programming on the capped simplex.

    Treats the allocation problem as a continuous nonlinear program and solves it from several
    random starting points, keeping the best answer. Fast and accurate when the appreciation
    surface has a single optimum; when it has more than one, a start can settle in the wrong one,
    which is what :class:`BasinHoppingSolver` addresses.

    The budget is an upper bound by default, not an equality: under-spending could be feasible. That
    matters on surfaces where spending the whole budget lowers appreciation. Where it does not,
    the constraint binds and the solution spends everything anyway. ``spend_all=True`` turns
    the bound into an equality, so every solution spends the budget exactly.
    """

    default_dmo_name = "Optimized (SLSQP)"
    method_name = "slsqp"
    method_label = "SLSQP"

    def solve(
        self,
        scenario,
        dmo_name,
        budget,
        *,
        reference_allocation=None,
        n_starts=100,
        seed=None,
        spend_all=False,
        max_calculation_time=None,
        **_ignored,
    ):
        """Run ``n_starts`` local solves and write back the best allocation.

        :param scenario: scenario name (must be in input_dict["scenarios"]).
        :param budget: total allocation budget (upper bound: sum(x) <= budget).
        :param dmo_name: name under which the winning allocation is written back.
        :param reference_allocation: feasible allocation used to seed the new option row
            (only when registering); defaults to the first existing option's row.
        :param n_starts: number of random multi-starts.
        :param seed: RNG seed for reproducible starts.
        :param spend_all: when True, the budget is spent exactly (sum(x) = budget) instead
            of being an upper bound.
        :param max_calculation_time: seconds the run may take: no new start begins once the
            time is spent, and the best answer so far stands (None = no limit).
        :return: an :class:`OptimizationResult` with per-start diagnostics.
        """
        self._prepare_input_dict(dmo_name, reference_allocation)
        starts = self._dirichlet_starts(n_starts, budget, seed=seed)
        eval_counter = [0]
        started_at = time.perf_counter()
        deadline = None if max_calculation_time is None else started_at + float(max_calculation_time)

        per_start = []
        best_x = None
        best_neg_f = np.inf

        for i, x0 in enumerate(starts):
            if deadline is not None and time.perf_counter() >= deadline:
                break
            res = self._slsqp_from_start(
                x0, scenario, dmo_name, budget, eval_counter, spend_all=spend_all, deadline=deadline
            )
            per_start.append(
                {
                    "i": i,
                    "x0": np.asarray(x0),
                    "x": np.asarray(res.x),
                    "appreciation": float(-res.fun),
                    "success": bool(res.success),
                    "nit": int(res.nit),
                    "message": str(res.message),
                }
            )
            if res.fun < best_neg_f:
                best_neg_f = res.fun
                best_x = np.asarray(res.x)

        if best_x is not None:
            self._write_back_result(dmo_name, best_x)

        found_x = best_x if best_x is not None else np.full(self._k, np.nan)
        found_f = -best_neg_f if best_x is not None else float("nan")
        winning_dmo, found_x, found_f = self._settle_incumbent(dmo_name, scenario, found_x, found_f)

        return self._build_result(
            dmo_name=winning_dmo,
            scenario=scenario,
            allocation=found_x,
            appreciation=found_f,
            budget=budget,
            started_at=started_at,
            n_starts=len(per_start),
            n_converged=sum(1 for r in per_start if r["success"]),
            n_function_evals=eval_counter[0],
            per_start_results=per_start,
        )

    def _dirichlet_starts(self, n_starts, budget, seed=None):
        """Random starting points on the budget face, ``Dirichlet(1, ..., 1) * budget``.

        These lie on sum(x) = B, which is feasible under sum(x) <= B. A solve can still move
        into the interior when the gradient favours under-spending.
        """
        rng = np.random.default_rng(seed)
        return rng.dirichlet(np.ones(self._k), size=n_starts) * budget

    def _objective_z(self, z, scenario, dmo_name, eval_counter, budget):
        """:meth:`BaseSolver._objective` in budget-normalised coordinates, ``x = budget * z``."""
        return self._objective(np.asarray(z, dtype=float) * budget, scenario, dmo_name, eval_counter)

    def _slsqp_minimizer_kwargs(self, scenario, dmo_name, eval_counter, budget, spend_all=False, deadline=None):
        """The SLSQP configuration shared by a single solve and by every hop of a hopping run.

        The solve runs in normalised coordinates, ``x = B * z``, on the unit capped simplex.
        SLSQP starts from an identity Hessian approximation and uses absolute tolerances, so on
        raw budgets in the millions its first trial step is microscopic relative to the variable
        scale and the improvement test aborts at the start point: the solver "converges" without
        moving. Normalising makes solver behaviour independent of the budget scale.

        scipy reads ``ineq`` constraints as ``fun(z) >= 0``, hence ``1 - sum(z) >= 0``, and
        ``eq`` constraints as ``fun(z) == 0``, so the same function serves both modes.

        A ``deadline`` (a ``time.perf_counter()`` value) is enforced through scipy's
        callback: it runs after every iteration and raises ``StopIteration`` once the time
        is spent, so a running solve stops within one iteration of its deadline instead of
        finishing first.
        """
        kwargs = {
            "method": "SLSQP",
            "bounds": [(0.0, 1.0)] * self._k,
            "constraints": ({"type": "eq" if spend_all else "ineq", "fun": lambda z: float(1.0 - np.sum(z))},),
            "args": (scenario, dmo_name, eval_counter, float(budget)),
            "options": {"ftol": 1e-6, "maxiter": 100, "disp": False, "eps": 1e-6},
        }
        if deadline is not None:

            def _stop_at_deadline(*_args, **_kwargs):
                if time.perf_counter() >= deadline:
                    raise StopIteration

            kwargs["callback"] = _stop_at_deadline
        return kwargs

    def _slsqp_from_start(self, x0, scenario, dmo_name, budget, eval_counter, spend_all=False, deadline=None):
        """Single SLSQP solve from ``x0``; ``res.x`` is mapped back to allocation units."""
        minimizer_kwargs = self._slsqp_minimizer_kwargs(
            scenario, dmo_name, eval_counter, budget, spend_all=spend_all, deadline=deadline
        )
        res = minimize(
            self._objective_z,
            np.asarray(x0, dtype=float) / float(budget),
            **minimizer_kwargs,
        )
        project = self._project_budget_face if spend_all else self._project_capped_simplex
        res.x = project(res.x * float(budget), float(budget))
        return res


class BasinHoppingSolver(SLSQPSolver):
    """SLSQP plus an escape loop, for surfaces with more than one optimum.

    Basin-hopping (Wales & Doye, 1997) alternates a local solve with a random jump: it solves,
    kicks the solution somewhere else in the feasible set, solves again, and accepts or rejects
    the new optimum by the Metropolis rule. Because the local solve is SLSQP, this is really
    SLSQP-hopping: same model, same feasible set, wrapped in a search for other optima.

    That is what it buys and what it costs. On a surface with one optimum it returns what SLSQP
    already found, for many times the work. On a surface with several it finds optima that
    multi-start SLSQP does not reach.
    """

    default_dmo_name = "Optimized (basin-hopping)"
    method_name = "basin_hopping"
    method_label = "basin-hopping"

    class _RandomFeasibleHop:  # pylint: disable=too-few-public-methods
        """The jump between two local solves, landing inside the feasible set.

        ``scipy.optimize.basinhopping`` calls ``take_step(x)`` between local solves. Its default
        jump ignores the feasible set; this one adds a Gaussian kick and then projects back onto
        the capped simplex, or onto the budget face when the solver runs with ``spend_all``, so
        every proposed start is feasible. Stateful (its own RNG, so restarts reproduce) and
        picklable; the ``stepsize`` attribute lets basin-hopping's adaptive step-size control
        tune the kick towards its target acceptance rate.
        """

        def __init__(self, budget, k, rng, step_frac=0.3, spend_all=False):
            self.budget = float(budget)
            self.k = int(k)
            self.rng = rng
            self.stepsize = step_frac * float(budget)
            self.spend_all = bool(spend_all)

        def __call__(self, x):
            x_new = np.asarray(x, dtype=float) + self.rng.normal(scale=self.stepsize, size=self.k)
            if self.spend_all:
                return BaseSolver._project_budget_face(x_new, self.budget)
            x_new = np.clip(x_new, 0.0, self.budget)
            total = x_new.sum()
            if total > self.budget:
                x_new = x_new * (self.budget / total)
            return x_new

    def solve(
        self,
        scenario,
        dmo_name,
        budget,
        *,
        reference_allocation=None,
        n_hops=100,
        n_starts=1,
        temperature=1.0,
        step_frac=0.3,
        seed=None,
        spend_all=False,
        max_calculation_time=None,
        **_ignored,
    ):
        """Run ``n_starts`` hopping chains of ``n_hops`` hops and write back the best allocation.

        :param scenario: scenario name (must be in input_dict["scenarios"]).
        :param budget: allocation budget (upper bound: sum(x) <= budget).
        :param dmo_name: name under which the winning allocation is written back.
        :param reference_allocation: feasible allocation seeding the new option row.
        :param n_hops: hops per chain.
        :param n_starts: number of independent chains, each from its own random start.
        :param temperature: Metropolis acceptance temperature.
        :param step_frac: jump size as a fraction of the budget.
        :param seed: RNG seed for reproducible starts, jumps and acceptance.
        :param spend_all: when True, the budget is spent exactly (sum(x) = budget) instead
            of being an upper bound; the local solves and the jumps both stay on the face.
        :param max_calculation_time: seconds the run may take: the chain stops hopping and no
            new chain starts once the time is spent, and the best answer so far stands
            (None = no limit).
        :return: an :class:`OptimizationResult` with per-chain diagnostics.
        """
        self._prepare_input_dict(dmo_name, reference_allocation)
        starts = self._dirichlet_starts(n_starts, budget, seed=seed)
        eval_counter = [0]
        started_at = time.perf_counter()
        deadline = None if max_calculation_time is None else started_at + float(max_calculation_time)

        # Hopping runs in the same normalised coordinates as the local solve, which also makes
        # step_frac independent of the case's budget scale.
        minimizer_kwargs = self._slsqp_minimizer_kwargs(
            scenario, dmo_name, eval_counter, budget, spend_all=spend_all, deadline=deadline
        )
        project = self._project_budget_face if spend_all else self._project_capped_simplex

        # scipy stops hopping when the callback returns True, which turns the deadline into a
        # stop between two hops rather than an estimate of how many hops would have fitted.
        def _deadline_reached(_x, _f, _accept):
            return time.perf_counter() >= deadline

        callback = _deadline_reached if deadline is not None else None

        per_start = []
        best_x = None
        best_neg_f = np.inf

        for i, x0 in enumerate(starts):
            if deadline is not None and time.perf_counter() >= deadline:
                break
            if seed is None:
                step_rng, hop_rng = np.random.default_rng(), np.random.default_rng()
            else:
                step_rng, hop_rng = np.random.default_rng([seed, i, 0]), np.random.default_rng([seed, i, 1])
            take_step = self._RandomFeasibleHop(1.0, self._k, step_rng, step_frac=step_frac, spend_all=spend_all)

            res = basinhopping(
                self._objective_z,
                np.asarray(x0, dtype=float) / float(budget),
                niter=n_hops,
                T=temperature,
                minimizer_kwargs=minimizer_kwargs,
                take_step=take_step,
                # ``seed`` rather than ``rng``: scipy only introduced ``rng`` in 1.15, and
                # ``seed`` accepts the same Generator on every version from 1.13 onwards.
                seed=hop_rng,
                callback=callback,
            )
            x_best_start = project(np.asarray(res.x) * float(budget), float(budget))
            per_start.append(
                {
                    "i": i,
                    "x0": np.asarray(x0),
                    "x": x_best_start,
                    "appreciation": float(-res.fun),
                    "success": bool(res.lowest_optimization_result.success),
                    "nit": int(res.nit),
                    "message": str(res.message[0]) if isinstance(res.message, (list, tuple)) else str(res.message),
                }
            )
            if res.fun < best_neg_f:
                best_neg_f = res.fun
                best_x = x_best_start

        if best_x is not None:
            self._write_back_result(dmo_name, best_x)

        found_x = best_x if best_x is not None else np.full(self._k, np.nan)
        found_f = -best_neg_f if best_x is not None else float("nan")
        winning_dmo, found_x, found_f = self._settle_incumbent(dmo_name, scenario, found_x, found_f)

        return self._build_result(
            dmo_name=winning_dmo,
            scenario=scenario,
            allocation=found_x,
            appreciation=found_f,
            budget=budget,
            started_at=started_at,
            n_starts=len(per_start),
            n_converged=sum(1 for r in per_start if r["success"]),
            n_function_evals=eval_counter[0],
            per_start_results=per_start,
        )


class Optimize:
    """
    The Optimize class finds the distribution of internal input values that maximizes the
    appreciation value of decision-maker options.

    :meth:`run` dispatches to one of the solver classes in this module and returns an
    :class:`OptimizationResult`, which carries the allocation together with how long the run
    took, how many evaluations it cost and how much of the budget it spent.
    :meth:`optimize_single_scenario` runs the same thing behind a frozen contract and returns
    the updated input dictionary instead.
    """

    #: Method name to solver class, for :meth:`run`.
    METHOD_REGISTRY = {
        "grid": GridSearch,
        "slsqp": SLSQPSolver,
        "basin_hopping": BasinHoppingSolver,
    }

    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict

    @property
    def budget(self):
        """Total budget available to allocate; see :attr:`BaseSolver.budget`."""
        return BaseSolver(self.input_dict, self.output_dict).budget

    def run(
        self, scenario, method="basin_hopping", *, dmo_name=None, budget=None, method_kwargs=None, **shared_kwargs
    ):
        """Run one or several solvers and return the best result.

        Solver settings can be given in two ways. Keyword arguments go to every method that
        runs, which is the convenient form for a single method or for a setting they share
        such as ``seed``. ``method_kwargs`` addresses one method by name, which is what you
        need when two methods take different parameters::

            case_optimizer.run("Base case", method="slsqp", n_starts=50)
            case_optimizer.run(
                "Base case",
                method=["grid", "slsqp"],
                seed=1,
                method_kwargs={"grid": {"max_combinations": 1000}, "slsqp": {"n_starts": 50}},
            )

        :param scenario: scenario name (must be in input_dict["scenarios"]).
        :param method: a single method name or a list of names; the default is
            ``"basin_hopping"``. Supported: ``"grid"``, ``"slsqp"``, ``"basin_hopping"``.
            Unknown names raise ``NotImplementedError``.
        :param dmo_name: name for the optimizer's decision-maker option. Each solver has its
            own default; a name given here is extended with the method and the scenario.
        :param budget: total allocation budget; inferred from the case if None.
        :param method_kwargs: settings per method, ``{method name: {setting: value}}``. These
            win over the shared keyword arguments. An entry for a method that is not running
            raises ``NotImplementedError``, so a typo cannot pass unnoticed.
        :param shared_kwargs: settings passed to every method that runs.
        :return: a single :class:`OptimizationResult`. For a list of methods, every method's
            appreciation and allocation is printed and the best is returned; only the winning
            allocation is written back to the case.
        """
        if budget is None:
            budget = self.budget

        methods = [method] if isinstance(method, str) else list(method)
        for name in methods:
            if name not in self.METHOD_REGISTRY:
                raise NotImplementedError(f"method={name!r} not implemented. Supported: {list(self.METHOD_REGISTRY)}")
        for name in method_kwargs or {}:
            if name not in methods:
                raise NotImplementedError(
                    f"method_kwargs holds settings for {name!r}, which is not among the methods being run: {methods}"
                )

        if len(methods) == 1:
            # A single method runs on this case, so the winning option and the frozen
            # boundaries land here rather than on a copy.
            solver = self.METHOD_REGISTRY[methods[0]](self.input_dict, self.output_dict)
            name = self._dmo_name_for(dmo_name, solver, scenario)
            settings = self._settings_for(methods[0], shared_kwargs, method_kwargs)
            result = solver.solve(scenario, dmo_name=name, budget=budget, **settings)
            self.input_dict = solver.input_dict
            return result
        return self._run_several(methods, scenario, dmo_name, budget, shared_kwargs, method_kwargs)

    @staticmethod
    def _settings_for(method, shared_kwargs, method_kwargs):
        """The settings one method runs with: the shared ones, overridden by its own."""
        return {**shared_kwargs, **(method_kwargs or {}).get(method, {})}

    @staticmethod
    def _configured_dmo_name(input_dict):
        """The optimizer name configured on the case, or None.

        A case can carry an ``Optimize_DMO_name`` entry in its configuration sheet. When the
        caller does not pass a name, that entry is the base of the option name. A missing
        sheet, a missing entry or an empty (NaN) value all mean no configured name.
        """
        configurations = input_dict.get("configurations")
        if configurations is None:
            return None
        matches = np.where(np.asarray(configurations) == "Optimize_DMO_name")[0]
        if not matches.size:
            return None
        value = input_dict["configuration_value"][matches[0]]
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        return str(value)

    def _dmo_name_for(self, dmo_name, solver, scenario):
        """Name the decision-maker option a :meth:`run` result is written back to.

        The name always records the scenario it was optimized for: an allocation is only
        optimal for that scenario, so optimizing the same case for two scenarios has to
        produce two options rather than overwrite one. It also records the method, so a case
        optimized twice shows which solver produced which allocation.
        """
        if dmo_name:
            return f"{dmo_name} ({solver.method_label}) ({scenario})"
        configured = self._configured_dmo_name(self.input_dict)
        if configured:
            return f"{configured} ({solver.method_label}) ({scenario})"
        return f"{solver.default_dmo_name} ({scenario})"

    def _run_several(self, methods, scenario, dmo_name, budget, shared_kwargs, method_kwargs):
        """Run every method in ``methods`` and return the best result.

        Each method runs on its own copy of the case so they do not see each other's added
        decision-maker options. All are printed, then the winner's case is adopted.
        """
        runs = []
        for chosen in methods:
            solver = self.METHOD_REGISTRY[chosen](copy.deepcopy(self.input_dict), self.output_dict)
            name = self._dmo_name_for(dmo_name, solver, scenario)
            settings = self._settings_for(chosen, shared_kwargs, method_kwargs)
            res = solver.solve(scenario, dmo_name=name, budget=budget, **settings)
            print(f"[{chosen}] appreciation={res.appreciation:.6f} allocation={np.asarray(res.allocation).tolist()}")
            runs.append((res, solver))

        best_res, best_solver = max(runs, key=lambda pair: pair[0].appreciation)
        self.input_dict = best_solver.input_dict
        return best_res

    def optimize_single_scenario(self, scenario, dmo_name, max_combinations=60000, **kwargs):
        """Optimize one scenario and return the updated input dictionary.

        This is the entry point the Papilio front end calls, positionally and with a
        combination ceiling from the grid-search era, so its contract is frozen: it returns
        the updated ``input_dict`` and nothing else. The run itself is method agnostic and uses
        the package defaults (basin-hopping, ``spend_all=True``, a 60-second time limit);
        ``max_combinations`` is forwarded and only matters when a caller picks
        ``method="grid"`` explicitly. Keyword arguments reach the solver, so the defaults can be
        overridden per call.
        """
        kwargs.setdefault("method", "basin_hopping")
        kwargs.setdefault("spend_all", True)
        kwargs.setdefault("max_calculation_time", 60)
        self.run(scenario, dmo_name=dmo_name, max_combinations=max_combinations, **kwargs)
        return self.input_dict
