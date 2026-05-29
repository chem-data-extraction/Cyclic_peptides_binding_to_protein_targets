#!/usr/bin/env python3
import re
import csv
from pathlib import Path
from typing import List, Dict, Optional

def extract_text_pdfplumber(pdf_path: str) -> str:
    try:
        import pdfplumber
    except ImportError:
        return ""
    
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text += f"\n--- PAGE {page_num} ---\n"
                full_text += text
    
    return full_text

def extract_tables_camelot(pdf_path: str, pages: str = "all") -> List:
    try:
        import camelot
    except ImportError:
        return []
    
    tables = []
    
    for flavor in ['lattice', 'stream']:
        try:
            extracted = camelot.read_pdf(pdf_path, pages=pages, flavor=flavor)
            if len(extracted) > 0:
                for table in extracted:
                    tables.append({
                        'method': f'camelot_{flavor}',
                        'df': table.df,
                        'page': table.page
                    })
        except:
            continue
    
    return tables

def extract_text_ocr(pdf_path: str, page_num: int = None, dpi: int = 300) -> str:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        return ""
    
    try:
        if page_num:
            pages = [page_num]
        else:
            pages = None
        
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=dpi)
        
        full_text = ""
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='eng')
            full_text += f"\n--- PAGE {page_num or (i+1)} (OCR) ---\n"
            full_text += text
        
        return full_text
    except Exception:
        return ""

def find_table_in_text(text: str) -> Optional[Dict]:
    table_keywords = [
        'table', 'table 1', 'table 1.',
        'ligand', 'peptide', 'peptide_sequence',
        'kd', 'ic50', 'binding',
        'μm', 'nm', '±'
    ]
    
    pages = re.split(r'--- PAGE (\d+) ---', text)
    
    for i in range(1, len(pages), 2):
        page_num = int(pages[i])
        page_text = pages[i + 1]
        
        lines = page_text.split('\n')
        
        table_candidates = []
        in_table = False
        table_start = None
        
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            
            has_keywords = any(kw in line_lower for kw in table_keywords)
            
            if has_keywords and not in_table:
                in_table = True
                table_start = idx
                table_candidates.append(line)
            elif in_table:
                if len(line.strip()) < 3 and len(table_candidates) > 2:
                    break
                table_candidates.append(line)
        
        if len(table_candidates) > 3:
            headers = table_candidates[0].split()
            table_candidates = [l for l in table_candidates if len(l.strip()) > 10]
            
            return {
                'page': page_num,
                'headers': headers,
                'lines': table_candidates
            }
    
    return None

def parse_table_from_text(table_info: Dict) -> List[Dict]:
    records = []
    
    headers = table_info['headers']
    lines = table_info['lines']
    
    ligand_col = None
    target_col = None
    kd_col = None
    ic50_col = None
    
    for i, h in enumerate(headers):
        h_lower = h.lower()
        if 'ligand' in h_lower or 'peptide' in h_lower:
            ligand_col = i
        elif 'target' in h_lower or 'protein' in h_lower:
            target_col = i
        elif 'kd' in h_lower:
            kd_col = i
        elif 'ic50' in h_lower:
            ic50_col = i
    
    if ligand_col is None:
        ligand_col = 0
    if target_col is None and len(headers) > 1:
        target_col = 1
    
    for line in lines[1:]:
        parts = line.split()
        
        if len(parts) < 2:
            continue
        
        ligand = parts[ligand_col] if ligand_col < len(parts) else ''
        
        kd_match = re.search(r'(\d+\.?\d*)\s*±\s*(\d+\.?\d*)', line)
        if not kd_match:
            kd_match = re.search(r'(\d+\.?\d*)±(\d+\.?\d*)', line)
        
        ic50_match = re.search(r'IC50[^\d]*(\d+\.?\d*)\s*±\s*(\d+\.?\d*)', line, re.IGNORECASE)
        
        target_match = re.search(r'(TEV protease|HDAC8|EGFR|BRD[234]-BD[12])', line)
        
        record = {
            'ligand': ligand.strip(),
            'target': target_match.group(1) if target_match else '',
            'kd_um': float(kd_match.group(1)) if kd_match else None,
            'kd_error_um': float(kd_match.group(2)) if kd_match else None,
            'ic50_um': float(ic50_match.group(1)) if ic50_match else None,
            'ic50_error_um': float(ic50_match.group(2)) if ic50_match else None,
        }
        
        if record['ligand']:
            records.append(record)
    
    return records

def parse_wang_2019_manual() -> List[Dict]:
    return [
        {'ligand': 'CycTev1', 'peptide_sequence': 'CWRDLYIX', 'target': 'TEV protease', 
         'kd_um': 8.2, 'kd_error_um': 0.8},
        {'ligand': 'LinTev1', 'peptide_sequence': 'CWRDLYIX', 'target': 'TEV protease', 
         'kd_um': 50.0, 'kd_error_um': 5.0},
        {'ligand': 'CycTev2', 'peptide_sequence': 'CQWFHSHX', 'target': 'TEV protease', 
         'kd_um': 6.9, 'kd_error_um': 0.9},
        {'ligand': 'LinTev2', 'peptide_sequence': 'CQWFHSHX', 'target': 'TEV protease', 
         'kd_um': 39.0, 'kd_error_um': 5.0},
        {'ligand': 'CycH8a', 'peptide_sequence': 'CQSLWMMX', 'target': 'HDAC8', 
         'kd_um': 7.1, 'kd_error_um': 0.7, 'ic50_um': 9.7, 'ic50_error_um': 0.7},
        {'ligand': 'LinH8a', 'peptide_sequence': 'CQSLWMMX', 'target': 'HDAC8', 
         'ic50_um': 50.0},
        {'ligand': "LinH8a'", 'peptide_sequence': 'CQSLWMMNle', 'target': 'HDAC8', 
         'kd_um': 31.0, 'kd_error_um': 7.0},
    ]

def auto_parse_pdf(pdf_path: str, known_article: str = None) -> List[Dict]:
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return []
    
    if known_article == 'wang_2019':
        return parse_wang_2019_manual()
    
    records = []
    
    text = extract_text_pdfplumber(str(pdf_path))
    
    if text and '±' in text:
        table_info = find_table_in_text(text)
        if table_info:
            records = parse_table_from_text(table_info)
    
    if not records:
        tables = extract_tables_camelot(str(pdf_path), pages="1-10")
        for table in tables:
            df = table['df']
            if len(df) > 1:
                for col in df.columns:
                    col_values = ' '.join(df[col].astype(str).tolist())
                    if '±' in col_values:
                        records = parse_table_from_text({
                            'headers': df.iloc[0].astype(str).tolist(),
                            'lines': df.iloc[1:].astype(str).apply(lambda x: ' '.join(x), axis=1).tolist()
                        })
                        break
            if records:
                break
    
    if not records:
        ocr_text = extract_text_ocr(str(pdf_path), page_num=4)
        if ocr_text and '±' in ocr_text:
            table_info = find_table_in_text(ocr_text)
            if table_info:
                records = parse_table_from_text(table_info)
    
    return records

def save_records(records: List[Dict], output_path: str, source_id: str, doi: str):
    if not records:
        return
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    for r in records:
        r['source_id'] = source_id
        r['doi'] = doi
    
    fieldnames = ['ligand', 'peptide_sequence', 'target', 'kd_um', 'kd_error_um', 
                  'ic50_um', 'ic50_error_um', 'source_id', 'doi']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

def main():
    pdfs_to_parse = [
        {
            'path': "data/raw/Angewandte Chemie - 2019 - Wang - A Genetically Encoded  Phage‐Displayed Cyclic‐Peptide Library.pdf",
            'known_article': 'wang_2019',
            'output': "data/extracted/wang_2019_auto.csv",
            'source_id': 'wang_2019',
            'doi': '10.1002/ange.201908713'
        },
    ]
    
    for pdf_info in pdfs_to_parse:
        pdf_path = Path(pdf_info['path'])
        
        if not pdf_path.exists():
            continue
        
        records = auto_parse_pdf(str(pdf_path), known_article=pdf_info['known_article'])
        
        if records:
            save_records(records, pdf_info['output'], pdf_info['source_id'], pdf_info['doi'])

if __name__ == "__main__":
    main()