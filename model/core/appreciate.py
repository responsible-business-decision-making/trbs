"""
This file contains the Appreciate class that deals with the calculation of appreciations.
"""
import math
import pandas as pd
import numpy as np


class Appreciate:
    """This class deals with the calculation of appreciations"""

    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.start_and_end_points = self._get_start_and_end_points()

    def _get_values_from_target(self, dictionary, target):
        """

        :param dictionary:
        :param target:
        :return:
        """
        values = []

        for key, value in dictionary.items():
            if key == target:
                values.append(value)
            elif isinstance(value, dict):
                values.extend(self._get_values_from_target(value, target))

        return values

    # TODO: monetary values
    def _get_start_and_end_points(self):
        """

        :return:
        """
        boundaries = {}
        all_key_output_values = self._get_values_from_target(self.output_dict, "key_outputs")
        values_as_df = pd.DataFrame.from_dict(all_key_output_values)

        for key_output in values_as_df.columns:
            boundaries[key_output] = [values_as_df[key_output].min(), values_as_df[key_output].max()]

        return boundaries

    def _appreciate_single_key_output(self, value, args: dict):
        """

        :param value:
        :param args:
        :return:
        """
        start_and_end = self.start_and_end_points[args["key_outputs"]]
        stb_ind = args["key_output_smaller_the_better"]

        # By construction of the start and end point it is not possible for the value to lie outside these bounds.
        # Therefore start <= value <= end always holds

        # Option 1: Linear appreciation
        #   - if STB = 1: (end - val) / (end - start) * 100
        #   - if STB = 0: (val - start) / (end - start) * 100
        if args["key_output_linear"]:
            return [-1, 1][stb_ind] * (start_and_end[stb_ind] - value) / (start_and_end[1] - start_and_end[0]) * 100
        # Option 2: Non-linear appreciation
        #   - if STB = 1: (-sin(0.5 * pi * (val-start) / (end - start) + 1) * 100
        #   - if STB = 0: sin(0.5 * pi * (val - start) / (end - start) + 0) * 100
        core_part = (value - start_and_end[0]) / (start_and_end[1] - start_and_end[0])
        return ([1, -1][stb_ind] * math.sin(0.5 * math.pi * core_part) + stb_ind) * 100

    def appreciate_single_decision_maker_option(self, scenario, decision_maker_option, value_dict_in):
        """

        :param value_dict_in:
        :param scenario:
        :param decision_maker_option:
        :return:
        """
        print("\n", scenario, "|", decision_maker_option)

        value_dict_in["appreciations"] = {}
        for index, key_output in enumerate(self.input_dict["key_outputs"]):
            key_output_value = value_dict_in["key_outputs"][key_output]
            appreciation_args = {
                key: value[index] for key, value in self.input_dict.items() if key.startswith("key_output")
            }
            appreciation = self._appreciate_single_key_output(key_output_value, appreciation_args)

            value_dict_in["appreciations"][key_output] = appreciation

        weighted_appreciations = self._apply_weights(value_dict_in["appreciations"])
        value_dict_in["weighted_appreciations"] = {
            key: weighted_appreciations[index] for index, key in enumerate(self.input_dict["key_outputs"])
        }

    def appreciate_single_scenario(self, scenario, value_dict_in):
        """

        :param value_dict_in:
        :param scenario:
        :return:
        """
        for decision_maker_option, value_dict_out in value_dict_in.items():
            self.appreciate_single_decision_maker_option(scenario, decision_maker_option, value_dict_out)

    def appreciate_all_scenarios(self):
        """This function ..."""
        for scenario, value_dict in self.output_dict.items():
            self.appreciate_single_scenario(scenario, value_dict)

    @staticmethod
    def _apply_weights_single_key_output(weights):
        """

        :param weights:
        :return:
        """
        # 'sum_within_theme' or 'sum_theme' cannot be 0
        if not weights["sum_within_theme"] or not weights["sum_theme"]:
            return 0
        return (weights["key_output"] / weights["sum_within_theme"]) * (weights["theme"] / weights["sum_theme"])

    def _calculate_weights(self):
        key_outputs = self.input_dict["key_outputs"]
        key_output_themes = self.input_dict["key_output_theme"]
        weights = self.input_dict["key_output_weight"]
        themes = self.input_dict["themes"]
        theme_weights = self.input_dict["theme_weight"]

        adjusted_weights = []
        for index, _ in enumerate(key_outputs):
            theme = key_output_themes[index]
            # Find all key outputs weights that share the same theme as 'key_output' (>= 1)
            theme_indices = [
                theme_index for theme_index, theme_value in enumerate(key_output_themes) if theme_value == theme
            ]
            weights_within_theme = weights[theme_indices]
            # Find theme weight of 'key_output' - as a number instead of array
            theme_weight = theme_weights[np.where(themes == theme)[0]][0]

            weights_dict = {
                "key_output": weights[index],
                "theme": theme_weight,
                "sum_theme": np.sum(theme_weights),
                "sum_within_theme": np.sum(weights_within_theme),
            }
            adjusted_weights.append(self._apply_weights_single_key_output(weights_dict))

        return adjusted_weights

    def _apply_weights(self, appreciation_dict: dict):
        """This function ..."""
        # ensure appreciation vector has same order as weight & key_outputs vector
        appreciations = [appreciation_dict[key_output] for key_output in self.input_dict["key_outputs"]]
        # calculate the (adjusted) weight for given key_output & theme weight
        weights = self._calculate_weights()
        weighted_appreciations = np.array(appreciations) * np.array(weights)

        print(f"{self.input_dict['key_outputs']}: {appreciations} * {weights} = {weighted_appreciations}")
        return weighted_appreciations
