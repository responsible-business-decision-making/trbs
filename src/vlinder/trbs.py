"""
This module contains the TRBS class. This is the parent class that deals with anything related to a Responsible
Business Simulator Case.
"""
from vlinder.case_exporter import CaseExporter
from vlinder.case_importer import CaseImporter
from vlinder.evaluate import Evaluate
from vlinder.appreciate import Appreciate
from vlinder.visualize import Visualize


class TheResponsibleBusinessSimulator:
    """
    This class is the base class of an tRBS-case and contains all necessary information to import data, evaluate
    dependencies and calculate appreciations.
    """

    def __init__(self, file_path, file_extension, name):
        self.file_path = file_path
        self.file_extension = file_extension
        self.name = name
        self.input_dict = {}
        self.dataframe_dict = {}
        self.output_dict = {}
        self.visualizer = None
        self.exporter = None

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
        if not self.visualizer:
            self.visualizer = Visualize(self.output_dict, self._get_options())
        return self.visualizer.create_visual(visual_request, key, **kwargs)

    def transform(self, output_path, requested_format):
        """This function deals with transforming a case to a new format."""
        if not self.exporter:
            self.exporter = CaseExporter(output_path, self.name, self.dataframe_dict)
        self.exporter.create_template_for_requested_format(requested_format)

    def modify(self, input_dict_key, element_key, new_value)
        """
        This function changes the value of one of the inputs in the input_dict.
        :param input_dict_key: the key in the input_dict for which the value should be changed. Currently supported: ['key_output_weight', 'scenario_weight', 'theme_weight']
        :param element_key: is the name of the element within the input_dict_key to be changed
        :param new_value: is the new value to be changed to
        """
        supported_input_keys = ['key_output_weight', 'scenario_weight', 'theme_weight']
        if input_dict_key not in supported_input_keys:
            raise ValueError("Please specify one of", supperted_input_keys)
        index = np.where(self.input_dict[input_dict_key] == element_key)
        old_value = case.input_dict[input_dict_key][index]
        self.input_dict[input_dict_key][index] = new_value
        print(f"The weight for {element_key} in {input_dict_key} is changed from {old_value[0]} to {new_value}.")
