# importing some packages
import pandas as pd


# specify the 10 tables
tables = [
    "configurations",
    "key_outputs",
    "decision_makers_options",
    "scenarios",
    "fixed_inputs",
    "intermediates",
    "dependencies",
    "theme_weights",
    "key_output_weights",
    "scenario_weights",
]

# import the 10 tables from csv files into a dictionary of pandas dataframes
path = "C:\\Users\\jswart004\\Documents\\Work\\propositions\\trbs\\beerwiser\\csv\\"
df_dict = {}
for t in tables:
    df = pd.read_csv(path + t + ".csv", sep=";")
    df_dict[t] = df

# convert df to xlsx
path = "C:\\Users\\jswart004\\Documents\\Work\\propositions\\trbs\\beerwiser\\xlsx\\"
with pd.ExcelWriter(path + "beerwiser.xlsx") as writer:
    for t in tables:
        df_dict[t].to_excel(writer, sheet_name=t)
