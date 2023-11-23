"""
This module contains the CaseExporter() class. This class deals with transforming a case or exporting the outputs.
"""
import os
from pathlib import Path
import pandas as pd


class CaseExporter:
    """
    This class deals with the transformation into a different format and export of output of an RBS case.
    """

    def __init__(self, output_path, name, dataframe_dict):
        self.output_path = Path(output_path)
        self.folder_name = ""
        self.name = name
        self.dataframe_dict = dataframe_dict
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
