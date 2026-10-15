"""Command-line interface. SPDX-License-Identifier: MIT."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

from . import __version__
from .analysis import check_table_points, inspect_benchmark, summarize_replay
from .catalog import DataError, discover_root, load_manifest, resolve_file, validate_dataset


def write_summary(root: Path, path: Path, records: list[dict], force: bool = False):
    if path.suffix.casefold() != ".csv":
        raise DataError("Summary output must have a .csv extension")
    if path.resolve().is_relative_to((root / "data").resolve()):
        raise DataError("Generated summaries must be outside the frozen data directory")
    if not records:
        raise DataError("Cannot export an empty summary")
    if path.exists() and not force:
        raise DataError("Summary output already exists; use --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if force else "x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and validate the AURA-Q research-data collection")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--root", help="Directory containing DATA_MANIFEST.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="List retained files, rows and data categories")
    validate = commands.add_parser("validate", help="Verify manifest, data and optional table arithmetic")
    validate.add_argument("--table-checks", action="store_true")
    inspect = commands.add_parser("inspect", help="Inspect one author-curated intent benchmark")
    inspect.add_argument("--file", default="intent_benchmark_v3_frozen.csv")
    summary = commands.add_parser("summarize", help="Compute descriptive policy means for a retained replay")
    summary.add_argument("--file", default="gold_decision_records.csv")
    summary.add_argument("--output", type=Path, help="Optional generated CSV path outside data/")
    summary.add_argument("--force", action="store_true", help="Replace an existing generated CSV outside data/")
    commands.add_parser("reproduce", help="Reconstruct 29 released exploratory table point estimates")
    args = parser.parse_args(argv)
    try:
        root = discover_root(args.root)
        if args.command == "catalog":
            result = [{k: item[k] for k in ["path", "kind", "rows", "bytes"]}
                      for item in load_manifest(root)["files"]]
        elif args.command == "validate":
            result = validate_dataset(root)
            if args.table_checks:
                result["table_arithmetic"] = check_table_points(root)
        elif args.command == "inspect":
            result = inspect_benchmark(resolve_file(root, args.file))
        elif args.command == "summarize":
            result = summarize_replay(resolve_file(root, args.file))
            if args.output:
                write_summary(root, args.output, result, force=args.force)
        else:
            result = check_table_points(root)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (DataError, OSError, UnicodeError) as exc:
        print(f"auraq-data: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
