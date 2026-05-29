# Practice 5 — Cleaning, normalization and publication

> Follow `specs/cleaning_pipeline.json`. Run `scripts/clean_dataset.py` and `scripts/validate_project.py`.

## Input files

| Файл |	Описание |
|------|-------------|
| data/extracted/pdf_extracted_records.csv |	AcK sequences of peptides from Excel Patel 2020 |
| data/extracted/web_extracted_records.csv	| PDB metadata from RCSB PDB web parsing |
| data/extracted/kd_values.csv	| Kd values from the main PDF of Patel 2020 |
| data/extracted/charitou_peptides.csv |	30 Cyclic Peptide Structures from Charitou 2022 |
| data/extracted/rcsb_metadata.csv	| RCSB PDB metadata (resolution, method, name) |
| data/extracted/wang_2019_auto.csv	| 7 Kd values from Wang 2019 |
| data/interim/merged_records.csv	| Intermediate merged file (created by the build script) |

## Cleaning steps

Walk through each step in `specs/cleaning_pipeline.json`: merge, units, sequences, missing values, deduplication, validation, export.
All sources are combined using scripts/build_dataset.py according to the following strategy:

1. Main table: pdf_extracted_records.csv (47609 AcK sequences from Excel Patel 2020)
2. Structural data (charitou_peptides.csv): combined according to the purified peptide sequence
3. Web metadata (rcsb_metadata.csv): combined by PDB ID
4. Kd data (kd_values.csv): combined by target type (BRD2-BD1, BRD3-BD1, etc.)
5. Wang 2019 data: added as separate records with source_id = 'wang_2019'

## Normalization rules

Document unit → nM conversion, sequence uppercase rules, and missing-value tokens.
|Исходная единица	| Нормализованная единица	| Преобразование |
|------|-------------|-----------|
| μM (из Wang 2019)	| nM	| × 1000 |
| nM (из Patel 2020)	| nM	| без изменений |
| Å (ангстремы)	| Å	| без изменений |

## Deduplication strategy

Keys used to define duplicates (e.g. `record_id`, or sequence + target + value + source_id).

1. Primary key: record_id (unique for each source)
2. For Kd values: checking duplicates by (peptide, target, source_id)
3. For AcK sequences: duplicates are deleted based on the exact peptide_sequence match

## Validation results

List errors and warnings.

Launch scripts/validate_project.py for verification purposes:
1. Availability of required columns
2. Absence of null values in required fields
3. Correctness of data types

## Final dataset description

Row count, targets covered, date built, path: `data/processed/dataset.csv`.

## Publication readiness checklist

dataset.csv corresponds to specs/dataset_schema.json
All source_ids are documented in the source map
LICENSE — CC-BY-4.0
CITATION.cff is filled in — authors, version, DOI are required
dataset_card.md updated — requires a description of the dataset
reports/final_report.md completed
