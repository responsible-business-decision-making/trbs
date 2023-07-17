# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""This module contains all tests for the Evaluate() class"""

import pytest
import numpy as np
from core.evaluate import Evaluate, EvaluationError
from core.utils import round_all_dict_values


@pytest.fixture(name="evaluate_beerwiser")
def fixture_evaluate_beerwiser():
    """
    This fixture initialises a Beerwiser case. Input dictionary is created using repr(case.input_dict) on 17/07/2023.
    :return Evaluate(): an Evaluate class for Beerwiser
    """
    input_dict = {
        "configurations": np.array(["use_theme_weights"], dtype=object),
        "configuration_value": np.array([0]),
        "key_outputs": np.array(
            ["Accidents reduction", "Water use reduction", "Production cost reduction"], dtype=object
        ),
        "key_output_unit": np.array(["#/year", "hl/year", "%"], dtype=object),
        "key_output_theme": np.array(["People", "Planet", "Profit"], dtype=object),
        "themes": np.array(["People", "Planet", "Profit"], dtype="<U32"),
        "key_output_minimum": np.array([np.nan, np.nan, np.nan]),
        "key_output_maximum": np.array([np.nan, np.nan, np.nan]),
        "key_output_monetary": np.array([0, 0, 0]),
        "key_output_smaller_the_better": np.array([0, 0, 0]),
        "key_output_linear": np.array([1, 1, 0]),
        "key_output_automatic": np.array([1, 1, 1]),
        "key_output_start": np.array([np.nan, np.nan, np.nan]),
        "key_output_end": np.array([np.nan, np.nan, np.nan]),
        "key_output_threshold": np.array([np.nan, np.nan, np.nan]),
        "decision_makers_options": np.array(
            ["Equal spread", "Focus on training", "Focus on water recycling"], dtype=object
        ),
        "internal_variable_inputs": np.array(
            ["Invest in training of employees", "Invest in water recycling"], dtype=object
        ),
        "decision_makers_option_value": np.array([[150000, 150000], [250000, 50000], [50000, 250000]]),
        "scenarios": np.array(["Base case", "Optimistic", "Pessimistic"], dtype=object),
        "external_variable_inputs": np.array(["Cost of accident", "Effectiveness water recycling"], dtype=object),
        "scenario_value": np.array([[1.5e04, 9.8e-01], [1.2e04, 1.0e00], [2.0e04, 9.0e-01]]),
        "fixed_inputs": np.array(
            ["# employees", "Current # accidents", "Current production cost", "Current water use", "Water unit cost"],
            dtype=object,
        ),
        "fixed_input_value": np.array([5.0e02, 5.1e01, 7.5e06, 1.5e07, 5.0e-02]),
        "fixed_input_unit": np.array(["#", "#", "$", "hl", "$"], dtype=object),
        "intermediates": np.array(
            [
                "Accidents reduction %",
                "Water use reduction % when effective",
                "Water use reduction %",
                "Production cost reduction $",
                "Cost of training per employee",
                "New water use",
                "New # accidents",
            ],
            dtype=object,
        ),
        "intermediate_unit": np.array(["%", "%", "%", "$", "$", "hl/year", "#/year"], dtype=object),
        "intermediate_minimum": np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]),
        "intermediate_maximum": np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]),
        "dependencies": np.array([0, 1, 8, 9, 11, 2, 3, 4, 6, 10, 5, 12, 7]),
        "destination": np.array(
            [
                "Accidents reduction %",
                "Water use reduction % when effective",
                "Cost of training per employee",
                "New # accidents",
                "New water use",
                "Water use reduction %",
                "Accidents reduction",
                "Water use reduction",
                "Production cost reduction $",
                "New # accidents",
                "Production cost reduction $",
                "New water use",
                "Production cost reduction",
            ],
            dtype=object,
        ),
        "argument_1": np.array(
            [
                "Invest in training of employees",
                "Invest in water recycling",
                "Invest in training of employees",
                "Current # accidents",
                "Current water use",
                "Water use reduction % when effective",
                "Current # accidents",
                "Water use reduction %",
                "Accidents reduction",
                "Accidents reduction",
                "Water use reduction",
                "Water use reduction",
                "Production cost reduction $",
            ],
            dtype=object,
        ),
        "argument_2": np.array(
            [
                "",
                "",
                "# employees",
                "",
                "",
                "Effectiveness water recycling",
                "Accidents reduction %",
                "Current water use",
                "Cost of accident",
                "",
                "Water unit cost",
                "",
                "Current production cost",
            ],
            dtype=object,
        ),
        "operator": np.array(
            ["Squeezed *", "Squeezed *", "/", "*", "*", "*", "*", "*", "*", "-*", "*", "-*", "/"], dtype=object
        ),
        "maximum_effect": np.array(
            [0.48, 0.5, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        ),
        "accessibility": np.array(
            [0.95, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        ),
        "probability_of_success": np.array(
            [0.9, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        ),
        "saturation_point": np.array(
            [
                300000.0,
                275000.0,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            ]
        ),
        "theme_weight": np.array([2, 1, 3]),
        "key_output_weight": np.array([2.0, 1.0, 3.0]),
        "scenario_weight": np.array([2.0, 1.0, 3.0]),
    }
    return Evaluate(input_dict)


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
        "": 1,
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
    "arg1, arg2, args, expected_result",
    [
        (
            10,
            15,
            {"saturation_point": 30, "accessibility": 0.9, "probability_of_success": 0.80, "maximum_effect": 0.5},
            0.12,
        ),
        (
            10,
            15,
            {"saturation_point": 5, "accessibility": 0.95, "probability_of_success": 0.85, "maximum_effect": 0.7},
            0.565,
        ),
    ],
)
def test_squeeze(evaluate_beerwiser, arg1, arg2, args, expected_result):
    """
    This function tests _squeeze to return a correctly calculated values using the Squeezed * operator. Tested for both
    when min(x,y) / saturation_point > 1 and min(x,y) / saturation_point < 1.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    :param arg1: first argument that is used for all operators (including squeezed)
    :param arg2: second argument that is used for all operators (including squeezed)
    :param args: dictionary containing arguments used solely for squeezed
    :param expected_result: expected value of evaluated squeeze function
    """
    result = round(evaluate_beerwiser._squeeze(arg1, arg2, args), 3)
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
