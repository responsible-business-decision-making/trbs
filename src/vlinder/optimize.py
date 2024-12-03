# pylint: disable=W0212

"""
This module contains the Optimize class, which performs grid search optimization
to maximize the appreciation of decision-maker options.
"""

import math
from math import comb
from itertools import combinations_with_replacement, permutations
import numpy as np
from vlinder.appreciate import Appreciate
from vlinder.evaluate import Evaluate
from vlinder.utils import suppress_print


class Optimize:
    """
    The Optimize class performs grid search optimization to find the optimal distribution of internal input values
    that maximizes the appreciation value of decision-maker options.
    """

    def __init__(self, input_dict, output_dict):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.boundaries = None

    def find_dict_values(self, scenario):
        """
        This function retrieves values based on the input and output dictionaries.
        """
        # Identify the decision-maker's option (DMO) with the highest appreciation in the given scenario
        dmo_name = self.output_dict[scenario]["highest_weighted_dmo"]

        # Identify the highest appreciation of that DMO
        max_appreciated_value = self.output_dict[scenario][dmo_name]["decision_makers_option_appreciation"]

        # Identify the distibution of that DMO
        decision_maker_options = self.input_dict["decision_makers_option_value"][
            np.where(self.input_dict["decision_makers_options"] == dmo_name)[0][0]
        ]

        best_dmo_data = {
            "dmo_name": dmo_name,
            "decision_maker_options": decision_maker_options,
            "max_appreciated_value": max_appreciated_value,
        }

        # Sum the values for this DMO (this represents the total investment)
        max_investment = sum(decision_maker_options)

        return best_dmo_data, max_investment

    @staticmethod
    def scale_max_investment(max_investment):
        """
        This function scales down the maximum investment value to make it more manageable for combinatorial purposes.
        It rounds the investment down to the nearest hundred, taking into account the order of magnitude.
        """
        # Determine the order of magnitude of the investment (in thousands)
        order_of_magnitude = math.floor(math.log10(abs(max_investment))) - 3

        # Normalize the value to thousands
        normalized_max_investment = max_investment / (10**order_of_magnitude)

        # Round the value to the nearest hundred
        scaled_max_investment = math.floor(round(normalized_max_investment, 1) / 100) * 100

        return scaled_max_investment

    @staticmethod
    def calculate_step_size(max_investment, scaled_max_investment, num_internal_inputs, max_combinations):
        """
        This function calculates the optimal step size to reduce the number of combinations.
        The goal is to stay under the maximum allowable number of combinations for efficiency.
        """
        step_size_tmp = 1

        while True:
            # Calculate the number of units with the current step size
            units = scaled_max_investment // step_size_tmp

            # Calculate the number of combinations using binomial coefficient
            combinations = comb(units + num_internal_inputs - 1, num_internal_inputs - 1)

            if combinations <= max_combinations and scaled_max_investment % step_size_tmp == 0:
                # If the number of combinations is within the constraints, use this step size
                break

            # Increase the step size if the number of combinations exceeds the limit
            step_size_tmp += 1

        # Scale the step size based on the original max investment
        step_size = max_investment / (scaled_max_investment / step_size_tmp)

        return step_size

    @staticmethod
    def generate_combinations(max_investment, step_size, num_internal_inputs):
        """
        This function generates all valid combinations of internal input values whose sum equals max_investment.
        """
        base_combinations = np.arange(0, max_investment + step_size, step_size)
        valid_combinations = []

        # Generate combinations and filter those that sum to the max investment
        for combination in combinations_with_replacement(base_combinations, num_internal_inputs):
            if sum(combination) == max_investment:
                # Add all unique permutations of the combination
                for perm in set(permutations(combination)):
                    valid_combinations.append(perm)

        return valid_combinations

    @suppress_print
    def grid_search(self, scenario, combinations, opt_dmo_name, best_dmo_data):
        """
        Performs a grid search over all possible combinations of internal input values.
        The function evaluates each combination, calculates the appreciation value, and returns the best one.
        """
        # Get minimum and maximum values for the key outputs across all scenarios
        self.boundaries = Appreciate(self.input_dict, self.output_dict)._get_start_and_end_points()

        # Initialize the grid search decision-maker option
        self.input_dict["decision_makers_options"] = np.array(
            np.append(self.input_dict["decision_makers_options"], opt_dmo_name), dtype=object
        )
        self.input_dict["decision_makers_option_value"] = np.vstack(
            [self.input_dict["decision_makers_option_value"], best_dmo_data["decision_maker_options"]]
        )
        self.input_dict["key_output_automatic"] = np.zeros(len(self.input_dict["key_output_automatic"]), dtype=int)
        self.input_dict["key_output_start"] = np.array([value[0] for value in self.boundaries.values()])
        self.input_dict["key_output_end"] = np.array([value[1] for value in self.boundaries.values()])

        # Arrays to store results
        appreciated_values = []
        tmp_opt_decision_maker_options = None
        tmp_opt_max_appreciated_value = -np.inf

        # Evaluate each combination
        for index, combination in enumerate(combinations):
            comb_array = np.array(combination)

            # Ensure the combination length matches the number of internal inputs
            if len(comb_array) == len(self.input_dict["internal_variable_inputs"]):
                self.input_dict["decision_makers_option_value"][
                    np.where(self.input_dict["decision_makers_options"] == opt_dmo_name)[0][0]
                ] = comb_array

                # Evaluate and appreciate
                output_dict = Evaluate(self.input_dict).evaluate_selected_scenario(scenario)[opt_dmo_name]
                Appreciate(self.input_dict, output_dict).appreciate_single_decision_maker_option(output_dict)

                # Compute the appreciated value
                appreciated_value = output_dict["decision_makers_option_appreciation"]
                appreciated_values.append((index, comb_array, appreciated_value))

                # Update the best combination if this is the highest appreciation value
                if appreciated_value > tmp_opt_max_appreciated_value:
                    tmp_opt_max_appreciated_value = appreciated_value
                    tmp_opt_decision_maker_options = comb_array

        if tmp_opt_max_appreciated_value > best_dmo_data["max_appreciated_value"]:
            self.input_dict["decision_makers_option_value"][
                np.where(self.input_dict["decision_makers_options"] == opt_dmo_name)[0][0]
            ] = tmp_opt_decision_maker_options
            best_dmo = opt_dmo_name
            best_appreciated_value = tmp_opt_max_appreciated_value
        else:
            self.input_dict["decision_makers_option_value"][
                np.where(self.input_dict["decision_makers_options"] == opt_dmo_name)[0][0]
            ] = best_dmo_data["decision_maker_options"]
            best_dmo = best_dmo_data["dmo_name"]
            best_appreciated_value = best_dmo_data["max_appreciated_value"]

        return best_dmo, best_appreciated_value

    def optimize_single_scenario(self, scenario, tmp_opt_dmo_name, max_combinations):
        """
        Wrapper function that performs the full grid search optimization process.
        It retrieves values, calculates the step size, generates valid combinations,
        and finds the best distribution of internal inputs to maximize appreciation.
        """
        if tmp_opt_dmo_name in self.input_dict["decision_makers_options"]:
            print("This DMO name already exits, please choose another")
            return self.input_dict

        # Step 1: Retrieve values and setup boundaries
        best_dmo_data, max_investment = self.find_dict_values(scenario)

        # Step 2: Scale down the maximum investment for more efficient combinatorial calculations
        scaled_max_investment = self.scale_max_investment(max_investment)

        # TO DO: max_combinations based on CPU
        # Step 3: Find the optimal step size for generating combinations
        step_size = self.calculate_step_size(
            max_investment, scaled_max_investment, len(self.input_dict["internal_variable_inputs"]), max_combinations
        )

        # Step 4: Generate all valid combinations of internal input values
        combinations = self.generate_combinations(
            max_investment, step_size, len(self.input_dict["internal_variable_inputs"])
        )

        # Step 5: Perform grid search over the generated combinations and fill in input_dict
        best_dmo, best_appreciated_value = self.grid_search(scenario, combinations, tmp_opt_dmo_name, best_dmo_data)

        # Print the results
        print("For scenario: ", scenario)
        print("------------------------------------")
        print(
            "Initial best appreciation:",
            round(best_dmo_data["max_appreciated_value"], 2),
            "for DMO:",
            best_dmo_data["dmo_name"],
        )
        print(
            "With the following internal variable distribution: ",
            "["
            + ", ".join(
                str(int(num)) if num.is_integer() else str(num) for num in best_dmo_data["decision_maker_options"]
            )
            + "]",
        )
        print("------------------------------------")
        print("Optimized appreciation:", round(best_appreciated_value, 2), "for DMO:", best_dmo)
        print(
            "With the following internal variable distribution: ",
            "["
            + ", ".join(
                str(int(num)) if num.is_integer() else str(num)
                for num in self.input_dict["decision_makers_option_value"][
                    np.where(self.input_dict["decision_makers_options"] == best_dmo)[0][0]
                ]
            )
            + "]",
        )
        print("------------------------------------")
        print(
            "Total increase appreciated value:",
            round(best_appreciated_value - best_dmo_data["max_appreciated_value"], 2),
        )

        return self.input_dict
