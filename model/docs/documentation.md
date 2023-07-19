## Documentation: ResponsibleBusinessSimulator

### Goal of this document
The goal of this document to keep track of what can (and cannot) be done with the (functions of) the 
`ResponsibleBusinessSimulator` class. The structure of this document is as follows: each core function is discussed in
a separate chapter, with the focus on the currently available options. 

### Function: *build()*
What **does** it do?
- Load a case given the user provided a proper `name`, `file_format` and `path`. 

What **doesn't** it do?
- Validate the correctness of the case it loads.

### Function: *evaluate()*
This function creates a `Evaluate` class (see: core/evaluate.py).

What **does** this class do?
- Creates a `value_dict` that is used to look up the current values of key outputs, internal variables, external
variables and fixed values. Values are updated in this dictionary when dependencies are calculated. Intermediates are
added along the way and do not need to be initialized. A missing value `""` is set to 1.
- Calculates dependencies based on a list of allowed operators:
  - `Squeezed *`: 
 $$f(x, y, sp, acc, p, me) = \min\left(1, \frac{\min(x,y)}{sp}\right) \cdot acc \cdot p \cdot me, \qquad \text{if } sp \neq 0$$
  where $sp=$ saturation_point, $acc=$ accessibility, $p=$ probability of success and $me=$ maximum effect. 
  Note that when $sp= 0$, we set $f(x, y, sp, acc, p, me)=0$
  - `-`: $$f(x, y) = x - y$$
  - `+`: $$f(x, y) = x + y$$
  - `*`: $$f(x, y) = x \cdot y$$
  - `/`: $$f(x, y) = \frac{x}{y}, \qquad \text{if } y \neq 0 \text{ else } f(x, y) = 0$$
  - `-*`: $$f(x, y) = -x \cdot y$$
  - `-/`: $$f(x, y) = \frac{-x}{y}, \qquad \text{if } y \neq 0 \text{ else } f(x, y) = 0$$
- Operators that are not part of the list above will raise an `EvaluationError`. 
- The `output_dict` consists of the values of ONLY the key outputs, per scenario and per decision maker option.

What **doesn't** this class do?
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
- `Weights` ($w$) are calculated as 


What **doesn't** this class do?
- a