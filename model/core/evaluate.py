"""
This file contains the evaluate() function that deals with the calculation of key output values for the decision makers
options.
"""


def evaluate(
    argument_1_value: str,
    argument_2_value: str,
):
    """
    This function ...
    """

    return argument_1_value + argument_2_value


if __name__ == "__main__":
    from pathlib import Path
    from import_case import import_case

    file_format = "xlsx"
    path = Path.cwd() / "model/data" / "beerwiser"
    case_data = import_case(file_format, path)

    print(case_data)

    evaluate(1, 2)
