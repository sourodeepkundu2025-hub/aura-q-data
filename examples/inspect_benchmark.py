"""Inspect the retained 50-case suite. SPDX-License-Identifier: MIT."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from auraq_data.analysis import inspect_benchmark
from auraq_data.catalog import resolve_file

print(json.dumps(inspect_benchmark(resolve_file(root, "intent_benchmark_v3_frozen.csv")), indent=2))
