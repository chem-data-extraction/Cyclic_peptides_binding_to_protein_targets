# Practice 2 — Source map

## Source search strategy

| Database | Purpose | Priority
|----------|---------|---------|
| PubMed | Main source of scientific articles on peptides and proteins | high |
| Google Scholar | Review articles | high |
| ChEMBL | Structured affinity data, API access | high |
| BindingDB | Experimental binding measurements, API access | high |
| PDB (RCSB) | 3D structures of peptide-protein complexes | high |
| GitHub | Open datasets (CPSea, cPEPmatch, Cyclic-peptide-benchmark) | medium |
| Zenodo / Figshare | Datasets and supplementary materials | medium |
| Kaggle | Competition datasets | low |

## Source groups

Summarize each group in `source_map.json`:

- apis
- datasets
- scientific_papers
- supplementary_materials
- github_repositories
- aggregators
- review_articles

## Priority sources

Rank sources by reliability, license, and expected yield. Which will you extract first?

|Priority | Group | Source | What we extract | Justification |
|---------|--------|----------|---------------|------------|
| 1 | APIs	|  ChEMBL API	|  affinity_value, affinity_unit, affinity_type, target_type	|  Structured data, API access, reliable |
| 1	| APIs	|  BindingDB API	|  peptide_sequence, affinity_value, affinity_unit, target_name	|  Filter by macrocycle, experimental measurements |
| 1	| APIs	|  PDB (RCSB) API	|  peptide_sequence, structure_resolution, cyclization_positions	|  Experimental 3D structures, gold standard |
| 2	| Papers |  PubMed (DOI)	|  cyclization_type, mutations, pH, temperature, buffer, method	|  Experimental details not in databases |
| 2	| Supplementary	|  DOI links, journal sites	|  XLSX, CSV, PDF tables with affinities	|  Often contain raw untransformed data |
| 3	| GitHub	|  CPSea	|   Predicted structures, large-scale cyclic peptide data	|  Large volume but predicted, needs validation |
| 3	| GitHub	|  cPEPmatch  | 	Experimental crystal structures, cyclization types | 432+ structures, MIT license, curated |
| 3	| GitHub	|  Cyclic-peptide-benchmark | Validated docking benchmarks |	Backbone + disulfide sets, ready for ML |
| 4	| Reviews	|  Nature Reviews, Chemical Reviews	| Target lists, references to key papers, method summaries | Metadata only, no direct affinity values |
| 5	| Benchmarks	|  Kaggle, PDBbind	| Competition datasets, training benchmarks |	Require verification, potential quality issues |

## Access conditions

Note paywalls, registration, API keys, and institutional access. Record `access_status`, `access_method`, and `access_date` per source.


| Source  |	Access status |	Access method |	Access date |	Notes |
|---------|---------------|---------------|-------------|---------|
| ChEMBL API | 	Open	|  REST API (no key required) | 	2026-05-28	Rate limits apply |
| BindingDB API | 	Open	 | 	REST API (key optional)	 | 	2026-05-28	 | 	Registration recommended |
| PDB (RCSB) API | 	Open	 | 	REST API, GraphQL	 | 	2026-05-28	 | 	No key required, fair use |
| PubMed | 	Open (abstracts)	 | 	Entrez API, DOI	2026-05-28	 | 	Full text via institutional access |
| Google Scholar | 	Open (metadata)	Manual search	 | 	2026-05-28	 | 	No official API |
| CPSea | 	Open | 	GitHub (clone)	 | 	2026-05-28	 | 	MIT license |
| cPEPmatch	|  Open	GitHub (clone) | 		2026-05-28	 | 	MIT license |
| Zenodo | 	Open | 	 REST API	 | 	2026-05-28	 | 	No key required |
| PDBbind | 	Restricted	 | 	Registration required	| 2026-05-28 |	Academic license, email request |
| Nature Reviews | 	Paywall	Institutional access	| 2026-05-28 |	Only abstracts open |

## Expected data types

Tables, figures, HTML tables, CSV dumps, API JSON, etc.

| Source  |	Data types    |
|---------|---------------|
| ChEMBL API	|  JSON (assay, activity, target, molecule) |
| BindingDB API	|  JSON, CSV export |
| PDB (RCSB) API	|  PDB, mmCIF, FASTA, JSON (metadata) |
| PubMed	| HTML (abstract), XML (Entrez), PDF (full text) |
| Supplementary files	 XLSX, CSV, PDF (tables), DOCX |
| GitHub |  CSV, Jupyter notebooks, Python scripts, JSON
| Zenodo/Figshare	|  CSV, JSON, ZIP archives |
| Kaggle	|  CSV, Parquet |

## Expected conflicts and overlaps

Example: database Kd may disagree with primary paper — which wins? Document resolution rules.

Affinity value mismatch — Database Kd may differ from primary paper

Sequence representation — Modified residues (AcK, N-Me, D-amino acids)

Cyclization type — thioether vs disulfide vs backbone

Target naming — UniProt ID vs common name vs gene symbol

Units — nM vs µM vs pM


Resolution rules:
Conflict	Resolution
Database vs paper affinity	Paper wins (primary source, extraction_confidence = high)
Multiple papers, same peptide	Take most recent or best resolved structure
Affinity type mismatch (Kd vs IC50)	Kd preferred for binding affinity
Unit inconsistency	Normalize to nM
Target name mismatch	Map to standard via source_map.json aliases
Cyclization type unclear	Infer from sequence (CxxC → disulfide, AcK/lan → thioether)



Overlap handling:
FIELD_PRIORITY = {
    "affinity_value": ["paper", "bindingdb", "chembl"],
    "peptide_sequence": ["pdb", "paper", "bindingdb"],
    "cyclization_type": ["pdb", "paper", "cpepmatch"],
    "method": ["paper", "chembl"],
    "structure_resolution": ["pdb"]
}


## Coverage gaps

Targets, assay types, or years missing from your map. Plan follow-up searches or justify exclusions.

Less missing:

| Field	| Coverage	| Sources |
|-------|-----------|---------|
| affinity_value	| High	| ChEMBL, BindingDB, PDBbind |
| peptide_sequence |	High |	PDB, ChEMBL, papers |
| target_type / target_class |	High |	ChEMBL, UniProt |
| 3D structure	| High |	PDB, CPSea, cPEPmatch |
| source_id / doi	| High |	All sources |
| peptide_length	| High	| PDB (calculated), papers |
| structure_resolution	| High	| PDB |

Moderate missing:
| Field	| Coverage	| Sources |
|-------|-----------|---------|
| peptide_cyclization_type	| Medium	| PDB (REMARK), papers, cPEPmatch |
| method (SPR/ITC/FP)	| Medium	| ChEMBL (assay_type), papers |
| temperature_C	| Medium	| Papers |
| pH	| Medium	| Papers |
| buffer	| Medium	| Papers |

Most missing:
| Field	| Coverage	| Recovery plan |
|-------|-----------|---------------|
| cyclization_positions	| Low	| Parse PDB CONECT records, manual from papers |
| mutations	| Low	| Extract from paper methods section |
| binding_mode / contacts	| Low	| Calculate from PDB (PyMOL, MD analysis) |
| experimental details (pH, T)	| Low	| Prioritize papers with rich supplements |
| affinity_error / error_nM	| Low	| Extract from papers with reported SD/SEM |
