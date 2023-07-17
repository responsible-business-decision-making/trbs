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
- a
- b

What **doesn't** this class do?
- a
