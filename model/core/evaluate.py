"""
This file contains the Evaluate class that deals with the calculation of key output values for
the decision makers options.
"""
import numpy as np


class EvaluationError(Exception):
    """
    This class deals with the error handling of our evaluate calculations.
    """

    def __init__(self, message):  # ignore warning about super-init | pylint: disable=W0231
        self.message = message

    def __str__(self):
        return f"Evaluation Error: {self.message}"


class Evaluate:
    """This class deals with the calculation of key output values for the decision makers options."""

    def __init__(self, input_dict):
        self.input_dict = input_dict
        self.value_dict = {}
        # dictionary containing all functions to which operators are related
        self.operators_dict = {
            "-": lambda x, y: x - y,
            "+": lambda x, y: x + y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y if y else 0,
            "-*": lambda x, y: -x * y,
        }

    def _create_value_dict(self, scen_index: int, dmo_index: int) -> None:
        """
        This function creates a 'value-dictionary' that maps all variables to their current value.
        :return:
        """
        self.value_dict = {
            # add key outputs. Initialise at zero.
            **{key: 0 for key in self.input_dict["key_outputs"]},
            # add internal variable values (for given dmo and scenario)
            **dict(
                zip(
                    self.input_dict["internal_variable_inputs"],
                    self.input_dict["decision_makers_option_value"][dmo_index],
                )
            ),
            # add external variable values
            **dict(zip(self.input_dict["external_variable_inputs"], self.input_dict["scenario_value"][scen_index])),
            # add fixed values
            **dict(zip(self.input_dict["fixed_inputs"], self.input_dict["fixed_input_value"])),
            "": 1,
        }

    def _find_index(self, key: str, value: str) -> int:
        """This helper function returns the FIRST index of a value for a given key and value of self.input_dict."""
        return np.where(self.input_dict[key] == value)[0][0]

    def _squeeze(self, argument_1_value: int, argument_2_value: int, squeeze_args: dict):
        """This functions evaluates ONLY the Squeeze * operator function."""
        division_part = self.operators_dict["/"](
            min(argument_1_value, argument_2_value), squeeze_args["saturation_point"]
        )
        result = (
            min(1, division_part)
            * squeeze_args["accessibility"]
            * squeeze_args["probability_of_success"]
            * squeeze_args["maximum_effect"]
        )
        print(
            f"\t add: {result} = min({argument_1_value},{argument_2_value}) / {squeeze_args['saturation_point']}"
            f"* {squeeze_args['accessibility']} * {squeeze_args['probability_of_success']} *"
            f"{squeeze_args['maximum_effect']}"
        )
        return result

    def _get_key_outputs(self) -> dict:
        """
        This function retrieves the current values of the key outputs, based on the value_dict.
        :return: a dictionary matching key outputs to their values, i.e. {KO1: 1.12, KO2: 2.33, ...}
        """
        key_output_values = [self.value_dict[key_output] for key_output in self.input_dict["key_outputs"]]
        return dict(zip(self.input_dict["key_outputs"], key_output_values))

    def _evaluate_single_dependency(self, argument_1_value: int, argument_2_value: int, operator: str):
        """
        This function ...
        [Single row of dependencies]
        """
        if operator not in self.operators_dict.keys():  # ignore warning about .keys() | pylint: disable=C0201
            raise EvaluationError(f"operator {operator} not available")

        # apply operations based on occurrence in operators_dict
        result = self.operators_dict[operator](argument_1_value, argument_2_value)
        print(f"\tadd: '{result}' = '{argument_1_value}' {operator} '{argument_2_value}'")
        return result

    def evaluate_all_dependencies(self, scenario, decision_makers_option):
        """
        [All dependencies, for single dmo and single scenario]
        --> this function should create/renew the value_dict
        :return:
        """
        scen_index = self._find_index("scenarios", scenario)
        dmo_index = self._find_index("decision_makers_options", decision_makers_option)
        self._create_value_dict(scen_index, dmo_index)
        print(f"\n\nScenario: {scenario} | Decision Makers Option: {decision_makers_option}")

        # calculate each destination -- already ordered on hierarchy during the import
        for index, dest in enumerate(self.input_dict["destination"]):
            dest_value = self.value_dict.get(dest, 0)
            arg1 = self.input_dict["argument_1"][index]
            arg2 = self.input_dict["argument_2"][index]
            operator = self.input_dict["operator"][index]

            print(f"\n{index}. '{dest} (value: {dest_value})' = '{arg1}' {operator} '{arg2}'")

            # Squeezed * has its own evaluation function
            if operator == "Squeezed *":
                arg2 = arg1 if not arg2 else arg2  # Override default of '1' if needed
                result = {
                    dest: dest_value
                    + self._squeeze(
                        self.value_dict[arg1],
                        self.value_dict[arg2],
                        {
                            "saturation_point": self.input_dict["saturation_point"][index],
                            "accessibility": self.input_dict["accessibility"][index],
                            "probability_of_success": self.input_dict["probability_of_success"][index],
                            "maximum_effect": self.input_dict["maximum_effect"][index],
                        },
                    )
                }
            # All other operators are calculated using a general approach
            else:
                result = {
                    dest: dest_value
                    + self._evaluate_single_dependency(self.value_dict[arg1], self.value_dict[arg2], operator)
                }

            # update the value dictionary
            self.value_dict.update(result)

        # structure the output dictionary
        output_dict = {"key_outputs": self._get_key_outputs()}
        return output_dict

    def evaluate_selected_scenario(self, scenario):
        """
        [All dependencies, for all dmos for a single scenario]
        :return:
        output_dict: a dictionary that contains the outputs per decision makers options (for a single scenario)
        """
        output_dict = {}
        for decision_makers_option in self.input_dict["decision_makers_options"]:
            output_dict[decision_makers_option] = self.evaluate_all_dependencies(scenario, decision_makers_option)

        return output_dict

    def evaluate_all_scenarios(self):
        """
        This function evaluates the dependencies for all scenario's and all decision makers options.
        :return:
        output_dict: for each scenario, a dictionary for all decision makers options is returned
        """
        output_dict = {}
        for scenario in self.input_dict["scenarios"]:
            output_dict[scenario] = self.evaluate_selected_scenario(scenario)

        return output_dict
