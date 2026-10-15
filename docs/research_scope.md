# Research scope

AURA-Q addresses preference-aware QPU recommendation. Requests can prioritize result quality, completion time or cost. A local language model interprets the soft preference and proposes a typed profile. Deterministic controls retain responsibility for constraints, feasibility, ranking and the decision record.

The primary study evaluates backend routing with predefined preferences. A separate component study evaluates intent interpretation on authored English requests. Their combination motivates a governed interface, but the measured routing improvement cannot be assigned to language-model inference because the primary replay did not use it.

## Released evidence

| Collection | Coverage | Evidence type |
| --- | --- | --- |
| Curated intent suites | 30 and 50 request cases | Authored synthetic prompts and expected labels/constraints. |
| Exploratory replay exports | 30 files, each with 9,600 policy rows | Historical backend-derived noisy simulation with generated resource contexts. |
| Figure-data tables | Ablation, intent models, sensitivity, grid and profile effects | Retained numeric summaries; origin differs by table. |

Replay files share source fixtures and seeds. Their 288,000 policy rows are repeated analyses, not 288,000 independent quantum circuits or hardware jobs. The 30- and 50-case suites should likewise be reported separately rather than as a claim about 80 independent users.

Historical backend labels identify fake-backend noise models, not present hardware calibration or live provider performance. Recorded routing costs are normalized resource units. The `gold_budget_usd` field in curated requests is the historical parser label for an authored numeric constraint.

## Comparison boundaries

The four-stage and model-coupling analyses can use variant-specific preference objectives. A lower regret computed under a changed objective does not establish a better decision under one shared gold objective. The tools reconstruct the stored arithmetic and keep that interpretation explicit.

The four point estimates in `profile_stratified_forest.csv` originate in the primary RUN-017 profile summary. Primary raw decisions are outside this deposit, so those estimates cannot be regenerated from the released RUN-018 files. Saved figure-specific interval endpoints do not replace the manuscript's selection-aware primary intervals.

The collection excludes primary RUN-017 raw records, original finite-shot backend outcomes, raw model responses and historical execution source. It supports the analyses enumerated in [the evidence map](EVIDENCE_MAP.csv), rather than complete re-execution of every manuscript result. Physical-QPU performance, general quantum advantage and superiority to published systems are not established by these data.
