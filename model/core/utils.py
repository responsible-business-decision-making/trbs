"""
This module contains general helper functions
"""


def round_all_dict_values(my_dict, digits=2):
    """
    This function rounds all values in a dictionary to the number of digits specified. Works for nested dictionaries.
    :param my_dict: (nested) dictionary
    :param digits: number of digits of the rounded values
    :return: dictionary with rounded values
    """
    rounded_dict = {}
    for key, value in my_dict.items():
        if isinstance(value, dict):
            rounded_dict[key] = round_all_dict_values(value)
        elif isinstance(value, list):
            rounded_dict[key] = [round(val, digits) for val in value]
        else:
            rounded_dict[key] = round(value, digits)
    return rounded_dict


def get_values_from_target(dictionary: dict, target: str):
    """
    This function return all (nested) values for a given dictionary and target key
    :param dictionary: dictionary where values need to be subtracted from
    :param target: target key
    :return: list of values
    """
    values = []

    for key, value in dictionary.items():
        if key == target:
            values.append(value)
        elif isinstance(value, dict):
            values.extend(get_values_from_target(value, target))

    return values
