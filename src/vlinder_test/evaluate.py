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
            "-/": lambda x, y: -x / y if y else 0,
            ">": lambda x, y: 1 if x > y else 0,
            "<": lambda x, y: 1 if x < y else 0,
            ">=": lambda x, y: 1 if x >= y else 0,
            "<=": lambda x, y: 1 if x <= y else 0,
            "min": lambda x, y: min(x, y),  # ignore warning about unnecessary lambda | pylint: disable=W0108
            "max": lambda x, y: max(x, y),  # ignore warning about unnecessary lambda | pylint: disable=W0108
        }

    def _create_value_dict(self, scen_index: int, dmo_index: int) -> None:
        """
        This function creates a 'value-dictionary' that maps all variables to their current value.
        :param scen_index: index of the current scenario in the input_dictionary
        :param dmo_index: index of the current decision makers option in the input_dictionary
        :return None: self.value_dict is updated in this function
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
        }

    def _find_index(self, key: str, value: str or int) -> int:
        """This helper function returns the FIRST index of a value for a given key and value of self.input_dict."""
        return np.where(self.input_dict[key] == value)[0][0]

    def _squeeze(self, argument_1_value: float, squeeze_args: dict) -> int:
        """This functions evaluates ONLY the squeeze * operator function."""
        division_part = self.operators_dict["/"](argument_1_value, squeeze_args["saturation_point"])
        result = (
            min(1, division_part)
            * squeeze_args["accessibility"]
            * squeeze_args["probability_of_success"]
            * squeeze_args["maximum_effect"]
        )
        return result

    def _get_key_outputs(self) -> dict:
        """
        This function retrieves the current values of the key outputs, based on the value_dict.
        :return: a dictionary matching key outputs to their values, i.e. {KO1: 1.12, KO2: 2.33, ...}
        """
        key_output_values = [self.value_dict[key_output] for key_output in self.input_dict["key_outputs"]]
        return dict(zip(self.input_dict["key_outputs"], key_output_values))

    def _get_value_of_argument(self, arg: str) -> float:
        """
        This function transforms a string to a number (if applicable) else it looks up the correct value in the
        value dictionary.
        :param arg: the value that needs to be checked
        :return: the correct value of the argument
        """
        try:
            value = float(arg)
        except ValueError:
            value = self.value_dict[arg]
        return value

    def _evaluate_single_dependency(self, argument_1_value: float, argument_2_value: float, operator: str) -> int:
        """
        This function evaluates a single dependency. Raises an EvaluationError when the operator is unknown.
        :param argument_1_value: value of first argument
        :param argument_2_value: value of second argument
        :param operator: operator needed to calculate result based on the two arguments
        :return result: calculated value based on inputs & operator
        """
        if operator not in self.operators_dict.keys():  # ignore warning about .keys() | pylint: disable=C0201
            raise EvaluationError(f"operator {operator} not available")

        # apply operations based on occurrence in operators_dict
        result = self.operators_dict[operator](argument_1_value, argument_2_value)
        return result

    def evaluate_all_dependencies(self, scenario: str, decision_makers_option: str) -> dict:
        """
        This function returns an output dictionary containing the values of the key outputs for a given scenario and
        a given decision makers option.
        :param scenario: string of scenario name
        :param decision_makers_option: string of decision makers option
        :return: dictionary containing all key outputs for given scenario and decision makers option
        """
        scen_index = self._find_index("scenarios", scenario)
        dmo_index = self._find_index("decision_makers_options", decision_makers_option)
        self._create_value_dict(scen_index, dmo_index)

        # calculate each destination -- already ordered on hierarchy during the import
        for index, dest in enumerate(self.input_dict["destination"]):
            dest_value = self.value_dict.get(dest, 0)
            arg1 = self.input_dict["argument_1"][index]
            arg2 = self.input_dict["argument_2"][index]
            operator = self.input_dict["operator"][index]

            # squeezed * has its own evaluation function
            if operator == "squeezed *":
                dest_result = dest_value + self._squeeze(
                    self._get_value_of_argument(arg1),
                    {
                        "saturation_point": self.input_dict["saturation_point"][index],
                        "accessibility": self.input_dict["accessibility"][index],
                        "probability_of_success": self.input_dict["probability_of_success"][index],
                        "maximum_effect": self.input_dict["maximum_effect"][index],
                    },
                )
            # All other operators are calculated using a general approach
            else:
                dest_result = dest_value + self._evaluate_single_dependency(
                    self._get_value_of_argument(arg1), self._get_value_of_argument(arg2), operator
                )

            # update the value dictionary
            result = {dest: dest_result}
            self.value_dict.update(result)

        # structure the output dictionary
        output_dict = {"key_outputs": self._get_key_outputs()}
        return output_dict

    def evaluate_selected_scenario(self, scenario: str) -> dict:
        """
        This function creates an output dictionary for all decision makers option within a given scenario.
        :param scenario:
        :return: a dictionary that contains the outputs per decision makers options (for a single scenario)
        """
        output_dict = {}
        for decision_makers_option in self.input_dict["decision_makers_options"]:
            output_dict[decision_makers_option] = self.evaluate_all_dependencies(scenario, decision_makers_option)

        return output_dict

    def evaluate_all_scenarios(self) -> dict:
        """
        This function evaluates the dependencies for all scenario's and all decision makers options.
        :return: for each scenario, a dictionary for all decision makers options is returned
        """
        output_dict = {}
        for scenario in self.input_dict["scenarios"]:
            output_dict[scenario] = self.evaluate_selected_scenario(scenario)
            print(f"- Evaluated '{scenario}' successfully for all decision makers options!")

        return output_dict
