"""
This file contains with the calculation of key output values for the decision makers options.
"""
import itertools

def evaluate(argument_1_value: str, argument_2_value: str, operator: str):
    """
    This function ...
    """
    # dictionary containing all functions to which operators are related
    operators_dict = {"-": lambda x, y: x - y, "+": lambda x, y: x + y, "*": lambda x, y: x * y}

    # apply operations based on occurrence in operators_dict
    if operator in operators_dict.keys():  # ignore warning about .keys() | pylint: disable=C0201
        return operators_dict[operator](argument_1_value, argument_2_value)

    return f"{operator} not available"


def _create_value_dict(data_dict: dict, dmo_index: int) -> dict:
    """
    This function creates a 'value-dictionary' that maps all variables to their current value.
    :return:
    """
    value_dict = {
        # add key outputs. initialise at zero
        **{key: 0 for key in data_dict["key_outputs"]},
        # add internal variable inputs (for given dmo_index
        **dict(zip(data_dict["internal_variable_inputs"], data_dict["decision_makers_option_value"][dmo_index]))
    }

    return value_dict


def _calculate_single_dmo(data_dict: dict):
    for index, dest in enumerate(data_dict["destination"]):

        argument_1 = data_dict["argument_1"][index]
        argument_2 = data_dict["argument_2"][index]
        # print(index, dest, argument_1, argument_2)


def calculate(data_dict: dict) -> dict:
    """
    This function ...
    :return:
    """
    output_dict = {}

    model_options_index = itertools.product(range(len(data_dict["decision_makers_options"])), range(len(data_dict["scenarios"]))))

    for index, decision_maker_option in enumerate(data_dict["decision_makers_options"]):
        print(decision_maker_option)
        print(_create_value_dict(data_dict, index))

    return output_dict


if __name__ == "__main__":
    from pathlib import Path
    from import_case import import_case

    file_format = "xlsx"
    path = Path.cwd() / "model/data" / "beerwiser"
    case_data = import_case(file_format, path)

    print(calculate(case_data))
