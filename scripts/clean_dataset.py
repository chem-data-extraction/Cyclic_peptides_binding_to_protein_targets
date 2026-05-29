#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def normalize_sequence(seq: str) -> str:
    if pd.isna(seq):
        return ""
    seq = str(seq)
    seq = re.sub(r'\([^)]+\)', '', seq)
    seq = re.sub(r'C?GSGSGSamber$', '', seq)
    seq = re.sub(r'C?GSGSGS$', '', seq)
    seq = re.sub(r'amber$', '', seq)
    seq = re.sub(r'^M', '', seq)
    seq = re.sub(r'[^A-ZX]', '', seq)
    return seq.upper()

def normalize_affinity_value(value, source_id: str, original_unit: str = "") -> tuple:
    if pd.isna(value) or value == "":
        return "", ""
    try:
        val = float(value)
    except (ValueError, TypeError):
        return "", ""
    if source_id == "wang_2019":
        return val * 1000, "nM"
    else:
        return val, "nM"

def determine_cyclization_type(row) -> str:
    source_id = row.get("source_id", "")
    ligand = row.get("ligand", "")
    pep_name = row.get("peptide_name", "")
    if source_id == "paper_patel_pnas_2020":
        return "thioether"
    elif source_id == "wang_2019":
        if "Cyc" in str(ligand) or "Cyc" in str(pep_name):
            return "cyclic"
        elif "Lin" in str(ligand) or "Lin" in str(pep_name):
            return "linear"
    elif source_id == "charitou_2022":
        return row.get("peptide_cyclization_type", "unknown")
    return "unknown"

def determine_target_class(target_type: str) -> str:
    if pd.isna(target_type):
        return "unknown"
    target = str(target_type)
    if "BRD" in target:
        return "bromodomain"
    elif "TEV" in target:
        return "protease"
    elif "HDAC" in target:
        return "deacetylase"
    else:
        return "unknown"

def main():
    input_path = ROOT / "data/interim/merged_records.csv"
    output_path = ROOT / "data/processed/dataset.csv"
    
    if not input_path.exists():
        return
    
    df = pd.read_csv(input_path, low_memory=False)
    
    df["peptide_sequence"] = df["peptide_sequence"].apply(normalize_sequence)
    
    df = df[df["peptide_sequence"].notna()]
    df = df[df["peptide_sequence"] != ""]
    
    normalized_affinity = []
    for idx, row in df.iterrows():
        val, unit = normalize_affinity_value(
            row.get("affinity_value"), 
            row.get("source_id", ""),
            row.get("affinity_unit", "")
        )
        normalized_affinity.append(val)
    df["affinity_value"] = normalized_affinity
    df["affinity_unit"] = "nM"
    
    df["peptide_cyclization_type"] = df.apply(determine_cyclization_type, axis=1)
    df["target_class"] = df["target_type"].apply(determine_target_class)
    
    df["target_class_sequence"] = df["target_class_sequence"].fillna("")
    df["cyclization_positions"] = df["cyclization_positions"].fillna("")
    df["temperature_C"] = df["temperature_C"].fillna("")
    df["pH"] = df["pH"].fillna("")
    df["buffer"] = df["buffer"].fillna("")
    df["mutations"] = df["mutations"].fillna("")
    df["method"] = df["method"].fillna("")
    df["source_type"] = df["source_type"].fillna("")
    df["source_url"] = df["source_url"].fillna("")
    df["doi"] = df["doi"].fillna("")
    df["extraction_method"] = df["extraction_method"].fillna("")
    df["notes"] = df["notes"].fillna("")
    
    df = df.drop_duplicates(subset=["peptide_sequence", "target_type", "source_id"], keep="first")
    
    columns = [
        "record_id", "peptide_sequence", "peptide_cyclization_type",
        "target_type", "target_class_sequence", "target_class",
        "affinity_value", "affinity_unit", "affinity_type",
        "source_id", "source_type", "source_url", "doi",
        "extraction_method", "extraction_confidence", "method",
        "cyclization_positions", "temperature_C", "pH", "buffer",
        "mutations", "structure_resolution", "uniprot_id", "notes"
    ]
    
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    
    df = df[columns]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

if __name__ == "__main__":
    main()