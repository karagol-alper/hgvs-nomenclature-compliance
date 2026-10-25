# Data dictionary

Every file holds counts or percentages extracted from a published paper (see `source` columns and
`docs/source_notes.md` for the verbatim numbers and the page each came from). Where a paper reports a percentage
and a denominator but not a count, the scripts recover the count as `round(pct × n / 100)`; those columns are named
`k`, `nomen_k`, `refseq_k` or `events` in the derived outputs.

| File | Content | Source |
| --- | --- | --- |
| `studies.csv` | Study-level estimates entering the forest plot: `events` / `n` per study, stratum, unit, outcome, period, source URL | Berwouts 2011 (via Keppens 2020), Keppens 2020, Lansdon 2026, Lefter 2021, Yen 2017, Chen 2025 |
| `eqa_yearly.csv` | Total EQA series by scheme year: % compliant nomenclature (`nomen_pct`, `nomen_n`) and % of reports citing a current-version LRG/NM reference sequence (`refseq_pct`, `refseq_n`; Keppens et al.'s reference-sequence compliance measure, 31.9% overall) | Keppens et al. 2020, Hum Mutat 41:7, Table 3 (Total column) |
| `eqa_provider_yearly.csv` | The same by provider (ESP, Gen&Tiss) and indication (NSCLC, mCRC) | Keppens 2020, Table 3 |
| `eqa_participations.csv` | Compliance by number of successive EQA participations (1–6) | Keppens 2020, Table 3 |
| `eqa_transitions.csv` | Compliance in the next scheme given the previous result | Keppens 2020, Table 3 |
| `eqa_methods.csv` | Compliance by test method (commercial / non-commercial, NGS / non-NGS) | Keppens 2020, Figure 1 and text |
| `eqa_genes.csv` | Compliance and share of type 2/3 errors by gene | Keppens 2020, text (its Table S1) |
| `eqa_error_types.csv` | Composition of outcomes among 4,053 scored entries | Keppens 2020, Results 3.1 |
| `eqa_returning_variants.csv` | Variants distributed in more than one scheme year, % compliant per year | Keppens 2020, Table 2 |
| `manuscript_criteria.csv` | Rubric results for 52 Genetics in Medicine / GIM Open manuscripts (critical / small / no error) | Lansdon et al. 2026, Clin Chem 72:652, Table 1 |
| `findability.csv` | 18 published variants searched in ClinVar, LitVar2 and Franklin | Lansdon 2026, Results |
| `tool_agreement.csv` | Agreement of HGVS descriptions between annotation tools and with ClinVar | Yen 2017 (Genome Med 9:7); Chen 2025 (Hum Genomics 19:70; counts back-computed from match fractions) |
| `journal_pilot.csv` | HUGO pilot of validation-file requirements at Human Mutation and Genetics in Medicine | Higgins et al. 2021, Hum Mutat 42:3 |
| `mutalyzer_assessments.csv` | Name Checker outcome composition, Sep 2014–Oct 2019 | Lefter et al. 2021, Bioinformatics 37:2811, Figure 3 |
| `hgvs_versions.csv` | Complete HGVS Nomenclature release log, 2000–2026 | hgvs-nomenclature.org version pages (accessed 20 Oct 2026); den Dunnen et al. 2016 |

Percent columns are stored as reported (12.1 means 12.1%). No individual-level or patient data are included.
