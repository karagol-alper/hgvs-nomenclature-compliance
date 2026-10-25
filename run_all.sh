#!/usr/bin/env bash
# Reproduces every result, figure and supplementary file from the data in data/.
set -euo pipefail
cd "$(dirname "$0")"
python3 src/analysis.py
python3 src/analysis_supplementary.py
python3 src/build_supp_xlsx.py
python3 src/manuscript/build_manuscript.py
if [ -d node_modules/docx ]; then node src/build_supp_docx.js; else echo "skipping Supplementary_Information.docx (run: npm install)"; fi
echo "done: see results/, figures/, supplementary/"
