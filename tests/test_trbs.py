# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains tests for the unique logic in trbs.py
Most function are calls to other classes. The testing for that can be found in the respective test-file for that class.
"""
import pytest

from vlinder.trbs import TheResponsibleBusinessSimulator, CaseError


@pytest.fixture(name="case_beerwiser")
def fixture_case_beerwiser():
    """
    This fixture initialises a CaseImporter for the beerwiser case.
    :return: an CaseImporter class for the beerwiser case.
    """
    return TheResponsibleBusinessSimulator("Beerwiser")


def test_status_after_build(case_beerwiser):
    """
    Test to check whether building a case yields the correct status
    """
    # check if set correctly
    case_beerwiser.build()
    status_expected = {0: "build"}
    assert case_beerwiser.status == status_expected

    # and reset correctly after building again
    case_beerwiser.status[999] = "some high status code"
    case_beerwiser.build()
    assert case_beerwiser.status == status_expected


def test_evaluate_before_build(case_beerwiser):
    """
    Test to check whether evaluating a case before building raises the correct error
    """
    with pytest.raises(CaseError) as case_error:
        case_beerwiser.evaluate()
    expected_error = "Case Error: first build a case with .build()"
    assert str(case_error.value) == expected_error


def test_status_after_evaluate(case_beerwiser):
    """
    Test to check whether evaluating after building a case yields the correct status
    """
    # check if set correctly
    case_beerwiser.build()
    case_beerwiser.evaluate()
    status_expected = {0: "build", 1: "evaluate"}
    assert case_beerwiser.status == status_expected

    # and reset correctly after building again
    case_beerwiser.status[999] = "some high status code"
    case_beerwiser.evaluate()
    assert case_beerwiser.status == status_expected


def test_appreciate_too_early(case_beerwiser):
    """
    Test to check whether the correct error is raised when appreciating before build or evaluate
    """
    with pytest.raises(CaseError) as build_error:
        case_beerwiser.appreciate()

    case_beerwiser.build()
    with pytest.raises(CaseError) as evaluate_error:
        case_beerwiser.appreciate()

    assert str(build_error.value) == "Case Error: first build a case with .build()"
    assert str(evaluate_error.value) == "Case Error: first evaluate a case with .evaluate()"


def test_status_after_appreciate(case_beerwiser):
    """
    Test to check whether evaluating after building a case yields the correct status
    """
    case_beerwiser.build()
    case_beerwiser.evaluate()
    case_beerwiser.appreciate()
    status_expected = {0: "build", 1: "evaluate", 2: "appreciate"}
    assert case_beerwiser.status == status_expected


def test_visualize_before_build(case_beerwiser):
    """
    Test to check whether visualizing before building a case yields the correct error
    """
    with pytest.raises(CaseError) as case_error:
        case_beerwiser.visualize('SHOULD_NOT_MATTER', 'CAN BE ANYTHING')
    expected_error = "Case Error: first build a case with .build()"
    assert str(case_error.value) == expected_error


def test_transform_before_build(case_beerwiser):
    """
    Test to check whether transforming before building a case yields the correct error
    """
    with pytest.raises(CaseError) as case_error:
        case_beerwiser.transform('SHOULD NOT MATTER')
    expected_error = "Case Error: first build a case with .build()"
    assert str(case_error.value) == expected_error


def test_modify_before_build(case_beerwiser):
    """
    Test to check whether modifying a case before building yields the correct error
    """
    with pytest.raises(CaseError) as case_error:
        case_beerwiser.modify('A', 'B', 'C')
    expected_error = "Case Error: first build a case with .build()"
    assert str(case_error.value) == expected_error


@pytest.mark.parametrize("setup_methods, expected_error", [
    ([], "Case Error: first build a case with .build()"),
    (["build"], "Case Error: first evaluate a case with .evaluate()"),
    (["build", "evaluate"], "Case Error: first appreciate a case with .appreciate()"),
])
def test_make_report_or_optimize(case_beerwiser, setup_methods, expected_error):
    """
    Test to check whether asking for a report or optimisation too soon will result in the appropriate error
    """
    # Call each setup method in sequence on the case_beerwiser
    for method in setup_methods:
        getattr(case_beerwiser, method)()

    with pytest.raises(CaseError) as case_error:
        case_beerwiser.make_report('A')

    assert str(case_error.value) == expected_error

    with pytest.raises(CaseError) as case_error:
        case_beerwiser.optimize('ScenA')

    assert str(case_error.value) == expected_error


def test_optimize_without_