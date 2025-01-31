# pylint: disable=cyclic-import, protected-access
"""
This module contains all tests for the Visualize() and the DependencyGraph() class. Note that the Visualize class is
NOT case dependent. Therefore, an arbitrary outcome dictionary is used in these unit tests.

The following functions are skipped: _table_styler, _graph_styler, _create_table (returns styler class),
The following functions are partly tested: _create_barchart (only errors), create_visuals (only errors)
"""
import pytest
import numpy as np
import pandas as pd
from vlinder.visualize import Visualize, VisualizationError, DependencyGraph
from .params import OUTPUT_DICT_GENERIC, INPUT_DICT_BEERWISER


@pytest.fixture(name="test_outcomes")
def fixture_visualize_outcomes():
    """
    This fixture initialises a Visualize class.
    :return: a Visualize class for a generic outcome dictionary
    """
    return Visualize(INPUT_DICT_BEERWISER, OUTPUT_DICT_GENERIC, 2 * 3 * 3)


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


def test_find_all_predecessors():
    """
    This function tests find_all_predecessors to return the predecessors of a node
    """
    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)
    dep.create_inc_mat()
    dep.create_network()

    result = dep.find_all_predecessors(node="goedenavond", max_generation=1)[0]
    expected_result = set(["later", "hallo"])
    assert result == expected_result


def test_is_even():
    """
    This function tests is_even to return true for an input value of 4
    """
    result = DependencyGraph.is_even(4)
    expected_result = True
    assert result == expected_result


def test_create_inc_mat():
    """
    This function tests create_inc_mat if it creates the correct incidence matrix based on some dependencies
    """
    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)

    expected_result = pd.DataFrame(
        {
            "goedemorgen": [1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            "goedemiddag": [0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
            "goedenavond": [0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
        },
        index=["hey", "doei", "hoi", "dag", "hallo", "later"],
    )

    dep.create_inc_mat()
    result = dep.inc_mat
    assert result.equals(expected_result) is True


def test_ko_filter():
    """
    This function tests ko_filter if the correct amount of generations is returned for a network
    """
    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = ["√", "goedemiddag", "goedenavond"]
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)

    dep.create_inc_mat()
    dep.create_network()

    result = dep.ko_filter("goedemiddag", max_gen=None)

    assert result == 1


def test_x_coords():
    """
    This function tests x_coords if the correct dictionary with coordinates is created for a certain network
    """
    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = np.array(["goedemorgen", "goedemiddag", "goedenavond"])
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)

    dep.create_inc_mat()
    dep.create_x_coords()
    result = dep.x_coords
    expected_result = {
        "hoi": 0,
        "hallo": 0,
        "later": 0,
        "hey": 0,
        "doei": 0,
        "dag": 0,
        "goedemorgen": 1,
        "goedemiddag": 1,
        "goedenavond": 1,
    }
    assert result == expected_result


def test_y_coords():
    """
    This function tests y_coords if the correct dictionary with coordinates is created for a certain network
    """
    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = np.array(["goedemorgen", "goedemiddag", "goedenavond"])
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)

    dep.create_inc_mat()
    dep.create_network()
    dep.create_x_coords()
    dep.create_y_coords()
    result = dep.y_coords
    expected_result = {
        "dag": -5.0,
        "doei": -1.0,
        "goedenavond": -8,
        "goedemiddag": -4,
        "goedemorgen": 0,
        "hallo": -7.0,
        "hey": 1.0,
        "hoi": -3.0,
        "later": -9.0,
    }
    assert result == expected_result


@pytest.mark.parametrize(
    "selected_ko, max_gen, save, expected_outcome",
    [
        (4, 3, True, "'4' is not a valid option"),
        ("goedenavond", "vier", True, "'vier' is not a valid option"),
        ("goedenavond", 4, "waar", "'waar' is not a valid option"),
    ],
)
def test_draw_graph(selected_ko, max_gen, save, expected_outcome):
    """
    This function tests draw_graph if the correct errors are given when parameter values are filled in incorrectly
    :param selected_ko: the key output
    :param max_gen: the maximum of generations of predecessors one wants in its network
    :param save: a boolean parameter if there has to be made a screenshot from the graph
    """

    input_dict = {}
    input_dict["dependencies_order"] = [0, 1, 2]
    input_dict["destination"] = np.array(["goedemorgen", "goedemiddag", "goedenavond"])
    input_dict["hierarchy"] = [1, 1, 1]
    input_dict["key_outputs"] = ["goedemorgen", "goedemiddag", "goedenavond"]
    input_dict["argument_1"] = ["hey", "hoi", "hallo"]
    input_dict["argument_2"] = ["doei", "dag", "later"]

    dep = DependencyGraph(input_dict)
    with pytest.raises(VisualizationError) as visualization_error:
        dep.draw_graph(selected_ko, max_gen, save)
    assert str(visualization_error.value) == f"Visualization Error: {expected_outcome}"
