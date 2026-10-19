# RBS case schema & validation reference

A case is 11 tables. In CSV they are 11 files named exactly as below, semicolon (`;`)
separated, in `<path>/<CaseName>/csv/`. The same names are sheet names in xlsx and file
stems in json. The loader reads tables by name — **all 11 must be present**.

## Folder / loading convention
`TheResponsibleBusinessSimulator(name, file_path, extension)` reads from
`file_path / name / extension /`. So CSV authoring lives at `<path>/<CaseName>/csv/`, and
`case.transform('xlsx', output_path=Path('<path>')/name)` writes `<path>/<CaseName>/xlsx/<CaseName>.xlsx`.

## The 11 tables (exact columns)

| File / sheet | Columns (header, in order) |
|---|---|
| `configurations` | `configuration;value` |
| `key_outputs` | `key_output;theme;monetary;smaller_the_better;linear;automatic;start;end` |
| `theme_weights` | `theme;weight` |
| `key_output_weights` | `key_output;weight` |
| `decision_makers_options` | `internal_variable_input;decision_makers_option;value` |
| `scenarios` | `external_variable_input;scenario;value` |
| `scenario_weights` | `scenario;weight` |
| `fixed_inputs` | `fixed_input;value` |
| `dependencies` | `destination;argument_1;argument_2;operator` |
| `generic_text_elements` | `generic_text_element;value` |
| `case_text_elements` | `case_text_element;value` |

### Column meanings
- **configurations**: key/value settings. At minimum `language;EN` (or `NL`). Optional keys
  like `report_dependencies;true` toggle report pages; `Optimize_DMO_name` feeds `.optimize()`.
- **key_outputs**: one row per KPI.
  - `theme` — the theme this KPI rolls up into (must appear in `theme_weights`).
  - `monetary` — `1` if the value is a currency amount, else `0`.
  - `smaller_the_better` — `1` if a lower value is better, else `0`.
  - `linear` — `1` for linear appreciation, `0` for a sine (non-linear) curve.
  - `automatic` — `1` to auto-derive start/end from min/max across all options×scenarios
    (leave `start`/`end` empty); `0` to supply explicit `start` and `end`.
- **decision_makers_options**: long format. One row per (internal_variable_input, option).
  Each option must assign a value to **every** internal variable input.
- **scenarios**: long format. One row per (external_variable_input, scenario). Each scenario
  must assign a value to **every** external variable input.
- **fixed_inputs**: constants referenced by dependencies (single value, all scenarios).
- **dependencies**: the calculation graph. Each row computes `destination = argument_1 <op> argument_2`.
  Evaluation order (hierarchy) is derived automatically.
- **generic_text_elements** / **case_text_elements**: UI/report text. `case_text_elements`
  must include a textual `strategic_challenge` as its first row.

## Allowed operators (dependencies)
`-`  `+`  `*`  `/`  `-*`  `-/`  `>`  `<`  `>=`  `<=`  `min`  `max`

- `/` and `-/` return `0` when the denominator is `0`.
- `>`, `<`, `>=`, `<=` return `1`/`0` (indicator).
- Any other operator raises `EvaluationError`.

## Writing understandable dependencies (preferred)
Keep every dependency short and self-explanatory. Prefer descriptive names over cryptic
codes, and avoid abstract "saturation point / max effect" chains with `min(·,1)` caps.

Guidelines:
- Name each intermediate `destination` after what it represents (e.g.
  `Kwaliteit uit productie`, `Totale kosten`) — never `X_1`, `SQ_2`, `AC_3`.
- Model effects as a readable **rate × input**, using `fixed_inputs` named like
  `Kwaliteitspunten per productie-euro` or `Extra toeschouwers per euro`.
- Build a KPI as `baseline + uplift`, and make it scenario-sensitive by multiplying with an
  external factor (e.g. `Publieksopkomst factor`).

```
Kwaliteit uit productie;<investment input>;Kwaliteitspunten per productie-euro;*
Sportieve kwaliteit index;Basis sportieve kwaliteit;Kwaliteit uit productie;+
```

Only introduce `min`/`max` caps or multi-step saturation when the user explicitly wants
diminishing returns — not by default.

## Arguments: what is a valid argument?
Each `argument_1` / `argument_2` must be one of:
- an internal variable input name, or
- an external variable input name, or
- a `fixed_input` name, or
- a `destination` defined by another dependency row (including a key output), or
- a numeric literal (e.g. `1`).

A key output may be used as an argument in a later dependency; ordering is handled by the
hierarchy pass.

## Validation rules (enforced on `.build()`)
A `TemplateError` is raised if any of these fail:
1. **All 11 tables present** with all required columns; mandatory fields non-empty.
2. **Every internal variable input is used** in `dependencies`.
3. **Every external variable input is used** in `dependencies`.
4. **Every argument name is defined** (input / fixed / destination / numeric). Undefined → error.
5. **Input names are unique** across internal, external and fixed (no overlap).
6. **Each option assigns a value to every internal input**; **each scenario to every external input**.
7. **Weights match names exactly, both ways**:
   - `theme_weights.theme` == set of `key_outputs.theme`
   - `key_output_weights.key_output` == set of `key_outputs.key_output`
   - `scenario_weights.scenario` == set of `scenarios.scenario`
8. **Start/end vs automatic**: `automatic=1` ⇒ `start` and `end` empty; `automatic=0` ⇒ both provided.

Warnings (not fatal): extra columns are dropped with a warning; a `fixed_input` not used in
any dependency is warned about.

## Common pitfalls
- A KPI whose value is identical across **all** options and scenarios can make an automatic
  appreciation divide by zero — ensure each KPI varies with at least one option or scenario.
- Do not put a `;` inside any text value (it is the delimiter). Wrap long text in `"..."`.
- Theme/KPI/scenario names must match **character-for-character** (including accents, `&`,
  spacing) across every table that references them.
