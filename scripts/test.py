#!/usr/bin/env python3
from __future__ import annotations

import json
import csv
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "data/extracted/extraction_log.jsonl"
OUTPUT_CSV = ROOT / "data/extracted/web_extracted_records.csv"

TARGETS = {
    'PKA': {
        'search_name': 'cAMP-dependent protein kinase catalytic subunit alpha',
        'pdb_ids': ['3wne', '3zgc', '3av9', '3ava', '3avb']
    },
    'EGFR': {
        'search_name': 'epidermal growth factor receptor',
        'pdb_ids': ['5th2']
    },
    'PD-L1': {
        'search_name': 'programmed cell death protein 1',
        'pdb_ids': ['4ib5']
    },
    'tPA': {
        'search_name': 'tissue-type plasminogen activator',
        'pdb_ids': ['1smf']
    },
    'RAF': {
        'search_name': 'RAF kinase',
        'pdb_ids': ['4m1d']
    },
    'CD13': {
        'search_name': 'CD13',
        'pdb_ids': ['4ou3']
    },
}

KNOWN_CHEMBL_IDS = {
    'cAMP-dependent protein kinase catalytic subunit alpha': 'CHEMBL4101',
    'epidermal growth factor receptor': 'CHEMBL203',
    'programmed cell death protein 1': 'CHEMBL6036',
    'tissue-type plasminogen activator': 'CHEMBL2840',
    'RAF kinase': 'CHEMBL4108',
    'CD13': 'CHEMBL1909',
}

def get_chembl_id(target_name: str, search_term: str) -> str:
    if search_term in KNOWN_CHEMBL_IDS:
        return KNOWN_CHEMBL_IDS[search_term]
    
    api_url = f"https://www.ebi.ac.uk/chembl/api/data/target?q={search_term}&format=json&limit=10"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'targets' in data:
            for target in data['targets']:
                pref_name = target.get('pref_name', '')
                organism = target.get('organism', '')
                
                if search_term.lower() in pref_name.lower():
                    if 'Homo sapiens' in organism:
                        return target.get('target_chembl_id')
            
            if data['targets']:
                return data['targets'][0].get('target_chembl_id')
        
        return None
    except Exception:
        return None

def get_activities(chembl_id: str, target_display_name: str, limit: int = 100) -> List[Dict]:
    url = "https://www.ebi.ac.uk/chembl/api/data/activity"
    params = {
        'target_chembl_id': chembl_id,
        'format': 'json',
        'limit': limit,
        'standard_type__in': 'IC50,Ki,Kd'
    }
    
    results = []
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'activities' in data:
            for act in data['activities']:
                std_type = act.get('standard_type')
                std_value = act.get('standard_value')
                std_units = act.get('standard_units', 'nM')
                pchembl = act.get('pchembl_value')
                molecule_name = act.get('molecule_pref_name', '')
                molecule_chembl_id = act.get('molecule_chembl_id', '')
                
                if std_value and std_type:
                    try:
                        value = float(std_value)
                    except (ValueError, TypeError):
                        continue
                    
                    results.append({
                        'target_display_name': target_display_name,
                        'target_chembl_id': chembl_id,
                        'affinity_type': std_type,
                        'affinity_value': value,
                        'affinity_unit': std_units,
                        'pchembl_value': pchembl,
                        'molecule_name': molecule_name,
                        'molecule_chembl_id': molecule_chembl_id,
                        'source': 'chembl_api'
                    })
        
        return results
    except Exception:
        return []

def append_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def main() -> None:
    all_records = []
    all_pdb_mapping = []
    
    for display_name, target_info in TARGETS.items():
        search_term = target_info['search_name']
        pdb_ids = target_info['pdb_ids']
        
        chembl_id = get_chembl_id(display_name, search_term)
        
        if chembl_id:
            activities = get_activities(chembl_id, display_name, limit=100)
            
            if activities:
                all_records.extend(activities)
                
                for pdb_id in pdb_ids:
                    all_pdb_mapping.append({
                        'pdb_id': pdb_id,
                        'target_name': display_name,
                        'target_chembl_id': chembl_id
                    })
        
        append_log({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": "web_extraction",
            "target": display_name,
            "chembl_id": chembl_id,
            "records_found": len(activities) if 'activities' in locals() else 0
        })
    
    if all_records:
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['target_display_name', 'target_chembl_id', 'affinity_type', 
                         'affinity_value', 'affinity_unit', 'pchembl_value',
                         'molecule_name', 'molecule_chembl_id', 'source']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)
        
        mapping_csv = OUTPUT_CSV.parent / "pdb_to_target_mapping.csv"
        with open(mapping_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['pdb_id', 'target_name', 'target_chembl_id'])
            writer.writeheader()
            writer.writerows(all_pdb_mapping)

if __name__ == "__main__":
    main()