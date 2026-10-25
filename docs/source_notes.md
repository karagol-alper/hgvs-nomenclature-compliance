# Source notes (verbatim numbers extracted from fetched pages)

## Keppens C, Tack V, et al. Hum Mutat 2020;41(1):7-16. doi:10.1002/humu.23926 (PMC6973115)
Corpus: ESP + Gen&Tiss EQA written reports/datasheets, EGFR/KRAS/NRAS, 2012-2018, 351 international labs (ESP) + 64 French labs (Gen&Tiss).
- 4,802 entries; 749 (15.6%) no nomenclature; 4,053 assessed; 12.1% fully HGVS compliant.
- ESP 15.4% (n=2,530); Gen&Tiss 9.3% (n=1,523).
- By gene: EGFR 12.0% (2,377); KRAS 12.4% (1,217); NRAS 11.9% (459).
- Error types (of 4,053): type1 clerical 64.4%; type2 (prefix omitted/legacy/wrong aa code) 2.4%; type3 (only one level) 2.0%; combination 19.1%.
- Lab-level nomenclature compliance by scheme year (Total column, Table 3): 2012 2.0% (94); 2013 4.0% (301); 2014 4.2% (334); 2015 3.9% (204); 2016 17.4% (305); 2017 27.6% (268); 2018 22.3% (206).
- Reference-sequence compliance by year: 2012 16.7% (102); 2013 33.1% (330); 2014 27.5% (356); 2015 35.9% (206); 2016 34.3% (306); 2017 35.0% (286); 2018 33.0% (206).
- Ref seq overall (n=1,792 reports): 31.9% LRG/NM with current version; 9.5% previous version; 3.1% other format; 10.0% no version; 1.8% error; 43.8% none.
- By method: NGS 20.9% (447); commercial non-NGS 9.6% (768); noncommercial non-NGS 9.9% (717); noncommercial NGS 24.6% (300) vs commercial NGS 17.2% (147).
- By number of participations: 1: 4.6% (614) ... 5: 36.2% (152); 6: 19.5% (41).
- Paper states current HGVS version at time = 19.01; 2016 update examples: brackets for predicted protein changes, "variant" not "mutation", Ter/* not X for stop, X = any amino acid.
- Berwouts 2011 (cited): CFTR EQA, 22% of 631 reports HGVS-conforming; 5% nomenclature with potential to generate interpretation errors.
- Journals (Human Mutation, EJHG) require Mutalyzer/VariantValidator verification.

## Lansdon LA, Porath B, ..., Freeman PJ. Clin Chem 2026;72(6):652-661. doi:10.1093/clinchem/hvag010. Published 7 Mar 2026 (received 7 Oct 2025).
Corpus: 52 manuscripts submitted to Genetics in Medicine / GIM Open in 2023-2024, re-reviewed with standardized rubric.
- 100% (52/52) had >=1 critical error (expected to reduce findability).
- 51/52 (98%) critical error in small-variant (SNV/indel) nomenclature; most common = omission of g. and/or chromosome reference sequence.
- Reference sequence not provided: 25/52 (48%).
- c. nomenclature HGVS-compliant: 16/52 without error; 36 critical error.
- p. nomenclature: 13 without error; 27 small error (parentheses); 12 critical error (23%).
- g. nomenclature: 3 without error; 49 critical.
- Reference transcript version omitted: 5/52 (10%). Absent c.: 2/52 (4%); absent p.: 4/52 (8%).
- Genome build not indicated: 19/46 (41%) of NGS papers. Stable gene IDs missing: 44/52 (85%). Gene symbols not italicized: 19/52 (37%).
- Classification criteria omitted: 35/52 (67%).
- Findability (18 variants from 4 PMC manuscripts): exact-string search found in ClinVar 5/18 (28%), 9/18 (50%) with p. dropped; LitVar2 3/18 (17%), 6/18 (33%) with gene+c. only; Franklin 2/18 (11%); all three 2/18 (11%); any tool 15/18 (83%).
- Technical editing protocol: https://github.com/openvar/GIM_Technical_Editing (v1.0.0 Zenodo 10.5281/zenodo.18221414).
- Cites: Higgins et al. 2021 Hum Mutat 42:3-7 (HUGO pilot); Freeman et al. 2024 Nat Genet 56:2284-6; Chen et al. 2025 Hum Genomics 19:70; Conlin et al. 2025 Clin Chem 71:45-53; Park & Park 2022 Lab Med 53:242-5; Yen 2017 Genome Med 9:7.

## Lefter M, et al. Mutalyzer 2. Bioinformatics 2021;37(18):2811-2817. (from abstract/snippets)
- Mutalyzer launched Aug 2010; >133 million descriptions processed; over a 5-year period ~50% correct input, 41% syntactic or semantic error, ~7% auto-corrected; 15.8% failed syntactic check; 25.4% failed semantic check; 3' rule applied in 36% of cases; ~11% of inputs are 'no variant' notations. Human Mutation & EJHG require Mutalyzer/VariantValidator verification.

## HGVS Nomenclature official version history (hgvs-nomenclature.org/stable/versions/, /versions/21.1/, /versions/21.0/, /versions/older-versions/; fetched 2026-10-20)
- Version 0: pre-versions (Antonarakis 1998 etc.); Version 1: den Dunnen & Antonarakis 2000 publication.
- 2.120831 (31 Aug 2012): parentheses around protein descriptions may be omitted with experimental evidence; new upstream start codons p.Met1ext-5.
- 2.121101 (1 Nov 2012): stop-loss p.321Argext?; frameshift p.Ile321Argfs*?.
- 15.11 (Nov 2015; published den Dunnen et al. Hum Mutat 2016;37:564-569, online 25 Mar 2016, issue June 2016): accepted SVD-WG001 (no-change "=" e.g. g.11890634G=) and SVD-WG002 (n. reference type).
- 19.01 (Jan 2019): accepted SVD-WG006 (circular DNA), SVD-WG005 (methylation gom/lom), SVD-WG004 (named extension ISCN).
- 20.05 (May 2020): accepted SVD-WG007 (adjoined transcripts/gene fusions), SVD-WG008 (acceptable reference sequences requirements).
- 21.0.0 (Jan 2024; page lists 2024-08-12, likely typo; paper: Hart et al. Genome Med 2024): Semantic Versioning adopted; name "HGVS Nomenclature"; new domain hgvs-nomenclature.org; HVNC under HUGO; formal grammar started; syntax summary; software list; fusion recs aligned with VICC/HGNC/ISCN ("adjoined transcript").
- 21.0.1 (2024-02-22): deletion page updated; "indel" removed except where it should not be used.
- 21.0.2 (2024-03-15): syntax.yaml updated.
- 21.0.3 (2024-07-19): numbering diagram; supernumerary chromosomes fix; fusion formatting.
- 21.0.4 (2024-08-15): admin docs, MIT license; coding/non-coding identity handling changed.
- 21.1.0 (2024-11-16): fusion recommendations organized; clarified spaces not permitted; numbering page; LOVD HGVS syntax checker added to software list.
- 21.1.1 (2025-01-03): clarified "reference sequence" on substitution page.
- 21.1.2 (2025-03-10): SVD-WG010 rejected; history updated.
- 21.1.3 (2025-06-13): changed "X" to "Xaa"; negative examples highlighted.
- 21.1.4 (2026-05-11): repeats divisible by three only within CDS; SVD-WG011 added; ISCN docs improved.
- 21.1.5 (2026-09-17): in version menu, no notes.
- Versioning: x.y.z semantic; since 21.0.0 (Jan 2024) numbers are not dates; earlier numbers = YY.MM (15.11=Nov 2015, 19.01=Jan 2019, 20.05=May 2020) and 2.YYMMDD.

## Higgins J, Dalgleish R, den Dunnen JT, ..., Cutting GR. Hum Mutat 2021;42(1):3-7. doi:10.1002/humu.24144 (online 10 Dec 2020). Accepted manuscript from ORCA Cardiff.
HUGO/HVP committee (convened 2018) pilot, from April 2019:
- Human Mutation: 425 initial submissions over 6 months; 349 had variant data; 208 (over half) included the validation file. 187 manuscripts under revision reported variants; 162 included a validation file; 25 used alternative software or variants previously reported.
- Genetics in Medicine: 193 revised manuscripts over 3 months; 35 contained variant data, all 35 included a variant file; 4 sent back for correction.
- Recommendations: HGVS at DNA level in text/tables with reference genome version; verify with Mutalyzer/VariantValidator or supply ClinVar/LOVD IDs; provide output files; editorial compliance check; authors responsible.
- Aries integrated variant validation into Editorial Manager (no date).

## Yen JL, et al. Genome Med 2017;9:7. doi:10.1186/s13073-016-0396-7 (PMC5267466) — annotation-tool/database discordance
- Ground truth 126 variants; tools SnpEff v4.1L, VEP v82, Variation Reporter.
- SnpEff vs VEP exact match: c. 92.6% (100/108); p. 75% (81/108). VR vs others: <=50.6% c., 63.2% p.
- Accuracy vs ground truth: c. 80-90%; p. 50-70%.
- vs ClinVar (106,110 small variants): SNV c. concordance >99.9%; insertion concordance 75-80%; deletions c. 86%, insertions 88%; non-SNV protein 60-70% did not match ClinVar; 5-20% completely discordant (n=11,945).
- vs COSMIC (2,215,076 after normalization): exact c. match VEP 85.9%, SnpEff 76.8%; exact p. match SnpEff 75.8%, VEP 59.4%; insertions <15%; estimated COSMIC annotation error rate 5-10%.
- 3' rule: 16.6% (113/681) of ClinVar insertions wrong (right-shifting/duplication); ~522/568 coding discrepancies attributed to ClinVar right-shifting errors; COSMIC reported all duplications as insertions. ~10% of ClinVar transcript versions differed; 1.8% accessions absent.

## EMQN Variant Nomenclature Policy v13 (2024; DOC2702): requires latest HGVS (lists 20.05); since 2019 minor bracket/semicolon errors = feedback comments, no deduction; major errors (wrong nucleotide/aa) lose marks; LRG discontinued -> MANE Select/Plus Clinical; legacy names allowed alongside HGVS; predicted protein in parentheses.

## Freeman PJ, et al. Nat Genet 2024;56:2284-2286 (online 2 Oct 2024) — comment; Leiden repository copy
- ">95% of submitted manuscripts need correction of variant descriptions before publication" (GIM technical editing experience); "<2% of manuscripts contain the complete set of descriptions" HGVS requires. VariantValidator in use since 2018; REST API summer 2024.

## tmVar 3.0 (Wei et al., Bioinformatics 2022;38(18):4449-4451)
- Whole PubMed+PMC processed; normalized to RS IDs 50.23%, CA IDs 25.43%; "more than half of the variant mentions cannot be linked to an existing record in dbSNP or CAR"; edge cases: natural-language descriptions, missing spaces (BRAFV600E).

## Chen YA, et al. Hum Genomics 2025;19:70 (bioRxiv 2024.10.11.617756) — ClinVar (Jan 7 2024) 164,549 curated variants; ANNOVAR/SnpEff 5.2/VEP 111
- On ClinVar-selected transcripts: HGVSc agreement across all three tools 58.52%; HGVSp 84.04%; coding-impact 85.58%.
- Match to ClinVar HGVSc: SnpEff 0.988, VEP 0.977, ANNOVAR 0.753; HGVSp: VEP 0.991, SnpEff 0.986, ANNOVAR 0.981.
- Indel HGVSp match: ANNOVAR 0.646; SnpEff 0.722. Non-preferred syntax ~0.5-1.4% of HGVSp discrepancies.

## Lefter 2021 Mutalyzer 2 — detail (OUP full text)
- Logs Sep 2014 - Oct 2019 (five years). Name Checker ~87M descriptions, 20% (17M) unique; 26M unique across all tools resubmitted to Mutalyzer 2.0.32.
- Figure 3: correct, no warning 50.4%; correct with warnings ~1.2%; syntactically incorrect 15.8%; failed semantic analysis 25.4%; corrected/canonized ~7.1%; 'no variant' notations ~11%.
- 3' rule applied 36%; variant type updated per prioritization 29% (>65% ins->dup); accession without version 35%.
- Website inputs 85% syntactically correct; batch 80%; 95% of syntactic failures via web service.
- Human Mutation and EJHG require Mutalyzer-type verification.
