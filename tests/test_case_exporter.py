# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the CaseExporter() class
"""
import shutil
from pathlib import Path
import pytest
from vlinder.case_importer import CaseImporter
from vlinder.case_exporter import CaseExporter


@pytest.fixture(name="export_beerwiser")
def fixture_export_beerwiser():
    """
    This fixture initialises an export class for a Beerwiser case
    """
    # get a dataframe dictionary from beerwiser -- this class is tested in test_case_importer
    case = CaseImporter(Path.cwd() / "src/vlinder/data", "beerwiser", "csv")
    input_dict, _ = case.import_case()
    # initialize exporter
    yield CaseExporter(Path.cwd(), "beerwiser", input_dict)
    # remove stuff after testing is done
    shutil.rmtree(Path.cwd() / "test_folder")


def test_create_output_folder(export_beerwiser):
    """
    This function tests _create_output_folder to create an output folder
    :param export_beerwiser: a CaseExporter() fixture of Beerwiser
    """
    export_beerwiser._create_output_folder("test_folder")
    expected_folder_location = Path.cwd() / "test_folder"
    assert expected_folder_location.exists()


def test_store_as_excel_template(export_beerwiser):
    """
    This function tests _store_as_excel_template to have stored an xlsx file. Note that the format of this file
    is NOT checked with this test, just the existence
    :param export_beerwiser: a CaseExporter() fixture of Beerwiser
    """
    export_beerwiser._create_output_folder("test_folder")
    export_beerwiser._store_as_excel_template()
    expected_file_location = Path.cwd() / "test_folder" / "beerwiser.xlsx"
    assert expected_file_location.exists()


def test_input_to_dataframe(export_beerwiser):
    """
    This function tests input_to_dataframe for Beerwiser and checks whether the created
    dataframe_dict follows the required structure defined in src/vlinder/data/template.xlsx
    :param export_beerwiser: a CaseExporter() fixture of Beerwiser
    """
    # Make folder for test
    export_beerwiser._create_output_folder("test_folder")
    # Create dataframe_dict using input_to_dataframe
    dataframe_dict = export_beerwiser.input_to_dataframe()
    # Check that keys in the dataframe_dict are correct
    assert list(dataframe_dict.keys()) == [
        "configurations",
        "generic_text_elements",
        "case_text_elements",
        "key_outputs",
        "decision_makers_options",
        "scenarios",
        "fixed_inputs",
        "dependencies",
        "theme_weights",
        "key_output_weights",
        "scenario_weights",
    ]
    # Check correctness of columns within each dataframe_dict['configurations']
    assert list(dataframe_dict["configurations"].columns) == ["configuration", "value"]
    # Check correctness of columns within each dataframe_dict['generic_text_elements']
    assert list(dataframe_dict["generic_text_elements"].columns) == ["generic_text_element", "value"]
    # Check correctness of columns within each dataframe_dict['case_text_elements']
    assert list(dataframe_dict["case_text_elements"].columns) == ["case_text_element", "value"]
    # Check correctness of columns within each dataframe_dict['key_outputs']
    assert list(dataframe_dict["key_outputs"].columns) == [
        "key_output",
        "theme",
        "monetary",
        "smaller_the_better",
        "linear",
        "automatic",
        "start",
        "end",
    ]
    # Check correctness of columns within each dataframe_dict['decision_makers_options']
    assert list(dataframe_dict["decision_makers_options"].columns) == [
        "internal_variable_input",
        "decision_makers_option",
        "value",
    ]
    # Check correctness of columns within each dataframe_dict['scenarios']
    assert list(dataframe_dict["scenarios"].columns) == ["external_variable_input", "scenario", "value"]
    # Check correctness of columns within each dataframe_dict['fixed_inputs']
    assert list(dataframe_dict["fixed_inputs"].columns) == ["fixed_input", "value"]
    # Check correctness of columns within each dataframe_dict['dependencies']
    assert list(dataframe_dict["dependencies"].columns) == ["destination", "argument_1", "argument_2", "operator"]
    # Check correctness of columns within each dataframe_dict['theme_weights']
    assert list(dataframe_dict["theme_weights"].columns) == ["theme", "weight"]
    # Check correctness of columns within each dataframe_dict['key_output_weights']
    assert list(dataframe_dict["key_output_weights"].columns) == ["key_output", "weight"]
    # Check correctness of columns within each dataframe_dict['scenario_weights']
    assert list(dataframe_dict["scenario_weights"].columns) == ["scenario", "weight"]


@pytest.mark.parametrize("requested_format", ["csv", "json", "xlsx"])
def test_create_template_for_requested_format(export_beerwiser, requested_format):
    """
    This function tests create_template_for_requested_format to create a file in the requested format. Note that only
    the existence of this is tested, NOT the content.
    :param export_beerwiser: a CaseExporter() fixture of Beerwiser
    :param requested_format:
    """
    export_beerwiser._create_output_folder("test_folder")
    export_beerwiser.create_template_for_requested_format(requested_format)
    if requested_format == "xlsx":
        expected_file_location = Path.cwd() / requested_format / "beerwiser.xlsx"
    else:
        expected_file_location = Path.cwd() / requested_format / f"configurations.{requested_format}"
    assert expected_file_location.exists()
    shutil.rmtree(Path.cwd() / requested_format)
