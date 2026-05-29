#!/usr/bin/env python3
import re
import pandas as pd
import pdfplumber
from pathlib import Path

def extract_table_from_pdf(pdf_path: str) -> pd.DataFrame:
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            
            text = re.sub(r'\(cid:80\)', 'μ', text)
            text = re.sub(r'\(cid:[0-9]+\)', '', text)
            
            lines = text.split('\n')
            
            peptides = None
            for line in lines:
                found = re.findall(r'\d+\.\d+[A-C]', line)
                if len(found) >= 2:
                    peptides = found
                    break
            
            if not peptides:
                continue
            
            for line in lines:
                target_match = re.search(r'(BRD[234]-BD[12])', line)
                if not target_match:
                    continue
                
                target = target_match.group(1)
                values = []
                
                greater = re.search(r'>\s*(\d+(?:\.\d+)?)\s*μM', line)
                if greater:
                    val = float(greater.group(1)) * 1000
                    values.append(('>', val, None))
                
                pm_matches = re.findall(r'(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)', line)
                for v, e in pm_matches:
                    val = float(v)
                    err = float(e)
                    if val < 10 and 'nM' not in line:
                        values.append(('±', val * 1000, err * 1000))
                    else:
                        values.append(('±', val, err))
                
                if not values:
                    nums = re.findall(r'(?<![>\.\d])(\d+(?:\.\d+)?)(?![\.\d])(?!\s*±)', line)
                    for n in nums:
                        val = float(n)
                        if val < 10:
                            values.append(('num', val * 1000, None))
                        else:
                            values.append(('num', val, None))
                
                valid_values = [v for v in values if v[1] is not None]
                
                for i, peptide in enumerate(peptides):
                    if i < len(valid_values):
                        _, kd, err = valid_values[i]
                        all_data.append({
                            'peptide': peptide,
                            'target': target,
                            'kd_nM': kd,
                            'error_nM': err,
                            'page': page_num
                        })
    
    return pd.DataFrame(all_data)

def main():
    pdf_path = Path("data/raw/pnas.202003086.pdf")
    
    if not pdf_path.exists():
        return
    
    df = extract_table_from_pdf(str(pdf_path))
    
    if df.empty:
        return
    
    df = df.drop_duplicates(subset=['peptide', 'target'])
    df = df[df['kd_nM'].notna()]
    df = df[df['kd_nM'] <= 50000]
    df = df.sort_values(['peptide', 'target'])
    
    output_dir = Path("data/extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_csv = output_dir / "kd_values.csv"
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    main()