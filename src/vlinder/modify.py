# pylint: disable=W0212
"""
This module contains the Modify class, which performs a modification in the input dict.
"""
import numpy as np


class Modify:
    """
    The Modify class performs a modification in the input dict.
    """

    def __init__(self, input_dict):
        self.input_dict = input_dict
        self.boundaries = None

    def modify(self, input_dict_key, element_key, new_value):
        """
        This function modifies a specific value in the input dict.
        """       
        supported_input_keys = ["key_output_weight", "scenario_weight", "theme_weight"]

        if input_dict_key not in supported_input_keys:
            raise ValueError("Please specify one of", supported_input_keys)

        master_key = input_dict_key.split("_weight")[0] + "s"
        index = np.where(self.input_dict[master_key] == element_key)
        old_value = self.input_dict[input_dict_key][index]

        self.input_dict[input_dict_key][index] = new_value

        print(f"The weight for {element_key} in {input_dict_key} is changed from {old_value[0]} to {new_value}.") 
        return self.input_dict
