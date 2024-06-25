"""
This module contains the CaseImporter() class. This class deals with importing and validating an RBS case.
"""
from pathlib import Path
import warnings
import pandas as pd
import numpy as np
from vlinder.utils import check_numeric


class TemplateError(Exception):
    """
    This class deals with the error handling of our CaseImporter().
    """

    def __init__(self, message):  # ignore warning about super-init | pylint: disable=W0231
        self.message = message

    def __str__(self):
        return f"Template Error: {self.message}"


class CaseImporter:  # pylint: disable=too-few-public-methods
    """
    This class deals with import and validation of an RBS case, either as csv, xlsx or json.
    :param file_path: Path to folder that contains a folder structure of at least "name" - "file_format"
    """

    def __init__(self, file_path, name, extension):
        self.path_base = Path(file_path) / name / extension
        self.file_path = file_path
        self.name = name
        self.extension = extension
        self.importers = {
            "csv": lambda table: pd.read_csv(self.path_base / f"{table}.csv", sep=";"),
            "json": lambda table: pd.read_json(self.path_base / f"{table}.json", orient="table"),
            "xlsx": lambda table: pd.read_excel(self.path_base / f"{self.name}.xlsx", sheet_name=table),
        }
        self.dataframes_dict = {}
        self.input_dict = {}

        # -- Build template validators based on template.xlsx
        self.validate_dict = self._build_template_validators()

    @staticmethod
    def _build_template_validators() -> dict:
        """
        This function builds a validation dictionary of type:
        {table/sheet 1: [list of necessary columns], table/sheet 2: [list of necessary columns], ...}
        :return: dictionary with all necessary columns per table / sheet
        """
        template = pd.read_excel(Path(__file__).parent / "data/template.xlsx", sheet_name=None)
        return {key: value.columns.values.tolist() for key, value in template.items()}

    def _check_data_columns(self, to_check: pd.DataFrame, table: str) -> pd.DataFrame:
        """
        This function checks whether all necessary columns of a given table are provided. If necessary columns are
        missing a TemplateError is raised. If to many columns are provided the user receives a warning, but no error
        is raised.
        :param to_check: dataframe that needs to be checked
        :param table: name of the table the dataframe is supposed to be
        :return: the dataframe with any additional non-necessary columns removed
        """
        column_list = to_check.columns.values.tolist()

        # 1. Validate all necessary columns are there
        missing_cols = [col for col in self.validate_dict[table] if col not in column_list]
        if missing_cols:
            raise TemplateError(f"column(s) '{', '.join(missing_cols)}' are missing for '{table}'")
        # 2. Warn the user about columns that will not be used
        extra_cols = [col for col in column_list if col not in self.validate_dict[table]]
        if extra_cols:
            warnings.warn(f"column(s) '{', '.join(extra_cols)}' are not used for '{table}'")
        return to_check.drop(columns=extra_cols)

    def _create_dataframes_dict(self, table: str) -> None:
        """
        This function add a pd.DataFrame to the dataframes_dict
        :param table: name of the table to add
        """
        try:
            table_data = self.importers[self.extension](table)
        except (ValueError, FileNotFoundError) as missing_table:
            raise TemplateError(f"Sheet '{table}' is missing") from missing_table
        table_data = self._check_data_columns(table_data, table)
        self.dataframes_dict[table] = table_data

    def _convert_to_numpy_arrays_2d(self, table: str, data: pd.DataFrame) -> None:
        """
        This function transforms a dataframe into a 2-dimensional numpy array of values. Used for both
        the decision makers options table and the scenarios table
        :param table: name of the table
        :param data: dataframe that needs to be converted
        """
        target_column = [col for col in data.columns if col.endswith("_variable_input")]
        if len(target_column) != 1:
            raise TemplateError(f"Too many '_variable_input' columns in {table}")

        # prepare and store data
        pivoted_data = data.pivot(index=table[:-1], columns=target_column[0], values="value")
        self.input_dict[table] = pivoted_data.index.to_numpy()
        self.input_dict[f"{target_column[0]}s"] = pivoted_data.columns.to_numpy()
        # BUSINESS RULE: Replace missing combination by zero
        # user DOES NOT have to provide all possible (vars, dmo) or (vars, scenario) value combinations
        self.input_dict[f"{table[:-1]}_value"] = pivoted_data.values

    @staticmethod
    def _apply_first_level_hierarchy_to_row(row: pd.Series, all_inputs: np.array) -> int:
        """
        This function determines whether a dependency needs to be wait on other dependencies (hierarchy = 2) or can be
        calculated from the provided inputs or numeric argument value. (hierarchy = 1)
        :param row: a single row from the dependencies table
        :param all_inputs: an array containing all fixed, internal and external inputs
        :return: hierarchy level of either 1 or 2
        """
        args_with_known_value = sum(
            [(row[arg] in all_inputs or check_numeric(row[arg])) for arg in ["argument_1", "argument_2"]]
        )
        # if both values of the args are known return level 1, else return level 2
        if args_with_known_value == 2:
            return 1
        return 2

    @staticmethod
    def _apply_second_level_hierarchy_to_row(row: pd.Series, data: pd.DataFrame) -> int:
        """
        This function determines higher level hierarchies, given _apply_first_level_hierarchy_to_row has been called
        already on the data.
        :param row: a single row from the depencies table
        :param data: a dataframe containing (a subset of) dependencies
        :return: hierarchy level
        """
        # Hierarchy level 1 can be calculated always -- based on solely input values
        if row["hierarchy"] == 1:
            return row["hierarchy"]

        # iterate through the dependencies and increase if a row needs another destination to be calculated first
        hierarchy_start = row["hierarchy"]
        for _, dep in data.iterrows():
            if dep["destination"] == row["argument_1"]:
                row["hierarchy"] += 1
            elif dep["destination"] == row["argument_2"]:
                row["hierarchy"] += 1

        # apply a correction when argument & dependency are equal
        row["hierarchy"] -= sum(row[column] == row["destination"] for column in ["argument_1", "argument_2"])
        row["hierarchy"] = max(row["hierarchy"], hierarchy_start)
        return row["hierarchy"]

    def _convert_to_ordered_dependencies(self, data: pd.DataFrame) -> None:
        """
        This function converts the dependency table into a sorted version, based on calculated hierarchies.
        The sorted arrays are stored in the input dictionary.
        :param data: dataframe containing a dependencies table
        """
        # step 1: collect all input where the value is known
        all_inputs = np.hstack(
            (
                self.input_dict["fixed_inputs"],
                self.input_dict["internal_variable_inputs"],
                self.input_dict["external_variable_inputs"],
            )
        ).ravel()

        # STEP 2: determine hierarchies
        # step 2A: first-level hierarchies | calculations that use solely input variables
        data["hierarchy"] = data.apply(self._apply_first_level_hierarchy_to_row, all_inputs=all_inputs, axis=1)
        subdata = data[data["hierarchy"] != 1]
        steps = 1
        # STEP 2B: higher-level hierarchies | calculation that depend on other destinations
        # remove the lowest available hierarchy in each step, iterate until all dependencies have been removed
        while not subdata.empty:
            data["hierarchy"] = data.apply(self._apply_second_level_hierarchy_to_row, data=subdata, axis=1)
            subdata = data[data["hierarchy"] > min(subdata["hierarchy"])]
            steps += 1
        print(f"Hierarchy calculated in {steps} iterations")

        # use stable sorting to ensure user-order is used for equal hierarchies
        data = data.sort_values("hierarchy", kind="stable")

        # step 3: store the data in the input_dict
        for col in self.validate_dict["dependencies"]:
            self.input_dict[col] = data[col].to_numpy()
        self.input_dict["hierarchy"] = data["hierarchy"].to_numpy()
        self.input_dict["dependencies_order"] = data.index.to_numpy()

    def _convert_to_numpy_arrays_weights(self, table: str, data: pd.DataFrame) -> None:
        """
        This function converts the different weight tables to numpy arrays for the input dictionary.
        :param table: name of the table
        :param data: dataframe of the table
        """
        option, weight = self.validate_dict[table]
        # if the option arrays (theme, key_output, scenario) has not been added previously, add it now
        if f"{option}s" not in self.input_dict:
            self.input_dict[f"{option}s"] = data[option].to_numpy()

        # ensure the order of weights vector is the same as the order used previously
        ordered_data = pd.DataFrame(self.input_dict[f"{option}s"], columns=[option]).merge(data)
        self.input_dict[f"{option}_{weight}"] = ordered_data[weight].to_numpy()

    def _convert_to_numpy_arrays(self, table: str, data: pd.DataFrame) -> None:
        """
        This function converts a dataframe to numpy arrays in the input dictionary
        :param table: name of the table
        :param data: dataframe of the table
        """
        columns = self.validate_dict[table]
        for col in columns:
            key_name = table if col == table[:-1] else f"{table[:-1]}_{col}"
            self.input_dict[key_name] = data[col].to_numpy()

    def _create_input_dict(self):
        two_dim = ["decision_makers_options", "scenarios"]
        for table, data in self.dataframes_dict.items():
            # Option 1: data is transformed to a matrix
            if table in two_dim:
                self._convert_to_numpy_arrays_2d(table, data)
            # Option 2: data contains dependencies and hierarchy needs to be calculated
            elif table == "dependencies":
                self._convert_to_ordered_dependencies(data.copy())
            # Option 3: data is about weights and need to match order of previously added data
            elif table.endswith("_weights"):
                self._convert_to_numpy_arrays_weights(table, data)
            # Option 4: data is transformed to a vector
            else:
                self._convert_to_numpy_arrays(table, data)

    def _convert_to_relative_weights(self) -> None:
        """
        This function calculates and assigns relative weights to key outputs based the associated theme weights.
        """
        unique_themes, theme_counts = np.unique(self.input_dict["key_output_theme"], return_counts=True)
        theme_count_dict = dict(zip(unique_themes, theme_counts))
        theme_weight_dict = dict(zip(self.input_dict["themes"], self.input_dict["theme_weight"]))

        relative_weights = [
            self.input_dict["key_output_weight"][i]
            if theme_count_dict[theme] == 1
            else (self.input_dict["key_output_weight"][i] / theme_count_dict[theme]) * theme_weight_dict[theme]
            for i, theme in enumerate(self.input_dict["key_output_theme"])
        ]

        self.input_dict["key_output_relative_weight"] = np.array(relative_weights)

    def _enrich_input_dict(self):
        self._convert_to_relative_weights()

    def import_case(self) -> dict:
        """
        This function creates the input dictionary. It wraps other functions that deal with reading and validating
        the data.
        :return: dictionary with all necessary inputs for a case
        """
        for table in self.validate_dict:
            self._create_dataframes_dict(table)
        self._create_input_dict()
        self._enrich_input_dict()
        return self.input_dict, self.dataframes_dict
