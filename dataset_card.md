# Dataset card — Cyclic peptides binding to protein targets

## Dataset title

Cyclic peptides binding to protein targets (project for the course "Extraction and preparation of chemical information", version 0.1.0)

## Dataset summary

A collection of experimental data on the binding of cyclic peptides to target proteins in tabular format. It includes peptide sequences, type of cyclization, target proteins, affinity values (KD), experimental metadata, and structural information from the PDB.

## Scientific task

Analysis of the relationship between the cyclic peptide structure (type of cyclization, amino acid sequence), target protein class (bromodomains, proteases, deacetylases) and binding strength for the selection of promising cyclic peptide ligands in drug development tasks.

## Record unit

One row = one experimentally measured binding value of a cyclic peptide to a target protein from a specific source.

## Data sources

Defined in `specs/source_map.json`:
| Source | Type |
|--------|------|
| Cyclic peptides can engage a single binding pocket through highly divergent modes (doi: 10.1073/pnas.2003086117) | PDF/Excel |
| Cyclization and Docking Protocol for Cyclic Peptide–Protein Modeling Using HADDOCK2.4 (doi: 10.1021/acs.jctc.2c00075) | PDF |
| RCSB PDB (url: https://www.rcsb.org/) | web parsing |

## Data extraction procedure

1. PDF/Excel: `scripts/extract_pdf_1.py`, `scripts/extract_pdf_2.py`, `scripts/extract_pdf_3.py`, `scripts/extract_xlsx_1.py`  guided by `specs/pdf_extraction_manifest.json`
2. Web: `scripts/extract_web.py` guided by `specs/web_extraction_manifest.json`
3. Logs: `data/extracted/extraction_log.jsonl`

## Data cleaning and normalization

`scripts/build_dataset.py` merges extracts; `scripts/clean_dataset.py` clearing sequences from markers `(AcK)`, linkers `CGSGSGSamber`, starting `M`, reduction of affinity units to nM, omission processing, removal of duplicates and renaming columns per `specs/cleaning_pipeline.json`.

## Dataset schema

Field definitions, types, and examples: `specs/dataset_schema.json`. Final columns in `data/processed/dataset.csv`.

**Main fields:**
- `record_id` is the unique identifier of the record
- `peptide_sequence' — the amino acid sequence of the peptide
- `peptide_cyclization_type' — the type of cyclization (thioether, cyclic, linear, backbone, disulfide)
- `target_type' — name of the target protein
- `target_class' — protein class (bromodomain, protease, deacetylase)
- `affinity_value' — affinity value in nM
- `affinity_type' — measurement type (KD)
- `pdb_id' — PDB structure identifier (if available)
- `structure_resolution` — resolution of the structure in Å
- `source_id` — source identifier

## Validation

Rules in `specs/validation_rules.json`; checks via `scripts/validate_project.py` and `tests/test_required_artifacts.py`.

## Known limitations

- For Patel data (PNAS 2020), the affinity values (KD) are taken from a separate table.
- In the Wang 2019 data, affinity values were initially specified in µM and were converted to nM.
- For records without PDB structures, the fields `pdb_id` and `structure_resolution` remain empty.
- Sequences with non-standard amino acids are stored as is.

## Recommended use

- Training in structured scientific data extraction.
- Analysis of the relationship between the structure of cyclic peptides and their affinity.
- Prototyping of data processing pipelines.
- Benchmarking of linking table parsing methods.

## Not recommended use

- Making clinical decisions.
- Uncritical meta-analysis without checking primary sources.
- Commercial use without checking the source data licenses.

## License

The dataset (data/processed/dataset.csv) is licensed under CC BY 4.0.

The initial data is taken from scientific articles listed in `CITATION.cff'.

When using a dataset, it is necessary to cite both the original articles and this dataset.

## Citation

The file `CITATION.cff' contains the full information for citation.
