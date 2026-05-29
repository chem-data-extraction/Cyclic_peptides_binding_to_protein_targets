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

## Schema alignment

The dataset follows the schema defined in `specs/dataset_schema.json`. Key fields:

|  Field  |      How to populate    |
|---------|-------------------------|
| record_id	| Generate unique ID per record: rec_pep_egfr_2025_001 |
| peptide_sequence	|  Extract from paper/table; single-letter code, uppercase |
| peptide_cyclization_type	|   Determine from description: head-tail, disulfide, side-chain; if not specified - unknown |
| target_type	|   Extract protein target name; standardize (EGFR, HER2, PD-L1) |
| target_class_sequence 	|   Extract from paper if target fragment is specified; if not - null |
| target_class	|   Determine by protein type: kinase, protease, receptor, GPCR, ion_channel |
| affinity_value	|   Extract numeric value; if range is given - use null + note in notes |
| affinity_unit 	|   Extract unit: nM, µM, pM; standardize format |
| affinity_type	 |   Determine measurement type: IC50, Ki, Kd |
| source_id 	|   Use ID from specs/source_map.json, e.g., paper_green_2018 |
| source_type	|   Specify: scientific_paper, database, patent, thesis |
| source_url	|   Insert DOI or source page link; if not available - null |
| doi	|   Insert DOI if available; if not - null |
| extraction_method	 |   Specify: pdf_table, pdf_text, manual_curation, api; if unknown - null |
| extraction_confidence 	|   Rate: high (clear numbers in table), medium (extracted from text/figure), low (estimated), unknown |
| method	|    Extract method: SPR, ITC, fluorescence, AlphaScreen; if not specified - null |
| cyclization_positions 	|   Extract from text or scheme; example: "1-16", "Cys3-Cys11"; if not specified - null |
| temperature_C	 |   Extract numeric value; if not specified - null |
| pH	|   Extract numeric value; if not specified - null |
| buffer	|   Extract buffer composition; if not specified - null |
| mutations	 |   Extract mutation description; if no mutations - null |
| notes 	|   Add notes: range instead of exact number, inferred units, author caveats, etc. |

## Regeneration

- Regenerate this file from scripts; avoid hand-editing except for small template fixes during setup.
- Run `python scripts/build_dataset.py` to merge extracts -> `data/interim/merged_records.csv`.
- Run `python scripts/clean_dataset.py` to produce `data/processed/dataset.csv`
- Run `python scripts/validate_project.py` to validate the final dataset.

## Versioning
- Current version: 0.1.0 (2026-05-29)


