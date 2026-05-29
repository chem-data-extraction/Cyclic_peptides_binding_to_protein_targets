#!/usr/bin/env python3
import re
import time
import csv
import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

PDB_IDS = [
    '3wne', '3zgc', '3av9', '3ava', '3avb', '3avf', '3avg', '3avh', '3avi',
    '3avj', '3avk', '3avm', '3avn', '5xn3', '1sfi', '3p8f', '4k1e', '4kel',
    '3wnf', '4ou3', '1smf', '3p72', '2ck0', '5th2', '5djc', '4ib5', '5h5q',
    '5eoc', '5wxr', '4m1d'
]

OUTPUT_CSV = Path("data/extracted/rcsb_metadata.csv")
LOG_FILE = Path("data/extracted/rcsb_extraction_log.jsonl")
SNAPSHOT_DIR = Path("data/raw/web")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_page(pdb_id: str):
    url = f"https://www.rcsb.org/structure/{pdb_id}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_path = SNAPSHOT_DIR / f"{pdb_id}_{timestamp}.html"
        snapshot_path.write_text(response.text, encoding='utf-8')
        
        return response.text, snapshot_path
    except Exception:
        return None, None

def parse_page(html: str, pdb_id: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    
    result = {
        'pdb_id': pdb_id,
        'title': '',
        'classification': '',
        'organism': '',
        'expression_system': '',
        'method': '',
        'resolution': '',
        'deposition_authors': '',
        'uniprot_id': '',
        'pdb_doi': '',
        'status': 'success'
    }
    
    try:
        title_span = soup.find('span', id='structureTitle')
        if title_span:
            result['title'] = title_span.get_text(strip=True)
        
        class_li = soup.find('li', id='header_classification')
        if class_li:
            class_link = class_li.find('a')
            if class_link:
                result['classification'] = class_link.get_text(strip=True)
        
        org_li = soup.find('li', id='header_organism')
        if org_li:
            org_link = org_li.find('a')
            if org_link:
                result['organism'] = org_link.get_text(strip=True)
        
        expr_li = soup.find('li', id='header_expression-system')
        if expr_li:
            expr_link = expr_li.find('a')
            if expr_link:
                result['expression_system'] = expr_link.get_text(strip=True)
        
        method_li = soup.find('li', id='exp_details_0_method')
        if not method_li:
            method_li = soup.find('li', id='exp_header_0_method')
        if method_li:
            method_text = method_li.get_text(strip=True)
            result['method'] = method_text.replace('Method:', '').strip()
        
        res_li = soup.find('li', id='exp_details_0_diffraction_resolution')
        if not res_li:
            res_li = soup.find('li', id='exp_header_0_diffraction_resolution')
        if res_li:
            res_text = res_li.get_text(strip=True)
            res_value = res_text.replace('Resolution:', '').replace('Å', '').strip()
            try:
                result['resolution'] = float(res_value)
            except:
                result['resolution'] = res_value
        
        authors_li = soup.find('li', id='header_deposition-authors')
        if authors_li:
            authors = [a.get_text(strip=True) for a in authors_li.find_all('a')]
            result['deposition_authors'] = ', '.join(authors)
        
        uniprot_link = soup.find('a', href=re.compile(r'reference_sequence_identifiers.database_accession:P\d+'))
        if uniprot_link:
            result['uniprot_id'] = uniprot_link.get_text(strip=True)
        
        doi_li = soup.find('li', id='header_doi')
        if doi_li:
            doi_link = doi_li.find('a')
            if doi_link:
                full_doi = doi_link.get_text(strip=True)
                result['pdb_doi'] = full_doi.replace('https://doi.org/', '')
        
    except Exception:
        result['status'] = 'parse_error'
    
    return result

def append_log(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

def main():
    all_records = []
    
    for idx, pdb_id in enumerate(PDB_IDS, 1):
        html, snapshot_path = fetch_page(pdb_id)
        
        if html:
            data = parse_page(html, pdb_id)
            all_records.append(data)
            
            append_log({
                "timestamp": datetime.now().isoformat(),
                "pdb_id": pdb_id,
                "status": "success",
                "snapshot": str(snapshot_path)
            })
        else:
            all_records.append({'pdb_id': pdb_id, 'status': 'fetch_failed'})
            append_log({
                "timestamp": datetime.now().isoformat(),
                "pdb_id": pdb_id,
                "status": "fetch_failed"
            })
        
        time.sleep(0.5)
    
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['pdb_id', 'title', 'classification', 'organism', 
                     'expression_system', 'method', 'resolution', 
                     'deposition_authors', 'uniprot_id', 'pdb_doi', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

if __name__ == "__main__":
    main()