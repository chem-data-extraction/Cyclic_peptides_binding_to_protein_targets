# Practice 3 — PDF extraction

> Align with `specs/pdf_extraction_manifest.json` and `data/extracted/pdf_extracted_records.csv`.

## Selected PDF sources

| source_id | pdf_id | Year (approx.) | Path |
|-----------|--------|----------------|------|
| patel_2020_pnas | patel_2020_pnas_main | 2020 | data/raw/pnas.202003086.pdf |
| sup_charitou_2022_jctc | sup_charitou_2022_jctc_suppl | 2020 | data/raw/cyclization-and-docking-protocol-for-cyclic-peptide-protein-modeling-using-haddock2-4.pdf |
| sup_patel_2020_pnas | patel_2020_pnas_suppl | 2020 | data/raw/pnas.2003086117.sd01.xlsx |

## Why these PDFs were selected

Explain relevance, open access, table quality, and overlap with your research question.
|        PDF	  |       Reason        |
|-----------------|-----------------------------|
| Patel 2020 main | It contains experimental Kd for cyclic peptides (SPR data) - key binding affinity data for the dataset. CC-BY-4.0 license |
| Charitou 2022 supplementary |	It contains 30 cyclic peptide-protein complexes. Complements it with structural data |
| Patel 2020 supplementary (Excel) |	contains complete peptide sequences (Dataset S1-S5) and raw sequencing data |

## Pages used

List page numbers per PDF and what appears on each (tables, figures, methods).

| PDF |	   Pages   |         What is contained      |
|-----|------------|-----------------------------|
| Patel 2020 main |	Fig. 1B, 4B, 5D	| Tables of Kd values (SPR) |
| Charitou 2022 supplementary | Table S1-S2	 | List of 30 PDB IDs and cyclization types |
| Patel 2020 suppl (Excel) |	Dataset S1-S5	| Full sequences, counts, frequencies |

## Extraction methods

Tools considered: PyMuPDF, pdfplumber, Camelot, Tabula, manual entry. What you actually used and why.

| Source |	Tool	  |         Reason              |
|--------|------------|-----------------------------|
| Patel 2020 main | 	pdfplumber + regex	| Kd data embedded in text, not in tables with borders |
| Charitou 2022 suppl	| camelot (lattice mode)	| Tables S1-S2 have clearly drawn borders; Camelot extracts them directly |
| Patel 2020 suppl	| pandas.read_excel() |	Excel file, not PDF |

Two different approaches were used:
1. Camelot — for PDFs with drawn table borders (Charitou)
2. pdfplumber — for PDFs without tables or with text-based data (Patel main)


## Extracted fields

Map PDF content to schema fields. Note manual corrections.

From Patel 2020 main (kd_values.csv):

| CSV field	| Source in PDF |	Example            |
|-----------|---------------|----------------------|
| peptide	| Figure 1A, 4A, 5C (peptide labels)| 	3.1B |
| target	| Table rows (BRD3-BD1, BRD4-BD1, etc.) |	BRD3-BD1 |
|   kd_nM	| Text pattern number ± number |	0.25 |
| error_nM	| Text pattern number ± number	| 0.05 |
|   page	| Page number where data found |	3 |

From Charitou 2022 suppl (charitou_peptides.csv):

| CSV field |	Source in PDF (Table S1/S2) |	Example |
|-----------|-------------------------------|-----------|
| pdb_id	|               Column 1    	|   3wne    |
| peptide_sequence	| Column 5 (Sequence)	|  PKIDNG   |
| peptide_length	|   Column 2	        |    6      |
| structure_resolution	|   Column 4	  |     1.70    |
| peptide_cyclization_type	| Assigned from table type | 	backbone (head-to-tail) / disulfide |
| source_id	| Hardcoded	|charitou_2022 |
| doi	| Hardcoded	| 10.1021/acs.jctc.2c00075 |

From Patel 2020 suppl (Excel):

| CSV field	|         Source in Excel	    | Example   |
|-----------|-------------------------------|-----------|
| record_id	| Generated from target, round, ORF	| rec_patel_BRD3-BD1_R3_orf0002_0001 |
| peptide_sequence |	Peptide column |	(AcK)TWLIP(AcK)IR(AcK)TL(AcK) |
| peptide_cyclization_type	| Assigned (thioether macrocycle) |	thioether |
| target_type	| Target name from selection |	BRD3-BD1 |
| target_class	| Protein family |	bromodomain |
| affinity_unit	| Assigned (no value in Excel)	| nM |
| affinity_type	| Assigned	| KD |
| source_id	| Hardcoded	| paper_patel_pnas_2020 |
| extraction_method	| Method used	| excel_import |
| method	| Assay type (from article)	| SPR |
| notes	| Round, ORF, reads	| RaPID selection round 3 against BRD3-BD1. ORF2: reads=12, proportion=None% |

## Extraction problems

Scanned PDFs, merged cells, units in captions, ambiguous sequences, etc.

|         Problem	            | Solution  |
|-------------------------------|-----------|
| Kd values embedded in text, not tables	| Used pdfplumber + regex pattern (\d+\.?\d*)\s*±\s*(\d+\.?\d*) |
| Missing table borders in Patel PDF |	Could not use Camelot; switched to pdfplumber |
| Merged cells in Charitou tables	| Camelot lattice mode handled them correctly |
| Non-standard amino acids (AcK)	| Preserved as (AcK) in sequences |
| Inconsistent resolution format	| Used regex (\d+\.\d{2}) to extract float |
| Excel file (.xlsx) not a PDF	 | Used pandas.read_excel() instead of PDF tools |

## Output files

| File	| Path	| Description|
|-------|------------|-----------|
| Extracted records (Patel Kd)	| data/extracted/kd_values.csv	| 23 Kd records with peptide, target, value, error |
| Extracted records (Charitou)	| data/extracted/charitou_peptides.csv	| 30 PDB records with sequences, resolution, cyclization type |
| Extraction log |	data/extracted/extraction_log.jsonl	| JSONL with timestamp, status, records
| Raw PDFs	| data/raw/	| Original PDF and Excel files |
