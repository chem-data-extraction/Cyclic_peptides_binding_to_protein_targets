#!/usr/bin/env python3
import pandas as pd
import re
from pathlib import Path

patel = pd.read_csv("data/interim/pdf_extracted_records_normalized.csv")
kd_values = pd.read_csv("data/interim/kd_values_normalized.csv")
wang = pd.read_csv("data/interim/wang_2019_auto_normalized.csv")
charitou = pd.read_csv("data/interim/charitou_peptides_normalized.csv")
rcsb = pd.read_csv("data/interim/rcsb_metadata_normalized.csv")

def clean_sequence(seq):
    if pd.isna(seq):
        return ""
    seq = str(seq)
    seq = re.sub(r'\([^)]+\)', '', seq)
    seq = re.sub(r'[^A-Z]', '', seq)
    return seq.upper()

def extract_reads_from_notes(notes):
    if pd.isna(notes):
        return None
    match = re.search(r'reads=(\d+)', str(notes))
    return int(match.group(1)) if match else None

def extract_round_from_notes(notes):
    if pd.isna(notes):
        return None
    match = re.search(r'round (\d+)', str(notes))
    return int(match.group(1)) if match else None

def load_kd_by_target(kd_df):
    kd_by_target = {}
    best_kd_by_target = {}
    
    for _, row in kd_df.iterrows():
        target = row.get('target_type', '')
        peptide = row.get('peptide', '')
        kd_value = row.get('affinity_value', '')
        kd_error = row.get('error_nM', '')
        
        if not target or pd.isna(kd_value):
            continue
        
        if target not in kd_by_target:
            kd_by_target[target] = []
            best_kd_by_target[target] = {
                'value': float('inf'),
                'value_raw': None,
                'error_raw': None,
                'peptide': ''
            }
        
        kd_by_target[target].append(f"{peptide}={kd_value}±{kd_error}nM")
        
        try:
            kd_float = float(kd_value) if kd_value else float('inf')
            if kd_float < best_kd_by_target[target]['value']:
                best_kd_by_target[target] = {
                    'value': kd_float,
                    'value_raw': kd_value,
                    'error_raw': kd_error,
                    'peptide': peptide
                }
        except (ValueError, TypeError):
            pass
    
    return {'all_kd': kd_by_target, 'best_kd': best_kd_by_target}

PEPTIDE_SEQUENCE_MAP = {
    "3.1A": "TWLIPIRTL",
    "3.1B": "PNEFYSKTTLSHI",
    "3.1C": "SCRILLKWAIIHN",
    "3.2A": "WIIPVRG",
    "3.2B": "WIIPVRGN",
    "3.2C": "WIIPKKAG",
    "4.2A": "NGWWIPL",
    "4.1D": "WIIPVRGN",
}

charitou_dict = {}
if not charitou.empty:
    for _, row in charitou.iterrows():
        seq = row.get('peptide_sequence', '')
        if seq and seq not in charitou_dict:
            charitou_dict[seq] = {
                'pdb_id': row.get('pdb_id', ''),
                'structure_resolution': row.get('structure_resolution', ''),
                'peptide_cyclization_type': row.get('peptide_cyclization_type', '')
            }

rcsb_dict = {}
if not rcsb.empty:
    for _, row in rcsb.iterrows():
        pdb = row.get('pdb_id', '')
        if pdb and pdb not in rcsb_dict:
            rcsb_dict[pdb] = {
                'title': row.get('title', ''),
                'organism': row.get('organism', ''),
                'method': row.get('method', ''),
                'uniprot_id': row.get('uniprot_id', ''),
                'structure_resolution': row.get('structure_resolution', '')
            }

kd_data = load_kd_by_target(kd_values)

patel_records = []
for idx, row in patel.iterrows():
    target = row.get('target_type', '')
    notes = str(row.get('notes', '') or '')
    
    reads = extract_reads_from_notes(notes)
    selection_round = extract_round_from_notes(notes)
    
    seq_clean = clean_sequence(row.get('peptide_sequence', ''))
    peptide_length = len(seq_clean) if seq_clean else 0
    
    affinity_value = ''
    affinity_error = ''
    kd_peptide_name = ''
    kd_note = ''
    
    best_kd_dict = kd_data.get('best_kd', {})
    if target in best_kd_dict:
        best = best_kd_dict[target]
        best_value = best.get('value')
        if best_value and best_value != float('inf'):
            affinity_value = str(best.get('value_raw', best_value))
            affinity_error = str(best.get('error_raw', ''))
            kd_peptide_name = best.get('peptide', '')
            all_kd_list = kd_data.get('all_kd', {}).get(target, [])
            if all_kd_list:
                kd_note = f" Best KD for {target}: {kd_peptide_name}={affinity_value}±{affinity_error}nM"
                kd_note += f" | All KD: {'; '.join(all_kd_list)}"
    
    pdb_id = ''
    structure_resolution = ''
    peptide_cyclization_type = row.get('peptide_cyclization_type', 'thioether')
    
    if seq_clean in charitou_dict:
        pdb_id = charitou_dict[seq_clean]['pdb_id']
        structure_resolution = charitou_dict[seq_clean]['structure_resolution']
        if charitou_dict[seq_clean]['peptide_cyclization_type']:
            peptide_cyclization_type = charitou_dict[seq_clean]['peptide_cyclization_type']
    
    title = ''
    organism = ''
    method = ''
    uniprot_id = ''
    
    if pdb_id and pdb_id in rcsb_dict:
        title = rcsb_dict[pdb_id]['title']
        organism = rcsb_dict[pdb_id]['organism']
        method = rcsb_dict[pdb_id]['method']
        uniprot_id = rcsb_dict[pdb_id]['uniprot_id']
        if not structure_resolution and rcsb_dict[pdb_id]['structure_resolution']:
            structure_resolution = rcsb_dict[pdb_id]['structure_resolution']
    
    if kd_note:
        notes = notes + kd_note
    
    record = {
        'record_id': row.get('record_id', f"record_{idx}"),
        'peptide_sequence': row.get('peptide_sequence', ''),
        'peptide_length': peptide_length,
        'peptide_cyclization_type': peptide_cyclization_type,
        'target_type': target,
        'target_class_sequence': row.get('target_class_sequence', ''),
        'target_class': row.get('target_class', 'bromodomain'),
        'affinity_value': affinity_value,
        'affinity_unit': 'nM',
        'affinity_type': 'KD',
        'kd_error_nM': affinity_error,
        'pdb_id': pdb_id,
        'structure_resolution': structure_resolution,
        'title': title,
        'organism': organism,
        'method': method,
        'uniprot_id': uniprot_id,
        'reads': reads if reads else '',
        'selection_round': selection_round if selection_round else '',
        'source_id': row.get('source_id', 'paper_patel_pnas_2020'),
        'source_type': row.get('source_type', 'scientific_paper'),
        'source_url': row.get('source_url', 'https://doi.org/10.1073/pnas.2003086117'),
        'doi': row.get('doi', '10.1073/pnas.2003086117'),
        'extraction_method': row.get('extraction_method', 'excel_import'),
        'extraction_confidence': row.get('extraction_confidence', 'high'),
        'cyclization_positions': '',
        'temperature_C': '',
        'pH': '',
        'buffer': '',
        'mutations': '',
        'notes': notes.strip(),
    }
    patel_records.append(record)

patel_df = pd.DataFrame(patel_records)

kd_records = []
for _, row in kd_values.iterrows():
    peptide_name = row.get('peptide', '')
    target = row.get('target_type', '')
    affinity = row.get('affinity_value', '')
    affinity_error = row.get('error_nM', '')
    page = row.get('page', '')
    
    if not target or pd.isna(affinity):
        continue
    
    peptide_seq = PEPTIDE_SEQUENCE_MAP.get(peptide_name, '')
    
    if '3.1' in str(peptide_name) or '3.2' in str(peptide_name) or '4.2' in str(peptide_name):
        cycl_type = 'thioether'
    else:
        cycl_type = 'unknown'
    
    if 'BRD' in str(target):
        target_class = 'bromodomain'
    else:
        target_class = ''
    
    pdb_id = ''
    structure_resolution = ''
    seq_clean = clean_sequence(peptide_seq)
    
    if seq_clean and seq_clean in charitou_dict:
        pdb_id = charitou_dict[seq_clean]['pdb_id']
        structure_resolution = charitou_dict[seq_clean]['structure_resolution']
    
    title = ''
    organism = ''
    method = ''
    uniprot_id = ''
    
    if pdb_id and pdb_id in rcsb_dict:
        title = rcsb_dict[pdb_id]['title']
        organism = rcsb_dict[pdb_id]['organism']
        method = rcsb_dict[pdb_id]['method']
        uniprot_id = rcsb_dict[pdb_id]['uniprot_id']
    
    record = {
        'record_id': f"kd_{peptide_name}_{target.replace('-', '_')}",
        'peptide_sequence': peptide_seq,
        'peptide_length': len(seq_clean) if seq_clean else 0,
        'peptide_cyclization_type': cycl_type,
        'target_type': target,
        'target_class_sequence': '',
        'target_class': target_class,
        'affinity_value': str(affinity),
        'affinity_unit': 'nM',
        'affinity_type': 'KD',
        'kd_error_nM': str(affinity_error) if affinity_error else '',
        'pdb_id': pdb_id,
        'structure_resolution': structure_resolution,
        'title': title,
        'organism': organism,
        'method': method,
        'uniprot_id': uniprot_id,
        'reads': '',
        'selection_round': '',
        'source_id': 'patel_kd_values',
        'source_type': 'scientific_paper',
        'source_url': 'https://doi.org/10.1073/pnas.2003086117',
        'doi': '10.1073/pnas.2003086117',
        'extraction_method': 'excel_import',
        'extraction_confidence': 'high',
        'cyclization_positions': '',
        'temperature_C': '',
        'pH': '',
        'buffer': '',
        'mutations': '',
        'notes': f"KD measurement for peptide {peptide_name} against {target}. Page: {page}",
    }
    kd_records.append(record)

kd_df = pd.DataFrame(kd_records)

wang_records = []
for _, row in wang.iterrows():
    ligand = row.get('ligand', '')
    peptide_seq = row.get('peptide_sequence', '')
    target = row.get('target', '')
    
    if 'Cyc' in str(ligand):
        cyclization = 'cyclic'
    elif 'Lin' in str(ligand):
        cyclization = 'linear'
    else:
        cyclization = 'unknown'
    
    affinity = row.get('affinity_value')
    if pd.notna(affinity) and affinity:
        affinity_nm = float(affinity) * 1000
    else:
        affinity_nm = ''
    
    kd_error = row.get('kd_error_um')
    if pd.notna(kd_error) and kd_error:
        kd_error_nm = float(kd_error) * 1000
    else:
        kd_error_nm = ''
    
    if 'TEV' in str(target):
        target_class = 'protease'
    elif 'HDAC' in str(target):
        target_class = 'deacetylase'
    else:
        target_class = ''
    
    seq_clean = clean_sequence(peptide_seq)
    pdb_id = ''
    structure_resolution = ''
    
    if seq_clean in charitou_dict:
        pdb_id = charitou_dict[seq_clean]['pdb_id']
        structure_resolution = charitou_dict[seq_clean]['structure_resolution']
    
    title = ''
    organism = ''
    uniprot_id = ''
    
    if pdb_id and pdb_id in rcsb_dict:
        title = rcsb_dict[pdb_id]['title']
        organism = rcsb_dict[pdb_id]['organism']
        uniprot_id = rcsb_dict[pdb_id]['uniprot_id']
    
    notes = f"Wang 2019. Ligand: {ligand}"
    if affinity_nm:
        notes += f" KD={affinity_nm}±{kd_error_nm} nM"
    
    record = {
        'record_id': f"wang_{ligand}",
        'peptide_sequence': peptide_seq,
        'peptide_length': len(clean_sequence(peptide_seq)),
        'peptide_cyclization_type': cyclization,
        'target_type': target,
        'target_class_sequence': '',
        'target_class': target_class,
        'affinity_value': affinity_nm,
        'affinity_unit': 'nM',
        'affinity_type': 'KD',
        'kd_error_nM': kd_error_nm,
        'pdb_id': pdb_id,
        'structure_resolution': structure_resolution,
        'title': title,
        'organism': organism,
        'method': 'SPR',
        'uniprot_id': uniprot_id,
        'reads': '',
        'selection_round': '',
        'source_id': 'wang_2019',
        'source_type': 'scientific_paper',
        'source_url': 'https://doi.org/10.1002/ange.201908713',
        'doi': '10.1002/ange.201908713',
        'extraction_method': 'auto_extract',
        'extraction_confidence': 'high',
        'cyclization_positions': '',
        'temperature_C': '',
        'pH': '',
        'buffer': '',
        'mutations': 'Nle = norleucine' if 'Nle' in str(peptide_seq) else '',
        'notes': notes,
    }
    wang_records.append(record)

wang_df = pd.DataFrame(wang_records)

columns = [
    'record_id', 'peptide_sequence', 'peptide_length', 'peptide_cyclization_type',
    'target_type', 'target_class_sequence', 'target_class',
    'affinity_value', 'affinity_unit', 'affinity_type', 'kd_error_nM',
    'pdb_id', 'structure_resolution', 'title', 'organism', 'method', 'uniprot_id',
    'reads', 'selection_round', 'source_id', 'source_type', 'source_url', 'doi',
    'extraction_method', 'extraction_confidence', 'cyclization_positions',
    'temperature_C', 'pH', 'buffer', 'mutations', 'notes'
]

for col in columns:
    if col not in patel_df.columns:
        patel_df[col] = ''
    if col not in kd_df.columns:
        kd_df[col] = ''
    if col not in wang_df.columns:
        wang_df[col] = ''

all_records = pd.concat([patel_df[columns], kd_df[columns], wang_df[columns]], ignore_index=True)
all_records = all_records.fillna('')

if 'reads' in all_records.columns:
    all_records['reads_sort'] = pd.to_numeric(all_records['reads'], errors='coerce')
    all_records = all_records.sort_values(['reads_sort', 'selection_round'], ascending=[False, True])
    all_records = all_records.drop(columns=['reads_sort'])
else:
    all_records = all_records.sort_values('source_id')

output_path = Path("data/interim/merged_records.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
all_records.to_csv(output_path, index=False, encoding='utf-8')