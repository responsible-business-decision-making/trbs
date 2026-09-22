# pylint: disable=W0212

"""
Shared fixtures for the optimizer tests.

``test_optimize_solvers.py`` covers the solver classes reached through ``Optimize.run``, one
section per solver, and ``test_optimize_orchestrator.py`` covers the entry points. Everything
they share in terms of setup lives here.

Every fixture deep-copies the dictionaries from ``params.py``. Those are module-level and a
shallow copy would let one test's allocation leak into the next one's expected values, which
makes a suite that passes as a whole fail when a single file is run on its own.
"""

import copy

import pytest

from vlinder.appreciate import Appreciate
from vlinder.optimize import BaseSolver
from vlinder.trbs import TheResponsibleBusinessSimulator
from vlinder.utils import suppress_print
from .params import INPUT_DICT_BEERWISER, OUTPUT_DICT_BEERWISER

#: Beerwiser's budget: the "Equal spread" option allocates 150000 to each of its two levers.
BEERWISER_BUDGET = 300000.0
#: Appreciation of Beerwiser's global optimum, the clip kink at [25000, 275000].
BEERWISER_OPTIMUM = 65.7115899862911
#: Appreciation of the "Equal spread" option under the base case.
BEERWISER_EQUAL_SPREAD = 65.51984611881377


@pytest.fixture(name="beerwiser_dicts")
def fixture_beerwiser_dicts():
    """A private, fully appreciated copy of Beerwiser's input and output dictionaries.

    ``params.py`` carries only the key output values, so the appreciations, the weights and the
    best option per scenario are derived here. Deriving them makes these tests independent of
    whether another test file happened to run first and fill them in on the shared dictionary.
    """
    input_dict = copy.deepcopy(INPUT_DICT_BEERWISER)
    output_dict = _raw_key_outputs(OUTPUT_DICT_BEERWISER)
    suppress_print(Appreciate(input_dict, output_dict).appreciate_all_scenarios)()
    return input_dict, output_dict


def _raw_key_outputs(output_dict):
    """Rebuild an output dictionary from its key output values alone.

    The dictionaries in ``params.py`` are module-level and shared, so a test file that has
    already run may have left derived entries on them, such as the best option per scenario.
    Appreciating a dictionary that already carries those entries fails, because the appreciation
    pass would treat that name as another option. Rebuilding from the key outputs makes these
    fixtures independent of what ran before them.
    """
    return {
        scenario: {
            dmo: {"key_outputs": dict(values["key_outputs"])}
            for dmo, values in options.items()
            if isinstance(values, dict) and "key_outputs" in values
        }
        for scenario, options in copy.deepcopy(output_dict).items()
    }


@pytest.fixture(name="prepared_solver")
def fixture_prepared_solver(beerwiser_dicts):
    """A solver on Beerwiser with its decision-maker option registered and boundaries frozen.

    Returns a :class:`BaseSolver`, which carries everything the free evaluation functions need
    and nothing solver-specific. Tests that need a particular solver build one on
    ``solver.input_dict``.
    """
    input_dict, output_dict = beerwiser_dicts
    solver = BaseSolver(input_dict, output_dict)
    solver._prepare_input_dict("Test DMO", [150000, 150000])
    return solver


@pytest.fixture(name="beerwiser_appreciated")
def fixture_beerwiser_appreciated():
    """A real Beerwiser case taken through build, evaluate and appreciate."""
    case = TheResponsibleBusinessSimulator("Beerwiser")
    case.build()
    case.evaluate()
    case.appreciate()
    return case
