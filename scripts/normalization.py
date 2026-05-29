#!/usr/bin/env python3
import pandas as pd
import re

def normalize(seq):
    if pd.isna(seq):
        return ""
    seq = str(seq)
    seq = re.sub(r'\([^)]+\)', '', seq)
    seq = re.sub(r'C?GSGSGSamber$', '', seq)
    seq = re.sub(r'C?GSGSGS$', '', seq)
    seq = re.sub(r'amber$', '', seq)
    seq = re.sub(r'^M', '', seq)
    seq = re.sub(r'[^A-Z]', '', seq)
    return seq.upper()


patel = pd.read_csv("data/extracted/charitou_peptides.csv")
charitou = pd.read_csv("data/extracted/pdf_extracted_records.csv")
wang = pd.read_csv("data/extracted/wang_2019_auto.csv")
kd_values = pd.read_csv("data/extracted/kd_values.csv")
wed_values = pd.read_csv("data/extracted/rcsb_metadata.csv")

patel["peptide_sequence"] = patel["peptide_sequence"].apply(normalize)
charitou["peptide_sequence"] = charitou["peptide_sequence"].apply(normalize)
wang["peptide_sequence"] = wang["peptide_sequence"].apply(normalize)

wang.rename(columns={"target": "target_type"}, inplace=True)
kd_values.rename(columns={"target": "target_type"}, inplace=True)

wang.rename(columns={"kd_nm": "affinity_value"}, inplace=True)
kd_values.rename(columns={"kd_nM": "affinity_value"}, inplace=True)
wed_values.rename(columns={"resolution": "structure_resolution"}, inplace=True)

patel.to_csv("data/interim/charitou_peptides_normalized.csv", index=False)
charitou.to_csv("data/interim/pdf_extracted_records_normalized.csv", index=False)
wang.to_csv("data/interim/wang_2019_auto_normalized.csv", index=False)
kd_values.to_csv("data/interim/kd_values_normalized.csv", index=False)
wed_values.to_csv("data/interim/rcsb_metadata_normalized.csv", index=False)

print(f"Patel: {len(patel)} записей")
print(f"Charitou: {len(charitou)} записей")
print(f"Wang: {len(wang)} записей")