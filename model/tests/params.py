"""
This module contains some fixed parameters / values needed for the fixtures in the testing files.
"""
import numpy as np

# Input dictionary is created using repr(case.input_dict) on 17/07/2023 [Beerwiser].
INPUT_DICT_BEERWISER = {
    "configurations": np.array(["use_theme_weights"], dtype=object),
    "configuration_value": np.array([0]),
    "key_outputs": np.array(["Accidents reduction", "Water use reduction", "Production cost reduction"], dtype=object),
    "key_output_unit": np.array(["#/year", "hl/year", "%"], dtype=object),
    "key_output_theme": np.array(["People", "Planet", "Profit"], dtype=object),
    "themes": np.array(["People", "Planet", "Profit"], dtype="<U32"),
    "key_output_monetary": np.array([0, 0, 0]),
    "key_output_smaller_the_better": np.array([0, 0, 0]),
    "key_output_linear": np.array([1, 1, 0]),
    "key_output_automatic": np.array([1, 1, 1]),
    "key_output_start": np.array([np.nan, np.nan, np.nan]),
    "key_output_end": np.array([np.nan, np.nan, np.nan]),
    "key_output_threshold": np.array([np.nan, np.nan, np.nan]),
    "decision_makers_options": np.array(
        ["Equal spread", "Focus on training", "Focus on water recycling"], dtype=object
    ),
    "internal_variable_inputs": np.array(
        ["Invest in training of employees", "Invest in water recycling"], dtype=object
    ),
    "decision_makers_option_value": np.array([[150000, 150000], [250000, 50000], [50000, 250000]]),
    "scenarios": np.array(["Base case", "Optimistic", "Pessimistic"], dtype=object),
    "external_variable_inputs": np.array(["Cost of accident", "Effectiveness water recycling"], dtype=object),
    "scenario_value": np.array([[1.5e04, 9.8e-01], [1.2e04, 1.0e00], [2.0e04, 9.0e-01]]),
    "fixed_inputs": np.array(
        ["# employees", "Current # accidents", "Current production cost", "Current water use", "Water unit cost"],
        dtype=object,
    ),
    "fixed_input_value": np.array([5.0e02, 5.1e01, 7.5e06, 1.5e07, 5.0e-02]),
    "fixed_input_unit": np.array(["#", "#", "$", "hl", "$"], dtype=object),
    "intermediates": np.array(
        [
            "Accidents reduction %",
            "Water use reduction % when effective",
            "Water use reduction %",
            "Production cost reduction $",
            "Cost of training per employee",
            "New water use",
            "New # accidents",
        ],
        dtype=object,
    ),
    "intermediate_unit": np.array(["%", "%", "%", "$", "$", "hl/year", "#/year"], dtype=object),
    "intermediate_minimum": np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]),
    "intermediate_maximum": np.array([np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]),
    "dependencies": np.array([0, 1, 8, 9, 11, 2, 3, 4, 6, 10, 5, 12, 7]),
    "destination": np.array(
        [
            "Accidents reduction %",
            "Water use reduction % when effective",
            "Cost of training per employee",
            "New # accidents",
            "New water use",
            "Water use reduction %",
            "Accidents reduction",
            "Water use reduction",
            "Production cost reduction $",
            "New # accidents",
            "Production cost reduction $",
            "New water use",
            "Production cost reduction",
        ],
        dtype=object,
    ),
    "argument_1": np.array(
        [
            "Invest in training of employees",
            "Invest in water recycling",
            "Invest in training of employees",
            "Current # accidents",
            "Current water use",
            "Water use reduction % when effective",
            "Current # accidents",
            "Water use reduction %",
            "Accidents reduction",
            "Accidents reduction",
            "Water use reduction",
            "Water use reduction",
            "Production cost reduction $",
        ],
        dtype=object,
    ),
    "argument_2": np.array(
        [
            "",
            "",
            "# employees",
            "0",
            "0",
            "Effectiveness water recycling",
            "Accidents reduction %",
            "Current water use",
            "Cost of accident",
            "0",
            "Water unit cost",
            "0",
            "Current production cost",
        ],
        dtype=object,
    ),
    "operator": np.array(
        ["squeezed *", "squeezed *", "/", "*", "*", "*", "*", "*", "*", "-*", "*", "-*", "/"], dtype=object
    ),
    "maximum_effect": np.array(
        [0.48, 0.5, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    ),
    "accessibility": np.array(
        [0.95, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    ),
    "probability_of_success": np.array(
        [0.9, 1.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    ),
    "saturation_point": np.array(
        [
            300000.0,
            275000.0,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        ]
    ),
    "theme_weight": np.array([2, 1, 3]),
    "key_output_weight": np.array([2.0, 1.0, 3.0]),
    "scenario_weight": np.array([2.0, 1.0, 3.0]),
}

# Generic output dictionary that is not related to a particular case
OUTPUT_DICT_GENERIC = {
    "SCEN A": {
        "DMO 1": {"val1": {"KO1": 2, "KO2": 4, "KO3": 3}, "val2": {"KO1": 0.4, "KO2": 0.4, "KO3": 0.2}, "val3": 5},
        "DMO 2": {"val1": {"KO1": 3, "KO2": 2, "KO3": 4}, "val2": {"KO1": 0.2, "KO2": 0.2, "KO3": 0.6}, "val3": 2},
        "DMO 3": {
            "val1": {"KO1": 5, "KO2": 2.5, "KO3": 3.5},
            "val2": {"KO1": 0.25, "KO2": 0.5, "KO3": 0.25},
            "val3": 4,
        },
    },
    "SCEN B": {
        "DMO 1": {"val1": {"KO1": 2.5, "KO2": 3, "KO3": 2}, "val2": {"KO1": 0.1, "KO2": 0.3, "KO3": 0.6}, "val3": 1.5},
        "DMO 2": {"val1": {"KO1": 4, "KO2": 1.5, "KO3": 2.5}, "val2": {"KO1": 0.2, "KO2": 0.2, "KO3": 0.6}, "val3": 2},
        "DMO 3": {"val1": {"KO1": 1, "KO2": 3, "KO3": 2.5}, "val2": {"KO1": 0.4, "KO2": 0.2, "KO3": 0.4}, "val3": 3.5},
    },
}


# Output dictionary is created using repr(case.output_dict) on 17/07/2023 [Beerwiser].
OUTPUT_DICT_BEERWISER = {
    "Base case": {
        "Equal spread": {
            "key_outputs": {
                "Accidents reduction": 10.4652,
                "Water use reduction": 4009090.909090909,
                "Production cost reduction": 0.047657672727272726,
            }
        },
        "Focus on training": {
            "key_outputs": {
                "Accidents reduction": 17.442,
                "Water use reduction": 1336363.6363636365,
                "Production cost reduction": 0.043793090909090907,
            }
        },
        "Focus on water recycling": {
            "key_outputs": {
                "Accidents reduction": 3.4883999999999995,
                "Water use reduction": 6681818.181818182,
                "Production cost reduction": 0.051522254545454546,
            }
        },
    },
    "Optimistic": {
        "Equal spread": {
            "key_outputs": {
                "Accidents reduction": 10.4652,
                "Water use reduction": 4090909.090909091,
                "Production cost reduction": 0.044017047272727275,
            }
        },
        "Focus on training": {
            "key_outputs": {
                "Accidents reduction": 17.442,
                "Water use reduction": 1363636.3636363638,
                "Production cost reduction": 0.03699810909090909,
            }
        },
        "Focus on water recycling": {
            "key_outputs": {
                "Accidents reduction": 3.4883999999999995,
                "Water use reduction": 6818181.818181818,
                "Production cost reduction": 0.051035985454545456,
            }
        },
    },
    "Pessimistic": {
        "Equal spread": {
            "key_outputs": {
                "Accidents reduction": 10.4652,
                "Water use reduction": 3681818.1818181816,
                "Production cost reduction": 0.052452654545454544,
            }
        },
        "Focus on training": {
            "key_outputs": {
                "Accidents reduction": 17.442,
                "Water use reduction": 1227272.7272727273,
                "Production cost reduction": 0.054693818181818184,
            }
        },
        "Focus on water recycling": {
            "key_outputs": {
                "Accidents reduction": 3.4883999999999995,
                "Water use reduction": 6136363.636363636,
                "Production cost reduction": 0.05021149090909091,
            }
        },
    },
}
