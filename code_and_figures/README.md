# Code, data and figures — HGVS nomenclature compliance 2010–2026

Reproduces every number, table and figure in the manuscript and the Supplementary Information.

## Layout
- `analysis.py` — main-text meta-analysis (DerSimonian–Laird on logits, Wilson CIs) and the interrupted time series
  (segmented binomial regression, quasi-binomial scale, counterfactual, 2017 sensitivity, control series).
  Reads `data/studies.csv` and `data/eqa_yearly.csv`; writes `results.json`, `forest_data.csv`, `its_data.csv`.
- `analysis_supplementary.py` — Supplementary Figures S1–S9 and Tables S3–S13: per-scheme panel, interruption-year
  sweep, feedback dose–response, transitions, meta-analytic sensitivity (continuity corrections, Freeman–Tukey,
  fixed effect, Hartung–Knapp, prediction interval, leave-one-out), version omission, variant-stratified
  Mantel–Haenszel, findability, tool agreement, method and gene effects. Reads `data/*.csv` (and the two main CSVs:
  the script expects them one directory up as `../studies.csv` and `../eqa_yearly.csv`; adjust the paths at the top
  if you keep everything in `data/`). Writes `supp_results.json`, `S_*.csv`, `figures/S*.png`.
- `build_supp_docx.js` (Node, `docx` package) and `build_supp_xlsx.py` (openpyxl) rebuild Supplementary_Information.docx
  and Supplementary_Data.xlsx from the results.
- `charts/` — the three main-text figures as the hand-written SVG chart modules used in the manuscript document
  (forest plot, interrupted time series, four-scheme panel); their data rows are inline.
- `manuscript/refs.py` — the 72 verified reference records; `manuscript/build_manuscript.py` — numbers citations by
  first appearance and emits the section text (`sections.json`).
- `results/notes_sources.md` — verbatim numbers extracted from each source page, with URLs and access dates.

## Environment
Python 3.11+ with numpy, pandas, scipy, statsmodels 0.15, matplotlib, openpyxl; Node 18+ with the `docx` package;
LibreOffice for the PDF conversions. Run `python3 analysis.py` first, then `python3 analysis_supplementary.py`,
then the two build scripts.
