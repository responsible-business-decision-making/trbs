---
name: create-rbs-case
description: 'Build a Responsible Business Simulator (tRBS / vlinder) case from scratch, for ANY topic. USE WHEN the user wants to create a new RBS case, a tRBS case, a vlinder case, model a strategic decision, define key outputs / themes / decision maker options / scenarios, author or edit the case tables (configurations, key_outputs, dependencies, scenarios, weights, text elements), or build / validate / transform an RBS case between csv, xlsx and json. First interviews the user about the strategic challenge, decision options, KPIs and scenarios, then authors the 11 CSV tables, builds, validates and transforms the case. DO NOT USE FOR general Python questions unrelated to RBS cases.'
argument-hint: 'Describe the decision/topic to model, or point to an existing case to extend'
---

# Create an RBS case

Build a complete Responsible Business Simulator (tRBS) case for the `vlinder` package.
A case is 11 tables that together describe a strategic decision: which **decision maker
options** best serve a set of **key outputs** (KPIs grouped in **themes**), accounting for
external **scenarios**. This skill is topic-agnostic — always interview the user first.

## When to use
- The user wants a new RBS / tRBS / vlinder case on any subject.
- The user wants to add/modify key outputs, options, scenarios, dependencies or weights.
- The user wants to build, validate, or transform a case between csv / xlsx / json.

## Procedure

### 1. Interview the user (do not assume the topic)
Ask concise questions (batch them) and confirm before authoring. Cover:
1. **Strategic challenge** — what decision must be made, and in one short paragraph why.
2. **Decision maker options** — the mutually-exclusive variants to compare (include a
   reference/"current" option). These become `decision_makers_options`.
3. **Internal variable inputs** — the levers each option sets a value for (e.g. budgets,
   counts). Every option must assign a value to every internal input.
4. **Key outputs & themes** — the KPIs and the themes they group into. Flag each KPI's
   `monetary`, `smaller_the_better`, `linear`.
5. **Scenarios & external inputs** — the out-of-control factors and 2-4 scenarios
   (e.g. base/optimistic/pessimistic). Every scenario assigns a value to every external input.
6. **Weights** — theme weights (strategic priorities), key output weights, scenario weights
   (risk appetite).
7. **Admin** — case name, language, storage folder, source format (recommend `csv`), and
   which output format(s) to transform to (e.g. `xlsx`).

If the user is unsure, propose a sensible starting model with placeholder numbers and mark
them as "to refine in a workshop".

### 2. Author the 11 CSV tables
Create `<path>/<CaseName>/csv/` and write all 11 files, semicolon-separated.
Read [references/schema.md](./references/schema.md) for exact column names, allowed
operators, how to write short understandable dependencies (descriptive names, readable
rate × input effects — not cryptic saturation chains), and every validation rule the
importer enforces. Getting names to match **exactly** across tables is the single most
common failure.

### 3. Build, validate and transform
Run the bundled script, which builds → evaluates → appreciates → prints an appreciation
ranking → transforms to the requested format(s):

```
pipenv run python .github/skills/create-rbs-case/scripts/build_case.py \
  --name <CaseName> --path <path> --from csv --to xlsx
```

(Use `python` directly if the project is not using `pipenv`.)

### 4. Review with the user
- Confirm the build raises no `TemplateError` / `EvaluationError`.
- Show the per-scenario appreciation ranking and sanity-check that options are
  differentiated and the ordering is plausible.
- Iterate on numbers, weights, or structure as the user requests.

## Resources
- [references/schema.md](./references/schema.md) — the 11 tables, operators, patterns, and validation rules.
- [scripts/build_case.py](./scripts/build_case.py) — build/validate/transform CLI.

## Notes
- Prefer authoring in CSV (human-editable) then `case.transform(...)` to xlsx/json — never
  hand-edit binary xlsx.
- The `language` configuration value is only stored, not used to switch text; write the
  text elements directly in the desired language.
- Reference working example: the Futsal case under `data/Futsal/`.
