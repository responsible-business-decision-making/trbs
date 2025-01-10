# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the Make_report() class
"""
from pathlib import Path
import shutil
import pytest
from vlinder.make_report import MakeReport
from vlinder.visualize import Visualize
from .params import INPUT_DICT_BEERWISER, OUTPUT_DICT_BEERWISER


def visualize(visual_request, key, **kwargs):
    """
    This fixture initialises a Visualization class.
    :return: a Visualization class for the Beerwiser outcome dictionary
    """
    visualizer = Visualize(INPUT_DICT_BEERWISER, OUTPUT_DICT_BEERWISER, 3 * 3 * 3)
    return visualizer.create_visual(visual_request, key, **kwargs)


@pytest.fixture(name="test_outcomes_report")
def fixture_make_report_outcomes():
    """
    This fixture initialises a MakeReport class.
    :return: a MakeReport class for a Beerwiser dictionary
    """
    return MakeReport(
        output_path="output_path",
        name="name",
        input_dict=INPUT_DICT_BEERWISER,
        output_dict=OUTPUT_DICT_BEERWISER,
        visualize=visualize,
    )


@pytest.mark.parametrize("target_key, expected_result", [("test", "test_title"), ("test2", "Not defined in template")])
def test_make_title(test_outcomes_report, target_key, expected_result):
    """
    This function tests make_title to return the correct title of the imported Excel template.
    :param test_outcomes_report: A MakeReport Class
    :param target_key: the key of interest
    :param expected_result: the expected dimension level
    """

    result = test_outcomes_report.make_title(target=target_key)
    assert result == expected_result


@pytest.mark.parametrize("expected_result", ["Not defined in template"])
def test_make_strategic_challenge(test_outcomes_report, expected_result):
    """
    This function tests make_strategic_challenge to return the correct title of the imported Excel template.
    :param test_outcomes_report: A MakeReport Class
    :param expected_result: the expected dimension level
    """
    result = test_outcomes_report.make_strategic_challenge()
    assert result == expected_result


@pytest.mark.parametrize("target_key, expected_result", [("test", "test_intro"), ("test2", "Not defined in template")])
def test_make_introduction(test_outcomes_report, target_key, expected_result):
    """
    This function tests make_introduction to return the correct title of the imported Excel template.
    :param test_outcomes_report: A MakeReport Class
    :param target_key: the key of interest
    :param expected_result: the expected dimension level
    """
    result = test_outcomes_report.make_introduction(target=target_key)
    assert result == expected_result


@pytest.mark.parametrize("scenario, orientation", [(INPUT_DICT_BEERWISER["scenarios"][0], "Portrait")])
def test_make_slides_pdf(test_outcomes_report, scenario, orientation):
    """
    This function tests make_introduction to return the correct title of the imported Excel template.
    :param test_outcomes_report: A MakeReport Class
    :param scenario: the selected scenario
    :param orientation: the selected orientation
    """
    result = test_outcomes_report.make_slides_pdf(scenario=scenario, orientation=orientation)
    shutil.rmtree("images", ignore_errors=True)
    assert str(type(result)) == "<class 'fpdf.fpdf.FPDF'>"


@pytest.mark.parametrize("scenario, orientation", [(INPUT_DICT_BEERWISER["scenarios"][1], "Landscape")])
def test_create_report(
    test_outcomes_report, scenario, orientation, output_path=Path(str(Path.cwd()) + "/test_reports/")
):
    """
    This function tests make_introduction to return the correct title of the imported Excel template.
    :param test_outcomes_report: A MakeReport Class
    :param scenario: the selected scenario
    :param orientation: the selected orientation
    """
    result = test_outcomes_report.create_report(scenario=scenario, orientation=orientation, path=output_path)
    # Remove the folder which contains test_report
    shutil.rmtree("test_reports", ignore_errors=True)
    assert "test_reports/" in result
