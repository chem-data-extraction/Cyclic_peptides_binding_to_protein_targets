# Practice 1

## Topic

Cyclic peptides binding to protein targets (cyclic peptides binding to target proteins).

## Scientific task

Collect experimentally reported binding measurements of cyclic peptides with protein targets for comparing affinity values, analyzing the influence of cyclization type, and selecting promising peptide ligands for drug-discovery tasks.

## One-record definition

**One record** = one experimentally measured binding affinity or inhibition value (IC50, Ki, or Kd) of a cyclic peptide with a specific protein target from a specific source (one row in `data/processed/dataset.csv`).

## Examples of records

| Example | Why it counts |
|---------|---------------|
| IC50 = 12.5 nM for cyclic peptide sequence ACDEFGH (head-tail cyclization) against EGFR from Table 2 in Green 2018 | Single measurement + sequence + cyclization type + target + source |
| Kd = 0.5 nM for disulfide-cyclized peptide (Cys3-Cys11) against HER2 from Figure 2B in Brown 2020 | One numeric binding outcome tied to one peptide–target pair |

## Non-record examples

| Example | Why it is not a record |
|---------|-------------------------|
| General review paragraph on phage display or cyclic peptide libraries without numeric binding data | No measurement |
| Full list of 50 peptide sequences without per-sequence affinity | Not one measurement per row (unless split) |
| Predicted docking score without experimental citation | Out of scope if only experimental data allowed |
| "High affinity" or "active in micromolar range" without a specific number | No numeric value |

## Dataset fields

List each schema field and how you will populate it. Update `specs/dataset_schema.json` when fields change.
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

## Ambiguous cases

Document decisions here, for example:

- Multiple affinity values for the same peptide under different buffers / temperatures / pH -> Create separate records for each unique set of conditions. Fields buffer, temperature_C, pH help distinguish them.
- Range reported as "0.1–1 nM" -> Store affinity_value = null, put range in notes (e.g., "Reported as range 0.1–1 nM"). Set normalized_affinity_nm = null.
- Value only shown on a graph (no exact number in text) -> If estimable — set extraction_confidence = low and add note; if not estimable — do not include.
- Same peptide–target pair appears in both paper and database -> Deduplication in Practice 5. Rule: prioritize peer-reviewed paper over database; if values match — keep record with higher extraction_confidence.
- Unit not explicitly stated but clear from context -> Set affinity_unit accordingly, add notes = "Unit inferred from context".
- Cyclization type not described -> Set peptide_cyclization_type = unknown, add notes = "Cyclization type not specified".
- Multiple values for same peptide–target in one paper (e.g., IC50 and Kd) -> Keep both records (different affinity_type).
- Mutated peptide vs wild type -> Keep as separate records with mutations field populated.
