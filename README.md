# AURA-Q Curated Intent Benchmarks and Exploratory Simulator Data

Data accompanying **AURA-Q: Governed Agentic AI for Auditable QPU Selection**, by Sourodeep Kundu and Kalyanaraman P.

The deposit contains original, author-curated English requests and retained exploratory simulator replay outputs. The requests are synthetic evaluation cases, not records of real users. The replay uses historical backend-derived noisy simulation and generated queue, cost, preference and deadline contexts.

## Contents

- `data/benchmarks/`: the frozen 30-request and 50-request intent benchmarks, including expected preferences and constraints.
- `data/figure_tables/`: five tables underlying the ablation, intent-model, sensitivity, quality-latency and profile-effect figures.
- `data/exploratory_replays/`: 30 retained decision CSVs for gold, keyword, Qwen and Mistral variants, the preference sweep and the quality-latency grid.
- `DATA_MANIFEST.json`: exact file hashes, row counts, columns and available run identifiers.
- `DATA_DICTIONARY.md`: units, column meanings and comparison definitions.
- `verify_dataset.py`: a standard-library integrity and numerical consistency check.

Run `python verify_dataset.py` after downloading the repository snapshot. The checker does not submit jobs or call a language model.

## Interpretation

The primary paper evaluates the intent component separately from backend routing. The intent-model coupling and four-stage replay summaries are exploratory; each variant may generate a different preference objective. A lower value in those tables alone does not establish that a language-model variant better achieves one shared gold objective.

Costs and budgets in simulator routing are normalized resource units. Historical column names such as `cost_usd` do not represent provider invoices. In the curated intent benchmark, `gold_budget_usd` is the numeric constraint expected from the authored request parser. It is not a measured physical-QPU cost.

The profile-effect table reports AURA-Q regret minus shortest-queue regret: negative values favor AURA-Q. Its four point estimates come from the primary RUN-017 profile summary, whose raw records are outside this deposit. They cannot be recomputed from the released RUN-018 decision files. The retained figure-specific interval endpoints are not replacements for the selection-aware primary intervals in the manuscript.

This snapshot covers the records enumerated in the manifest. Primary RUN-017 raw decision records, original finite-shot backend outcomes, raw model responses and historical execution scripts are outside this deposit. The released tables do not independently reproduce every manuscript result. No physical-QPU study or quantum advantage is represented by these data.

## Citation and reuse

Cite this dataset title, the repository snapshot URL and version 1.0.0. No dataset DOI has been assigned. Metadata identifies both authors. No additional reuse license is granted by this deposit; contact the corresponding author at `pkalyanaraman@vit.ac.in` regarding reuse.
