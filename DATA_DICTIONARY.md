# Data dictionary

CSV values and original bytes are preserved. Empty values signify unavailable fields; they are not zero measurements. Exact headers and row counts are recorded per file in `DATA_MANIFEST.json`.

## Intent benchmark columns

| Column | Meaning |
| --- | --- |
| `split` | Recorded evaluation partition. |
| `case_id` | Unique authored request identifier within that suite. |
| `prompt` | Synthetic English request; adversarial cases are evaluation text, not instructions to the reader or software. |
| `gold_status` | Expected compilation or rejection status. |
| `gold_profile` | Expected preference class: quality, latency, budget or balanced. |
| `gold_deadline_seconds` | Expected numeric deadline in seconds. |
| `gold_budget_usd` | Historical name for the numeric budget expected by the request parser; not evidence of billing. |
| `gold_min_success_probability` | Expected minimum acceptable-result probability. |
| `gold_hardware_required`, `gold_simulator_allowed` | Expected execution-mode constraint flags. |
| `safety_category` | Authored case category, present in the 50-case suite. |

## Exploratory replay columns

| Column | Meaning |
| --- | --- |
| `run_id`, `experiment_id` | Recorded analysis identifiers. RUN-018 is the exploratory visual study. |
| `seed`, `step` | Generator seed and within-seed decision index. |
| `profile` | Preference identifier used by that variant. |
| `quality_weight`, `time_weight`, `cost_weight` | Utility weights used for ranking. |
| `circuit_id`, `family` | Circuit instance and family. |
| `policy` | Routing strategy, including an offline reference oracle where present. |
| `selected_backend` | Recorded historical fake-backend candidate, or abstention. |
| `acceptable_result` | Recorded acceptable-result proxy used by replay; not application accuracy. |
| `completion_seconds` | Generated queue plus modeled service completion time in seconds. |
| `cost_usd` | Historical name for normalized replay cost, not USD billing. |
| `preference_utility`, `oracle_utility` | Realized replay utility and offline feasible reference utility. |
| `preference_regret` | Reference utility minus selected-policy utility, under that record's objective. |
| `deadline_or_budget_violation` | Recorded replay constraint indicator. All compared guarded policies use the same feasibility screen. |
| `evidence_class`, `physical_qpu` | Simulator/replay scope and physical-device flag. |

## Figure-table definitions

- `four_stage_ablation.csv`: stage, strategy, mean preference regret, recorded interval endpoints and abstention rate. Uses variant-specific preference objectives; not a confirmatory end-to-end agent comparison.
- `intent_model_comparison.csv`: profile macro-F1, abstention F1, parser constraint match and exploratory coupling regret difference from gold. Metrics use the author-curated requests. A negative coupling difference is not proof of better interpretation because the objective can change.
- `one_parameter_sensitivity.csv`: quality weight is held at 0.2; time weight increases and cost weight is the remaining mass. The difference is AURA-Q minus shortest-queue regret.
- `quality_latency_heatmap.csv`: quality and time weights vary; cost weight is the remaining mass. Inspect the exact headers in the manifest for the recorded coordinates and differences.
- `profile_stratified_forest.csv`: AURA-Q minus shortest-queue regret by preference profile. Its point estimates originate in the primary RUN-017 profile summary. Those primary raw records are outside this deposit, so this table cannot be reconstructed from the released RUN-018 files. The saved figure-specific intervals should not be substituted for the manuscript's selection-aware primary intervals. Only the budget-first interval excludes zero in this retained table; quality-first has a positive point estimate.

`gold_decision_records.csv` and `run_018_gold.csv` are retained named variants rather than interchangeable file aliases. The manifest records their separate identities. The same applies to the keyword, Qwen and Mistral pairs. Their different hashes are preserved and no variant is substituted for the primary study.
