# Comparison definitions

The public tools reproduce descriptive arithmetic from the retained CSVs. They use each record's stored objective and do not replace the historical simulator, intent model or bootstrap implementation.

| Table | Point values reconstructed | Retained source |
| --- | ---: | --- |
| Four-stage ablation | 4 mean regrets | Gold decision file for stages 1–3; Qwen decision file for stage 4. |
| Intent-model coupling | 3 regret differences | Keyword/Qwen/Mistral mean minus gold mean. |
| Preference sensitivity | 7 regret differences | Corresponding numbered sweep file. |
| Quality–latency grid | 15 regret differences | File matching the recorded quality/time weights. |
| Profile forest | 0 from this deposit | Four primary RUN-017 summary points; primary raw records are excluded. |

The first four rows total **29 reconstructed point estimates**. Model classification scores and all confidence intervals are retained reported fields, not newly recomputed measurements.

For the sensitivity and grid tables, the difference is AURA-Q regret minus shortest-queue regret under the recorded objective. Negative values favor AURA-Q for that replay condition. Grid cost weight is the remaining mass after quality and time weights; in the one-parameter sweep, quality weight stays at 0.2.

For cross-model coupling, changing the predicted profile may also change the objective. Use the table as an exploratory calculation. To test intent-driven routing benefit, a further evaluation must compare outcomes against one common gold objective and account for interpretation errors and total decision overhead.

The comparison data do not reproduce QFaaS, MQT Predictor or other published systems with their original environments. No cross-paper numerical ranking is asserted by this repository.
