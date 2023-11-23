## Documentation: TheResponsibleBusinessSimulator

### Goal of this document
The goal of this document to keep track of what can (and cannot) be done with the (functions of) the 
`TheResponsibleBusinessSimulator` class. The structure of this document is as follows: each core function is discussed in
a separate chapter, with the focus on the currently available options. 

### Function: *build()*
What **does** it do?
- Load a case given the user provided a proper `name`, `file_extension` and `file_path`. 
- Verify that **at least** all tables are there and checks both for missing column names and extra column names.
- Calculate the `hierarchy`-level with an iterative proces:
  - If both `argument_1` and `argument_2` are in the set of (fixed input, internal variable input, 
  external variable input) then **hierarchy level = 1**
  - For the remaining set $S$ of dependencies **hierarchy level > 1**, we do the following: 
    1. add 1 to the hierarchy level for each 
    argument of a row that is equal to the destination of **another dependency**
    2. Remove the rows with the lowest hierarchy from set $S$. If set $S$ is non-empty go back to step a.
    3. If set $S$ is empty, stop the proces. 

What **doesn't** it do?
- Use the `configurations` sheet

### Function: *evaluate()*
This function creates a `Evaluate` class (see: core/evaluate.py).

What **does** this class do?
- Creates a `value_dict` that is used to look up the current values of key outputs, internal variables, external
variables and fixed values. Values are updated in this dictionary when dependencies are calculated. Intermediates are
added along the way and do not need to be initialized. A missing value `""` is set to 1.
- Calculates dependencies based on a list of allowed operators:
  - `squeezed *`: 
 $$f(x, y, sp, acc, p, me) = \min\left(1, \frac{\min(x,y)}{sp}\right) \cdot acc \cdot p \cdot me, \qquad \text{if } sp \neq 0$$
  where $sp=$ saturation_point, $acc=$ accessibility, $p=$ probability of success and $me=$ maximum effect. 
  Note that when $sp= 0$, we set $f(x, y, sp, acc, p, me)=0$
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
- The `output_dict` consists of the values of ONLY the key outputs, per scenario and per decision maker option.
- Use the build-in operations `min` and `max` to protect the ranges for a dependency row your liking.

What **doesn't** this class do (yet)?
- No checks and/or boundaries on calculated values. 

### Function: *appreciate()*
This function creates a `Appreciate` class (see: core/appreciate.py).

What **does** this class do?
- Calculates the `start_and_end_points` of the appreciation functions based on the minimum and maximum value of all 
key output values (so for all scenarios and decision makers options). 
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
  


What **doesn't** this class do (yet)?
- Weight scenarios