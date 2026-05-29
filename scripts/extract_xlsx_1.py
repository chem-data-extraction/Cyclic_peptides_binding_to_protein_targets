#!/usr/bin/env python3
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def process_sequence(raw_seq: str) -> str:
    if pd.isna(raw_seq):
        return ""
    
    raw_seq = str(raw_seq).strip()
    
    linker_patterns = [
        r'CGSGSGSamber.*$',
        r'CGSGSGS.*$',
        r'amber.*$',
        r'CGSGS.*$',
        r'GSGSGSamber.*$',
    ]
    
    seq = raw_seq
    for pattern in linker_patterns:
        seq = re.sub(pattern, '', seq, flags=re.IGNORECASE)
    
    seq = seq.strip()
    
    if len(seq) < 5:
        return ""
    
    if not re.match(r'^[ACDEFGHIKLMNPQRSTVWY]+$', seq):
        return ""
    
    seq = seq.replace('M', '(AcK)')
    seq = re.sub(r'\(AcK\)\s*\(AcK\)', '(AcK)(AcK)', seq)
    
    return seq

def extract_sheet_info(sheet_name: str):
    match = re.match(r'([A-Z0-9-]+)_R(\d+)', sheet_name)
    if match:
        return match.group(1), int(match.group(2))
    return sheet_name, None

def extract_all_data(input_path: str, output_csv: str, output_log: str, max_records_per_sheet: int = None):
    if not Path(input_path).exists():
        return None
    
    xl = pd.ExcelFile(input_path)
    sheet_names = [s for s in xl.sheet_names if not s.startswith('_') and s != 'Metadata']
    
    all_records = []
    log_entries = []
    total_records = 0
    
    for sheet_name in sheet_names:
        target, round_num = extract_sheet_info(sheet_name)
        
        if target is None:
            continue
        
        df = pd.read_excel(input_path, sheet_name=sheet_name, header=1)
        
        seq_col = None
        reads_col = None
        prop_col = None
        orf_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'peptide sequence' in col_lower or 'sequence' in col_lower:
                seq_col = col
            elif 'number of reads' in col_lower or 'reads' in col_lower:
                reads_col = col
            elif 'proportion' in col_lower:
                prop_col = col
            elif 'orf' in col_lower:
                orf_col = col
        
        if seq_col is None and len(df.columns) > 1:
            seq_col = df.columns[1]
        if reads_col is None and len(df.columns) > 2:
            reads_col = df.columns[2]
        if prop_col is None and len(df.columns) > 3:
            prop_col = df.columns[3]
        
        if seq_col is None:
            continue
        
        rows_processed = 0
        
        for idx, row in df.iterrows():
            if max_records_per_sheet and rows_processed >= max_records_per_sheet:
                break
            
            orf_num = idx + 1
            if orf_col and pd.notna(row[orf_col]):
                orf_val = str(row[orf_col])
                orf_match = re.search(r'(\d+)', orf_val)
                if orf_match:
                    orf_num = int(orf_match.group(1))
            
            raw_seq = str(row[seq_col]).strip() if pd.notna(row[seq_col]) else ""
            
            if not raw_seq or raw_seq in ['Peptide sequence', 'ORF', 'Number of Reads', 'Proportion of library reads']:
                continue
            
            processed_seq = process_sequence(raw_seq)
            if not processed_seq:
                continue
            
            reads = None
            if reads_col and pd.notna(row[reads_col]):
                try:
                    val = str(row[reads_col]).replace(',', '').strip()
                    if val and val != 'nan':
                        reads = int(float(val))
                except (ValueError, TypeError):
                    pass
            
            proportion = None
            if prop_col and pd.notna(row[prop_col]):
                try:
                    val = str(row[prop_col]).replace('%', '').replace(',', '.').strip()
                    if val and val != 'nan':
                        proportion = float(val)
                except (ValueError, TypeError):
                    pass
            
            record_id = f"rec_patel_{target}_R{round_num}_orf{orf_num:04d}_{total_records + rows_processed + 1:04d}"
            
            record = {
                "record_id": record_id,
                "peptide_sequence": processed_seq,
                "peptide_cyclization_type": "thioether",
                "target_type": target,
                "target_class_sequence": "",
                "target_class": "bromodomain",
                "affinity_value": "",
                "affinity_unit": "",
                "affinity_type": "",
                "source_id": "paper_patel_pnas_2020",
                "source_type": "scientific_paper",
                "source_url": "https://doi.org/10.1073/pnas.2003086117",
                "doi": "10.1073/pnas.2003086117",
                "extraction_method": "excel_import",
                "extraction_confidence": "high",
                "method": "",
                "cyclization_positions": "",
                "temperature_C": "",
                "pH": "",
                "buffer": "",
                "mutations": "",
                "structure_resolution": "",
                "notes": f"RaPID selection round {round_num} against {target}. ORF{orf_num}: reads={reads if reads else 'N/A'}, proportion={proportion if proportion else 'N/A'}"
            }
            
            all_records.append(record)
            
            log_entries.append({
                "timestamp": datetime.now().isoformat(),
                "source_id": "paper_patel_pnas_2020",
                "sheet": sheet_name,
                "round": round_num,
                "target": target,
                "row": int(idx),
                "orf": orf_num,
                "raw_sequence": raw_seq[:50],
                "processed_sequence": processed_seq,
                "reads": reads,
                "proportion": proportion,
                "record_id": record_id,
                "status": "extracted"
            })
            
            rows_processed += 1
        
        total_records += rows_processed
    
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if all_records:
        df_output = pd.DataFrame(all_records)
        
        schema_order = [
            "record_id", "peptide_sequence", "peptide_cyclization_type",
            "target_type", "target_class_sequence", "target_class",
            "affinity_value", "affinity_unit", "affinity_type",
            "source_id", "source_type", "source_url", "doi",
            "extraction_method", "extraction_confidence", "method",
            "cyclization_positions", "temperature_C", "pH", "buffer",
            "mutations", "structure_resolution", "notes"
        ]
        
        for col in schema_order:
            if col not in df_output.columns:
                df_output[col] = ""
        
        df_output = df_output[schema_order]
        df_output.to_csv(output_path, index=False)
        
        with open(output_log, 'w') as f:
            for entry in log_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return all_records

def main():
    input_file = "data/raw/pnas.2003086117.sd01.xlsx"
    output_csv = "data/extracted/pdf_extracted_records.csv"
    output_log = "data/extracted/extraction_log.jsonl"
    
    extract_all_data(input_file, output_csv, output_log, max_records_per_sheet=None)

if __name__ == "__main__":
    main()