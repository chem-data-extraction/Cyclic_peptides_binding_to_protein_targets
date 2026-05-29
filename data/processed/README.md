# Processed data

This folder holds the **publication-ready** dataset: one row per record, columns aligned with `specs/dataset_schema.json`.

## Main file

- `dataset.csv` — final dataset produced by `scripts/build_dataset.py` and `scripts/clean_dataset.py`, validated with `scripts/validate_project.py`

## Data sources
Defined in `specs/source_map.json`:
| Source | Type |
|--------|------|
| Cyclic peptides can engage a single binding pocket through highly divergent modes (doi: 10.1073/pnas.2003086117) | PDF/Excel |
| Cyclization and Docking Protocol for Cyclic Peptide–Protein Modeling Using HADDOCK2.4 (doi: 10.1021/acs.jctc.2c00075) | PDF |
| A Genetically Encoded, Phage-Displayed Cyclic Peptide Library (doi: 10.1002/anie.201908713) | PDF |
| RCSB PDB (url: https://www.rcsb.org/) | web parsing |

## Guidelines

- Regenerate this file from scripts; avoid hand-editing except for small template fixes during setup.
- Before submission, replace example rows with your project records.
- Record the dataset version or commit hash in `reports/final_report.md` and `dataset_card.md`.
