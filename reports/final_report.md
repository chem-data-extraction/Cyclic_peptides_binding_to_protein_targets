# Final report

## Project summary

**Title:** Cyclic peptides binding to protein targets.
**Author:** Kadochnikova Margarita
**Version:** 0.1.0 (2026-05-29)
**Course:** Extraction and preparation of chemical information

## Dataset goal

**Scientific question:** How are the cyclic peptide structure (type of cyclization, amino acid sequence), target protein class (bromodomains, proteases, deacetylases) and binding strength (KD) related?

## Data sources
Defined in `specs/source_map.json`:
| Source | Type |
|--------|------|
| Cyclic peptides can engage a single binding pocket through highly divergent modes (doi: 10.1073/pnas.2003086117) | PDF/Excel |
| Cyclization and Docking Protocol for Cyclic Peptide–Protein Modeling Using HADDOCK2.4 (doi: 10.1021/acs.jctc.2c00075) | PDF |
| A Genetically Encoded, Phage-Displayed Cyclic Peptide Library (doi: 10.1002/anie.201908713) | PDF |
| RCSB PDB (url: https://www.rcsb.org/) | web parsing |

## Data extraction

### PDF/Excel extraction

- **Patel et al. PNAS 2020:** Extract from the Excel file Supporting Information. 9 sheets were processed (BRD3-BD1_R3, BRD3-BD1_R4, BRD3-BD1_R5, BRD3-BD2_R3, BRD3-BD2_R4, BRD3-BD2_R5, BRD4-BD2_R3, BRD4-BD2_R4, BRD4-BD2_R5).
- **Wang et al. Angewandte 2019:** 7 records with KD and IC50 values were extracted.

### Web parsing

- **RCSB PDB:** BeautifulSoup and requests were used to get metadata by PDB ID. Fields are extracted: pdb_id,title,classification,organism,expression_system,method,resolution,deposition_authors,uniprot_id,pdb_doi,status.

### Extraction problems

- The sequences in the Patel data contain `(AcK)` markers that were removed during normalization
- In the Wang data, affinity values are given in µM, converted to nM
- There is no UniProt ID for some PDB records.

## Normalization and cleaning

### Processing steps

1. **Normalization of sequences:** removal of markers `(AcK)`, linkers `CGSGSGSamber`, starting `M`
2. **Reduction of affinity units:** all values are converted to nM
3. **PDB data enrichment:** sequence comparison of peptides with PDB structures
4. **Removing duplicates:** by the combination of `peptide_sequence` + `target_type`

### Normalization examples

| Initial sequence | After normalization |
|-----------------------|-------------------|
| `(AcK)TWLIP(AcK)IR(AcK)TL(AcK)` | `TWLIPIRTL` |
| `CWRDLYIX` | `CWRDLYIX` |
| `CQSLWMMNle` | `CQSLWMMN` |

### Conversion of affinity units

| Initial value | Initial unit | After conversion |
|---------------|--------------|------------------|
| 8.2 | µM | 8200 nM |
| 7.1 | µM | 7100 nM |
| 260 | nM | 260 nM |

## Validation

- Dataset schema: `specs/dataset_schema.json`
- Checking data types and required fields
- All records have the required fields filled in: `record_id`, `peptide_sequence`, `peptide_cyclization_type`, `target_type`, `target_class`, `affinity_value`, `affinity_unit`, `affinity_type`, `source_id`

## Final artifacts

| Artifact | Path |
|----------|------|
| Processed dataset | `data/processed/dataset.csv` |
| Schema | `specs/dataset_schema.json` |
| Source map | `specs/source_map.json` |
| Dataset card | `dataset_card.md` |
| Citation | `CITATION.cff` |
| License | `LICENSE` |
