"""Build, validate and transform an RBS (tRBS / vlinder) case.

Reads a case from <path>/<name>/<from>, runs build -> evaluate -> appreciate,
prints a per-scenario appreciation ranking, and optionally transforms the case
to one or more target formats (xlsx / json / csv).

Usage:
    python build_case.py --name MyCase --path data --from csv --to xlsx
    python build_case.py --name MyCase --path data --from csv --to xlsx json
    python build_case.py --name MyCase --path data --from csv   # validate only
"""

import argparse
from pathlib import Path

import pandas as pd
from vlinder.trbs import TheResponsibleBusinessSimulator


def main() -> None:
    """
    Build, validate and optionally transform an RBS case.

    Reads a case from <path>/<name>/<from>, runs build -> evaluate -> appreciate,
    prints a per-scenario appreciation ranking, and optionally transforms the case
    to one or more target formats (xlsx / json / csv).
    """
    parser = argparse.ArgumentParser(description="Build, validate and transform an RBS case.")
    parser.add_argument("--name", required=True, help="Case name (the folder under --path).")
    parser.add_argument("--path", default="data", help="Base folder containing <name>/<from>/ (default: data).")
    parser.add_argument("--from", dest="src", default="csv", help="Source format to load (default: csv).")
    parser.add_argument("--to", nargs="*", default=[], help="Target format(s) to transform to, e.g. --to xlsx json.")
    args = parser.parse_args()

    case = TheResponsibleBusinessSimulator(args.name, Path(args.path), args.src)
    case.build()
    print("BUILD OK")
    case.evaluate()
    print("EVALUATE OK")
    case.appreciate()
    print("APPRECIATE OK")

    scenarios = list(case.input_dict["scenarios"])
    dmos = list(case.input_dict["decision_makers_options"])
    totals = {
        s: {d: round(sum(case.output_dict[s][d]["weighted_appreciations"].values()), 1) for d in dmos}
        for s in scenarios
    }
    print("\nTotal weighted appreciation per option:")
    print(pd.DataFrame(totals).to_string())
    print("\nBest option per scenario:")
    for s in scenarios:
        print(f"  {s}: {case.output_dict[s]['highest_weighted_dmo']}")

    for fmt in args.to:
        case.transform(fmt, output_path=Path(args.path) / args.name)
        print(f"\nTRANSFORM OK -> {(Path(args.path) / args.name / fmt).resolve()}")


if __name__ == "__main__":
    main()
