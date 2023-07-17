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
    :return:
    """
    result = appreciate_beerwiser._get_start_and_end_points()
    rounded_result = round_all_dict_values(result)
    expected_result = {
        "Accidents reduction": [3.49, 17.44],
        "Water use reduction": [1227272.73, 6818181.82],
        "Production cost reduction": [0.04, 0.05],
    }
    assert rounded_result == expected_result
