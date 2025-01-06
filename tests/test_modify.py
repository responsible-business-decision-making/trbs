# Ignore PEP8 protected-access to client class | pylint: disable=W0212
"""
This module contains all tests for the modify method in the trbs.py file
"""
import pytest
import numpy as np
from vlinder.trbs import TheResponsibleBusinessSimulator


@pytest.mark.parametrize(
    "arg, expected_result",
    [
        (["theme_weight", "Planet", 1000], 1000),
        (["key_output_weight", "Accidents reduction", 2000], 2000),
        (["scenario_weight", "Base case", 3000], 3000),
    ],
)
def test_modify(arg, expected_result):
    """
    This function tests the modify method in the TheResponsibleBusinessSimulator class
    :param arg: the list to be checked
    :param expected_result: the expected content of this list
    """
    case = TheResponsibleBusinessSimulator("beerwiser")
    case.build()
    case.modify(arg[0], arg[1], arg[2])
    master_key = arg[0].split("_weight")[0] + "s"
    index = np.where(case.input_dict[master_key] == arg[1])[0][0]
    result = case.input_dict[arg[0]][index]
    assert result == expected_result
