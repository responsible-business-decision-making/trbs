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
    _, dataframes_dict = case.import_case()
    # initialize exporter
    yield CaseExporter(Path.cwd(), "beerwiser", dataframes_dict)
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
