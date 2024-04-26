# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""This module contains all tests for the Evaluate() class"""
from pathlib import Path
import pytest
from params import INPUT_DICT_BEERWISER
from vlinder.evaluate import Evaluate, EvaluationError
from vlinder.utils import round_all_dict_values
from vlinder.trbs import TheResponsibleBusinessSimulator


@pytest.fixture(name="evaluate_beerwiser")
def fixture_evaluate_beerwiser():
    """
    This fixture initialises a Beerwiser case.
    :return Evaluate(): an Evaluate class for Beerwiser
    """
    return Evaluate(INPUT_DICT_BEERWISER)


@pytest.fixture(name="evaluate_refugee")
def fixture_evaluate_refugee():
    """
    This fixture initialises a Refugee case.
    :return Evaluate(): an Evaluate class for Refugee
    """

    case = TheResponsibleBusinessSimulator("refugee", Path.cwd() / "src/vlinder/data", "xlsx")
    case.build()
    return Evaluate(case.input_dict)


@pytest.fixture(name="evaluate_dsm")
def fixture_evaluate_dsm():
    """
    This fixture initialises a DSM case.
    :return Evaluate(): an Evaluate class for DSM
    """

    case = TheResponsibleBusinessSimulator("DSM", Path.cwd() / "src/vlinder/data")
    case.build()
    return Evaluate(case.input_dict)


@pytest.fixture(name="evaluate_izz")
def fixture_evaluate_izz():
    """
    This fixture initialises a IZZ case.
    :return Evaluate(): an Evaluate class for IZZ
    """

    case = TheResponsibleBusinessSimulator("izz")
    case.build()
    return Evaluate(case.input_dict)


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


@pytest.mark.parametrize("arg, expected_result", [("2", 2.0), ("3.12", 3.12), ("A", 1.25)])
def test_get_value_of_argument(evaluate_beerwiser, arg, expected_result):
    """
    This function tests _get_value_of_argument to return the right value
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    :param arg: value of argument
    :param expected_result: expected result of this single dependency
    """
    evaluate_beerwiser.value_dict = {"A": 1.25}
    result = evaluate_beerwiser._get_value_of_argument(arg)
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


@pytest.mark.parametrize(
    "fixture_name, scenario, dmo, expected_result",
    [
        (
            "evaluate_beerwiser",
            "Optimistic",
            "Focus on water recycling",
            {
                "key_outputs": {
                    "Accidents reduction": 3.49,
                    "Water use reduction": 6818181.82,
                    "Production cost reduction": 0.05,
                }
            },
        ),
        (
            "evaluate_refugee",
            "Base case",
            "Employment & Language",
            {
                "key_outputs": {
                    "Quality of life Ukrainians": 0.07,
                    "Quality of life other refugees": -0.03,
                    "Quality of life inhabitants": -0.05,
                    "Unemployment reduction Ukrainians": 0.21,
                    "Unemployment reduction other refugees": 0.03,
                    "Unemployment reduction inhabitants": 0.01,
                    "Economic impact": 23857682.88,
                }
            },
        ),
        (
            "evaluate_dsm",
            "Base case",
            "Partner RE",
            {
                "key_outputs": {
                    "CAPEX": 0.0,
                    "Energy cost": 4335000.0,
                    "RE %": 0.5,
                    "Carbon footprint reduction": 10140.0,
                    "Actual carbon emission": 10140.0,
                    "Increase in employee engagement score": 0.02,
                    "Increase in employee recommendation rate": 0.01,
                    "Increase in Net Promotor Score": 0,
                    "Increase in brand value": 2149680.0,
                }
            },
        ),
        (
            "evaluate_izz",
            "Optimistic",
            "Social",
            {
                "key_outputs": {
                    "Decrease in absenteeism %": 0.0,
                    "Decrease in staff turnover %": 0.0,
                    "Increase in customer satisfaction": 0.01,
                    "Increase in employee satisfaction": 0.03,
                    "Decrease in absenteeism costs": 18610.66,
                    "Decrease in staff turnover costs": 734.7,
                    "Decrease in wage costs": 11235861.75,
                    "Increase in production capacity": 513.44,
                    "Total investment": 120000.0,
                }
            },
        ),
    ],
)
def test_evaluate_all_dependencies(fixture_name, expected_result, scenario, dmo, request):
    """
    This function tests evaluate_all_dependencies to return a dictionary containing the key_outputs for a given
    scenario and decision_makers_option.
    :param evaluate_beerwiser: an Evaluate() class for Beerwiser
    """
    case = request.getfixturevalue(fixture_name)
    result = case.evaluate_all_dependencies(scenario, dmo)
    rounded_result = round_all_dict_values(result)
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
