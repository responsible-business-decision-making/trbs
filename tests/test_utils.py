# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the utils.py file
"""
import pytest
from vlinder.utils import (
    round_all_dict_values,
    get_values_from_target,
    number_formatter,
    check_numeric,
    check_list_content,
)


@pytest.mark.parametrize(
    "my_dict, digits, expected_result",
    [
        (
            {"A": [2.45345, 3.52345], "B": {"C": 3.5356453, "D": [1.243235, 2.4]}},
            3,
            {"A": [2.453, 3.523], "B": {"C": 3.536, "D": [1.243, 2.4]}},
        ),
        (
            {"A": {"B": [2.3243, 3.12], "C": 1.234, "D": {"E": 1.3455}}},
            1,
            {"A": {"B": [2.3, 3.1], "C": 1.2, "D": {"E": 1.3}}},
        ),
    ],
)
def test_round_all_dict_values(my_dict, digits, expected_result):
    """
    This function tests round_all_dict_values to return a rounded dictionary
    :param my_dict: nested input dictionary
    :param digits: number of digits used for rounding
    :param expected_result: expected result of the test
    """
    result = round_all_dict_values(my_dict, digits)
    assert result == expected_result


@pytest.mark.parametrize(
    "dictionary, target, expected_result",
    [
        ({"A": {"B": "Apple", "C": "Banana"}, "B": ["Kiwi", "Mango"]}, "B", ["Apple", ["Kiwi", "Mango"]]),
        ({"A": 1.22, "B": {"A": "Text"}, "C": {"D": {"A": 5}}}, "A", [1.22, "Text", 5]),
    ],
)
def test_get_values_from_target(dictionary, target, expected_result):
    """
    This function tests get_values_from_target to return the right values given the target value
    :param dictionary: nested input dictionary
    :param target: target key of which values need to be collected
    :param expected_result: expected result of the test
    """
    result = get_values_from_target(dictionary, target)
    assert result == expected_result


@pytest.mark.parametrize(
    "number, expected_result",
    [
        (12.456874, "12.46"),
        (755, "755.00"),
        (1005.12, "1.0K"),
        (12567.43, "12.6K"),
        (7684536, "7.7M"),
        (-123456, "-123.5K"),
        (-123.3, "-123.30"),
    ],
)
def test_number_formatter(number, expected_result):
    """
    This function tests number_formatter to return a formatted string
    """
    result = number_formatter(number)
    assert result == expected_result


@pytest.mark.parametrize(
    "arg, expected_result",
    [
        ("256.74", True),
        ("256", True),
        (256, True),
        (256.74, True),
        ("N/A", False),
        ("2/3", False),
        ("23.34.56", False),
    ],
)
def test_check_numeric(arg, expected_result):
    """
    This function tests check_numeric to return the correct boolean
    :param arg: the value to be checked
    :param expected_result: the correct identification of numeric values
    """
    result = check_numeric(arg)
    assert result == expected_result


@pytest.mark.parametrize(
    "arg, expected_result",
    [
        ([23, 1.22, 66], "numeric"),
        ([{"A": 23}, {"B": 23, "C": [1, 2, 3]}], "dictionaries"),
        (["A", {"B": 5}], "other"),
    ],
)
def test_check_list_content(arg, expected_result):
    """
    This function tests check_list_content to correctly identify the content of a list
    :param arg: the list to be checked
    :param expected_result: the expected content of this list
    """
    result = check_list_content(arg)
    assert result == expected_result
