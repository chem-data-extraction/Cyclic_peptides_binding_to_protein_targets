#!/usr/bin/env python3
import pymupdf
import pandas as pd
import pdfplumber
import re

# doc = pymupdf.open('data/raw/Angewandte Chemie - 2019 - Wang - A Genetically Encoded  Phage‐Displayed Cyclic‐Peptide Library.pdf')

# page = pdfplumber.open('data/raw/Angewandte Chemie - 2019 - Wang - A Genetically Encoded  Phage‐Displayed Cyclic‐Peptide Library.pdf').pages[3]
# im = page.to_image(resolution=150)
# im.save('data/test/page_debug.png')


# with pdfplumber.open('data/raw/pnas.202003086.pdf') as pdf:
#     for i, page in enumerate(pdf.pages[0:4]):
#         text = page.extract_text()
#         print(f"\n{'='*50}")
#         print(f"СТРАНИЦА {i+1}")
#         print(f"{'='*50}")
#         print(text)

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

with pdfplumber.open('data/raw/Angewandte Chemie - 2019 - Wang - A Genetically Encoded  Phage‐Displayed Cyclic‐Peptide Library.pdf') as pdf:
    page = pdf.pages[3]
    raw_text = page.extract_text()
    cleaned_text = clean_pdf_text(raw_text)

    pattern = r'(CycTev\d+|LinTev\d+|CycH8a|LinH8a[^\s]*)\s+([A-Z]+[A-Za-z]*)\s+(TEV\s*protease|HDAC8)\s+([\d\.><±]+(?:\s*±\s*[\d\.]+)?)\s*(?:([\d\.><±]+(?:\s*±\s*[\d\.]+)?))?'

    matches = re.findall(pattern, cleaned_text)

    data = []
    for match in matches:
        ligand = match[0]
        sequence = match[1]
        target = match[2]
        kd = match[3]
        ic50 = match[4] if len(match) > 4 and match[4] else ''
        
        data.append({
            'Ligand': ligand,
            'Sequence': sequence,
            'Protein target': target,
            'Kd [μM]': kd,
            'IC50 [μM]': ic50
        })

    df = pd.DataFrame(data)
    print(df.to_string(index=False))

    df.to_csv('data/extracted/cyclic_peptides_correct.csv', index=False)