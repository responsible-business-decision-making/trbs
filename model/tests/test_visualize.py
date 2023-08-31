# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the Visualize() class. Note that the Visualize class is NOT case dependent.
Therefore, an arbitrary outcome dictionary is used in these unit tests.
"""
import pytest
from core.visualize import Visualize
from params import OUTPUT_DICT_GENERIC


@pytest.fixture(name="test_outcomes")
def fixture_visualize_outcomes():
    """
    This fixture initialises a Visualize class.
    :return: a Visualize class for a generic outcome dictionary
    """
    return Visualize(OUTPUT_DICT_GENERIC, 2 * 3 * 2)
