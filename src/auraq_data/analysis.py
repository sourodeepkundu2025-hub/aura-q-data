"""Descriptive analysis of retained records. SPDX-License-Identifier: MIT."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import math

from .catalog import DataError, csv_rows, finite_number, resolve_file


def summarize_replay(path: Path) -> list[dict]:
    values = defaultdict(list)
    abstentions, violations = Counter(), Counter()
    for row in csv_rows(path):
        required = {"policy", "preference_regret", "selected_backend", "deadline_or_budget_violation"}
        if not required.issubset(row):
            raise DataError("Replay summary requires policy, regret, backend and violation columns")
        policy = row["policy"]
        if not policy:
            raise DataError("Empty policy name")
        regret = finite_number(row["preference_regret"], "preference_regret")
        if regret < -1e-12:
            raise DataError("Negative preference regret")
        values[policy].append(regret)
        selected = row["selected_backend"].strip().casefold()
        abstentions[policy] += selected in {"", "none", "null", "abstain"}
        if "deadline_or_budget_violation" in row:
            value = finite_number(row["deadline_or_budget_violation"], "deadline_or_budget_violation")
            if value not in (0.0, 1.0):
                raise DataError("Violation indicator must be zero or one")
            violations[policy] += value
    if not values:
        raise DataError("No replay records to summarize")
    return [{"file": path.name, "policy": policy, "decisions": len(items),
             "mean_regret": math.fsum(items) / len(items),
             "abstention_rate": abstentions[policy] / len(items),
             "recorded_violation_rate": violations[policy] / len(items)}
            for policy, items in sorted(values.items())]


def inspect_benchmark(path: Path) -> dict:
    profiles, statuses, safety = Counter(), Counter(), Counter()
    count = 0
    for row in csv_rows(path):
        if not {"case_id", "prompt", "gold_profile", "gold_status"}.issubset(row):
            raise DataError("Requested file is not an intent benchmark")
        count += 1
        profiles[row["gold_profile"] or "unspecified"] += 1
        statuses[row["gold_status"]] += 1
        if "safety_category" in row:
            safety[row["safety_category"]] += 1
    return {"file": path.name, "requests": count, "gold_profiles": dict(sorted(profiles.items())),
            "gold_statuses": dict(sorted(statuses.items())), "safety_categories": dict(sorted(safety.items()))}


def check_table_points(root: Path) -> dict:
    cache = {}

    def means(name):
        if name not in cache:
            cache[name] = {r["policy"]: r["mean_regret"] for r in summarize_replay(resolve_file(root, name))}
        return cache[name]

    checked = 0

    def match(actual, expected, label):
        nonlocal checked
        if not math.isclose(finite_number(actual, label), expected, rel_tol=0, abs_tol=1e-12):
            raise DataError(f"Table point does not match retained records: {label}")
        checked += 1

    gold = means("gold_decision_records.csv")
    qwen = means("qwen_decision_records.csv")
    expected = [gold["shortest_queue"], gold["highest_proxy_fidelity"],
                gold["aura_q_preference"], qwen["aura_q_preference"]]
    ablation = list(csv_rows(resolve_file(root, "four_stage_ablation.csv")))
    if len(ablation) != 4:
        raise DataError("Four-stage table must have four rows")
    for row, point in zip(ablation, expected):
        match(row["mean_regret"], point, row["stage"])
    model_files = {"Keyword": "keyword_decision_records.csv", "Qwen": "qwen_decision_records.csv",
                   "Mistral": "mistral_decision_records.csv"}
    for row in csv_rows(resolve_file(root, "intent_model_comparison.csv")):
        if row["model"] not in model_files:
            raise DataError("Unknown model label in retained table")
        delta = means(model_files[row["model"]])["aura_q_preference"] - gold["aura_q_preference"]
        match(row["coupled_routing_regret_increase"], delta, row["model"])
    for i, row in enumerate(csv_rows(resolve_file(root, "one_parameter_sensitivity.csv"))):
        summary = means(f"run_018_sweep_{i}.csv")
        match(row["aura_minus_shortest_queue_regret"],
              summary["aura_q_preference"] - summary["shortest_queue"], f"sweep {i}")
    for row in csv_rows(resolve_file(root, "quality_latency_heatmap.csv")):
        quality = finite_number(row["quality_weight"], "quality_weight")
        time = finite_number(row["time_weight"], "time_weight")
        summary = means(f"run_018_grid_{quality:.2f}_{time:.2f}.csv")
        match(row["paired_regret_difference"], summary["aura_q_preference"] - summary["shortest_queue"],
              f"grid {quality:.2f}/{time:.2f}")
    return {"status": "PASS", "reconstructed_point_estimates": checked,
            "scope": "Exploratory table arithmetic under each recorded objective",
            "not_recomputed": ["confidence intervals", "model classification scores", "RUN-017 forest points"]}
