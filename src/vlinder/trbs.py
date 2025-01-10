# pylint: disable=no-member
# pylint: disable=W0511

"""
This module contains the tRBS class. This is the parent class that deals with anything related to a Responsible
Business Simulator Case.
"""

from pathlib import Path
import os
import copy

import numpy as np
import matplotlib

import vlinder as vl
from vlinder.case_exporter import CaseExporter
from vlinder.case_importer import CaseImporter
from vlinder.evaluate import Evaluate
from vlinder.appreciate import Appreciate
from vlinder.visualize import Visualize
from vlinder.make_report import MakeReport
from vlinder.optimize import Optimize


def list_demo_cases(file_path=None):
    """This function returns all demo cases that exist in the package"""
    file_path = file_path or Path(os.path.dirname(vl.__file__)) / "data"

    try:
        case_names = [name for name in os.listdir(file_path) if (file_path / name).is_dir()]
        return case_names
    except FileNotFoundError as error:
        raise FileNotFoundError(f"The directory {file_path} does not exist.") from error


class TheResponsibleBusinessSimulator:
    """
    This class is the base class of an tRBS-case and contains all necessary information to import data, evaluate
    dependencies and calculate appreciations.
    """

    def __init__(self, name, file_path=None, file_extension=None):
        self.file_path = file_path if file_path is not None else Path(os.path.dirname(vl.__file__)) / "data"
        self.file_extension = file_extension if file_extension is not None else "xlsx"
        self.name = name
        self.input_dict = {}
        self.dataframe_dict = {}
        self.output_dict = {}
        self.visualizer = None
        self.exporter = None
        self.report = None

    def __str__(self):
        input_data_formatted = (
            "\n\n".join(f"{key}\n\t{value}" for key, value in self.input_dict.items())
            if self.input_dict
            else "First .build() a case to import data"
        )
        return (
            f"Case: {self.name} ({self.file_extension}) \n"
            f"Data location: {self.file_path} \n"
            f"Input data: \n {input_data_formatted}"
        )

    def _get_options(self):
        """
        This function calculates the amount of different options (or calculations) of the model:
        Amount of scenarios x Amount of decision makers options x Amount of key outputs
        """
        return (
            len(self.input_dict["scenarios"])
            * len(self.input_dict["decision_makers_options"])
            * len(self.input_dict["key_outputs"])
        )

    def copy(self):
        """
        Creates a deep copy of the instance.
        """
        return copy.deepcopy(self)

    def build(self):
        """This function builds all necessary elements for a generic RBS case"""
        print(f"Creating '{self.name}'")
        case_import = CaseImporter(self.file_path, self.name, self.file_extension)
        self.input_dict, self.dataframe_dict = case_import.import_case()

    # TODO: param what to evaluate: single scenario = None, single dmo = None
    def evaluate(self):
        """This function deals with the evaluation of all dependencies"""
        case_evaluation = Evaluate(self.input_dict)
        self.output_dict = case_evaluation.evaluate_all_scenarios()

    def appreciate(self):
        """This function deals with the appreciation of the outcomes"""
        case_appreciation = Appreciate(self.input_dict, self.output_dict)
        case_appreciation.appreciate_all_scenarios()

    def visualize(self, visual_request, key, **kwargs):
        """This function deals with the visualizations of the outcomes"""
        # Set a Visualize class only if this has not yet been initialised.
        self.visualizer = Visualize(self.input_dict, self.output_dict, self._get_options())
        return self.visualizer.create_visual(visual_request, key, **kwargs)

    def transform(self, requested_format, output_path=None):
        """This function deals with transforming a case to a new format."""
        output_path = output_path if output_path is not None else Path.cwd() / "data"
        if not self.exporter:
            self.exporter = CaseExporter(output_path, self.name, self.dataframe_dict)
        self.exporter.create_template_for_requested_format(requested_format)

    def modify(self, input_dict_key, element_key, new_value):
        """
        This function changes the value of one of the inputs in the input_dict.
        The following keys in input_dict are currently supported: key_output_weight, scenario_weight, theme_weight
        :param input_dict_key: the key in the input_dict for which the value should be changed.
        :param element_key: is the name of the element within the input_dict_key to be changed
        :param new_value: is the new value to be changed to
        """
        supported_input_keys = ["key_output_weight", "scenario_weight", "theme_weight"]
        if input_dict_key not in supported_input_keys:
            raise ValueError("Please specify one of", supported_input_keys)
        master_key = input_dict_key.split("_weight")[0] + "s"
        index = np.where(self.input_dict[master_key] == element_key)
        old_value = self.input_dict[input_dict_key][index]
        self.input_dict[input_dict_key][index] = new_value
        print(f"The weight for {element_key} in {input_dict_key} is changed from {old_value[0]} to {new_value}.")

    def _check_steps_completed(self) -> bool:
        """This function checks whether all steps are performed.
        :return: boolean which indicates if all steps are performed
        """
        ready = False
        if len(self.input_dict) == 0:
            print("First .build() a case to import data")
        elif len(self.output_dict) == 0:
            print("First .evaluate() a case to calculate key output values")
        elif (
            "appreciations"
            not in self.output_dict[self.input_dict["scenarios"][0]][self.input_dict["decision_makers_options"][0]]
        ):
            print("First .appreciate() a case to process key output values")
        else:
            ready = True
        return ready

    def make_report(self, scenario, orientation="Landscape", output_path=Path(str(Path.cwd()) + "/reports/")):
        """This function deals with transforming a case to a Report.
        :param output_path: desired location of the report
        :param scenario: the selected scenario of the case
        :param orientation: the desired orientation for PDF format; there is a choice between Portrait of Landscape
        """
        if self._check_steps_completed():
            # Do not show the graphs in notebook when making a report
            matplotlib.pyplot.ioff()
            if not self.report:
                self.report = MakeReport(output_path, self.name, self.input_dict, self.output_dict, self.visualize)

            location_report = self.report.create_report(scenario, orientation, output_path)
            print(location_report)

    def optimize(self, scenario, **kwargs):
        """This function deals with finding the optimal distribution of decision maker options."""
        case_optimizer = Optimize(self.input_dict, self.output_dict)
        self.input_dict = case_optimizer.optimize_single_scenario(
            scenario, kwargs.get("new_dmo_name", "Optimized DMO"), kwargs.get("max_combinations", 60000)
        )
        new_case_name = kwargs.get("new_case_name", self.name + "- Optimized")
        self.name = new_case_name
