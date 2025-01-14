"""
This module contains some fixed parameters / values needed for the fixtures in the testing files.
"""

import numpy as np

# Input dictionary is created using repr(case.input_dict) on 17/07/2023 [Beerwiser].
INPUT_DICT_BEERWISER = {
    "configurations": np.array(["use_theme_weights", "language"]),
    "configuration_value": np.array([0, "EN"]),
    "generic_text_elements": np.array(
        [
            "title_strategic_challenge",
            "title_key_outputs",
            "title_dmo",
            "title_scenarios",
            "title_comparison_dmo",
            "title_comparison_scenario",
            "title_fixed_inputs",
            "title_dependency_graph",
            "title_weighted_graph",
            "text_strategic_challenge",
            "text_key_outputs",
            "text_dmo",
            "text_scenarios",
            "text_comparison_dmo",
            "text_comparison_scenario",
            "intro_key_outputs",
            "intro_decision_makers_options",
            "intro_scenarios",
            "intro_fixed_inputs",
            "intro_dependency_graph",
            "intro_weighted_graph",
            "header_theme",
            "header_key_outputs",
            "graph_title_dmo",
            "graph_y_label_dmo",
            "graph_text_dmo",
            "table_text_dmo",
            "graph_text_scenarios",
            "graph_title_scenarios",
            "graph_y_label_scenarios",
        ]
    ),
    "generic_text_element_value": np.array(
        [
            "Strategic challenge",
            "Key outputs",
            "Options",
            "Scenarios",
            "Strategic priorities",
            "Risk appetite",
            "Fixed inputs",
            "Dependency graph",
            "Resulting appreciations of different DMOs for scenario: ",
            "The strategic challenge that requires a decision",
            "The indicators used to evaluate the impact of your decision",
            "The options you have to influence your impact",
            "The uncertainty you want to account for",
            "Evaluate options by assessing strategic priorities",
            "Evaluate options by assessing risk appetite",
            "The outputs upon which the decision makers will base their decision. Key outputs are often referred to "
            "as KPIs. Key outputs are grouped into themes.",
            "Decision makers options are formulated by assigning a single value to all internal variable inputs. "
            "These inputs can be formulated and determined by the decision makers.",
            "Each external variable input can be thought of as a single aspect of external uncertainty affecting "
            "the outcome of the decision in scope. A scenario is defined by assigning a single value to all external "
            "variable inputs.",
            "The inputs which only take one value for all scenarios.",
            np.nan,
            np.nan,
            "Theme",
            "Key output",
            "Appreciations per option for scenario",
            "Appreciation",
            "The chart below shows the weighted appreciations per option, where key outputs are grouped into themes. "
            "The used theme weights are displayed in the pie chart on the right, showing the relative weights of all "
            "key outputs belonging to that theme. Use the dropdown menu to navigate through the various scenarios.",
            "The table below shows the key output values per option, based on the selected scenario. The option with "
            "the highest weighted appreciation is highlighted.",
            "The chart below shows the weighted appreciations per option, grouped into scenarios. The used scenario "
            "weights are displayed in the pie chart on the right.",
            "Appreciations per scenario",
            "Appreciation",
        ]
    ),
    "case_text_elements": np.array(["title_test", "strategic_challenge", "intro_test"]),
    "case_text_element_value": np.array(["test_title", "nan", "test_intro"]),
    "key_outputs": np.array(["Accidents reduction", "Water use reduction", "Production cost reduction"]),
    "key_output_theme": np.array(["People", "Planet", "Profit"]),
    "key_output_monetary": np.array([0, 0, 0]),
    "key_output_smaller_the_better": np.array([0, 0, 0]),
    "key_output_linear": np.array([1, 1, 0]),
    "key_output_automatic": np.array([1, 1, 1]),
    "key_output_start": np.array([np.nan, np.nan, np.nan]),
    "key_output_end": np.array([np.nan, np.nan, np.nan]),
    "key_output_threshold": np.array([np.nan, np.nan, np.nan]),
    "decision_makers_options": np.array(["Equal spread", "Focus on training", "Focus on water recycling"]),
    "internal_variable_inputs": np.array(["Invest in training of employees", "Invest in water recycling"]),
    "decision_makers_option_value": np.array([[150000, 150000], [250000, 50000], [50000, 250000]]),
    "scenarios": np.array(["Base case", "Optimistic", "Pessimistic"]),
    "external_variable_inputs": np.array(["Cost of accident", "Effectiveness water recycling"]),
    "scenario_value": np.array([[15000, 0.98], [12000, 1.00], [20000, 0.90]]),
    "fixed_inputs": np.array(
        [
            "# employees",
            "Current # accidents",
            "Current production cost",
            "Current water use",
            "Water unit cost",
            "AR_me",
            "AR_acc",
            "AR_pos",
            "AR_sp",
            "WURWE_me",
            "WURWE_acc",
            "WURWE_pos",
            "WURWE_sp",
        ]
    ),
    "fixed_input_value": np.array(
        [
            500,
            51,
            7500000,
            15000000,
            0.05,
            0.48,
            0.95,
            0.9,
            300000,
            0.5,
            1.0,
            1.0,
            275000,
        ]
    ),
    "destination": np.array(
        [
            "AR_1",
            "WURWE_1",
            "Cost of training per employee",
            "AR_2",
            "WURWE_2",
            "AR_3",
            "WURWE_3",
            "AR_4",
            "WURWE_4",
            "Accidents reduction %",
            "Water use reduction % when effective",
            "Water use reduction %",
            "Accidents reduction",
            "Water use reduction",
            "Production cost reduction $",
            "New # accidents",
            "Production cost reduction $",
            "New water use",
            "Production cost reduction",
        ]
    ),
    "argument_1": np.array(
        [
            "Invest in training of employees",
            "Invest in water recycling",
            "Invest in training of employees",
            "AR_1",
            "WURWE_1",
            "AR_2",
            "WURWE_2",
            "AR_3",
            "WURWE_3",
            "AR_4",
            "WURWE_4",
            "Water use reduction % when effective",
            "Current # accidents",
            "Water use reduction %",
            "Accidents reduction",
            "Current # accidents",
            "Water use reduction",
            "Current water use",
            "Production cost reduction $",
        ]
    ),
    "argument_2": np.array(
        [
            "AR_sp",
            "WURWE_sp",
            "# employees",
            1,
            1,
            "AR_acc",
            "WURWE_acc",
            "AR_pos",
            "WURWE_pos",
            "AR_me",
            "WURWE_me",
            "Effectiveness water recycling",
            "Accidents reduction %",
            "Current water use",
            "Cost of accident",
            "Accidents reduction",
            "Water unit cost",
            "Water use reduction",
            "Current production cost",
        ]
    ),
    "operator": np.array(
        [
            "/",
            "/",
            "/",
            "min",
            "min",
            "*",
            "*",
            "*",
            "*",
            "*",
            "*",
            "*",
            "*",
            "*",
            "*",
            "-",
            "*",
            "-",
            "/",
        ]
    ),
    "hierarchy": np.array([1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 15]),
    "dependencies_order": np.array([0, 5, 16, 1, 6, 2, 7, 3, 8, 4, 9, 10, 11, 12, 14, 17, 13, 18, 15]),
    "themes": np.array(["Planet", "People", "Profit"]),
    "theme_weight": np.array([1, 2, 3]),
    "key_output_weight": np.array([2, 1, 3]),
    "scenario_weight": np.array([2, 1, 3]),
    "key_output_relative_weight": np.array([2, 1, 3]),
}

# Generic output dictionary that is not related to a particular case
OUTPUT_DICT_GENERIC = {
    "SCEN A": {
        "DMO 1": {
            "val1": {"KO1": 2, "KO2": 4, "KO3": 3},
            "val2": {"KO1": 0.4, "KO2": 0.4, "KO3": 0.2},
            "val3": 5,
        },
        "DMO 2": {
            "val1": {"KO1": 3, "KO2": 2, "KO3": 4},
            "val2": {"KO1": 0.2, "KO2": 0.2, "KO3": 0.6},
            "val3": 2,
        },
        "DMO 3": {
            "val1": {"KO1": 5, "KO2": 2.5, "KO3": 3.5},
            "val2": {"KO1": 0.25, "KO2": 0.5, "KO3": 0.25},
            "val3": 4,
        },
    },
    "SCEN B": {
        "DMO 1": {
            "val1": {"KO1": 2.5, "KO2": 3, "KO3": 2},
            "val2": {"KO1": 0.1, "KO2": 0.3, "KO3": 0.6},
            "val3": 1.5,
        },
        "DMO 2": {
            "val1": {"KO1": 4, "KO2": 1.5, "KO3": 2.5},
            "val2": {"KO1": 0.2, "KO2": 0.2, "KO3": 0.6},
            "val3": 2,
        },
        "DMO 3": {
            "val1": {"KO1": 1, "KO2": 3, "KO3": 2.5},
            "val2": {"KO1": 0.4, "KO2": 0.2, "KO3": 0.4},
            "val3": 3.5,
        },
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
