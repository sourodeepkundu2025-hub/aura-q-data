"""Regression tests for data integrity and descriptive analysis. MIT licensed."""
from contextlib import redirect_stderr, redirect_stdout
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from auraq_data.analysis import check_table_points, inspect_benchmark, summarize_replay
from auraq_data.catalog import DataError, csv_rows, discover_root, finite_number, load_manifest, resolve_file, scoped_path, validate_dataset
from auraq_data.cli import main, write_summary


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="auraq-data-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fixture(self, rows=None, headers=None):
        headers = headers or ["policy", "preference_regret", "selected_backend", "deadline_or_budget_violation", "physical_qpu"]
        rows = rows or [
            {"policy":"alpha", "preference_regret":"0.1", "selected_backend":"fake_a", "deadline_or_budget_violation":"0", "physical_qpu":"False"},
            {"policy":"alpha", "preference_regret":"0.3", "selected_backend":"abstain", "deadline_or_budget_violation":"1", "physical_qpu":"False"}]
        path = self.root / "data" / "example.csv"
        path.parent.mkdir(exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        raw = path.read_bytes()
        manifest = {"files":[{"path":"data/example.csv", "bytes":len(raw),
                    "sha256":hashlib.sha256(raw).hexdigest(), "rows":len(rows),
                    "columns":headers, "kind":"test"}]}
        self.manifest(manifest)
        return path, manifest

    def manifest(self, value):
        (self.root / "DATA_MANIFEST.json").write_text(json.dumps(value), encoding="utf-8")

    def test_valid_dataset_and_descriptive_rates(self):
        path, _ = self.fixture()
        self.assertEqual(validate_dataset(self.root)["total_rows"], 2)
        row = summarize_replay(path)[0]
        self.assertAlmostEqual(row["mean_regret"], 0.2)
        self.assertEqual(row["abstention_rate"], 0.5)
        self.assertEqual(row["recorded_violation_rate"], 0.5)

    def test_hash_drift_fails(self):
        path, _ = self.fixture()
        path.write_bytes(path.read_bytes().replace(b"0.1", b"0.2"))
        with self.assertRaisesRegex(DataError, "SHA-256"):
            validate_dataset(self.root)

    def test_truncation_fails(self):
        path, _ = self.fixture()
        path.write_bytes(path.read_bytes()[:-1])
        with self.assertRaisesRegex(DataError, "Byte-count"):
            validate_dataset(self.root)

    def test_schema_drift_fails(self):
        _, manifest = self.fixture()
        manifest["files"][0]["columns"][0] = "unexpected"
        self.manifest(manifest)
        with self.assertRaisesRegex(DataError, "Column mismatch"):
            validate_dataset(self.root)

    def test_row_count_drift_fails(self):
        _, manifest = self.fixture()
        manifest["files"][0]["rows"] = 3
        self.manifest(manifest)
        with self.assertRaisesRegex(DataError, "Row-count"):
            validate_dataset(self.root)

    def test_missing_file_fails(self):
        path, _ = self.fixture()
        path.unlink()
        with self.assertRaisesRegex(DataError, "Missing dataset"):
            validate_dataset(self.root)

    def test_duplicate_manifest_path_fails(self):
        _, manifest = self.fixture()
        manifest["files"].append(dict(manifest["files"][0]))
        self.manifest(manifest)
        with self.assertRaisesRegex(DataError, "Duplicate manifest path"):
            load_manifest(self.root)

    def test_parent_traversal_is_rejected(self):
        with self.assertRaises(DataError):
            scoped_path(self.root, "../outside.csv")

    def test_windows_absolute_path_is_rejected(self):
        with self.assertRaises(DataError):
            scoped_path(self.root, "C:/outside.csv")

    def test_absolute_path_is_rejected(self):
        with self.assertRaises(DataError):
            scoped_path(self.root, "/outside.csv")

    def test_case_duplicate_path_is_rejected(self):
        _, manifest = self.fixture()
        other = dict(manifest["files"][0])
        other["path"] = "DATA/EXAMPLE.csv"
        manifest["files"].append(other)
        self.manifest(manifest)
        with self.assertRaisesRegex(DataError, "Duplicate manifest"):
            load_manifest(self.root)

    def test_unknown_file_name_is_rejected(self):
        self.fixture()
        with self.assertRaises(DataError):
            resolve_file(self.root, "not-in-manifest.csv")

    def test_invalid_manifest_json_is_reported(self):
        (self.root / "DATA_MANIFEST.json").write_text("{bad-json", encoding="utf-8")
        with self.assertRaises(DataError):
            load_manifest(self.root)

    def test_extra_csv_field_is_rejected(self):
        path = self.root / "malformed.csv"
        path.write_text("policy,preference_regret\nalpha,0.2,extra\n", encoding="utf-8")
        with self.assertRaisesRegex(DataError, "Malformed CSV"):
            list(csv_rows(path))

    def test_duplicate_header_is_rejected(self):
        path = self.root / "malformed.csv"
        path.write_text("policy,policy\nalpha,beta\n", encoding="utf-8")
        with self.assertRaisesRegex(DataError, "Invalid CSV header"):
            list(csv_rows(path))

    def test_non_finite_values_are_rejected(self):
        for value in ["nan", "inf", "-inf", "not-a-number"]:
            with self.subTest(value=value), self.assertRaises(DataError):
                finite_number(value, "test metric")

    def test_negative_regret_is_rejected(self):
        path, _ = self.fixture(rows=[{"policy":"alpha", "preference_regret":"-0.2", "selected_backend":"fake_a", "deadline_or_budget_violation":"0", "physical_qpu":"False"}])
        with self.assertRaisesRegex(DataError, "Negative"):
            summarize_replay(path)

    def test_physical_flag_changes_are_rejected(self):
        self.fixture(rows=[{"policy":"alpha", "preference_regret":"0.1", "selected_backend":"real", "deadline_or_budget_violation":"0", "physical_qpu":"True"}])
        with self.assertRaisesRegex(DataError, "physical-device"):
            validate_dataset(self.root)

    def test_duplicate_case_ids_are_rejected(self):
        self.fixture(rows=[{"case_id":"same", "prompt":"a"}, {"case_id":"same", "prompt":"b"}], headers=["case_id", "prompt"])
        with self.assertRaisesRegex(DataError, "duplicate case"):
            validate_dataset(self.root)

    def test_benchmark_inspection_counts_profiles(self):
        path, _ = self.fixture(rows=[{"case_id":"one", "prompt":"Prioritize quality", "gold_profile":"quality_first", "gold_status":"compiled"}],
                              headers=["case_id", "prompt", "gold_profile", "gold_status"])
        result = inspect_benchmark(path)
        self.assertEqual(result["requests"], 1)
        self.assertEqual(result["gold_profiles"], {"quality_first":1})

    def test_summary_refuses_frozen_data_output(self):
        path, _ = self.fixture()
        before = path.read_bytes()
        with self.assertRaisesRegex(DataError, "frozen data"):
            write_summary(self.root, path, summarize_replay(path))
        self.assertEqual(path.read_bytes(), before)

    def test_partial_replay_does_not_invent_zero_violations(self):
        path = self.root / "partial.csv"
        path.write_text("policy,preference_regret\nalpha,0.2\n", encoding="utf-8")
        with self.assertRaisesRegex(DataError, "requires"):
            summarize_replay(path)

    def test_summary_export_has_the_computed_mean(self):
        path, _ = self.fixture()
        output = self.root / "reports" / "result.csv"
        write_summary(self.root, output, summarize_replay(path))
        row = list(csv_rows(output))[0]
        self.assertAlmostEqual(float(row["mean_regret"]), 0.2)

    def test_summary_preserves_existing_report(self):
        path, _ = self.fixture()
        output = self.root / "report.csv"
        output.write_text("existing user work", encoding="utf-8")
        before = output.read_bytes()
        with self.assertRaisesRegex(DataError, "already exists"):
            write_summary(self.root, output, summarize_replay(path))
        self.assertEqual(output.read_bytes(), before)

    def test_summary_force_replaces_report(self):
        path, _ = self.fixture()
        output = self.root / "report.csv"
        output.write_text("old report", encoding="utf-8")
        write_summary(self.root, output, summarize_replay(path), force=True)
        self.assertEqual(list(csv_rows(output))[0]["policy"], "alpha")

    def test_force_cannot_replace_frozen_data(self):
        path, _ = self.fixture()
        before = path.read_bytes()
        with self.assertRaisesRegex(DataError, "frozen data"):
            write_summary(self.root, path, summarize_replay(path), force=True)
        self.assertEqual(path.read_bytes(), before)

    def test_empty_summary_is_rejected(self):
        with self.assertRaisesRegex(DataError, "empty summary"):
            write_summary(self.root, self.root / "empty.csv", [])

    def test_malformed_header_returns_concise_cli_error(self):
        path, manifest = self.fixture()
        raw = b'"unterminated header'
        path.write_bytes(raw)
        manifest["files"][0]["bytes"] = len(raw)
        manifest["files"][0]["sha256"] = hashlib.sha256(raw).hexdigest()
        self.manifest(manifest)
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["--root", str(self.root), "validate"])
        self.assertEqual(code, 2)
        self.assertIn("Cannot read CSV header", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    def test_cli_returns_structured_validation(self):
        self.fixture()
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), "validate"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["csv_files"], 1)

    def test_cli_bad_root_returns_two_without_traceback(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["--root", str(self.root), "validate"])
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", errors.getvalue())

    def test_discovery_does_not_replace_explicit_invalid_root(self):
        with self.assertRaises(DataError):
            discover_root(self.root)

    def test_full_frozen_collection_passes(self):
        result = validate_dataset(REPO)
        self.assertEqual(result["csv_files"], 37)
        self.assertEqual(result["total_rows"], 288113)

    def test_retained_table_points_reconstruct(self):
        result = check_table_points(REPO)
        self.assertEqual(result["reconstructed_point_estimates"], 29)
        self.assertIn("RUN-017 forest points", result["not_recomputed"])


if __name__ == "__main__":
    unittest.main()
