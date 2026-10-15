"""Scoped file access and integrity checks. SPDX-License-Identifier: MIT."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath


class DataError(ValueError):
    """The requested data or its manifest is invalid."""


def discover_root(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        root = Path(explicit).resolve()
        if not (root / "DATA_MANIFEST.json").is_file():
            raise DataError("No DATA_MANIFEST.json in the requested data root")
        return root
    for start in [Path.cwd(), Path(__file__).resolve().parents[2]]:
        for candidate in [start, *start.parents]:
            if (candidate / "DATA_MANIFEST.json").is_file():
                return candidate.resolve()
    raise DataError("Data root not found; pass --root /path/to/aura-q-data")


def scoped_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise DataError("Manifest paths must be nonempty POSIX relative paths")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or any(":" in p for p in parts.parts):
        raise DataError("Path escapes the dataset root")
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise DataError("Resolved path escapes the dataset root")
    return candidate


def load_manifest(root: Path) -> dict:
    try:
        value = json.loads((root / "DATA_MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataError("Cannot read a valid DATA_MANIFEST.json") from exc
    if not isinstance(value, dict) or not isinstance(value.get("files"), list) or not value["files"]:
        raise DataError("Manifest must contain a nonempty files list")
    seen = set()
    for item in value["files"]:
        if not isinstance(item, dict):
            raise DataError("Manifest file entry must be an object")
        required = {"path", "bytes", "sha256", "rows", "columns", "kind"}
        if not required.issubset(item):
            raise DataError("Incomplete manifest file entry")
        scoped_path(root, item["path"])
        key = item["path"].casefold()
        if key in seen:
            raise DataError("Duplicate manifest path")
        seen.add(key)
        if not isinstance(item["rows"], int) or item["rows"] < 0:
            raise DataError("Invalid manifest row count")
        if not isinstance(item["bytes"], int) or item["bytes"] < 0:
            raise DataError("Invalid manifest byte count")
        digest = item["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise DataError("Invalid SHA-256 digest")
        columns = item["columns"]
        if not isinstance(columns, list) or not columns or any(not isinstance(c, str) or not c for c in columns):
            raise DataError("Invalid manifest columns")
        if len(set(columns)) != len(columns):
            raise DataError("Duplicate manifest column")
    return value


def resolve_file(root: Path, name: str) -> Path:
    files = load_manifest(root)["files"]
    matches = [x for x in files if x["path"] == name]
    if not matches and "/" not in name and "\\" not in name:
        matches = [x for x in files if PurePosixPath(x["path"]).name == name]
    if len(matches) != 1:
        raise DataError("Choose one file listed in DATA_MANIFEST.json")
    result = scoped_path(root, matches[0]["path"])
    if not result.is_file():
        raise DataError(f"Missing dataset file: {matches[0]['path']}")
    return result


def csv_rows(path: Path):
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise DataError(f"Invalid CSV header: {path.name}")
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise DataError(f"Malformed CSV row {reader.line_num}: {path.name}")
                yield row
    except (OSError, UnicodeError, csv.Error) as exc:
        raise DataError(f"Cannot read CSV: {path.name}") from exc


def finite_number(value: str, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DataError(f"Invalid numeric value in {field}") from exc
    if not math.isfinite(number):
        raise DataError(f"Non-finite numeric value in {field}")
    return number


def validate_dataset(root: Path) -> dict:
    manifest = load_manifest(root)
    total = 0
    for item in manifest["files"]:
        path = scoped_path(root, item["path"])
        if not path.is_file():
            raise DataError(f"Missing dataset file: {item['path']}")
        if path.stat().st_size != item["bytes"]:
            raise DataError(f"Byte-count mismatch: {item['path']}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != item["sha256"]:
            raise DataError(f"SHA-256 mismatch: {item['path']}")
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                header = next(csv.reader(stream, strict=True), [])
        except (OSError, UnicodeError, csv.Error) as exc:
            raise DataError(f"Cannot read CSV header: {path.name}") from exc
        if header != item["columns"]:
            raise DataError(f"Column mismatch: {item['path']}")
        count, case_ids = 0, set()
        for row in csv_rows(path):
            count += 1
            if "case_id" in row:
                if not row["case_id"] or row["case_id"] in case_ids:
                    raise DataError(f"Missing or duplicate case ID: {path.name}")
                case_ids.add(row["case_id"])
            if "physical_qpu" in row and row["physical_qpu"].casefold() != "false":
                raise DataError(f"Unexpected physical-device record: {path.name}")
            if "preference_regret" in row and finite_number(row["preference_regret"], "preference_regret") < -1e-12:
                raise DataError(f"Negative preference regret: {path.name}")
        if count != item["rows"]:
            raise DataError(f"Row-count mismatch: {item['path']}")
        total += count
    return {"status": "PASS", "csv_files": len(manifest["files"]), "total_rows": total,
            "checks": ["SHA-256", "byte counts", "CSV schemas", "row counts",
                       "unique case IDs", "finite nonnegative regret", "simulator flags"]}
