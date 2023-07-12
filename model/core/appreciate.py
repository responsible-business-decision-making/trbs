"""
This file contains the Appreciate class that deals with the calculation of appreciations.
"""
import pandas as pd


class Appreciate:
    """This class deals with the calculation of appreciations"""

    def __init__(self, output_dict):
        self.output_dict = output_dict
        self.start_and_end_points = self._get_start_and_end_points()

        print(self.start_and_end_points)

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

    def appreciate_single_decision_maker_option(self, scenario, decision_maker_option, value_dict_in):
        """

        :param value_dict_in:
        :param scenario:
        :param decision_maker_option:
        :return:
        """
        print(scenario, "|", decision_maker_option)
        print(value_dict_in)

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
