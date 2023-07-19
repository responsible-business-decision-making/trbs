# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all test for the Appreciate() class
"""
import pytest
from core.appreciate import Appreciate
from core.utils import round_all_dict_values
from params import INPUT_DICT, OUTPUT_DICT


@pytest.fixture(name="appreciate_beerwiser")
def fixture_appreciate_beerwiser():
    """
    This fixture initialises a Beerwiser case.
    :return: an Evaluate class for Beerwiser
    """
    return Appreciate(INPUT_DICT, OUTPUT_DICT)


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
        (10, {"key_outputs": "Sample A", "key_output_smaller_the_better": 0, "key_output_linear": 1}, 33.33),
        (30, {"key_outputs": "Sample A", "key_output_smaller_the_better": 1, "key_output_linear": 1}, 0),
        (150, {"key_outputs": "Sample B", "key_output_smaller_the_better": 1, "key_output_linear": 0}, 15.71),
        (-20, {"key_outputs": "Sample A", "key_output_smaller_the_better": 0, "key_output_linear": 0}, 0),
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
    appreciate_beerwiser.start_and_end_points = {"Sample A": [5, 20], "Sample B": [0, 235]}
    result = round(appreciate_beerwiser._appreciate_single_key_output(value, args), 2)
    assert result == expected_result


def test_appreciate_single_decision_maker_option(appreciate_beerwiser):
    """
    This function tests aprreciate_single_decision_maker_option to return a dictionary that contains the correct values
    for key output, appreciations and weighted appreciations.
    :param appreciate_beerwiser: an Appreciate() class for Beerwiser
    """

    value_dict_in = appreciate_beerwiser.output_dict["Base case"]["Focus on training"]
    appreciate_beerwiser.appreciate_single_decision_maker_option("Base case", "Focus on training", value_dict_in)

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
    }
    assert result == expected_result
