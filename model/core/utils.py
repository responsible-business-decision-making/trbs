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
        else:
            rounded_dict[key] = round(value, digits)
    return rounded_dict
