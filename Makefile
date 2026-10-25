# Reproduces every result, figure and supplementary file. Requires Python 3.11+ (requirements.txt) and Node 18+ (npm install).
.PHONY: all main supp xlsx docx manuscript clean

all: main supp xlsx docx manuscript

main:            ## meta-analysis + interrupted time series -> results/
	python3 src/analysis.py

supp: main       ## supplementary analyses -> results/, figures/
	python3 src/analysis_supplementary.py

xlsx: main       ## Supplementary Data workbook -> supplementary/
	python3 src/build_supp_xlsx.py

docx: supp       ## Supplementary Information document -> supplementary/ (needs `npm install`)
	node src/build_supp_docx.js

manuscript:      ## numbered citations + reference list -> results/manuscript_sections.json, results/references.md
	python3 src/manuscript/build_manuscript.py

clean:
	rm -rf results/* figures/* supplementary/*
