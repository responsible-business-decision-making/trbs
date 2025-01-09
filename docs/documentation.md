# 📖 Documentation 
The goal of this document is to keep track on the functionalities of the `TheResponsibleBusinessSimulator` (tRBS) class. 

### 🏃‍ Use of the class
To initialise (and use) a demo case, you can simply run:  
```python
case = TheResponsibleBusinessSimulator('DEMO_CASE_NAME')
```
_💡 see the README.MD file in `src > vlinder > data` for the latest overview of demo cases._

To initialise (and use) a custom user-defined case, run: 
```python
from pathlib import Path
path_to_case_folder = Path('PATH/TO/CASE/')
extension = 'EXTENSION' # supported: xlsx, csv, json
case = TheResponsibleBusinessSimulator('CASE_NAME', path_to_case_folder, extension)
```
The folder of the custom case is expected to satisfy the following format: 
- In the `PATH/TO/CASE` folder
  - There is a folder name `CASE_NAME`
    - That contains a folder named `EXTENSION`
      - That contains the actual case 

### 💪 Functionalities 
The tRBS currently contains the following functionalities: 
- .build() 
- .evaluate()
- .appreciate()
- .visualize()
- .transform()
- .modify()
- .make_report() 
- .optimize()
- .copy() 

These function are discussed in more detail below. 

## 👷 .build()
**Usage:** 
```python
case.build()
```
**What does it do?**
- Builds the `input_dict` for the provided case. This dictionary contains all information needed for an RBS case.
- Verifies that at least all necessary tables and columns are represented in the case and warns the user about any redundant columns that were provided. 
- Calculates the `hierarchy` of the dependencies by means of an iterative process: 
  - If both `argument_1` and `argument_2` are inputs (either fixed, internal variable or external variable) then the hierarchy level is set to 1.
  - For the remaining set $S$ of dependencies with hierarchy level > 1, we iterate over the following steps: 
    1. add 1 to the hierarchy level for each 
    argument of a row that is equal to the destination of another dependency
    2. Remove the rows with the lowest hierarchy from set $S$. If set $S$ is non-empty go back to step a.
    3. If set $S$ is empty, stop the proces. 

## 🧮 .evaluate()
**Usage:**
```python
case.evaluate()
```

**What does it do?**
- This function creates an `Evaluate` class that deals with the evaluation (also: calculation) of all dependencies, 
for each decision makers option and scenario.
- Creates a `value_dict` that is used to look up the current values of key outputs, internal variables, external
variables and fixed values. Values are updated in this dictionary when dependencies are calculated. Intermediates are
added along the way and do not need to be initialized.
- Calculates dependencies based on a list of allowed operators:
  - `-`: $$f(x, y) = x - y$$
  - `+`: $$f(x, y) = x + y$$
  - `*`: $$f(x, y) = x \cdot y$$
  - `/`: $$f(x, y) = \frac{x}{y}, \qquad \text{if } y \neq 0 \text{ else } f(x, y) = 0$$
  - `-*`: $$f(x, y) = -x \cdot y$$
  - `-/`: $$f(x, y) = \frac{-x}{y}, \qquad \text{if } y \neq 0 \text{ else } f(x, y) = 0$$
  - `>` or `>=`: $$f(x, y) = I_{x>(=)y}$$
  - `<` or `<=`: $$f(x, y) = I_{x<(=)y}$$
  - `min` or `max`: $$f(x, y) = \min(x, y) \text{ or } f(x, y) = \max(x, y)
- Operators that are not part of the list above will raise an `EvaluationError`. 
- The values of the key outputs, for each scenario and decision makers options are added to the `output_dict`.

**💡 Tips and tricks**

The `Evaluate`-class can be used to look up the intermediates for a given scenario and decision makers option: 
```python
from vlinder.evaluate import Evaluate
case.build()
case_eval = Evaluate(case.input_dict)
case_eval.evaluate_all_dependencies('SCENARIO', 'DMO')
case_eval.value_dict
```

The `Squeezed` functionality is given by: 

$$f(x, y, sp, acc, p, me) = \min\left(1, \frac{x}{sp}\right) \cdot acc \cdot p \cdot me, \qquad \text{if } sp \neq 0$$
where $sp=$ saturation_point, $acc=$ accessibility, $p=$ probability of success and $me=$ maximum effect. 

## 🤩 .appreciate()
**Usage:**
```python
case.appreciate()
```

**What does it do?**
- This function creates a `Appreciate` class.
- Calculates the `start_and_end_points` of the appreciation functions based on the minimum and maximum value of all 
key output values (so for all scenarios and decision makers options) or the user-provided bounds. This depends on the value
of the indicator `automatic`. 
- Appreciates key outputs based on these calculated `start_and_end_points` and two indicators:
  - `key_output_smaller_the_better` ($I_{STB}$) which equals 1 if the smallest value should have the highest
  appreciation.
  - `key_output_linear` ($I_{l}$) that determines whether a linear or non-linear appreciation should be applied.
- The appreciations are calculated as 
  - if $I_l=1$: $$f(x, s, e) = (-1)^{I_{STB}} \cdot \frac{x - s - I_{STB}(e-s)}{e-s} \cdot 100$$ 
  where $x$ denotes the key output value, $s$ denotes the start value and $e$ the end value.
  - if $I_l=0$: $$f(x, s, e) = \left((-1)^{I_{STB}} \cdot \sin\left(\frac{1}{2} \cdot \pi \cdot \frac{x-s}{e-s}\right) + I_{STB}\right) \cdot 100$$
  where $x$ denotes the key output value, $s$ denotes the start value and $e$ the end value.
- For the calculation of the `Weights` ($w$) we first define the following variables:
  - $w_{ko}$ or `weights["key_output"]`: the weight of the given key output (user-input)
  - $w_{kos|t}$ or `weights["sum_within_theme"]`: the sum of the weights of all key outputs with the same theme as the 
  given key output
  - $w_{t}$ or `weights["theme"]`: the weight of the theme of the given key output (user-input)
  - $w_{ts}$ or `weights["sum_theme"]`: the sum of the weights of all themes 
- The weight for a given key output is then calculated as: $$w = \frac{w_{ko}}{w_{kos|t}} \cdot \frac{w_t}{w_{ts}}$$ 
- Scenario weights are used to also calculate appreciations across scenarios

**💡 Tips and tricks**
- If you do not want to use theme weighs, set the theme weights equal to the sum of the weights of the key outputs within
that theme. Then the weight becomes: 
$$w= \frac{w_{ko}}{w_{kos|t}} \cdot \frac{w_{kos|t}}{w_{ts}} = \frac{w_{ko}}{w_{ts}}$$
where by defintion the sum of theme weights equals the sum of all key outputs.

## 📊 .visualize()
**Usage:**
```python
# example of a table 
case.visualize(visual_request='table', key='key_outputs', scenario='SCENARIO_NAME')

# example of a barchart 
case.visualize('barchart', 'weighted_appreciations', scenario=selected_scenario, stacked=True)
```

**What does it do?**
- This function visualizes the content of the `output_dict`. 
- It uses a `visual_request` (table or barchart) and `key` of the `output_dict` as variables. If the key is associated
with a list of dimension 3, a `scenario` also needs to be provided.

**💡 Tips and tricks**

To get an overview of the supported `key`s and `**kwargs` values: 
```python
# supported keys 
case.visualizer.available_outputs

# supported kwargs
case.visualizer.available_kwargs
```

## ↪️ .transform()
**Usage:**
```python
case.transform("json")
case.transform("csv", output_path="SOME/OTHER/LOCATION")
```
**What does it do?**
- Transforms a case into one of the other supported formats. Default location: 'data' folder in your current working
directory. Another location can be provide with `output_path`. 

## 🛠️ modify()
**Usage:**
```python
case.modify(input_dict_key='theme_weight', element_key='THEME_NAME', new_value=123)
```
**What does it do?**
- Change a weight in the `input_dict` by providing a `input_dict_key`, `element_key` and `new_value`.

## 📝 make_report()
**Usage:**
```python
case.make_report("SCENARIO_NAME")

# change to portrait mode and store at own location
case.make_report("SCENARIO_NAME", orientation="Portrait", output_path="MY/LOCATION/PATH")
```
**What does it do?**
- Creates a report that summarizes the active case in a PDF file for a selected scenario. As a default it uses 
`orientation = 'Landscape'` and places it in a 'reports' folder in the current working directory.

## 📈 optimize()
**Usage:**
```python
case.optimize("SCENARIO_NAME")

# or use a copy if you do not want to change the original case
case_optimizer = case.copy()
case_optimizer.optimize("SCENARIO_NAME")
```
**What does it do?**
- Finds an improved budget allocation for decision makers options in a selected scenario by means of a grid search.
- Adds this allocation as a DMO to the `input_dict` with default name `CASE_NAME - Optimized`. Use `new_dmo_name` to
provide a custom name for the optimized DMO name. 

## 🖨️ copy()
**Usage:**
```python
case.copy()
```
**What does it do?**
- Creates a deep copy of the instance. 
