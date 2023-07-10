"""
This file contains the Evaluate class that deals with the calculation of key output values for
the decision makers options.
"""


class Evaluate:
    """This class deals with the calculation of key output values for the decision makers options."""

    def __init__(self, input_dict):
        self.input_dict = input_dict
        self.value_dict = {}

    def _create_value_dict(self, dmo_index: int) -> None:
        """
        This function creates a 'value-dictionary' that maps all variables to their current value.
        :return:
        """
        self.value_dict = {
            # add key outputs. initialise at zero
            **{key: 0 for key in self.input_dict["key_outputs"]},
            # add internal variable inputs (for given dmo and scenario)
            **dict(
                zip(
                    self.input_dict["internal_variable_inputs"],
                    self.input_dict["decision_makers_option_value"][dmo_index],
                )
            ),
        }

    @staticmethod
    def _evaluate_single_dependency(argument_1_value: str, argument_2_value: str, operator: str):
        """
        This function ...
        [Single row of dependencies]
        """
        # dictionary containing all functions to which operators are related
        operators_dict = {"-": lambda x, y: x - y, "+": lambda x, y: x + y, "*": lambda x, y: x * y}

        # apply operations based on occurrence in operators_dict
        if operator in operators_dict.keys():  # ignore warning about .keys() | pylint: disable=C0201
            return operators_dict[operator](argument_1_value, argument_2_value)

        return f"{operator} not available"

    def evaluate_all_dependencies(self, scenario, decision_maker_option):
        """
        [All dependencies, for single dmo and single scenario]
        --> this function should create/renew the value_dict
        :return:
        """
        print(scenario, decision_maker_option, self.value_dict)

    def evaluate_selected_scenario(self, scenario):
        """
        [All dependencies, for all dmos for a single scenario]
        :return:
        """
        for decision_maker_option in self.input_dict["decision_makers_options"]:
            self.evaluate_all_dependencies(scenario, decision_maker_option)

    def evaluate_all_scenarios(self):
        """
        [All dependencies, for all scenario's, for all dmo's]
        :return:
        """

        for scenario in self.input_dict["scenarios"]:
            self.evaluate_selected_scenario(scenario)
