# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the Appreciate() class
"""
import pytest
from params import INPUT_DICT_BEERWISER, OUTPUT_DICT_BEERWISER
from vlinder.appreciate import Appreciate
from vlinder.utils import round_all_dict_values, get_values_from_target


@pytest.fixture(name="appreciate_beerwiser")
def fixture_appreciate_beerwiser():
    """
    This fixture initialises a Beerwiser case.
    :return: an Evaluate class for Beerwiser
    """
    return Appreciate(INPUT_DICT_BEERWISER, OUTPUT_DICT_BEERWISER)


def test_get_start_and_end_points(appreciate_beerwiser):
    """
    This function tests _get_start_and_end_points() to return a dictionary with a list containing the min. and max.
    found key output value, over all scenarios.
    :param appreciate_beerwiser:
    """
    result = appreciate_beerwiser._get_start_and_end_points()
    rounded_result = round_all_dict_values(result)
    expected_result = {
        "Accidents reduction": [3.49, 17.44],
        "Water use reduction": [1227272.73, 6818181.82],
        "Production cost reduction": [0.04, 0.05],
    }
    assert rounded_result == expected_result


@pytest.mark.parametrize(
    "value, args, expected_result",
    [
        (10, {"key_output": "Sample A", "key_output_smaller_the_better": 0, "key_output_linear": 1}, 33.33),
        (30, {"key_output": "Sample A", "key_output_smaller_the_better": 1, "key_output_linear": 1}, 0),
        (150, {"key_output": "Sample B", "key_output_smaller_the_better": 1, "key_output_linear": 0}, 15.71),
        (-20, {"key_output": "Sample A", "key_output_smaller_the_better": 0, "key_output_linear": 0}, 0),
        (10, {"key_output": "Sample C", "key_output_smaller_the_better": 0, "key_output_linear": 0}, 0),
    ],
)
def test_appreciate_single_key_output(appreciate_beerwiser, value, args, expected_result):
    """
    This function tests _appreciate_single_key_output to return the correct appreciation value for various combinations
    of arguments.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    :param value: value of the key output
    :param args: arguments needed for appreciation of key output
    :param expected_result: expected appreciation value
    """
    # Set some own start and end points for testing purposes
    appreciate_beerwiser.start_and_end_points = {
        "Sample A": [5, 20],
        "Sample B": [0, 235],
        "Sample C": [10.345, 10.345],
    }
    result = round(appreciate_beerwiser._appreciate_single_key_output(value, args), 2)
    assert result == expected_result


def test_appreciate_single_decision_maker_option(appreciate_beerwiser):
    """
    This function tests aprreciate_single_decision_maker_option to return a dictionary that contains the correct values
    for key output, appreciations and weighted appreciations.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """

    value_dict_in = appreciate_beerwiser.output_dict["Base case"]["Focus on training"]
    appreciate_beerwiser.appreciate_single_decision_maker_option(value_dict_in)

    result = round_all_dict_values(appreciate_beerwiser.output_dict["Base case"]["Focus on training"])
    expected_result = {
        "key_outputs": {
            "Accidents reduction": 17.44,
            "Water use reduction": 1336363.64,
            "Production cost reduction": 0.04,
        },
        "appreciations": {
            "Accidents reduction": 100.0,
            "Water use reduction": 1.95,
            "Production cost reduction": 56.73,
        },
        "weighted_appreciations": {
            "Accidents reduction": 33.33,
            "Water use reduction": 0.33,
            "Production cost reduction": 28.36,
        },
        "decision_makers_option_appreciation": 62.02,
    }
    assert result == expected_result


def test_appreciate_single_scenario_only_structure(appreciate_beerwiser):
    """
    This function tests the STRUCTURE after appreciate_single_scenario of the output dictionary. Only the keys and the
    length of the values are checked (should be 3 now) as these values are a result from
    appreciate_single_decision_maker_option() which is already checked above.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """
    value_dict_in = appreciate_beerwiser.output_dict["Pessimistic"]
    appreciate_beerwiser.appreciate_single_scenario(value_dict_in)

    result = appreciate_beerwiser.output_dict["Pessimistic"]
    result_structure = {key: len(value) for key, value in result.items()}
    expected_structure = {"Equal spread": 4, "Focus on training": 4, "Focus on water recycling": 4}
    assert result_structure == expected_structure


def test_appreciate_all_scenarios_only_structure(appreciate_beerwiser):
    """
    This function tests for the presence of 'appreciations' and 'weighted_appreciations' in the output dictionary
    structure. The correctness of these values is already tested above.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """
    appreciate_beerwiser.appreciate_all_scenarios()
    result = appreciate_beerwiser.output_dict

    # There should be 3 x 3 (dmo x scenario) appreciation dictionaries and 3 x 3 weighted appreciation dictionaries
    count_dictionaries = {
        "appreciations": len(get_values_from_target(result, "appreciations")),
        "weighted_appreciations": len(get_values_from_target(result, "weighted_appreciations")),
        "decision_makers_option_appreciation": len(
            get_values_from_target(result, "decision_makers_option_appreciation")
        ),
    }
    expected_count = {"appreciations": 9, "weighted_appreciations": 9, "decision_makers_option_appreciation": 9}
    assert count_dictionaries == expected_count


@pytest.mark.parametrize(
    "weights_list, expected_result",
    [([3, 5, 3, 15], 0.33), ([2, 4, 8, 20], 0.05), ([10, 8, 0, 2], 0), ([2, 3, 4, 0], 0)],
)
def test_apply_weights_single_key_output(appreciate_beerwiser, weights_list, expected_result):
    """
    This function tests _apply_weights_single_key_output to return the correct weight for a variety of
    different inputs. Also boundary cases with zero weights are tested.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    :param weights_list: a list with weights needed to create weight dictionary
    :param expected_result: expected value for the weight
    """
    # prepare dictionary | easier to parametrize in this way
    weights_dict = {
        "key_output": weights_list[0],
        "theme": weights_list[1],
        "sum_within_theme": weights_list[2],
        "sum_theme": weights_list[3],
    }
    result = round(appreciate_beerwiser._apply_weights_single_key_output(weights_dict), 2)
    assert result == expected_result


def test_calculate_weights(appreciate_beerwiser):
    """
    This function tests _calculate_weights to return the correct values
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """
    result = appreciate_beerwiser._calculate_weights()
    rounded_result = [round(value, 2) for value in result]
    expected_result = [0.33, 0.17, 0.50]
    assert rounded_result == expected_result


def test_apply_weights(appreciate_beerwiser):
    """
    This function tests _apply_weights to return the correct weighted appreciations
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """
    appreciation_dict = {"Accidents reduction": 50, "Water use reduction": 49.756, "Production cost reduction": 81.12}
    result = appreciate_beerwiser._apply_weights(appreciation_dict)
    rounded_result = [round(value, 2) for value in result]
    expected_result = [16.67, 8.29, 40.56]
    assert expected_result == rounded_result


def test_apply_scenario_weights(appreciate_beerwiser):
    """
    This function tests _apply_scenario_weights to return the correct decision makers' option appreciations
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """
    appreciate_beerwiser._apply_scenario_weights()
    result = round_all_dict_values(appreciate_beerwiser.output_dict["Base case"]["Focus on training"])
    expected_result = {
        "key_outputs": {
            "Accidents reduction": 17.44,
            "Water use reduction": 1336363.64,
            "Production cost reduction": 0.04,
        },
        "appreciations": {
            "Accidents reduction": 100.0,
            "Water use reduction": 1.95,
            "Production cost reduction": 56.73,
        },
        "weighted_appreciations": {
            "Accidents reduction": 33.33,
            "Water use reduction": 0.33,
            "Production cost reduction": 28.36,
        },
        "decision_makers_option_appreciation": 62.02,
        "scenario_appreciations": 20.67,
    }
    assert result == expected_result
