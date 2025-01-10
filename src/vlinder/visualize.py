"""
This file contains the Visualize class that deals with the creation of all graphs and tables
"""
import re
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import dataframe_image as dfi
from vlinder.utils import round_all_dict_values, number_formatter, get_values_from_target, check_list_content


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

    def __init__(self, input_dict, outcomes, options):
        # for visualization purposes two digits is sufficient
        self.input_dict = input_dict
        self.outcomes = round_all_dict_values(outcomes)
        self.options = options
        self.colors = [
            "#295477",
            "#F3DD8C",
            "#D04A02",
            "#299D8F",
            "#E72B33",
            "#6A91B6",
            "#EB8C00",
            "#FFB600",
            "#5CB9BD",
            "#E27588",
        ]
        self.available_visuals = {
            "table": self._create_table,
            "barchart": self._create_barchart,
        }
        self.available_outputs = [
            "key_outputs",
            "appreciations",
            "weighted_appreciations",
            "decision_makers_option_appreciation",
            "key_outputs_theme",
            "scenarios",
            "fixed_inputs",
            "decision_makers_options",
            "scenario_appreciations",
        ]
        self.available_kwargs = [
            "scenario",
            "decision_makers_option",
            "stacked",
            "show_legend",
            "save",
            "number_iteration",
            "input_variables",
        ]

    def _validate_kwargs(self, **kwargs) -> None:
        """
        This function validates whether the provided additional arguments are relevant.
        :param **kwargs: the additional arguments provided
        :return: None if all **kwargs are available, else raise an VisualizationError.
        """
        for argument, _ in kwargs.items():
            if argument not in self.available_kwargs:
                raise VisualizationError(f"Invalid argument '{argument}'")

    def _find_dimension_level(self, my_dict: dict, target_key: str, level: int = 1):
        """
        This recursive function returns the dimension level (level of nesting) for a given dictionary and target key.
        For example in dictionary {A: {B: {C: 1.23, ..}, ..}, ..}. 'A' is nested at level 1, B at level 2 & C level 3.
        :param my_dict: input dictionary
        :param target_key: name of the key
        :param level: current dimension level
        :return: the dimension level (if target_key exists)
        """
        if target_key in my_dict:
            return level

        for _, value in my_dict.items():
            if isinstance(value, dict):
                found_level = self._find_dimension_level(value, target_key, level + 1)
                if found_level is not None:
                    return found_level
        return None

    @staticmethod
    def _str_snake_case_to_text(snake_case_str: str) -> str:
        """
        This styling function returns a formatted string where the snake case is replaced by spaces.
        :param snake_case_str: string to reformat
        :result: string where _ is replaced by spaces
        """
        words = snake_case_str.split("_")
        return " ".join(words)

    @staticmethod
    def _truncate_title_list(title_list: list) -> list:
        """
        This function truncates a list of strings to ensure that in total they have no more than 85 chars. For example,
        two strings could have 42 chars whereas, 10 strings can only use 8 chars.
        :param title_list: list of title names to be truncated
        :return: a truncated (where necessary) list of titles
        """
        max_char_length = int(85 / len(title_list))
        truncated_list = [
            f"{item[:(max_char_length - 2)]}.." if len(item) > max_char_length else item for item in title_list
        ]
        return truncated_list

    @staticmethod
    def _table_styler(styler: pd.DataFrame.style, table_name: str, **kwargs) -> pd.DataFrame.style:
        """
        This function adds a coherent style for all generated tables
        :param styler: a Pandas styler object
        :param table_name: name of the styled table
        :return: an updated styler object
        """
        # set color palette
        cmap = mpl.cm.Blues(np.linspace(0, 1, 30))
        cmap = mpl.colors.ListedColormap(cmap[:8, :-1])

        # Apply number formatting only to numeric columns
        numeric_columns = styler.data.select_dtypes(include=[np.number]).columns
        styler.format({col: number_formatter for col in numeric_columns})

        styler.set_caption(table_name)
        if "input_variables" not in kwargs:
            styler.background_gradient(cmap=cmap, axis=1)
        return styler

    def _graph_styler(self, axis: mpl.axis, title: str, show_legend: bool) -> mpl.axis:
        """
        This function adds a coherent style for all generated graphs.
        :param axis: a matplotlib axis object containing the graph
        :param title: title of the graph
        :return: formatted matplotlib axis object
        """
        xtick_formatted = self._truncate_title_list([label.get_text() for label in axis.get_xticklabels()])
        axis.set_title(title, color="#777777", fontsize=12)
        axis.set_ylim(0, 100)
        axis.set_xticklabels(xtick_formatted, rotation=0, fontweight="bold")
        axis.legend(loc="upper left", bbox_to_anchor=(1, 1))
        if not show_legend:
            axis.legend_ = None
        return axis

    def _format_data_for_visual(self, key_data: str) -> pd.DataFrame:
        """
        This function formats the values of the given key into a dataframe.
        :param key_data: name of the key that needs formatting
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

        # add the values from 'key_data' | this can be either a list of dictionaries or a list of values
        key_data_list = get_values_from_target(self.outcomes, key_data)
        key_data_list_content = check_list_content(key_data_list)

        if key_data_list_content == "numeric":
            # if the final dimension is numeric we initialised too many rows
            formatted_data = formatted_data.drop_duplicates(ignore_index=True)
            formatted_data["value"] = key_data_list
        elif key_data_list_content == "dictionaries":
            formatted_data[key_data] = [key for dictionary in key_data_list for key, _ in dictionary.items()]
            formatted_data["value"] = [value for dictionary in key_data_list for _, value in dictionary.items()]
        return formatted_data

    @staticmethod
    def _apply_filters(dataframe: pd.DataFrame, drop_used: bool = False, **kwargs) -> pd.DataFrame and str:
        """
        This function applies filters, based on **kwargs arguments, on the dataframe and generates a corresponding
        name for the visual.
        :param dataframe: dataframe that needs filtering
        :param drop_used: indicator whether the used filter column should be dropped
        :return: a filtered dataframe with corresponding name
        """
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

    def _create_table(self, key: str, **kwargs) -> pd.DataFrame.style:
        """
        This function creates a 2- or 3-dimensional table depending on the key.
        :param key: key of the values for the table
        :return: a styled table
        """
        if key in ["scenarios", "fixed_inputs", "decision_makers_options", "key_outputs_theme"]:
            dataframe = pd.DataFrame()
            kwargs["input_variables"] = True
            number_of_iter = kwargs.get("number_iteration", -1)
            if key == "key_outputs_theme":
                key = key[:-6]
                dataframe[key] = self.input_dict[key]
                key_value = key[:-1] + "_theme"
                dataframe[key_value] = self.input_dict[key_value]
            elif key == "fixed_inputs":
                if number_of_iter == -1:
                    dataframe[key] = self.input_dict[key]
                    key_value = key[:-1] + "_value"
                    dataframe[key_value] = self.input_dict[key_value]
                else:
                    start_idx = number_of_iter * 10
                    end_idx = start_idx + 10

                    dataframe[key] = self.input_dict[key][start_idx:end_idx]
                    key_value = key[:-1] + "_value"
                    dataframe[key_value] = self.input_dict[key_value][start_idx:end_idx]
            elif key == "scenarios":
                dataframe = self._create_table_n_col(
                    dataframe, key, key[:-1] + "_value", "external_variable_inputs", "External variable input"
                )
            elif key == "decision_makers_options":
                dataframe = self._create_table_n_col(
                    dataframe, key, key[:-1] + "_value", "internal_variable_inputs", "Internal variable input"
                )
            table_name = f"Values of {self._str_snake_case_to_text(key)}"
            styled_df = self._table_styler(dataframe.style, table_name, **kwargs)
            if number_of_iter == -1:
                name_table = "/table" + str(key)
            else:
                name_table = "/table" + str(key) + str(number_of_iter)
            if "save" in kwargs:
                dfi.export(styled_df, "images" + name_table + ".png", table_conversion="matplotlib")
        else:
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
            styled_df = self._table_styler(table_data.style, table_name)
        return styled_df

    # pylint: disable=too-many-arguments
    def _create_table_n_col(self, dataframe, col_names, col_values, row_names, left_col_header) -> pd.DataFrame:
        """
        This function makes it possible to iterate over all cells in a table
        :param data: empty dataframe
        :param col_names: column names of a table
        :param col_values: values in the columns
        :param row_names: names of all the values in the left column
        :param left_col_header: header of left column of a table
        """
        input_info_col_names = self.input_dict[col_names]
        input_info_col_values = self.input_dict[col_values]

        dataframe[left_col_header] = self.input_dict[row_names]
        for row in enumerate(input_info_col_names):
            dataframe[input_info_col_names[row[0]]] = input_info_col_values[row[0]]
        return dataframe

    def map_values(self, dmo):
        """
        This function maps the decision_makers_option to the corresponding theme
        :param dmo: name of the decision_makers_option
        :return: the corresponding theme
        """
        index = np.where(self.input_dict["key_outputs"] == dmo)[0][0]
        return self.input_dict["key_output_theme"][index]

    def _create_barchart(self, key: str, **kwargs) -> None:
        """
        This function creates and shows a barchart for a given data key.
        :param key: name of values of interest
        :return: a plotted barchart
        """
        dims = self._find_dimension_level(self.outcomes, key)
        if dims > 2 and "scenario" not in kwargs and not ("stacked" in kwargs and key == "scenario_appreciations"):
            raise VisualizationError(f"Too many dimensions ({dims}). Please specify a scenario")
        stacked = kwargs["stacked"] if "stacked" in kwargs else True
        show_legend = kwargs["show_legend"] if "show_legend" in kwargs else True

        appreciations = self._format_data_for_visual(key)
        bar_data, name_str = self._apply_filters(appreciations, drop_used=True, **kwargs)
        if (key == "decision_makers_option_appreciation") | (key == "scenario_appreciations"):
            rest_cols = [col for col in bar_data.columns if col not in ["decision_makers_option", "value"]]
            bar_data = bar_data.pivot(index="decision_makers_option", columns=rest_cols, values="value").reset_index()
            axis = bar_data.plot.bar(x="decision_makers_option", stacked=stacked, color=self.colors, figsize=(10, 5))
            self._graph_styler(axis, f"Values of {self._str_snake_case_to_text(key)}{name_str}", show_legend)
        else:
            # Apply the function to the "weighted_appreciations" column and add as new column
            bar_data["themes"] = bar_data[key].apply(self.map_values)
            # Create a dictionary to map themes to colors
            unique_themes = bar_data["themes"].unique()
            # give each decision makers options belonging to the same theme, the same color
            theme_colors = {theme: self.colors[i % len(self.colors)] for i, theme in enumerate(unique_themes)}
            # Map the colors to the themes
            bar_colors = bar_data["themes"].map(theme_colors)
            rest_cols = [col for col in bar_data.columns if col not in ["decision_makers_option", "value"]]
            bar_data = bar_data.pivot(index="decision_makers_option", columns=rest_cols, values="value").reset_index()
            axis = bar_data.plot.bar(x="decision_makers_option", stacked=stacked, color=bar_colors, figsize=(10, 5))
            # Add border to each bar
            for patch in axis.patches:
                patch.set_edgecolor("white")
                patch.set_linewidth(1)
            self._graph_styler(axis, f"Values of {self._str_snake_case_to_text(key)}{name_str}", show_legend)

        if "save" in kwargs:
            plt.savefig("images" + "/figure.png", bbox_inches="tight")
        else:
            plt.show()

    def create_visual(self, visual_request: str, key: str, **kwargs):
        """
        This function redirects the visual_request based on the requested format to the correct helper function.
        Validation checks are performed on the available visuals and outputs.See 'available_outputs' and
        'available_kwargs' for all possible options.
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
