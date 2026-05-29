#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

scripts = [
    "extract_pdf_1.py",
    "extract_pdf_2.py",
    "extract_pdf_3.py",
    "extract_xlsx_1.py"
]

for script in scripts:
    subprocess.run(["python3", str(ROOT / script)], check=True)