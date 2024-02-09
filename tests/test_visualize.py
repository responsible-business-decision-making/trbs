# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the Visualize() class. Note that the Visualize class is NOT case dependent.
Therefore, an arbitrary outcome dictionary is used in these unit tests.

The following functions are skipped: _table_styler, _graph_styler, _create_table (returns styler class),
The following functions are partly tested: _create_barchart (only errors), create_visuals (only errors)
"""
import pytest
import numpy as np
import pandas as pd
from params import OUTPUT_DICT_GENERIC
from vlinder.visualize import Visualize, VisualizationError


@pytest.fixture(name="test_outcomes")
def fixture_visualize_outcomes():
    """
    This fixture initialises a Visualize class.
    :return: a Visualize class for a generic outcome dictionary
    """
    return Visualize(OUTPUT_DICT_GENERIC, 2 * 3 * 3)


def test_validate_kwargs(test_outcomes):
    """
    This function tests _validate_kwargs to return None when valid **kwargs are provided
    :param test_outcomes: a Visualize class
    """
    result = test_outcomes._validate_kwargs(scenario="A", decision_makers_option="B", stacked=False)
    expected_result = None
    assert result == expected_result


def test_validate_kwargs_error(test_outcomes):
    """
    This function tests that _validate_kwargs to raise a VisualizationError when an unknown argument is provided.
    :param test_outcomes: a Visualize class
    """
    with pytest.raises(VisualizationError) as visualization_error:
        test_outcomes._validate_kwargs(this_does_not_exist="abc")
    expected_result = "Visualization Error: Invalid argument 'this_does_not_exist'"
    assert str(visualization_error.value) == expected_result


@pytest.mark.parametrize("target_key, expected_result", [("SCEN A", 1), ("AA", None), ("val2", 3)])
def test_find_dimension_level(test_outcomes, target_key, expected_result):
    """
    This function tests _find_dimension_level to return the correct dimension level.
    :param test_outcomes: a Visualize class
    :param target_key: the key of interest
    :param expected_outcome: the expected dimension level
    """
    result = test_outcomes._find_dimension_level(OUTPUT_DICT_GENERIC, target_key)
    assert result == expected_result


def test_str_snake_case_to_text(test_outcomes):
    """
    This function tests _str_snake_case_to_text to return a reformatted string.
    :param test_outcomes: a Visualize class
    """
    result = test_outcomes._str_snake_case_to_text("string_to_be_adjusted")
    expected_result = "string to be adjusted"
    assert result == expected_result


@pytest.mark.parametrize(
    "title_list, expected_result",
    [
        (
            ["this is a very long title name that needs to become shorter", "a", "b", "c", "d", "e"],
            ["this is a ve..", "a", "b", "c", "d", "e"],
        ),
        (["short", "shorter", "shorts"], ["short", "shorter", "shorts"]),
        (["very long but also only one so should be fine"], ["very long but also only one so should be fine"]),
    ],
)
def test_truncate_title_list(test_outcomes, title_list, expected_result):
    """
    This function tests _truncate_title_list to return a truncated list of title strings.
    :param test_outcomes: a Visualize class
    :param title_list: a list with strings
    :param expected_result: the expected truncated list
    """
    result = test_outcomes._truncate_title_list(title_list)
    assert result == expected_result


@pytest.mark.parametrize(
    "key_data, expected_result",
    [
        (
            "val1",
            pd.DataFrame(
                {
                    "scenario": ["SCEN A"] * 9 + ["SCEN B"] * 9,
                    "decision_makers_option": ["DMO 1"] * 3
                    + ["DMO 2"] * 3
                    + ["DMO 3"] * 3
                    + ["DMO 1"] * 3
                    + ["DMO 2"] * 3
                    + ["DMO 3"] * 3,
                    "val1": ["KO1", "KO2", "KO3"] * 3 + ["KO1", "KO2", "KO3"] * 3,
                    "value": [
                        2.0,
                        4.0,
                        3.0,
                        3.0,
                        2.0,
                        4.0,
                        5.0,
                        2.5,
                        3.5,
                        2.5,
                        3.0,
                        2.0,
                        4.0,
                        1.5,
                        2.5,
                        1.0,
                        3.0,
                        2.5,
                    ],
                }
            ),
        ),
        (
            "val3",
            pd.DataFrame(
                {
                    "scenario": ["SCEN A", "SCEN A", "SCEN A", "SCEN B", "SCEN B", "SCEN B"],
                    "decision_makers_option": ["DMO 1", "DMO 2", "DMO 3", "DMO 1", "DMO 2", "DMO 3"],
                    "value": [5.0, 2.0, 4.0, 1.5, 2.0, 3.5],
                }
            ),
        ),
    ],
)
def test_format_data_for_visual(test_outcomes, key_data, expected_result):
    """
    This function tests _format_data_for_visual to return a properly formatted dataframe.
    :param test_outcomes: a Visualize class
    :param key_data: key name of the requested values
    :param expected_result: expected dataframe
    """
    result = test_outcomes._format_data_for_visual(key_data)
    assert result.to_dict() == expected_result.to_dict()


@pytest.mark.parametrize(
    "drop_used, expected_result",
    [
        (True, pd.DataFrame({"Col2": ["X", "X", "Y"]})),
        (False, pd.DataFrame({"Col1": ["A", "A", "A"], "Col2": ["X", "X", "Y"], "Col3": [3, 3, 3]})),
    ],
)
def test_apply_filters(test_outcomes, drop_used, expected_result):
    """
    This function tests _apply_filters to return a correctly filtered dataframe.
    :param test_outcomes: a Visualize class
    """
    np.random.seed(42)
    test_data = pd.DataFrame(
        {
            "Col1": np.random.choice(["A", "B", "C"], 20),
            "Col2": np.random.choice(["X", "Y", "Z"], 20),
            "Col3": np.random.choice([1, 2, 3], 20),
        }
    )
    result = test_outcomes._apply_filters(test_data, drop_used, Col1="A", Col3=3, other_arg="abc")
    result_df = result[0].reset_index(drop=True)
    assert result_df.to_dict() == expected_result.to_dict()


def test_apply_filters_error(test_outcomes):
    """
    This function tests _apply_filters to raise a VisualizationError if the filter removes all data.
    :param test_outcomes: a Visualize class
    """
    test_data = pd.DataFrame({"ColA": ["A", "A"], "ColB": [1, 2]})
    expected_error = "Visualization Error: No data for given selection. Are your arguments correct?"
    with pytest.raises(VisualizationError) as visualization_error:
        test_outcomes._apply_filters(test_data, False, ColA="B")
    assert str(visualization_error.value) == expected_error


def test_create_barchart_error(test_outcomes):
    """
    This function tests _create_barchart to raise an error when too many dimensions are provided
    :param test_outcomes: a Visualize class
    """
    with pytest.raises(VisualizationError) as visualization_error:
        test_outcomes._create_barchart("val1")
    expected_error = "Visualization Error: Too many dimensions (3). Please specify a scenario"
    assert str(visualization_error.value) == expected_error


@pytest.mark.parametrize(
    "visual_request, key, expected_error",
    [
        ("non_existing_plot", "key_outputs", "'non_existing_plot' is not a valid chart type"),
        ("barchart", "non_existing_value", "'non_existing_value' is not a valid option"),
    ],
)
def test_create_visual_errors(test_outcomes, visual_request, key, expected_error):
    """
    This function tests create_visual to raise an error for invalid request
    :param test_outcomes: a Visualize class
    :param visual_request: requested visual
    :param key: key name of requested value
    :expected_error: expected raised error
    """
    with pytest.raises(VisualizationError) as visualization_error:
        test_outcomes.create_visual(visual_request, key)
    assert str(visualization_error.value) == f"Visualization Error: {expected_error}"
