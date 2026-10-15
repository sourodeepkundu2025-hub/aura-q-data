# Getting started

## Use the source checkout

Python 3.10 or newer is required for the supported utility environment. Core validation and analysis use only the Python standard library.

```bash
git clone --branch codex/aura-q-data-v1 https://github.com/sourodeepkundu2025-hub/aura-q-data.git
cd aura-q-data
python scripts/auraq.py --help
python scripts/auraq.py validate --table-checks
```

Run from the repository root, or pass `--root` before the command:

```bash
python scripts/auraq.py --root . catalog
python scripts/auraq.py --root . inspect --file intent_benchmark_v3_frozen.csv
python scripts/auraq.py --root . summarize --file gold_decision_records.csv
```

`catalog` reports filenames, data categories, row counts and bytes. `inspect` reports expected preference classes, statuses and safety categories for the chosen curated suite. `summarize` computes descriptive policy means, abstention rates and recorded constraint-violation rates for one retained replay.

## Install the CLI

```bash
python -m pip install -e .
auraq-data --root . validate --table-checks
auraq-data --root . reproduce
```

The package supplies utilities; the data remain in the checkout. Keep the dataset directory or use `--root` to point to it. The older `python verify_dataset.py` command now uses the same validated implementation.

## Export an analysis

```bash
python scripts/auraq.py summarize --file gold_decision_records.csv --output reports/gold_summary.csv
python examples/inspect_benchmark.py
python examples/compare_policies.py
```

Generated summaries must be written outside `data/`. Existing outputs are preserved by default; add `--force` only when you intend to replace a generated report. The CLI rejects an output path inside the frozen source-data directory even with `--force`. Read the [comparison definitions](comparisons.md) before interpreting a difference between model variants.

## Optional plots

```bash
python -m pip install -e ".[plots]"
python scripts/generate_previews.py
```

Only preview generation needs Matplotlib. It reads the existing figure tables and exports SVG assets plus their provenance. It does not rerun the historical simulator or intent study.

Validation failures return exit code 2 with a concise error. Check the requested data root, missing files and manifest version. For data drift, compare the file against a preserved snapshot rather than changing the manifest merely to make a modified file pass.
