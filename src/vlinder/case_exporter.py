"""
This module contains the CaseExporter() class. This class deals with transforming a case or exporting the outputs.
"""
import os
from pathlib import Path
import pandas as pd


# pylint: disable=too-few-public-methods
class CaseExporter:
    """
    This class deals with the transformation into a different format and export of output of an RBS case.
    """

    def __init__(self, output_path, name, input_dict):
        self.output_path = Path(output_path)
        self.folder_name = ""
        self.name = name
        self.input_dict = input_dict
        self.dataframe_dict = self.input_to_dataframe()
        self.transformers = {
            "json": lambda table: self.dataframe_dict[table].to_json(
                self.output_path / self.folder_name / f"{table}.json", orient="table", indent=4
            ),
            "xlsx": lambda table, writer: self.dataframe_dict[table].to_excel(writer, sheet_name=table, index=False),
            "csv": lambda table: self.dataframe_dict[table].to_csv(
                self.output_path / self.folder_name / f"{table}.csv", index=False, sep=";"
            ),
        }

    def _create_output_folder(self, folder_name: str) -> None:
        """
        This function creates a new folder to store the data
        :param folder_name: name of the output folder
        """
        try:
            os.makedirs(self.output_path / folder_name)
        except FileExistsError:
            print(f"Folder '{folder_name}' already exists. ")
        self.folder_name = folder_name

    def _store_as_excel_template(self) -> None:
        """
        This function stores the data in the dataframe_dict as an Excel-file. Each table will get its own sheet.
        """
        with pd.ExcelWriter(self.output_path / self.folder_name / f"{self.name}.xlsx") as writer:
            for table, _ in self.dataframe_dict.items():
                self.transformers["xlsx"](table, writer)

    def create_template_for_requested_format(self, requested_format: str) -> None:
        """
        This function stores the data in dataframe_dict into a new files of requested_format
        :param requested_format: format of the requested file
        """
        self._create_output_folder(requested_format)
        if requested_format == "xlsx":
            self._store_as_excel_template()
        else:
            for table, _ in self.dataframe_dict.items():
                self.transformers[requested_format](table)

    def input_to_dataframe(self):
        """
        This function converts the input_dict to a dataframe_dict format.
        """
        # Sheets that can be generated using _make_table
        df_dict_keys = [
            "configurations",
            "generic_text_elements",
            "case_text_elements",
            "key_outputs",
            "fixed_inputs",
        ]
        # Initialize empty dict for output
        dataframe_dict = {}
        # Make tables for keys in df_dict_keys
        for df_dict_key in df_dict_keys:
            df_temp = self._make_table(df_dict_key)
            dataframe_dict.update(
                {
                    df_dict_key: df_temp,
                }
            )
        # Append made key_outputs dataframe into make key_outputs and key_output_weights
        dataframe_dict.update(
            {
                "key_output_weights": dataframe_dict["key_outputs"].loc[:, ["key_output", "weight"]],
            }
        )
        dataframe_dict["key_outputs"].drop(["weight", "weight"], axis=1, inplace=True)
        # Add deicison_makers_options, scenario tables
        dataframe_dict.update(
            {
                "decision_makers_options": self._make_table_dmo(),
                "scenarios": self._make_table_scenarios(),
            }
        )
        # Add theme_weights and scenario_weights tables
        dataframe_dict.update(
            {
                "theme_weights": self._make_table_theme_weights(),
                "scenario_weights": self._make_table_scenario_weights(),
            }
        )
        # Add dependencies
        dataframe_dict.update({"dependencies": self._make_table_dependencies()})

        # Reorder tables in dataframe_dict
        desired_order = [
            "configurations",
            "generic_text_elements",
            "case_text_elements",
            "key_outputs",
            "decision_makers_options",
            "scenarios",
            "fixed_inputs",
            "dependencies",
            "theme_weights",
            "key_output_weights",
            "scenario_weights",
        ]

        dataframe_dict = {key: dataframe_dict[key] for key in desired_order}

        # Reorder keys
        return dataframe_dict

    def _make_table(self, stem):
        input_dict_keys = list(self.input_dict.keys())
        head = stem[:-1]
        tails = []
        for key in input_dict_keys:
            if key[: len(head)] == head:
                tails.append(key.split(head)[-1])
        cols = [head] + [tail[1:] for tail in tails]
        vals = [self.input_dict[head + key] for key in tails]
        df_temp = pd.DataFrame(dict(zip(cols, vals)))

        return df_temp

    def _make_table_theme_weights(self):
        return pd.DataFrame({"theme": self.input_dict["themes"], "weight": self.input_dict["theme_weight"]})

    def _make_table_scenario_weights(self):
        return pd.DataFrame({"scenario": self.input_dict["scenarios"], "weight": self.input_dict["scenario_weight"]})

    def _make_table_dmo(self):
        df_wide = pd.DataFrame(
            data=self.input_dict["decision_makers_option_value"],
            index=self.input_dict["decision_makers_options"],
            columns=self.input_dict["internal_variable_inputs"],
        )
        df_long = df_wide.reset_index().melt(id_vars="index", var_name="Column_Title", value_name="Value")
        df_long.columns = ["decision_makers_option", "internal_variable_input", "value"]
        df_temp = df_long.loc[:, ["internal_variable_input", "decision_makers_option", "value"]]
        return df_temp

    def _make_table_scenarios(self):
        df_wide = pd.DataFrame(
            data=self.input_dict["scenario_value"],
            index=self.input_dict["scenarios"],
            columns=self.input_dict["external_variable_inputs"],
        )
        df_long = df_wide.reset_index().melt(id_vars="index", var_name="Column_Title", value_name="Value")
        df_long.columns = ["scenario", "external_variable_input", "value"]
        df_temp = df_long.loc[:, ["external_variable_input", "scenario", "value"]]
        return df_temp

    def _make_table_dependencies(self):
        return pd.DataFrame(
            {
                "destination": self.input_dict["destination"],
                "argument_1": self.input_dict["argument_1"],
                "argument_2": self.input_dict["argument_2"],
                "operator": self.input_dict["operator"],
            }
        )
