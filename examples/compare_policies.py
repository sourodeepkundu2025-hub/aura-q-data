"""Read descriptive means under one retained objective. SPDX-License-Identifier: MIT."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))
from auraq_data.analysis import summarize_replay
from auraq_data.catalog import resolve_file

for row in summarize_replay(resolve_file(root, "gold_decision_records.csv")):
    print(f"{row['policy']:26} n={row['decisions']:4} mean_regret={row['mean_regret']:.6f}")
