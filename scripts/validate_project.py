#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "project.json",
    "specs/dataset_schema.json",
    "specs/source_map.json",
    "specs/pdf_extraction_manifest.json",
    "specs/web_extraction_manifest.json",
    "specs/cleaning_pipeline.json",
    "specs/validation_rules.json",
    "data/extracted/pdf_extracted_records.csv",
    "data/extracted/wang_2019_auto.csv",
    "data/extracted/charitou_peptides.csv",
    "data/extracted/rcsb_metadata.csv",
    "data/extracted/kd_values.csv",
    "data/processed/dataset.csv",
    "scripts/build_dataset.py",
    "scripts/clean_dataset.py"
]

CONFIDENCE_ALLOWED = {"", "high", "medium", "low", "unknown"}
AFFINITY_TYPES_ALLOWED = {"KD", "IC50", "Ki", ""}
AFFINITY_UNITS_ALLOWED = {"nM", "µM", "pM", "M", ""}
CYCLIZATION_TYPES_ALLOWED = {
    "", "thioether", "cyclic", "linear", "head-to-tail",
    "backbone (head-to-tail)", "disulfide", "side-chain", "unknown"
}
TARGET_CLASSES_ALLOWED = {
    "", "bromodomain", "protease", "deacetylase", "kinase",
    "hydrolase", "transferase", "unknown"
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def schema_field_names(schema: dict) -> list[str]:
    return [field["name"] for field in schema["fields"]]


def source_ids_from_map(source_map: dict) -> set[str]:
    ids: set[str] = set()
    for group_sources in source_map.get("source_groups", {}).values():
        for entry in group_sources:
            sid = entry.get("source_id")
            if sid:
                ids.add(sid)
    return ids


def check_required_files(root: Path = ROOT) -> list[str]:
    issues = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(f"Missing required file: {rel}")
    return issues


def check_json_parseable(root: Path = ROOT) -> list[str]:
    issues = []
    for path in root.rglob("*.json"):
        if ".pytest_cache" in path.parts or "venv" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            load_json(path)
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON: {path.relative_to(root)} ({exc})")
    return issues


def load_dataset(root: Path = ROOT) -> pd.DataFrame:
    path = root / "data/processed/dataset.csv"
    return pd.read_csv(path, low_memory=False)


def check_dataset_columns(df: pd.DataFrame, schema: dict) -> list[str]:
    expected = schema_field_names(schema)
    actual = list(df.columns)
    issues = []
    if actual != expected:
        missing = set(expected) - set(actual)
        extra = set(actual) - set(expected)
        if missing:
            issues.append(f"Missing columns: {missing}")
        if extra:
            issues.append(f"Extra columns not in schema: {extra}")
    return issues


def check_record_id(df: pd.DataFrame) -> list[str]:
    issues = []
    if df["record_id"].isna().any() or (df["record_id"].astype(str).str.strip() == "").any():
        issues.append("record_id contains null or empty values")
    if df["record_id"].duplicated().any():
        dupes = df.loc[df["record_id"].duplicated(), "record_id"].tolist()
        issues.append(f"Duplicate record_id values: {dupes[:10]}")
    return issues


def check_peptide_sequence(df: pd.DataFrame) -> list[str]:
    issues = []
    allowed_chars = set("ACDEFGHIKLMNPQRSTVWYX")
    for idx, val in df["peptide_sequence"].items():
        if pd.isna(val) or val == "":
            issues.append(f"peptide_sequence empty at row {idx}")
            continue
        seq_str = str(val).upper()
        invalid = set(seq_str) - allowed_chars
        if invalid:
            issues.append(f"peptide_sequence contains invalid chars {invalid} at row {idx}")
    return issues


def check_peptide_cyclization_type(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["peptide_cyclization_type"].items():
        if pd.isna(val):
            issues.append(f"peptide_cyclization_type empty at row {idx}")
            continue
        if str(val) not in CYCLIZATION_TYPES_ALLOWED:
            issues.append(f"Unexpected peptide_cyclization_type '{val}' at row {idx}")
    return issues


def check_target_class(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["target_class"].items():
        if pd.isna(val):
            issues.append(f"target_class empty at row {idx}")
            continue
        if str(val) not in TARGET_CLASSES_ALLOWED:
            issues.append(f"Unexpected target_class '{val}' at row {idx}")
    return issues


def check_source_id(df: pd.DataFrame, source_map: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    valid_ids = source_ids_from_map(source_map)

    if df["source_id"].isna().any() or (df["source_id"].astype(str).str.strip() == "").any():
        errors.append("source_id contains null or empty values")

    unknown = set(df["source_id"].dropna().astype(str)) - valid_ids
    if unknown:
        warnings.append(f"source_id not in source map: {sorted(unknown)}")
    return errors, warnings


def check_affinity_value(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["affinity_value"].items():
        if pd.isna(val) or val == "":
            issues.append(f"affinity_value empty at row {idx}")
            continue
        try:
            float(val)
            if float(val) < 0:
                issues.append(f"affinity_value negative at row {idx}: {val}")
        except (TypeError, ValueError):
            issues.append(f"affinity_value not numeric at row {idx}: {val!r}")
    return issues


def check_affinity_type(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["affinity_type"].items():
        if pd.isna(val) or val == "":
            issues.append(f"affinity_type empty at row {idx}")
            continue
        if str(val) not in AFFINITY_TYPES_ALLOWED:
            issues.append(f"Unexpected affinity_type '{val}' at row {idx}")
    return issues


def check_affinity_unit(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["affinity_unit"].items():
        if pd.isna(val) or val == "":
            issues.append(f"affinity_unit empty at row {idx}")
            continue
        if str(val) not in AFFINITY_UNITS_ALLOWED:
            issues.append(f"Unexpected affinity_unit '{val}' at row {idx}")
    return issues


def check_extraction_confidence(df: pd.DataFrame) -> list[str]:
    warnings = []
    if "extraction_confidence" not in df.columns:
        return warnings
    for val in df["extraction_confidence"].fillna("").astype(str):
        if val.lower() not in CONFIDENCE_ALLOWED and val not in CONFIDENCE_ALLOWED:
            warnings.append(f"Unexpected extraction_confidence: {val!r}")
            break
    return warnings


def check_structure_resolution(df: pd.DataFrame) -> list[str]:
    issues = []
    for idx, val in df["structure_resolution"].items():
        if pd.isna(val) or val == "":
            continue
        try:
            res = float(val)
            if res < 0 or res > 100:
                issues.append(f"unrealistic structure_resolution at row {idx}: {res} Å")
        except (TypeError, ValueError):
            issues.append(f"structure_resolution not numeric at row {idx}: {val!r}")
    return issues


def check_uniprot_id(df: pd.DataFrame) -> list[str]:
    warnings = []
    for idx, val in df["uniprot_id"].items():
        if pd.isna(val) or val == "":
            continue
        if not re.match(r'^[A-Z0-9]{6,10}$', str(val)):
            warnings.append(f"uniprot_id format unusual at row {idx}: {val}")
    return warnings


def validate(root: Path = ROOT) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_required_files(root))
    errors.extend(check_json_parseable(root))

    dataset_path = root / "data/processed/dataset.csv"
    if not dataset_path.is_file():
        errors.append("Dataset not found. Run build and clean scripts first.")
        return errors, warnings

    schema_path = root / "specs/dataset_schema.json"
    if not schema_path.is_file():
        errors.append("Schema not found")
        return errors, warnings

    source_map_path = root / "specs/source_map.json"
    if not source_map_path.is_file():
        errors.append("Source map not found")
        return errors, warnings

    schema = load_json(schema_path)
    source_map = load_json(source_map_path)
    df = load_dataset(root)

    errors.extend(check_dataset_columns(df, schema))
    errors.extend(check_record_id(df))
    errors.extend(check_peptide_sequence(df))
    errors.extend(check_peptide_cyclization_type(df))
    errors.extend(check_target_class(df))
    errors.extend(check_affinity_value(df))
    errors.extend(check_affinity_type(df))
    errors.extend(check_affinity_unit(df))
    errors.extend(check_structure_resolution(df))

    src_errors, src_warnings = check_source_id(df, source_map)
    errors.extend(src_errors)
    warnings.extend(src_warnings)
    warnings.extend(check_extraction_confidence(df))
    warnings.extend(check_uniprot_id(df))

    return errors, warnings


def main() -> int:
    errors, warnings = validate()
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())