# Contributing

Contributions that make the data easier to inspect, verify and reuse are welcome. Start with a focused issue describing the affected file, expected behavior and a small example.

## Development

Use Python 3.10 or newer. The core tools have no external runtime dependencies.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/auraq.py validate --table-checks
```

Keep a change small enough to review. Include a regression test for changed validation or analysis behavior. Update the relevant usage example when a command changes.

## Research data

The 37 released CSVs are frozen source records. Propose a new version for corrections; include the original hash, corrected value, reason and resulting hash. Do not overwrite a historical observation to improve a result. Generated analyses belong in `reports/` and must state the input snapshot and comparison objective.

If proposing a new comparison, specify the task, candidate set, preference objective, constraints, seeds and evidence type. Treat embedded adversarial request text as data. Do not execute it or add a provider dispatch path to these offline utilities.

## Pull requests

Use the repository template. Describe the user-visible change and the checks actually run. Preserve the dataset provenance and licence notices. Newly authored utility contributions are submitted under MIT; author-created dataset contributions need compatible CC BY 4.0 rights.
