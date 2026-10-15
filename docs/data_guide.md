# Data guide

`DATA_MANIFEST.json` is the file catalogue. Each entry records a relative path, exact byte length, SHA-256 hash, CSV header, row count and category. Available run IDs, policies and seeds are retained where those fields exist.

| Folder | Files | Main use |
| --- | ---: | --- |
| `data/benchmarks/` | 2 | Inspect authored requests and expected preference/constraint labels. |
| `data/exploratory_replays/` | 30 | Reconstruct descriptive policy means and sensitivity/grid differences. |
| `data/figure_tables/` | 5 | Inspect the archived estimates used in the paper's added visuals. |

Read [DATA_DICTIONARY.md](../DATA_DICTIONARY.md) for exact column definitions. Original bytes and column names remain unchanged, including legacy names that mention USD. The utility layer does not convert them into monetary measurements.

## Replay families

- `gold_decision_records.csv` and the keyword/Qwen/Mistral companions support the retained ablation and coupling summaries.
- `run_018_gold.csv` and its companions are separately retained variants. Their hashes differ, so they must not be silently substituted for the preceding files.
- `run_018_sweep_0.csv` through `run_018_sweep_6.csv` support the one-parameter sensitivity table.
- `run_018_grid_*.csv` names its recorded quality and time weights and supports the two-parameter grid table.

`seed` and `step` identify generated decisions within a replay; policy rows reuse contexts. Preserve that grain when making paired comparisons or resampling. The utility's mean summaries are descriptive and do not provide new confidence intervals.

## Integrity and changes

The Git attribute `data/** -text` prevents automatic line-ending conversion. Treat these source records as frozen. Put generated results in `reports/`, which is ignored by Git, and accompany shared analyses with the input snapshot and metric definitions. A corrected dataset needs a new version and a documented change, while the original commit remains citable.
