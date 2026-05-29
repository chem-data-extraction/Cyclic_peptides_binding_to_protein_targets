# Cyclic peptides binding to protein targets (cyclic peptides binding to target proteins).

## System description
Cyclic peptides and peptide-like macrocycles that bind protein targets. The system includes the cyclic ligand, the target protein, the binding assay, and the measured affinity or inhibition value.

## Planned use of the collected dataset
The dataset will be used to analyze how cyclic peptide structure and target class relate to binding strength, with the goal of selecting promising cyclic peptide ligands for drug-discovery tasks.

## Scientific task

Collect experimentally confirmed measurements of the binding of cyclic peptides to target proteins: peptide sequences, target proteins, affinity values (KD, IC50), type of cyclization, experimental conditions, structural data from the PDB.

## What is one record?

One **record** = one experimental value of the binding (KD or IC50) of a cyclic peptide to a target protein from a specific source. Matches one line in `data/processed/dataset.csv'.

## Repository structure

| Path | Role |
|------|------|
| `project.json` | Machine-readable project metadata |
| `specs/` | JSON schemas, source map, manifests, pipeline, validation rules |
| `data/raw/` | Unmodified PDFs, web snapshots, external exports |
| `data/extracted/` | Extraction outputs (CSV + `extraction_log.jsonl`) |
| `data/interim/` | Merged table before final cleaning |
| `data/processed/` | Publication dataset (`dataset.csv`) |
| `scripts/` | Reproducible extract, build, clean, validate |
| `reports/` | Human-readable practice and final reports |
| `notebooks/` | Optional exploration only |
| `tests/` | Pytest checks for required artifacts |

**Formats:** JSON for specs and manifests; CSV for tabular data; Python for pipelines; Markdown for reports and documentation only. Notebooks are optional.

## Data pipeline

```text
raw (PDF / web / external)
  → extract (pdf + web scripts) → data/extracted/*.csv
  → build (merge) → data/interim/merged_records.csv
  → clean → data/processed/dataset.csv
  → validate (rules + pytest)
```

## Required final artifacts

- `data/processed/dataset.csv` aligned with `specs/dataset_schema.json`
- Updated `specs/source_map.json` and extraction manifests
- Practice reports 1–5 and `reports/final_report.md`
- `dataset_card.md`, `LICENSE`, `CITATION.cff`
- Passing validation and tests

## How to run validation

```bash
pip install -r requirements.txt
python scripts/validate_project.py
pytest
```

## How to build the dataset

```bash
python scripts/build_dataset.py    # merge extracts → interim + processed
python scripts/clean_dataset.py    # normalize and write processed dataset
```

Placeholder extraction (no PDF/HTML libraries required):

```bash
python scripts/extract_pdf.py
python scripts/extract_web.py
```

## License and citation

- Replace the placeholder in **`LICENSE`** before publication (e.g. CC-BY-4.0 or CC0-1.0, subject to upstream source licenses).
- Fill in **`CITATION.cff`** with authors, version, and repository URL.
- Summarize the dataset for users in **`dataset_card.md`**.
