# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the CaseImporter() class.
NOTE: _create_input_dict & import_case are not tested as they are only helper function that call other functions
"""
import warnings
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from vlinder.case_importer import CaseImporter, TemplateError


@pytest.fixture(name="import_beerwiser_json")
def fixture_import_beerwiser_json():
    """
    This fixture initialises a CaseImporter for the beerwiser case.
    :return: an CaseImporter class for the beerwiser case.
    """
    return CaseImporter(Path.cwd() / "src/vlinder/data", "beerwiser", "json")


@pytest.fixture(name="import_beerwiser_csv")
def fixture_import_beerwiser_csv():
    """
    This fixture initialises a CaseImporter for the beerwiser case.
    :return: an CaseImporter class for the beerwiser case.
    """
    return CaseImporter(Path.cwd() / "src/vlinder/data", "beerwiser", "csv")


@pytest.fixture(name="import_beerwiser_xlsx")
def fixture_import_beerwiser_xlsx():
    """
    This fixture initialises a CaseImporter for the beerwiser case.
    :return: an CaseImporter class for the beerwiser case.
    """
    return CaseImporter(Path.cwd() / "src/vlinder/data", "beerwiser", "xlsx")


def test_build_template_validators(import_beerwiser_json):
    """
    This function tests _build_template_validators() to return a dictionary containing the 'table' and necessary
    columns within that table.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    result = import_beerwiser_json._build_template_validators()
    expected_result = {
        "configurations": ["configuration", "value"],
        "generic_text_elements": ["generic_text_element", "value"],
        "case_text_elements": ["case_text_element", "value"],
        "key_outputs": [
            "key_output",
            "theme",
            "monetary",
            "smaller_the_better",
            "linear",
            "automatic",
            "start",
            "end",
            "threshold",
        ],
        "decision_makers_options": ["internal_variable_input", "decision_makers_option", "value"],
        "scenarios": ["external_variable_input", "scenario", "value"],
        "fixed_inputs": ["fixed_input", "value"],
        "dependencies": [
            "destination",
            "argument_1",
            "argument_2",
            "operator",
            "maximum_effect",
            "accessibility",
            "probability_of_success",
            "saturation_point",
        ],
        "theme_weights": ["theme", "weight"],
        "key_output_weights": ["key_output", "weight"],
        "scenario_weights": ["scenario", "weight"],
    }
    assert result == expected_result


@pytest.mark.parametrize(
    "dataframe, table, expected_result",
    [
        (
            pd.DataFrame(columns=["theme", "weight", "EXTRA COL"]),
            "theme_weights",
            pd.DataFrame(columns=["theme", "weight"]),
        ),
        (
            pd.DataFrame(columns=["external_variable_input", "scenario", "value"]),
            "scenarios",
            pd.DataFrame(columns=["external_variable_input", "scenario", "value"]),
        ),
    ],
)
def test_check_data_columns(import_beerwiser_json, dataframe, table, expected_result):
    """
    This function tests _check_data_columns to return the same pd.DataFrame with ONLY the necessary columns. Warnings
    are tested separately below.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    :param dataframe: dataframe where the columns need to be checked
    :param table: table name of the dataframe
    :expected_result: dataframe that should be returned by _check_data_columns
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = import_beerwiser_json._check_data_columns(dataframe, table)

    pd.testing.assert_frame_equal(result, expected_result)


def test_check_data_columns_warning(import_beerwiser_json):
    """
    This function tests _check_data_columns to raise a warning when extra columns are provided.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    with warnings.catch_warnings(record=True) as warning_list:
        import_beerwiser_json._check_data_columns(
            pd.DataFrame(columns=["fixed_input", "value", "EXTRA COL"]), "fixed_inputs"
        )
    expected_result = "column(s) 'EXTRA COL' are not used for 'fixed_inputs'"
    assert str(warning_list[0].message) == expected_result


def test_check_data_columns_error(import_beerwiser_json):
    """
    This function tests _check_data_column to raise a TemplateError when necessary columns are missing
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    with pytest.raises(TemplateError) as template_error:
        import_beerwiser_json._check_data_columns(
            pd.DataFrame(columns=["internal_variable_input", "value"]), "decision_makers_options"
        )
    expected_result = "Template Error: column(s) 'decision_makers_option' are missing for 'decision_makers_options'"
    assert str(template_error.value) == expected_result


@pytest.mark.parametrize(
    "fixture_name, table",
    [
        ("import_beerwiser_csv", "dependencies"),
        ("import_beerwiser_json", "key_outputs"),
        ("import_beerwiser_xlsx", "scenarios"),
    ],
)
def test_create_dataframes_dict(fixture_name, table, request):
    """
    This function tests _create_dataframes to update self.dataframes_dict with a new {key: pd.DataFrame} pair.
    Only the structure of the output is tested.
    :param fixture_name: used version of the CaseImporter class. Fixtures differ in used extension / file format
    :param table: name of the table
    :param request: needed to transform fixture_name to a fixture value
    """
    case_importer = request.getfixturevalue(fixture_name)
    case_importer._create_dataframes_dict(table)
    result_structure = {key: type(value) for key, value in case_importer.dataframes_dict.items()}
    expected_structure = {table: pd.DataFrame}
    assert result_structure == expected_structure


def test_create_dataframes_dict_error(import_beerwiser_json):
    """
    This function tests _create_dataframes_dict to raise an error when a missing table name is called.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    with pytest.raises(TemplateError) as template_error:
        import_beerwiser_json._create_dataframes_dict("Missing Table")
    expected_result = "Template Error: Sheet 'Missing Table' is missing"
    assert str(template_error.value) == expected_result


def test_convert_to_numpy_arrays_2d(import_beerwiser_json):
    """
    This function tests _convert_to_numpy_arrays_2d to return properly pivoted numpy arrays from the given dataframe.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    input_dataframe = pd.DataFrame(
        {
            "internal_variable_input": ["A", "B", "A", "B"],
            "decision_makers_option": ["X", "X", "Y", "Y"],
            "value": [2, 3, 4, 5],
        }
    )
    import_beerwiser_json._convert_to_numpy_arrays_2d("decision_makers_options", input_dataframe)
    result = import_beerwiser_json.input_dict
    expected_result = {
        "decision_makers_options": np.array(["X", "Y"]),
        "internal_variable_inputs": np.array(["A", "B"]),
        "decision_makers_option_value": np.array([[2, 3], [4, 5]]),
    }
    assert all(np.array_equal(expected_result[key], result[key]) for key in result)


@pytest.mark.parametrize(
    "row, all_inputs, expected_output",
    [
        (pd.Series({"argument_1": "money", "argument_2": "love"}), np.array(["education", "money"]), 2),
        (pd.Series({"argument_1": "love", "argument_2": "love"}), np.array(["education", "police", "law"]), 2),
        (pd.Series({"argument_1": "law", "argument_2": "love"}), np.array(["love", "money", "law"]), 1),
    ],
)
def test_apply_first_level_hierarchy_to_row(import_beerwiser_json, row, all_inputs, expected_output):
    """
    This function tests _apply_first_level_hierarchy_to_row to return a 1 or 2 based on the presence of names in the
    input array. Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    :param row: a pd.Series containing the needed values from dependency row
    :param all_inputs: an array containing the available input names
    :param expected_output: the expected output of the function
    """
    result = import_beerwiser_json._apply_first_level_hierarchy_to_row(row, all_inputs)
    assert result == expected_output


@pytest.mark.parametrize(
    "row, expected_output",
    [
        (pd.Series({"destination": "law", "argument_1": "money", "argument_2": "love", "hierarchy": 1}), 1),
        (pd.Series({"destination": "education", "argument_1": "money", "argument_2": "love", "hierarchy": 3}), 5),
    ],
)
def test_apply_second_level_hierarchy_to_row(import_beerwiser_json, row, expected_output):
    """
    This function tests _apply_second_level_hierarchy_to_row to return the right hierarchy level. For testing purposes
    only the relevant columns are provided as input.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    :param row: single row of dependencies
    :param data: a dataframe containing all dependencies
    """
    input_dataframe = pd.DataFrame({"destination": np.array(["love", "law", "law", "money", "education"])})
    result = import_beerwiser_json._apply_second_level_hierarchy_to_row(row, input_dataframe)
    assert result == expected_output


def test_convert_to_ordered_dependencies(import_beerwiser_json):
    """
    This function tests test_convert_to_ordered_dependencies to add the dependencies in the correct order to the
    input dictionary
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    # set-up for testing
    import_beerwiser_json.input_dict = {
        "fixed_inputs": ["love", "money"],
        "internal_variable_inputs": [],
        "external_variable_inputs": [],
    }
    input_data = pd.DataFrame(
        {
            "destination": ["law", "super love", "lawyer", "IT", "crook", "education"],
            "argument_1": ["tech", "love", "education", "law", "5", "money"],
            "argument_2": ["", "", "law", "tech", "money", "love"],
            "operator": np.full(6, "N/A"),
            "maximum_effect": np.full(6, "N/A"),
            "accessibility": np.full(6, "N/A"),
            "probability_of_success": np.full(6, "N/A"),
            "saturation_point": np.full(6, "N/A"),
        }
    )
    # compare
    import_beerwiser_json._convert_to_ordered_dependencies(input_data)
    result = import_beerwiser_json.input_dict
    expected_result = {
        "fixed_inputs": ["love", "money"],
        "internal_variable_inputs": [],
        "external_variable_inputs": [],
        "destination": np.array(["crook", "education", "law", "super love", "lawyer", "IT"], dtype=object),
        "argument_1": np.array(["5", "money", "tech", "love", "education", "law"], dtype=object),
        "argument_2": np.array(["money", "love", "", "", "law", "tech"], dtype=object),
        "operator": np.full(6, "N/A", dtype=object),
        "maximum_effect": np.full(6, "N/A", dtype=object),
        "accessibility": np.full(6, "N/A", dtype=object),
        "probability_of_success": np.full(6, "N/A", dtype=object),
        "saturation_point": np.full(6, "N/A", dtype=object),
        "hierarchy": np.array([1, 1, 2, 2, 3, 3]),
        "dependencies_order": np.array([4, 5, 0, 1, 2, 3]),
    }
    assert all(np.array_equal(expected_result[key], result[key]) for key in result)


def test_convert_to_numpy_arrays_weights(import_beerwiser_json):
    """
    This function tests _convert_to_numpy_arrays_weights to properly update the input dictionary.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    import_beerwiser_json.input_dict = {"key_outputs": ["C", "B", "A"]}
    input_data = pd.DataFrame({"key_output": ["A", "B", "C"], "weight": [1, 5, 2]})
    import_beerwiser_json._convert_to_numpy_arrays_weights("key_output_weights", input_data)
    result = import_beerwiser_json.input_dict
    expected_result = {"key_outputs": np.array(["C", "B", "A"]), "key_output_weight": np.array([2, 5, 1])}
    assert all(np.array_equal(expected_result[key], result[key]) for key in result)


def test_convert_to_numpy_arrays(import_beerwiser_json):
    """
    This function tests _convert_to_numpy_arrays to properly update the input dictionary
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    input_dataframe = pd.DataFrame({"fixed_input": ["A", "B", "C", "D"], "value": [3, 5, 2, 8]})
    import_beerwiser_json._convert_to_numpy_arrays("fixed_inputs", input_dataframe)
    result = import_beerwiser_json.input_dict
    expected_result = {"fixed_inputs": np.array(["A", "B", "C", "D"]), "fixed_input_value": np.array([3, 5, 2, 8])}
    assert all(np.array_equal(expected_result[key], result[key]) for key in result)


@pytest.mark.parametrize(
    "input_dataframe, expected_output",
    [
        (
            {
                "key_output_theme": ["People", "Planet", "Profit"],
                "key_output_weight": [2, 1, 3],
                "themes": ["Planet", "People", "Profit"],
                "theme_weight": [1, 2, 3],
            },
            {
                "key_output_theme": ["People", "Planet", "Profit"],
                "key_output_weight": [2, 1, 3],
                "themes": ["Planet", "People", "Profit"],
                "theme_weight": [1, 2, 3],
                "key_output_relative_weight": np.array([2, 1, 3]),
            },
        ),
        (
            {
                "key_output_theme": ["Society", "Society", "Society", "Society", "Society", "Society", "Economy"],
                "key_output_weight": [1, 1, 1, 1, 1, 1, 1],
                "themes": ["Economy", "Society"],
                "theme_weight": [1, 1],
            },
            {
                "key_output_theme": ["Society", "Society", "Society", "Society", "Society", "Society", "Economy"],
                "key_output_weight": [1, 1, 1, 1, 1, 1, 1],
                "themes": ["Economy", "Society"],
                "theme_weight": [1, 1],
                "key_output_relative_weight": np.array(
                    [0.16666667, 0.16666667, 0.16666667, 0.16666667, 0.16666667, 0.16666667, 1]
                ),
            },
        ),
    ],
)
def test_convert_to_relative_weights(import_beerwiser_json, input_dataframe, expected_output):
    """
    This function tests _convert_to_relative_weights to properly update the input dictionary.
    Note: the file extension (here: json) is not relevant for this test, so only one needs to be tested
    :param import_beerwiser_json: an CaseImporter class for the beerwiser case
    """
    import_beerwiser_json.input_dict = input_dataframe
    import_beerwiser_json._convert_to_relative_weights()
    result = import_beerwiser_json.input_dict
    assert np.allclose(result["key_output_relative_weight"], expected_output["key_output_relative_weight"])
    for key in ["key_output_theme", "key_output_weight", "themes", "theme_weight"]:
        assert result[key] == expected_output[key]
