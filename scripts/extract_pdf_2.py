#!/usr/bin/env python3
import camelot
import pandas as pd
from pathlib import Path
import re

def clean_cell(cell):
    if not cell or pd.isna(cell):
        return ""
    cell = str(cell)
    cell = cell.replace('•', '')
    cell = cell.replace('\n', ' ')
    cell = ' '.join(cell.split())
    return cell.strip()

def extract_pdb_id(cell):
    cleaned = clean_cell(cell)
    if len(cleaned) == 4 and cleaned[0].isdigit():
        return cleaned
    return None

def extract_sequence(cell):
    cleaned = clean_cell(cell)
    match = re.search(r'([A-Z]{6,20})', cleaned)
    return match.group(1) if match else None

def extract_resolution(cell):
    cleaned = clean_cell(cell)
    match = re.search(r'(\d+\.\d{2})', cleaned)
    return float(match.group(1)) if match else None

def extract_length(cell):
    cleaned = clean_cell(cell)
    match = re.search(r'(\d+)', cleaned)
    return int(match.group(1)) if match else None

def main():
    pdf_path = "data/raw/ct2c00075_si_001_sup.pdf"
    
    if not Path(pdf_path).exists():
        return
    
    all_records = []
    
    tables = camelot.read_pdf(pdf_path, pages='3', flavor='lattice')
    
    if tables:
        df = tables[0].df
        
        for idx in range(1, len(df)):
            row = df.iloc[idx]
            
            pdb_id = extract_pdb_id(row[0])
            if not pdb_id:
                continue
            
            length = extract_length(row[1])
            resolution = extract_resolution(row[3])
            sequence = extract_sequence(row[4])
            
            if not sequence:
                continue
            
            all_records.append({
                'pdb_id': pdb_id,
                'peptide_sequence': sequence,
                'peptide_length': length if length else len(sequence),
                'structure_resolution': resolution,
                'peptide_cyclization_type': 'backbone (head-to-tail)',
                'source_id': 'charitou_2022',
                'doi': '10.1021/acs.jctc.2c00075'
            })
    
    tables = camelot.read_pdf(pdf_path, pages='4', flavor='lattice')
    
    if tables:
        df = tables[0].df
        
        for idx in range(1, len(df)):
            row = df.iloc[idx]
            
            pdb_id = extract_pdb_id(row[0])
            if not pdb_id:
                continue
            
            length = extract_length(row[1])
            resolution = extract_resolution(row[3])
            sequence = extract_sequence(row[4])
            
            if not sequence:
                continue
            
            all_records.append({
                'pdb_id': pdb_id,
                'peptide_sequence': sequence,
                'peptide_length': length if length else len(sequence),
                'structure_resolution': resolution,
                'peptide_cyclization_type': 'disulfide',
                'source_id': 'charitou_2022',
                'doi': '10.1021/acs.jctc.2c00075'
            })
    
    if all_records:
        output_path = Path("data/extracted/charitou_peptides.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(all_records)
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()