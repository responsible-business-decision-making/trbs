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
        self.available_visuals = {
            "appreciation_table": self._create_appreciation_table,
            "key_output_table": self._create_key_output_table,
            "appreciation_per_dmo": self._create_appreciation_dmo_barchart,
        }

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
        axis.set_title(title)
        return axis

    def _format_data_for_single_table(self, scenario: str, key: str) -> pd.DataFrame:
        """
        This function formats the values of the weighted appreciation into a dataframe.
        :param scenario: the given scenario
        :return: a pd.DataFrame with decision maker options as row index, key outputs as columns and weighted
        appreciations as values.
        """
        formatted_data = pd.DataFrame()
        for decision, value in self.outcomes[scenario].items():
            new_row = pd.DataFrame(value[key], index=[decision])
            formatted_data = pd.concat([formatted_data, new_row])

        return formatted_data

    def _create_key_output_table(self, scenario: str):
        key_output_table = self._format_data_for_single_table(scenario, "key_outputs")
        table_name = f"Table 1: Key Output values | {scenario}"
        return self._table_styler(key_output_table.style, table_name)

    def _create_appreciation_table(self, scenario: str):
        appreciation_table = self._format_data_for_single_table(scenario, "weighted_appreciations")
        table_name = f"Tabel 2: Weighted appreciations | {scenario}"
        return self._table_styler(appreciation_table.style, table_name)

    def _create_appreciation_dmo_barchart(self, scenario: str):
        appreciations = self._format_data_for_single_table(scenario, "weighted_appreciations").reset_index(
            names="Decision maker option"
        )
        axis = appreciations.plot.bar(x="Decision maker option", stacked=True)
        self._graph_styler(axis, f"Appreciation per decision maker's option | {scenario}")
        plt.show()

    def create_visual(self, visual_request, *args):
        if visual_request not in self.available_visuals:
            raise VisualizationError(f"'{visual_request}' is not a valid option")

        return self.available_visuals[visual_request](*args)
