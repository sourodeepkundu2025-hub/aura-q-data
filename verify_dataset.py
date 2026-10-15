"""Compatible entry point for the first dataset release. SPDX-License-Identifier: MIT."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from auraq_data.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["--root", str(Path(__file__).resolve().parent), "validate", "--table-checks"]))
