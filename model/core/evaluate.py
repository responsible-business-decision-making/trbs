"""
This file contains the evaluate() function that deals with the calculation of key output values for the decision makers
options.
"""


def evaluate(argument_1_value: str, argument_2_value: str, operator: str):
    """
    This function ...
    """
    # dictionary containing all functions to which operators are related
    operators_dict = {"-": lambda x, y: x - y, "+": lambda x, y: x + y, "*": lambda x, y: x * y}

    # apply operations based on occurence in operators_dict
    if operator in operators_dict.keys():  # ignore warning about .keys() | pylint: disable=C0201
        return operators_dict[operator](argument_1_value, argument_2_value)

    return f"{operator} not available"


if __name__ == "__main__":
    # from pathlib import Path
    # from import_case import import_case
    #
    # file_format = "xlsx"
    # path = Path.cwd() / "model/data" / "beerwiser"
    # case_data = import_case(file_format, path)

    print(evaluate(1, 2, "+"))
    print(evaluate(3, 4, "*"))
