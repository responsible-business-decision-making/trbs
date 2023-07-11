"""
This module contains the TRBS class. This is the parent class that deals with anything related to a Responsible
Business Simulator Case.
"""
from core.import_case import import_case
from core.evaluate import Evaluate
from core.appreciate import Appreciate


class ResponsibleBusinessSimulator:
    """
    This class is the base class of an tRBS-case and contains all necessary information to import data, evaluate
    dependencies and calculate appreciations.
    """

    def __init__(self, name, file_extension, file_path):
        self.name = name
        self.file_extension = file_extension
        self.file_path = file_path
        self.input_dict = {}
        self.output_dict = {}

    def __str__(self):
        input_data_formatted = "\n\n".join(f"{key}\n\t{value}" for key, value in self.input_dict.items())
        return (
            f"Case: {self.name} ({self.file_extension}) \n"
            f"Data location: {self.file_path} \n"
            f"Input data: \n {input_data_formatted}"
        )

    def build(self):
        """This function builds all necessary elements for a generic RBS case"""
        print(f"Creating '{self.name}'")
        self.input_dict = import_case(self.file_extension, self.file_path)

    def evaluate(self):
        """This function deals with the evaluation of all dependencies"""
        case_evaluation = Evaluate(self.input_dict)
        case_evaluation.evaluate_all_scenarios()

    def appreciate(self):
        """This function deals with the appreciation of the outcomes"""
        case_appreciation = Appreciate(self.output_dict)
        case_appreciation.appreciate_all()
