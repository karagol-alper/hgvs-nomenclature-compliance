# Correct use of HGVS nomenclature in clinical variant reporting and literature, 2010–2026

Analysis code and extracted data for the manuscript *Correct use of HGVS nomenclature in clinical variant reporting
and literature, 2010–2026: a meta-analysis of published audits and an interrupted time-series analysis of
nomenclature changes* by Alper Karagöl and Taner Karagöl (Istanbul University, Istanbul Medical Faculty; see
`CITATION.cff` for ORCIDs and present addresses).

The repository reproduces every number, table and figure in the main text and the Supplementary Information from
the counts in `data/`, which were extracted from the published audits listed in `data/README.md`.

## What it does

- **Meta-analysis of proportions** (`src/analysis.py`): Wilson 95% CIs; DerSimonian–Laird random-effects pooling on the
  logit scale; heterogeneity (Q, I²). Output: `results/results.json`, `results/forest_data.csv`.
- **Interrupted time series** (`src/analysis.py`): segmented binomial regression of the annual EQA compliance series
  (Keppens et al. 2020, 2012–2018) with the 2016 HGVS update as the interruption; quasi-binomial over-dispersion;
  counterfactual projection; break moved to 2017; control series (current-version reference sequence cited). Output:
  `results/its_data.csv` and `results/results.json`.
- **Supplementary analyses** (`src/analysis_supplementary.py`): replication in the four EQA sub-series, interruption-year
  sweep, feedback dose–response and transitions, variant-stratified Mantel–Haenszel comparison, meta-analytic
  sensitivity (continuity corrections, Freeman–Tukey, fixed effect, Hartung–Knapp, prediction interval,
  leave-one-out), version omission, test-method and gene effects, manuscript criteria, findability, tool agreement.
  Output: `results/supp_results.json`, `results/S_*.csv`, `figures/S1–S9.png`.
- **Supplementary files**: `src/build_supp_xlsx.py` writes `supplementary/Supplementary_Data.xlsx` (every count with
  its source; proportions and Wilson CIs as live formulas); `src/build_supp_docx.js` writes
  `supplementary/Supplementary_Information.docx` (methods, Figures S1–S9, Tables S1–S13, references).
- **Manuscript references** (`src/manuscript/`): `refs.py` holds the 72 verified reference records;
  `build_manuscript.py` numbers citations by first appearance and writes `results/manuscript_sections.json` and
  `results/references.md`.
- **Main-text figures** (`charts/`): the forest plot, the interrupted time series and the four-scheme panel as the
  hand-written SVG chart modules used in the manuscript document (data rows inline). Static PNG versions of the
  panel and of all supplementary figures are produced by `src/analysis_supplementary.py`.

## Reproduce

```bash
python3 -m pip install -r requirements.txt
npm install                     # only for the Supplementary Information .docx
./run_all.sh                    # or: make all
```

Individual steps: `make main`, `make supp`, `make xlsx`, `make docx`, `make manuscript`. Everything is derived from
`data/`; `results/`, `figures/` and `supplementary/` are regenerated and can be deleted (`make clean`).

Tested with Python 3.12, numpy 2.5, pandas 3.0, scipy 1.18, statsmodels 0.15, matplotlib 3.10, Node 20 and
`docx` 9. The Excel formulas were verified with LibreOffice; the `.docx` was rendered with LibreOffice.

## Layout

```
data/           extracted counts (one CSV per dataset) + data dictionary
src/            analysis and build scripts
src/manuscript/ reference records and citation numbering
charts/         SVG chart modules for the three main-text figures
docs/           verbatim source notes with URLs and access dates
results/        generated tables and model outputs (JSON, CSV)
figures/        generated supplementary figures (PNG, 300 dpi)
supplementary/  generated Supplementary Information (.docx) and Supplementary Data (.xlsx)
```

## Key results (from `results/`)

| Quantity | Estimate |
| --- | --- |
| Fully HGVS-compliant descriptions, pooled over three document-level audits | 14.2% (95% CI 7.5–25.1), I² = 96% |
| EQA reports, compliance before vs after the 2016 update | 3.9% (n = 933) → 22.2% (n = 779); RR 5.76 (4.07–8.14) |
| Level change at 2016 (segmented logit, quasi-binomial) | OR 4.82 (1.21–19.2); pre-slope OR 1.11/yr; slope change OR 1.07/yr |
| Break-year sweep, residual deviance 2014–2018 | 25.3, 24.2, 6.8, 10.8, 11.2 |
| Replication in the four EQA sub-series | RR 4.0, 4.6, 17.8, 9.7 (all p < 0.001) |
| Variant-stratified Mantel–Haenszel OR (9 variants) | 6.5 (4.9–8.5); 8 of 9 improved |

## Citation

See `CITATION.cff`. Data are from the published papers cited in `data/README.md`; please cite them when reusing
the counts.

## Licence

MIT (see `LICENSE`). The extracted counts remain subject to the terms of the papers they come from.
