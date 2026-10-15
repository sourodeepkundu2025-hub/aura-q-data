# Reproducibility

## Verify the snapshot

```bash
python scripts/auraq.py validate --table-checks
```

The checks cover file existence, exact byte counts and SHA-256 hashes, CSV schemas and row counts, unique authored case IDs, finite nonnegative regret, and simulator flags. Table checks reconstruct 29 point estimates with an absolute tolerance of `1e-12`.

The manifest identifies the released records. Its digest verifies identity against that record; it does not independently establish the scientific validity of the original experiment. For research reuse, preserve both the repository commit and the manifest.

## Reconstruct summaries

```bash
python scripts/auraq.py reproduce
python scripts/auraq.py summarize --file gold_decision_records.csv --output reports/gold_summary.csv
```

Means are recomputed from all policy rows in the chosen CSV using finite recorded regrets. Abstention and violation rates use that policy's row count as denominator. Summaries refuse incomplete replay schemas instead of treating missing violation fields as zero.

Historical confidence intervals and model classification scores are not recomputed by these commands. The RUN-017 forest points refer to primary raw data outside the collection. The utilities report these boundaries explicitly in their JSON output.

## Tests and CI

```bash
python -m unittest discover -s tests -v
```

Tests cover integrity drift, CSV corruption, missing or duplicate fields, invalid manifest paths, non-finite values, descriptive arithmetic, error handling and frozen-output protection. Full collection validation and the retained table reconstruction are also exercised.

The GitHub workflow uses read-only repository permissions and pinned official actions. It runs core checks on Python 3.10 and 3.12. The workflow badge displays GitHub's live result; a local test pass does not stand in for a cloud check result.

The new utility environment is separate from the historical quantum experiment environment. These tests do not execute a language model, simulator, paid service or hardware provider.
