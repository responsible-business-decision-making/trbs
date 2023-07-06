"""
This file contains the import_case() function that deals with reading the data (.csv, .json or .xlsx) and structuring
it as a dictionary of numpy arrays.
"""
# importing necessary dependencies
from pathlib import Path
import pandas as pd
import numpy as np


def import_case(file_format: str, path):
    """
    This function reads and formats the data for a specific case
    :param file_format: either csv, json or xlsx
    :param path: path to location of relevant data
    :return: a dictionary containing numpy arrays for all data input
    """
    # specify the 10 tables
    tables = [
        "configurations",
        "key_outputs",
        "decision_makers_options",
        "scenarios",
        "fixed_inputs",
        "intermediates",
        "dependencies",
        "theme_weights",
        "key_output_weights",
        "scenario_weights",
    ]

    # use Path to avoid issues between users on macOS and Windows
    path_base = Path(path) / file_format

    # depending on file_format, import into a dictionary with 10 pandas dataframes
    df_dict = {}
    if file_format == "csv":
        # path_csv = path + "csv\\"
        for t in tables:
            df = pd.read_csv(path_base / t / ".csv", sep=";")
            df_dict[t] = df
    elif file_format == "json":
        # path_json = path + "json\\"
        for t in tables:
            df = pd.read_json(path_base / t / ".json", orient="table")
            df_dict[t] = df
    elif file_format == "xlsx":
        # path_xlsx = path + "xlsx\\"
        for t in tables:
            df = pd.read_excel(path_base / "beerwiser.xlsx", sheet_name=t)
            df_dict[t] = df

    # transform the dictionary with 10 pandas dataframes into a dictionary with numpy arrays

    np_dict = {}

    # step 1
    df = df_dict["configurations"]
    np_dict["configurations"] = df.configuration.to_numpy()
    np_dict["configuration_value"] = df.value.to_numpy()

    # step 2
    df = df_dict["key_outputs"]
    np_dict["key_outputs"] = df.key_output.to_numpy()
    np_dict["key_output_unit"] = df.unit.to_numpy()
    np_dict["key_output_theme"] = df.theme.to_numpy()
    themes = np.array([])
    for i in range(len(df)):
        if not (df.theme.iloc[i] in themes):
            themes = np.append(themes, [df.theme.iloc[i]])
    np_dict["themes"] = themes
    np_dict["key_output_minimum"] = df.minimum.to_numpy()
    np_dict["key_output_maximum"] = df.maximum.to_numpy()
    np_dict["key_output_monetary"] = df.monetary.to_numpy()
    np_dict["key_output_smaller_the_better"] = df.smaller_the_better.to_numpy()
    np_dict["key_output_linear"] = df.linear.to_numpy()
    np_dict["key_output_automatic"] = df.automatic.to_numpy()
    np_dict["key_output_start"] = df.start.to_numpy()
    np_dict["key_output_end"] = df.end.to_numpy()
    np_dict["key_output_threshold"] = df.threshold.to_numpy()

    # step 3
    df = df_dict["decision_makers_options"]
    decision_makers_options = np.array([])
    internal_variable_inputs = np.array([])
    decision_makers_option_value = np.empty(
        (df.decision_makers_option.nunique(), df.internal_variable_input.nunique())
    )
    # TODO: check correctness of this code block. Not all entries of matrix are filled
    for i in range(len(df)):
        if not (df.decision_makers_option.iloc[i] in decision_makers_options):
            row_index = len(decision_makers_options)
            decision_makers_options = np.append(decision_makers_options, [df.decision_makers_option.iloc[i]])
        if not (df.internal_variable_input.iloc[i] in internal_variable_inputs):
            column_index = len(internal_variable_inputs)
            internal_variable_inputs = np.append(internal_variable_inputs, [df.internal_variable_input.iloc[i]])
        # print(row_index, column_index, df.value.iloc[i])
        decision_makers_option_value[row_index, column_index] = df.value.iloc[i]
    np_dict["decision_makers_options"] = decision_makers_options
    np_dict["internal_variable_inputs"] = internal_variable_inputs
    np_dict["decision_makers_option_value"] = decision_makers_option_value

    # step 4
    df = df_dict["scenarios"]
    scenarios = np.array([])
    external_variable_inputs = np.array([])
    scenario_value = np.empty((df.scenario.nunique(), df.external_variable_input.nunique()))
    # TODO: check correctness of this code block. Not all entries of matrix are filled
    for i in range(len(df)):
        if not (df.scenario.iloc[i] in scenarios):
            row_index = len(scenarios)
            scenarios = np.append(scenarios, [df.scenario.iloc[i]])
        if not (df.external_variable_input.iloc[i] in external_variable_inputs):
            column_index = len(external_variable_inputs)
            external_variable_inputs = np.append(external_variable_inputs, [df.external_variable_input.iloc[i]])
        scenario_value[row_index, column_index] = df.value.iloc[i]
    np_dict["scenarios"] = scenarios
    np_dict["external_variable_inputs"] = external_variable_inputs
    np_dict["scenario_value"] = scenario_value

    # step 5a
    df = df_dict["fixed_inputs"]
    np_dict["fixed_inputs"] = df.fixed_input.to_numpy()
    np_dict["fixed_input_value"] = df.value.to_numpy()
    np_dict["fixed_input_unit"] = df.unit.to_numpy()

    # step 5b
    df = df_dict["intermediates"]
    np_dict["intermediates"] = df.intermediate.to_numpy()
    np_dict["intermediate_unit"] = df.unit.to_numpy()
    np_dict["intermediate_minimum"] = df.minimum.to_numpy()
    np_dict["intermediate_maximum"] = df.maximum.to_numpy()

    # step 5c
    df = df_dict["dependencies"]
    dependencies_unsorted = df.index.to_numpy()
    destination_unsorted = df.destination.to_numpy()
    argument_1_unsorted = df.argument_1.to_numpy(na_value="")
    argument_2_unsorted = df.argument_2.to_numpy(na_value="")
    operator_unsorted = df.operator.to_numpy()
    maximum_effect_unsorted = df.maximum_effect.to_numpy()
    accessibility_unsorted = df.accessibility.to_numpy()
    probability_of_success_unsorted = df.probability_of_success.to_numpy()
    saturation_point_unsorted = df.saturation_point.to_numpy()

    # derive hierarchy & calculation order of dependencies in two steps
    # step 1: initialize hierarchy = 1 for destinations that depend on input model objects
    input_model_objects = np.append(
        np_dict["fixed_inputs"], np.append(internal_variable_inputs, external_variable_inputs)
    )

    # add '', which represents a missing argument and should be treated as input as well
    input_model_objects = np.append(input_model_objects, "")

    no_dependencies = len(dependencies_unsorted)
    hierarchy = np.empty(no_dependencies)
    calculation_order = np.empty(no_dependencies)
    c = 0
    for i in range(no_dependencies):
        if argument_1_unsorted[i] in input_model_objects and argument_2_unsorted[i] in input_model_objects:
            hierarchy[i] = 1
            c += 1
            calculation_order[i] = c
        else:
            hierarchy[i] = no_dependencies

    # step 2: iteratively increase hierarchy by 1
    for h in range(1, no_dependencies):
        for i in range(no_dependencies):
            if hierarchy[i] > h:
                if len(hierarchy[np.where(destination_unsorted == argument_1_unsorted[i])[0]]) == 0:
                    if np.max(hierarchy[np.where(destination_unsorted == argument_2_unsorted[i])[0]]) <= h:
                        hierarchy[i] = h + 1
                        c += 1
                        calculation_order[i] = c
                elif len(hierarchy[np.where(destination_unsorted == argument_2_unsorted[i])[0]]) == 0:
                    if np.max(hierarchy[np.where(destination_unsorted == argument_1_unsorted[i])[0]]) <= h:
                        hierarchy[i] = h + 1
                        c += 1
                        calculation_order[i] = c

    # order the dependency arrays
    sorted_index = np.argsort(calculation_order)
    np_dict["dependencies"] = dependencies_unsorted[sorted_index]
    np_dict["destination"] = destination_unsorted[sorted_index]
    np_dict["argument_1"] = argument_1_unsorted[sorted_index]
    np_dict["argument_2"] = argument_2_unsorted[sorted_index]
    np_dict["operator"] = operator_unsorted[sorted_index]
    np_dict["maximum_effect"] = maximum_effect_unsorted[sorted_index]
    np_dict["accessibility"] = accessibility_unsorted[sorted_index]
    np_dict["probability_of_success"] = probability_of_success_unsorted[sorted_index]
    np_dict["saturation_point"] = saturation_point_unsorted[sorted_index]

    # step 6a
    df = df_dict["theme_weights"]
    themes_unsorted = df.theme.to_numpy()
    theme_weight_unsorted = df.weight.to_numpy()
    theme_weight = np.empty_like(theme_weight_unsorted)
    for i in range(len(themes)):
        theme_weight[i] = theme_weight_unsorted[np.where(themes_unsorted == themes[i])[0][0]]
    np_dict["theme_weight"] = theme_weight
    # step 6b
    df = df_dict["key_output_weights"]
    key_outputs_unsorted = df.key_output.to_numpy()
    key_output_weight_unsorted = df.weight.to_numpy()
    no_key_outputs = len(np_dict["key_outputs"])
    key_output_weight = np.empty(no_key_outputs)
    for i in range(no_key_outputs):
        key_output_weight[i] = key_output_weight_unsorted[
            np.where(key_outputs_unsorted == np_dict["key_outputs"][i])[0][0]
        ]
    np_dict["key_output_weight"] = key_output_weight

    # step 7
    df = df_dict["scenario_weights"]
    scenarios_unsorted = df.scenario.to_numpy()
    scenario_weight_unsorted = df.weight.to_numpy()
    no_scenarios = len(np_dict["scenarios"])
    scenario_weight = np.empty(no_scenarios)
    for i in range(no_scenarios):
        scenario_weight[i] = scenario_weight_unsorted[np.where(scenarios_unsorted == scenarios[i])[0][0]]
    np_dict["scenario_weight"] = scenario_weight

    return np_dict
