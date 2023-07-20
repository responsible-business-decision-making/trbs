"""
This file contains the Visualize class that deals with the creation of all graphs and tables
"""
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from core.utils import round_all_dict_values, number_formatter


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

    def __init__(self, outcomes):
        # for visualization purposes two digits is sufficient
        self.outcomes = round_all_dict_values(outcomes)
        self.colors = ["#D04A02", "#EB8C00", "#FFB600", "#295477", "#299D8F"]
        self.available_visuals = {
            "table": self._create_table,
            "barchart": self._create_barchart,
        }
        self.available_outputs = ["key_outputs", "appreciations", "weighted_appreciations"]

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

    def _format_data_for_single_table(self, scenario: str, key: str) -> pd.DataFrame:
        """
        This function formats the values of the given key into a dataframe.
        :param scenario: the given scenario
        :return: a pd.DataFrame with decision maker options as row index, key outputs as columns and weighted
        appreciations as values.
        """
        formatted_data = pd.DataFrame()
        for decision, value in self.outcomes[scenario].items():
            new_row = pd.DataFrame(value[key], index=[decision])
            formatted_data = pd.concat([formatted_data, new_row])

        return formatted_data

    def _create_table(self, key, **kwargs):
        """
        This function creates a 2- or 3-dimensional table
        """
        # dim_level = self._find_dimension_level(self.outcomes, key)
        if "scenario" not in kwargs:
            raise VisualizationError(
                "Table creation is only supported for a single scenario. Specify this with 'scenario='"
            )

        table_data = self._format_data_for_single_table(kwargs["scenario"], key)
        table_name = f"Values of {self._str_snake_case_to_text(key)} | {kwargs['scenario']}"
        return self._table_styler(table_data.style, table_name)

    def _create_barchart(self, key, **kwargs):
        appreciations = self._format_data_for_single_table(kwargs["scenario"], key).reset_index(
            names="Decision maker option"
        )
        axis = appreciations.plot.bar(x="Decision maker option", stacked=True, color=self.colors, figsize=(10, 5))
        self._graph_styler(axis, f"Values of {self._str_snake_case_to_text(key)} | {kwargs['scenario']}")

        plt.show()

    def create_visual(self, visual_request, key, **kwargs):
        """
        This function redirects the visual_request based on the requested format to the correct helper function
        :param visual_request: type of visual that is requested
        :param key: key in output_dict containing the values to be visualised
        :param **kwargs: any additional arguments provide by the user
        :return: requested visual
        """
        if visual_request not in self.available_visuals:
            raise VisualizationError(f"'{visual_request}' is not a valid chart type")
        if key not in self.available_outputs:
            raise VisualizationError(f"'{key}' is not a valid option")

        return self.available_visuals[visual_request](key, **kwargs)
