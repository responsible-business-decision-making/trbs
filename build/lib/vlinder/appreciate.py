"""
This file contains the Appreciate class that deals with the calculation of appreciations.
"""
import math
import pandas as pd
import numpy as np
from vlinder.utils import get_values_from_target


class Appreciate:
    """This class deals with the calculation of appreciations"""

    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.start_and_end_points = self._get_start_and_end_points()

    # TODO: monetary values
    def _get_start_and_end_points(self) -> dict:
        """
        This function obtains the minimum and maximum values of the calculated key_output values, over ALL scenarios
        and decision makers options.
        :return: a dictionary of type {key_output 1: [min, max], key_output 2: [min, max], .. }
        """
        boundaries = {}
        all_key_output_values = get_values_from_target(self.output_dict, "key_outputs")
        values_as_df = pd.DataFrame.from_dict(all_key_output_values)

        for key_output in values_as_df.columns:
            boundaries[key_output] = [values_as_df[key_output].min(), values_as_df[key_output].max()]

        return boundaries

    def _appreciate_single_key_output(self, value: float, args: dict) -> float:
        """
        This function appreciates a single key output, given the value, arguments and start & end point.
        :param value: value of key output
        :param args: dictionary containing whether the key output should be appreciated linear or smaller the better.
        :return: the appreciated value of the key output
        """
        start_and_end = self.start_and_end_points[args["key_output"]]
        stb_ind = args["key_output_smaller_the_better"]

        # Option 0A: values lie outside the boundaries. Return maximum or minimum based on STB
        if value < start_and_end[0] or value > start_and_end[1]:
            return stb_ind * (value < start_and_end[0]) * 100 + (1 - stb_ind) * (value > start_and_end[1]) * 100

        # Option 0B: start and end value are the same --> indifferent so return 0
        if start_and_end[1] - start_and_end[0] < 1e-6:
            return 0

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

    def appreciate_single_decision_maker_option(self, value_dict_in: dict) -> None:
        """
        This function calculates the appreciation values, both weighted as well as unweighted for the key outputs for a
        given scenario and decision makers option. Results are stored within the output_dict.
        :param scenario: given scenario
        :param decision_maker_option: given dmo
        :param value_dict_in: dictionary corresponding with given scenario and dmo
        :return: None as results are stored within the output_dict
        """
        value_dict_in["appreciations"] = {}
        for index, key_output in enumerate(self.input_dict["key_outputs"]):
            key_output_value = value_dict_in["key_outputs"][key_output]
            appreciation_args = {
                "key_output": key_output,
                "key_output_smaller_the_better": self.input_dict["key_output_smaller_the_better"][index],
                "key_output_linear": self.input_dict["key_output_linear"][index],
            }
            appreciation = self._appreciate_single_key_output(key_output_value, appreciation_args)

            value_dict_in["appreciations"][key_output] = appreciation

        weighted_appreciations = self._apply_weights(value_dict_in["appreciations"])
        value_dict_in["weighted_appreciations"] = {
            key: weighted_appreciations[index] for index, key in enumerate(self.input_dict["key_outputs"])
        }
        value_dict_in["decision_makers_option_appreciation"] = sum(weighted_appreciations)

    def appreciate_single_scenario(self, value_dict_in: dict) -> None:
        """
        This function calculates the appreciation values, both weighted as well as unweighted for the key outputs for a
        given scenario and ALL decision makers options. Results are stored within the output_dict.
        :param scenario: given scenario
        :param value_dict_in: dictionary corresponding with given scenario
        :return: None as results are stored within the output_dict
        """
        for _, value_dict_out in value_dict_in.items():
            self.appreciate_single_decision_maker_option(value_dict_out)

    def appreciate_all_scenarios(self) -> None:
        """
        This function calculates the appreciation values, both weighted as well as unweighted for the key outputs for a
        given scenario and ALL decision makers options. Results are stored within the output_dict.
        :return: None as results are stored within the output_dict
        """ ""
        for _, value_dict in self.output_dict.items():
            self.appreciate_single_scenario(value_dict)
        self._apply_scenario_weights()
        print("Key output values have been processed | Appreciated, weighted & aggregated")

    @staticmethod
    def _apply_weights_single_key_output(weights: dict) -> float:
        """
        This function calculates the weight for a single key output.
        :param weights: dictionary containing necessary parameters. Should contain:
            - 'sum_within_theme': sum of all weights of all key outputs with the same theme
            - 'sum_theme': sum of the theme weights (theme weights are user input)
            - 'key_output': weight of this key_output
            - 'theme': weight of the theme of the key_output
        :return: the calculated weight of the key output
        """
        # 'sum_within_theme' or 'sum_theme' cannot be 0
        if not weights["sum_within_theme"] or not weights["sum_theme"]:
            return 0
        return (weights["key_output"] / weights["sum_within_theme"]) * (weights["theme"] / weights["sum_theme"])

    def _calculate_weights(self) -> list:
        """
        This function creates a weights list for all key outputs.
        :return: list with weights for all key outputs
        """
        key_output_themes = self.input_dict["key_output_theme"]
        weights = self.input_dict["key_output_weight"]
        theme_weights = self.input_dict["theme_weight"]

        adjusted_weights = []
        for index, _ in enumerate(self.input_dict["key_outputs"]):
            theme = key_output_themes[index]
            # Find all key outputs weights that share the same theme as 'key_output' (>= 1)
            theme_indices = [
                theme_index for theme_index, theme_value in enumerate(key_output_themes) if theme_value == theme
            ]
            weights_within_theme = weights[theme_indices]
            # Find theme weight of 'key_output' - as a number instead of array
            theme_weight = theme_weights[np.where(self.input_dict["themes"] == theme)[0]][0]

            weights_dict = {
                "key_output": weights[index],
                "theme": theme_weight,
                "sum_theme": np.sum(theme_weights),
                "sum_within_theme": np.sum(weights_within_theme),
            }
            adjusted_weights.append(self._apply_weights_single_key_output(weights_dict))

        return adjusted_weights

    def _apply_weights(self, appreciation_dict: dict) -> np.array:
        """
        This function applies the weights to the appreciations
        :param appreciation_dict: dictionary contain the unweighted appreciations
        :return: a numpy array with the weighted appreciations
        """
        # ensure appreciation vector has same order as weight & key_outputs vector
        appreciations = [appreciation_dict[key_output] for key_output in self.input_dict["key_outputs"]]
        # calculate the (adjusted) weight for given key_output & theme weight
        weights = self._calculate_weights()
        weighted_appreciations = np.array(appreciations) * np.array(weights)

        return weighted_appreciations

    def _apply_scenario_weights(self) -> None:
        """
        This function applies scenario weights to the decision makers' option appreciations
        :return: None as results are stored within the output_dict
        """
        total_weight = sum(self.input_dict["scenario_weight"])

        for scenario, weight in zip(self.input_dict["scenarios"], self.input_dict["scenario_weight"]):
            for option in self.input_dict["decision_makers_options"]:
                appreciation = self.output_dict[scenario][option]["decision_makers_option_appreciation"]
                weighted_appreciation = appreciation * weight / total_weight
                self.output_dict[scenario][option]["scenario_appreciations"] = weighted_appreciation
