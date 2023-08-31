# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""This module contains all tests for the Evaluate() class"""

import pytest
from core.evaluate import Evaluate, EvaluationError
from core.utils import round_all_dict_values
from params import INPUT_DICT_BEERWISER


@pytest.fixture(name="evaluate_beerwiser")
def fixture_evaluate_beerwiser():
    """
    This fixture initialises a Beerwiser case.
    :return Evaluate(): an Evaluate class for Beerwiser
    """
    return Evaluate(INPUT_DICT_BEERWISER)


def test_create_value_dict(evaluate_beerwiser):
    """
    This functions tests _create_value_dict returning a correctly initialized value dictionary, for the
    'optimistic' (=1) scenario with 'focus on water recycling' (=2).
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    evaluate_beerwiser._create_value_dict(1, 2)
    result = evaluate_beerwiser.value_dict
    expected_result = {
        "Accidents reduction": 0,
        "Water use reduction": 0,
        "Production cost reduction": 0,
        "Invest in training of employees": 50000,
        "Invest in water recycling": 250000,
        "Cost of accident": 12000.0,
        "Effectiveness water recycling": 1.0,
        "# employees": 500.0,
        "Current # accidents": 51.0,
        "Current production cost": 7500000.0,
        "Current water use": 15000000.0,
        "Water unit cost": 0.05,
    }

    assert result == expected_result


@pytest.mark.parametrize(
    "key, value, expected_result",
    [
        ("key_output_unit", "hl/year", 1),
        ("decision_makers_options", "Equal spread", 0),
        ("operator", "*", 3),
        ("saturation_point", 275000.0, 1),
    ],
)
def test_find_index(evaluate_beerwiser, key, value, expected_result):
    """
    This function tests _find_index to return the FIRST index of a given key and value of input_dict. Tested for a
    variety of cases: different types of 'value', objects where 'value' occurs once or more than once.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    :param key: key in input_dict
    :param value: value in object of input_dict where index needs to be found
    :param expected_result: expected index that is returned by the test
    """
    result = evaluate_beerwiser._find_index(key, value)
    assert result == expected_result


@pytest.mark.parametrize(
    "arg1, args, expected_result",
    [
        (
            10,
            {"saturation_point": 30, "accessibility": 0.9, "probability_of_success": 0.80, "maximum_effect": 0.5},
            0.12,
        ),
        (
            10,
            {"saturation_point": 5, "accessibility": 0.95, "probability_of_success": 0.85, "maximum_effect": 0.7},
            0.565,
        ),
    ],
)
def test_squeeze(evaluate_beerwiser, arg1, args, expected_result):
    """
    This function tests _squeeze to return a correctly calculated values using the Squeezed * operator. Tested for both
    when min(x,y) / saturation_point > 1 and min(x,y) / saturation_point < 1.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    :param arg1: first argument that is used for all operators (including squeezed)
    :param arg2: second argument that is used for all operators (including squeezed)
    :param args: dictionary containing arguments used solely for squeezed
    :param expected_result: expected value of evaluated squeeze function
    """
    result = round(evaluate_beerwiser._squeeze(arg1, args), 3)
    assert result == expected_result


def test_get_key_outputs(evaluate_beerwiser):
    """
    This function tests _get_key_outputs to return a dictionary of type: {KO1: value, KO2: value, ...}.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    # initialise value dictionary | otherwise key_outputs are not in the value dictionary
    evaluate_beerwiser._create_value_dict(1, 2)
    result = evaluate_beerwiser._get_key_outputs()
    expected_result = {"Accidents reduction": 0, "Water use reduction": 0, "Production cost reduction": 0}
    assert result == expected_result


@pytest.mark.parametrize(
    "arg1, arg2, operator, expected_result",
    [
        (8, 12, "-", -4),
        (22, 19, "+", 41),
        (13, 7, "*", 91),
        (20, 0, "/", 0),
        (99, 9, "/", 11),
        (12, 8, "-*", -96),
        (121, -11, "-/", 11),
        (0, 0, "-/", 0),
        (5, 10, "<", 1),
        (15, 10, ">", 1),
        (10, 10, "<=", 1),
        (5, 10, ">=", 0),
        (2, 3, "min", 2),
        (10, 10.5, "max", 10.5),
    ],
)
def test_evaluate_single_dependency(evaluate_beerwiser, arg1, arg2, operator, expected_result):
    """
    This function tests _evaluate_single_dependency to return the proper value for ALL allowed operators. Also, the
    exemption case for division (division by zero should return zero) is tested.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    :param arg1: value of first argument
    :param arg2: value of second argument
    :param operator: operator needed to calculate result based on the two arguments
    :param expected_result: expected result of this single dependency
    """
    result = evaluate_beerwiser._evaluate_single_dependency(arg1, arg2, operator)
    assert result == expected_result


def test_evaluate_single_dependency_evaluation_error(evaluate_beerwiser):
    """
    This function tests _evaluate_single_dependency to raise an EvaluationError when an undefined operator is used.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    with pytest.raises(EvaluationError) as evaluation_error:
        evaluate_beerwiser._evaluate_single_dependency(3, 8, "/*")
    expected_result = "Evaluation Error: operator /* not available"
    assert str(evaluation_error.value) == expected_result


def test_evaluate_all_dependencies(evaluate_beerwiser):
    """
    This function tests evaluate_all_dependencies to return a dictionary containing the key_outputs for a given
    scenario and decision_makers_option.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """

    result = evaluate_beerwiser.evaluate_all_dependencies("Optimistic", "Focus on water recycling")
    rounded_result = round_all_dict_values(result)
    expected_result = {
        "key_outputs": {
            "Accidents reduction": 3.49,
            "Water use reduction": 6818181.82,
            "Production cost reduction": 0.05,
        }
    }
    assert rounded_result == expected_result


def test_evaluate_selected_scenario_only_structure(evaluate_beerwiser):
    """
    This function tests the STRUCTURE of the dictionary returned by evaluate_selected_scenario(). Only the keys and the
    structure of the values are checked as these values are a result from evaluate_all_dependencies() which is already
    checked above.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    result = evaluate_beerwiser.evaluate_selected_scenario("Optimistic")
    result_structure = {key: type(value) for key, value in result.items()}
    expected_structure = {"Equal spread": dict, "Focus on training": dict, "Focus on water recycling": dict}
    assert result_structure == expected_structure


def test_evaluate_all_scenarios_only_structure(evaluate_beerwiser):
    """
    This function tests the STRUCTURE of the dictionary returned by evaluate_all_scenarios(). Only the keys and the
    structure of the values are checked as these values are a result from evaluate_selected_scenario() which is already
    checked above.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    result = evaluate_beerwiser.evaluate_all_scenarios()
    result_structure = {key: type(value) for key, value in result.items()}
    expected_structure = {"Base case": dict, "Optimistic": dict, "Pessimistic": dict}
    assert result_structure == expected_structure
