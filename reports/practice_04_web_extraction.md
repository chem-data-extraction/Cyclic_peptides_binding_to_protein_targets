# Practice 4 — Web extraction

## Selected web sites

| source_id | page_id | URL |
|-----------|---------|-----|
| db_rcsb_pdb | pdb_entry_details | https://www.rcsb.org/structure/{pdb_id} |

## Why these sites were selected

Structured data, license, complement to PDFs, update frequency.

Classic web parsing with requests + BeautifulSoup was used.
1. Structured HTML with consistent IDs - PDB pages have a predictable structure with unique IDs for each element.
2. Open access, no login required — All pages are publicly available, no API key or authorization required.
3. License - PDB data in the public domain (CC0).

## Page structure

Describe HTML layout: tables, pagination, JSON-LD, iframes.
Page https://www.rcsb.org/structure/3WNE It has the following elements:
|          HTML-element         |	 What it contains    |	   Code      |
|-------------------------------|------------------------|---------------|
| <span id="structureTitle">	|   Structure name	     | soup.find('span', id='structureTitle') |
| <li id="header_classification"> |	Classification (type of protein) |	soup.find('li', id='header_classification') |
| <li id="header_organism">	| Source organism	| soup.find('li', id='header_organism') |
| <li id="header_expression-system">	| Expression system	soup.find('li', id='header_expression-system') |
| <li id="exp_details_0_method"> |	Experimental method (X-ray, Cryo-EM) |	soup.find('li', id='exp_details_0_method') |
| <li id="exp_details_0_diffraction_resolution"> |	Resolution in Å	| soup.find('li', id='exp_details_0_diffraction_resolution') |
| <li id="header_deposition-authors">	| Authors of the deposit	| soup.find('li', id='header_deposition-authors') |
| <a href="...P\d+...">	| Uniprot ID	| soup.find('a', href=re.compile(...)) |
| <li id="header_doi">	| DOI structures |	soup.find('li', id='header_doi') |

## Extraction methods

Tool (`requests`, `BeautifulSoup`, etc.), selectors from manifest `parser_plan`, rate limits, `robots.txt` notes.
| Parameter  |	Value      |
|------------|-------------|
| Tools |	requests + BeautifulSoup (Python) | 
| Request Headers |	User-Agent (to avoid being blocked) | 
| Delay between requests |	time.sleep(0.5) |
| robots.txt	| https://www.rcsb.org/robots.txt - access to /structure/ is allowed |
| Error handling |	try/except + writing to the JSONL log |
| Saving snapshots |	HTML pages are saved in data/raw/web/{pdb_id}_{timestamp}.html |

What does the script do:
1. The URL is generated for each PDB ID: https://www.rcsb.org/structure /{pdb_id}
2. Sends a GET request from the User-Agent
3. Saves an HTML copy of the page
4. HTML parsing via BeautifulSoup
5. Extracts fields by id and CSS selectors
6. Records the result in CSV and log

## Extracted fields

Which DOM fields map to schema columns.

| Поле в CSV |	What is it |	Where does the (selector) come from |	Example of a value |
|------------|-------------|----------------------------------------|----------------------|
| pdb_id	| Structure ID |	From a variable (not from HTML) | 	3wne |
| title |	Structure name |	span#structureTitle |	"Cyclic hexapeptide PKIDNG in complex with HIV-1 integrase" |
| classification |	Classification (type of molecule) |	li#header_classification a	| "VIRAL PROTEIN/PEPTIDE" |
| organism	| Organism-source protein |	li#header_organism a	| "Human immunodeficiency virus 1" |
| expression_system	| System expression |	li#header_expression-system a	| "Escherichia coli" |
| method	| Method of determining the structure	| li#exp_details_0_method	| "X-RAY DIFFRACTION" |
| resolution	| Resolution |	li#exp_details_0_diffraction_resolution |	1.70 |
| deposition_authors | 	Authors |	li#header_deposition-authors a	| "Wielens, J., Chalmers, D.K., Parker, M.W." |
| uniprot_id	| Protein identifier in UniProt	| a[href*='database_accession:P']	| "P12497" |
| pdb_doi |	DOI structures in the PDB |	li#header_doi a	| "10.2210/pdb3wne/pdb" |

All selectors use unique `id` attributes, making them stable against minor layout changes. For fields that may be missing (e.g., `expression_system` for some entries), the parser gracefully returns an empty string.

## Extraction problems

Dynamic content, login walls, changed markup, inconsistent units.

The main problems are blocking bots (solved by the User-Agent and with a delay of 0.5 seconds), the absence of some fields on the pages (checking via if), different resolution formats (cleaning the text). The site uses ready-made HTML, so there were no problems with dynamic content.

## Output files
The pdb_id list contained additional information, namely structural metadata from the RCSB PDB website.

The result is stored in:
- `data/extracted/web_extracted_records.csv` (a csv file that has the following columns: pdb_id,title,classification,organism,expression_system,method,resolution,deposition_authors,uniprot_id,pdb_doi)
- `data/raw/web/*.html` snapshots
- `data/extracted/extraction_log.jsonl` (web-related lines)
