"""
This file contains the Visualize class that deals with the creation of all graphs and tables
"""
import re
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from core.utils import round_all_dict_values, number_formatter, get_values_from_target


class VisualizationError(Exception):
    """
    This class deals with the error handling of the Visualize class
    """

    def __init__(self, message):  # ignore warning about super-init | pylint: disable=W0231
        self.message = message

    def __str__(self):
        return f"Visualization Error: {self.message}"


class Visualize:
    """This class deals with the creation of all graphs and tables"""

    def __init__(self, outcomes, options):
        # for visualization purposes two digits is sufficient
        self.outcomes = round_all_dict_values(outcomes)
        self.options = options
        self.colors = ["#D04A02", "#EB8C00", "#FFB600", "#295477", "#299D8F"]
        self.available_visuals = {
            "table": self._create_table,
            "barchart": self._create_barchart,
        }
        self.available_outputs = ["key_outputs", "appreciations", "weighted_appreciations"]
        self.available_kwargs = ["scenario", "decision_makers_option", "stacked"]

    def _validate_kwargs(self, **kwargs):
        for argument, _ in kwargs.items():
            if argument not in self.available_kwargs:
                raise VisualizationError(f"Invalid argument '{argument}'")

    def _find_dimension_level(self, my_dict, target_key, level=1) -> int or None:
        if target_key in my_dict:
            return level

        for _, value in my_dict.items():
            if isinstance(value, dict):
                found_level = self._find_dimension_level(value, target_key, level + 1)
                if found_level is not None:
                    return found_level
        return None

    @staticmethod
    def _str_snake_case_to_text(snake_case_str):
        words = snake_case_str.split("_")
        return " ".join(words)

    @staticmethod
    def _table_styler(styler, table_name: str):
        # set color palette
        cmap = mpl.cm.Blues(np.linspace(0, 1, 30))
        cmap = mpl.colors.ListedColormap(cmap[:8, :-1])

        # style
        styler.format(number_formatter)
        styler.set_caption(table_name)
        styler.background_gradient(cmap=cmap, axis=1)
        return styler

    @staticmethod
    def _graph_styler(axis, title):
        xtick_formatted = [label.get_text() for label in axis.get_xticklabels()]
        axis.set_title(title, color="#777777", fontsize=12)
        axis.set_ylim(0, 100)
        axis.set_xticklabels(xtick_formatted, rotation=0, fontweight="bold")
        axis.legend(loc="upper left", bbox_to_anchor=(1, 1))
        return axis

    def _format_data_for_visual(self, key_data: str) -> pd.DataFrame:
        """
        This function formats the values of the given key into a dataframe.
        :return: a pd.DataFrame with decision maker options as row index, key outputs as columns and weighted
        appreciations as values.
        """
        dim_level = self._find_dimension_level(self.outcomes, key_data)
        dim_names = ["scenario", "decision_makers_option"]

        # iterate until we are at the level where the 'key_data' can be found
        dict_for_iteration = self.outcomes.copy()
        formatted_data = pd.DataFrame(index=range(self.options))
        while dim_level > 1:
            dim_values = []
            tmp_dict = {}
            for key, value in dict_for_iteration.items():
                dim_values.append(key)
                # ensure keys are unique, so we don't lose any values
                tmp_dict.update({f"@{key}@{tmp_key}": tmp_value for tmp_key, tmp_value in value.items()})

            # for higher dimensions entries will be duplicated in the columns
            replicate_n = int(self.options / len(dim_values))
            # using a re(gex) expression the entries to ensure uniqueness in the for-loop are removed again.
            formatted_data[dim_names.pop(0)] = [
                re.sub(r"@.*?@", "", value) for value in dim_values for _ in range(replicate_n)
            ]
            dict_for_iteration = tmp_dict
            dim_level -= 1

        # add the values from the 'key_data' dictionary
        key_data_list = get_values_from_target(self.outcomes, key_data)
        keys = [key for dictionary in key_data_list for key, _ in dictionary.items()]
        values = [value for dictionary in key_data_list for _, value in dictionary.items()]
        formatted_data[key_data] = keys
        formatted_data["value"] = values
        return formatted_data

    @staticmethod
    def _apply_filters(dataframe: pd.DataFrame, drop_used=False, **kwargs):
        name_str = ""
        for arg, value in kwargs.items():
            if arg not in dataframe.columns:
                continue
            dataframe = dataframe[dataframe[arg] == value]
            if drop_used:
                dataframe = dataframe.drop(columns=[arg], axis=1)
            name_str += f" | {value}"

        # Check if dataframe is empty after applying filters
        if dataframe.empty:
            raise VisualizationError("No data for given selection. Are your arguments correct?")

        return dataframe, name_str

    def _create_table(self, key, **kwargs):
        """
        This function creates a 2- or 3-dimensional table
        """
        table_data = self._format_data_for_visual(key)

        # Filter the data based on potentially provided arguments by the user.
        table_data, name_str = self._apply_filters(table_data, **kwargs)
        table_data = (
            table_data.set_index(["scenario", key])
            .pivot(columns="decision_makers_option", values="value")
            .rename_axis((None, None))
            .rename_axis(None, axis=1)
        )
        table_name = f"Values of {self._str_snake_case_to_text(key)}{name_str}"
        return self._table_styler(table_data.style, table_name)

    def _create_barchart(self, key, **kwargs):
        dims = self._find_dimension_level(self.outcomes, key)
        if dims > 2 and "scenario" not in kwargs:
            raise VisualizationError(f"Too many dimensions ({dims}). Please specify a scenario")
        stacked = kwargs["stacked"] if "stacked" in kwargs else True

        appreciations = self._format_data_for_visual(key)
        bar_data, name_str = self._apply_filters(appreciations, drop_used=True, **kwargs)
        rest_cols = [col for col in bar_data.columns if col not in ["decision_makers_option", "value"]]
        bar_data = bar_data.pivot(index="decision_makers_option", columns=rest_cols, values="value").reset_index()
        axis = bar_data.plot.bar(x="decision_makers_option", stacked=stacked, color=self.colors, figsize=(10, 5))
        self._graph_styler(axis, f"Values of {self._str_snake_case_to_text(key)}{name_str}")

        plt.show()

    def create_visual(self, visual_request, key, **kwargs):
        """
        This function redirects the visual_request based on the requested format to the correct helper function
        :param visual_request: type of visual that is requested
        :param key: key in output_dict containing the values to be visualised
        :param **kwargs: any additional arguments provide by the user
        :return: requested visual
        """
        self._validate_kwargs(**kwargs)
        if visual_request not in self.available_visuals:
            raise VisualizationError(f"'{visual_request}' is not a valid chart type")
        if key not in self.available_outputs:
            raise VisualizationError(f"'{key}' is not a valid option")

        return self.available_visuals[visual_request](key, **kwargs)
