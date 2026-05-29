#!/usr/bin/env python3
import re
import pandas as pd
import pdfplumber

def clean_pdf_text(text):
    text = re.sub(r'\d+mm\([^)]*\)', ' ', text)
    text = re.sub(r'\d+mm', ' ', text)
    fixes = {
        'Tabelle1': 'Table 1',
        '[mm]': '[μM]',
        'TEVprotease': 'TEV protease',
        ':': '±'
    }
    
    for wrong, correct in fixes.items():
        text = text.replace(wrong, correct)
    
    return text

def parse_value_with_error(value_str):
    if not value_str or value_str == '':
        return None, None
    
    value_str = value_str.strip()
    
    if value_str.startswith('>'):
        value_str = value_str[1:]
    
    value = None
    error = None
    
    if '±' in value_str:
        parts = value_str.split('±')
        try:
            value = float(parts[0])
            error = float(parts[1])
        except:
            pass
    else:
        try:
            value = float(value_str)
        except:
            pass
    
    return value, error

with pdfplumber.open('data/raw/Angewandte Chemie - 2019 - Wang - A Genetically Encoded  Phage‐Displayed Cyclic‐Peptide Library.pdf') as pdf:
    page = pdf.pages[3]
    raw_text = page.extract_text()
    cleaned_text = clean_pdf_text(raw_text)
    
    pattern = r'(CycTev\d+|LinTev\d+|CycH8a|LinH8a[^\s]*)\s+([A-Z]+[A-Za-z]+(?:Nle)?)\s+(TEV\s*protease|HDAC8)\s+([\d\.><±]+(?:\s*±\s*[\d\.]+)?)\s+([\d\.><±]+(?:\s*±\s*[\d\.]+)?)?'
    
    matches = re.findall(pattern, cleaned_text)
    
    data = []
    for match in matches:
        ligand = match[0]
        sequence = match[1]
        target = match[2]
        kd_str = match[3]
        ic50_str = match[4] if len(match) > 4 and match[4] else ''
        
        kd_um, kd_error_um = parse_value_with_error(kd_str)
        
        if kd_um is not None:
            kd_nm = kd_um * 1000
            kd_error_nm = kd_error_um * 1000 if kd_error_um is not None else None
        else:
            kd_nm = None
            kd_error_nm = None
        
        ic50_um, ic50_error_um = parse_value_with_error(ic50_str)
        
        if ic50_um is not None:
            ic50_nm = ic50_um * 1000
            ic50_error_nm = ic50_error_um * 1000 if ic50_error_um is not None else None
        else:
            ic50_nm = None
            ic50_error_nm = None
        
        data.append({
            'ligand': ligand,
            'peptide_sequence': sequence,
            'target': target,
            'kd_nm': kd_nm,
            'kd_error_nm': kd_error_nm,
            'ic50_nm': ic50_nm,
            'ic50_error_nm': ic50_error_nm
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/extracted/wang_2019_auto.csv', index=False)