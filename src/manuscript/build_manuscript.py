"""Numbers citations by first appearance across the manuscript sections and writes per-section markdown + the
reference list to results/manuscript_sections.json. Citation syntax in the text: [@key] or [@key1; @key2].
Run: python3 src/manuscript/build_manuscript.py"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from refs import REFS

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = {}  # ordered sections

S['title_page'] = """**Full title:** Correct use of HGVS nomenclature in clinical variant reporting and literature, 2010–2026: a meta-analysis of published audits and an interrupted time-series analysis of nomenclature changes

**Running title:** HGVS nomenclature compliance, 2010–2026

**Authors:** Alper Karagöl¹†\\*, Taner Karagöl¹¶\\*

¹ Istanbul University, Istanbul Medical Faculty, Istanbul, Turkey

† Present address: Broad Institute of MIT and Harvard, Cambridge, MA, USA; Department of Mechanical Engineering, Massachusetts Institute of Technology, Cambridge, MA, USA

¶ Present address: McGovern Institute for Brain Research, Massachusetts Institute of Technology, Cambridge, MA, USA

\\* To whom correspondence should be addressed: Alper Karagöl (akaragol@mit.edu; ORCID 0009-0001-7864-0732); Taner Karagöl (karagolt@mit.edu; ORCID 0009-0005-1011-7661)

**Article type:** Original research (systematic review with meta-analysis and interrupted time-series analysis)

**Word count:** abstract {ABS_WORDS}; main text ≈ {MAIN_WORDS} (excluding tables, figure legends and references). 4 tables, 3 figures, Supplementary Information (9 figures, 13 tables), Supplementary Data, code archive.

**Keywords:** HGVS nomenclature; sequence variant description; external quality assessment; interrupted time series; meta-analysis; variant findability; clinical genomics; reporting standards"""

S['abstract'] = """## Abstract

**Background.** The Human Genome Variation Society (HGVS) nomenclature is the standard for describing sequence variants, but audits of its use are scattered across corpora and the effect of successive revisions of the standard on compliance has not been quantified.

**Methods.** Peer-reviewed audits (2011–2026) that counted HGVS-compliant and non-compliant variant descriptions in journal manuscripts, clinical reports, checker submissions and databases were pooled by random-effects meta-analysis of proportions, and the dated history of HGVS changes was compiled from the official version record. A segmented binomial regression was fitted to the only annual compliance series available, 1,712 external quality assessment (EQA) report entries scored 2012–2018, with the 2016 update (version 15.11) as the interruption; sensitivity analyses varied the break year and used a control series and four scheme sub-series.

**Results.** Nine studies were included, six with usable counts. Fully compliant descriptions were a minority in every corpus: pooled 14.2% (95% CI 7.5–25.1; I² = 96%) across three document-level audits, ranging from 0 of 52 manuscripts (2023–2024) to 50.4% of 26 million checker submissions. Omitted reference sequences (44–48%), genome builds (41%), misplaced parentheses (52%) and legacy protein-only names were the commonest errors. Compliance in EQA reports rose from 3.9% to 22.2% at the 2016 update (level-change odds ratio 4.82, 95% CI 1.21–19.2) with no trend before or after; 2016 was the best-fitting break year, the step replicated in all four sub-series (risk ratios 4.0–17.8) and the control series did not move. Later journal mandates raised validation-file attachment to 60–100% without eliminating errors.

**Conclusions.** HGVS nomenclature is used correctly in a minority of clinical variant descriptions. The 2016 update coincided with a one-off improvement in clinical reports that EQA feedback and automated annotation sustained; author instructions alone did not change what authors write, and automated validation at submission is the only intervention with a measured effect."""

S['introduction'] = """## Introduction

Unambiguous description of sequence variants underpins variant classification, data sharing and the retrieval of published evidence during diagnostic interpretation [@richards2015; @rehm2015; @landrum2018]. When a variant is described inconsistently, evidence about it cannot be found: searches of ClinVar, LitVar2 and Franklin with nomenclature exactly as published retrieved only 11–28% of variants from four recent clinical genetics articles [@lansdon2026; @allot2023]. Inconsistent description has also been linked to clinical misinterpretation, for example when a reference-sequence update moved the canonical BRAF substitution from p.Val599Glu to p.Val600Glu, or when cystic fibrosis carrier results were reported under legacy names [@tack2016; @keppens2020].

Proposals for a systematic variant nomenclature date from 1993 [@beaudet1993; @beutler1993], were consolidated by an ad hoc committee in 1996 [@adhoc1996; @beutler1996] and by the Nomenclature Working Group in 1998 [@antonarakis1998], and took their current form in the recommendations of den Dunnen and Antonarakis in 2000 and 2001 [@dendunnen2000; @dendunnen2001]. The recommendations, maintained by the Human Genome Variation Society (HGVS) and later by a committee under the Human Genome Organisation, were extended to structural variation [@taschner2011], formalized as a grammar [@laros2011], revised in the 2016 update that introduced dated version numbers [@dendunnen2016], and re-founded in January 2024 as version 21.0.0 with semantic versioning, a machine-readable grammar and a new website [@hart2024; @hgvsversions]. A tool ecosystem grew around them: the Mutalyzer and VariantValidator checkers [@wildeman2008; @lefter2021; @freeman2018], the hgvs Python package [@hart2015; @wang2018], the LOVD databases [@fokkema2011; @fokkema2021], ClinVar [@landrum2018], the ClinGen Allele Registry [@pawliczek2018] and the GA4GH Variation Representation Specification [@wagner2021], together with the reference-sequence sets the nomenclature depends on: RefSeq, Locus Reference Genomic and the MANE transcript set [@oleary2016; @macarthur2014; @morales2022]. Clinical reporting standards from the College of American Pathologists, the ACMG/AMP and the AMP/ASCO/CAP consortium adopted HGVS nomenclature for molecular reports [@gulley2007; @richards2015; @li2017], as did the cytogenomic nomenclature for sequence-level description of structural variants [@hastings2024] and the ACMG/ClinGen standard for copy-number variants [@riggs2020]; findability further depends on stable gene and disease identifiers from HGNC and OMIM [@seal2023; @amberger2019].

Whether the standard is actually followed has been examined piecemeal. External quality assessment (EQA) schemes have reported low compliance in BRCA1/2, hereditary fever, cystic fibrosis and oncology biomarker testing [@mueller2004; @touitou2009; @berwouts2011; @tack2016; @deans2016; @keppens2020], and EQA guidelines now require nomenclature to be scored [@vankrieken2013; @deans2017]. Journals have piloted validation-file requirements [@higgins2021], reported that more than 95% of submissions need nomenclature correction [@freeman2024], and found critical errors in every manuscript audited at Genetics in Medicine in 2023–2024 [@lansdon2026]. Annotation tools and databases disagree with one another on the HGVS description of the same variant [@yen2017; @park2022; @chen2025], a problem the standards community has acknowledged [@conlin2025], and literature-mining systems can link fewer than half of the variant mentions they find to any database record [@wei2013; @wei2022; @allot2023]. These findings have not been synthesized, and no study has tested whether revisions of the nomenclature itself changed how variants are written.

This study had four aims: to pool the published audits of HGVS usage into estimates of correct use by corpus; to compile the dated record of nomenclature changes from 2000 to 2026; to test, by interrupted time-series analysis, whether the 2016 update was followed by a change in compliance; and to catalogue the errors that audits find, as a basis for recommendations to journals, laboratories and standards bodies."""

S['methods'] = """## Methods

### Search strategy and study selection

The review followed the PRISMA 2020 principles for identification, screening and reporting [@page2021], adapted to a small literature. Searches were run on 20 October 2026 with a general web search engine over the terms "HGVS nomenclature compliance", "HGVS external quality assessment", "variant nomenclature errors manuscripts", "Mutalyzer literature variant descriptions" and "annotation discordance HGVS ClinVar", followed by forward and backward citation chasing from every retrieved study. PubMed, Europe PMC, Crossref and OpenAlex could not be queried from the analysis environment, so no controlled-vocabulary database search was possible; the search is therefore not exhaustive, and this is the principal limitation of the evidence base. Inclusion criteria were a peer-reviewed publication from 2010 to 2026 that scored variant descriptions against the HGVS recommendations current at the time and reported, or allowed recovery of, the number scored and the number compliant for a defined corpus. Commentaries without counts, tool papers without usage audits and studies of gene-symbol nomenclature alone were excluded. Of fourteen records retrieved, nine met the criteria (see Results) and six reported counts that enter the pooled analysis. Three included studies [@berwouts2011; @tack2016; @deans2016] and the 2024 nomenclature paper [@hart2024] could not be retrieved from their publishers and are represented through the figures reported by Keppens et al. [@keppens2020] and by the official HGVS version record [@hgvsversions].

### Definition of correct use and data extraction

A description was counted as fully compliant only when the audit scored it as complete and correct under the recommendations current at the time: a versioned reference sequence; the DNA level with its c. or g. prefix; the protein level with the p. prefix and, where the audit required it, parentheses around predicted changes; the 3′ rule; and the del, dup, ins and delins conventions [@dendunnen2016]. Legacy protein-only names (T790M, ΔF508) were non-compliant in every audit. Element-level outcomes (reference sequence given, version given, c., p. and g. levels, genome build) were extracted separately and never pooled with full-compliance outcomes. Where a paper reports a percentage and a denominator but not the count, the count was recovered as round(percentage × n / 100); these cells are marked in Supplementary Data. Corpora were stratified as journal manuscripts, clinical reports scored in EQA schemes, descriptions submitted to a nomenclature checker, and database or annotation-tool outputs, and pooled only within a stratum because the unit of analysis differs (manuscript, report, variant entry, submitted string, variant).

### Nomenclature change record

Versions and dates were taken from the HGVS Nomenclature version pages (21.0 and 21.1 series and the older-versions page) on 20 October 2026 [@hgvsversions] and from the 2016 and 2024 publications [@dendunnen2016; @hart2024]; adoption milestones were added from the HUGO journal guidance [@higgins2021; @hugorsv], the EMQN nomenclature policy [@emqn2024] and the ACMG/AMP standard [@richards2015].

### Statistical analysis

Proportions carry Wilson score 95% confidence intervals [@wilson1927; @newcombe1998]. Full-compliance proportions were pooled on the logit scale with DerSimonian–Laird random effects [@dersimonian1986], heterogeneity was quantified with Cochran's Q and I² [@higgins2002], and a zero cell received a 0.5 continuity correction. Because prevalence-type meta-analyses are sensitive to the transform and to small k, sensitivity analyses used continuity corrections of 0.1 and 1.0, the Freeman–Tukey double-arcsine transform with harmonic-mean back-transformation [@barendregt2013; @freemantukey1950], a fixed-effect model, Hartung–Knapp confidence intervals [@inthout2014], a 95% prediction interval and leave-one-out exclusion.

The interrupted time series used the only annual compliance series available, the "Total" column of the scheme-year table reported by Keppens et al. [@keppens2020] (2012–2018; 1,712 scored entries), and followed the segmented-regression approach of Wagner et al. and Lopez Bernal et al. [@wagner2002; @lopezbernal2017] adapted to binomial data: logit(p_t) = β0 + β1·t + β2·post_t + β3·(t − 2016)·post_t, with the proportion compliant as outcome, the number of entries as variance weight, t = year − 2012 and post_t = 1 from 2016, so that β2 is the level change at the 2016 update and β3 the change in slope. Over-dispersion was allowed by a quasi-binomial scale (Pearson χ²/df); the counterfactual is the pre-break model projected forward; autocorrelation was examined with the Durbin–Watson statistic on deviance residuals. Sensitivity analyses moved the break to each year from 2014 to 2018, fitted the same model to a control series (the share of reports citing a current-version LRG or RefSeq reference sequence, an element whose rules the 2016 update did not change), and fitted a panel of the four provider–indication sub-series with scheme fixed effects and a common break. Supplementary analyses used a weighted logistic trend for compliance by number of EQA participations, risk and odds ratios for transitions between successive schemes and for test-method and gene effects, and a Mantel–Haenszel odds ratio stratified by variant for the nine variants distributed both before and after 2016, with the Breslow–Day test and an exact sign test. All computation used Python 3 with numpy, pandas, scipy and statsmodels 0.15 [@seabold2010]; the scripts, the extracted counts and the figure files are provided as supplementary material."""

S['results_timeline'] = """## Results

### Changes to the HGVS nomenclature, 2000–2026

The rules authors are scored against changed substantively three times in the study window (Table 1): the 2016 update, which presented version 15.11 as the first dated version and set the conventions most often scored in audits ("variant" rather than "mutation", parentheses around predicted protein changes, Ter or * for a stop codon, X for an unknown amino acid) [@dendunnen2016]; versions 19.01 and 20.05, which added circular DNA, methylation and gene-fusion descriptions and the requirements for acceptable reference sequences [@hgvsversions]; and the January 2024 re-foundation as version 21.0.0, which brought semantic versioning, a formal grammar, a one-page syntax summary and governance under HUGO [@hart2024]. Every release since has been a minor or patch change, including the removal of "indel" (21.0.1), the prohibition of spaces inside a description (21.1.0) and the replacement of "X" by "Xaa" (21.1.3) [@hgvsversions]. Around the standard, the adoption milestones that could plausibly change practice were the ACMG/AMP interpretation standard of 2015 [@richards2015], the HUGO guidance asking journals to require checker output files (2020–2021) [@higgins2021; @hugorsv], and EQA policies that score nomenclature with a one-cycle grace period after each release [@emqn2024]. Dates are from the official version pages unless linked otherwise; newest first."""

S['results_audits'] = """### Included audits

Nine peer-reviewed studies met the inclusion criteria (Table 2), six of which report compliance counts that enter the forest plot; only one audits journal manuscripts systematically [@lansdon2026], and no study has scored published articles across journals, so the literature stratum rests on editorial-office data [@higgins2021; @freeman2024; @lansdon2026]. The clinical-report stratum is carried by two EQA audits [@berwouts2011; @keppens2020], the checker stratum by the Mutalyzer usage logs [@lefter2021], and the database and tool stratum by two studies of annotation concordance that compared SnpEff, VEP and ANNOVAR output with ClinVar and COSMIC [@yen2017; @chen2025; @cingolani2012; @mclaren2016; @wang2010; @tate2019] and by the whole-literature normalization statistics of tmVar 3.0 [@wei2022]. Percentages are plotted in Figure 1; the table holds what each audit scored and the findings that are not plotted."""

S['results_pooled'] = """### Compliance across corpora

Pooling the three document-level audits gives 14.2% fully compliant descriptions (95% CI 7.5–25.1%), but the studies disagree far more than chance allows (I² = 96%, τ² = 0.27 on the logit scale), so the pooled value summarizes a direction rather than estimating any one corpus (Figure 1). The two clinical-report audits alone pool to 16.4% (8.8–28.4%; I² = 98%), and the estimate is stable to the transform and the continuity correction (10.1–15.6%) but not to leaving out a study (5.0–16.4%; Supplementary Figure S7)."""

S['results_pooled2'] = """The one element that pools cleanly is whether a reference sequence is given at all: 56.1% (53.8–58.3%, I² = 0%) in clinical reports (2012–2018) [@keppens2020] and manuscripts (2023–2024) [@lansdon2026] alike, and among descriptions that do cite a reference the version is omitted at the same rate in both corpora (17.8% vs 18.5%; Supplementary Table S9). Within a description, the genomic level is the weakest element in manuscripts (3/52 error-free) and the protein level the next (13/52); between annotation tools, the protein level was the point of disagreement in 2017 (75% identical vs 93% for c.) [@yen2017], while by 2025 three tools agreed on p. more often than on c. (84% vs 59%), with indel p. descriptions still matching ClinVar in only 65–72% of cases [@chen2025]. Tool outputs agree with each other more often than authors agree with the rules, which is consistent with the effect of automation on compliance: next-generation sequencing pipeline users reached 20.9% full compliance in EQA reports against 9.6% (commercial) and 9.9% (non-commercial) for non-NGS methods (OR 2.43, 95% CI 1.82–3.23) [@keppens2020]."""

S['results_annual'] = """### Annual trend in EQA reports, 2012–2018

The only published series with a compliance rate for every year is the ESP and Gen&Tiss EQA data for EGFR, KRAS and NRAS reports [@keppens2020]: flat at 2–4% from 2012 to 2015, then 17–28% from 2016 onward, with no comparable step in the share of reports citing a current-version reference sequence (Figure 2). No yearly series exists for published articles, so the interrupted time series is estimated on clinical reports and read across to the literature with the caveats given in the Discussion."""

S['results_annual2'] = """The break sits where the rules changed: version 15.11 was dated November 2015, the 2016 update appeared online in March 2016 [@dendunnen2016], 2016 was the first scheme year after it, and Keppens et al. score parentheses on predicted protein changes as required only from 2016 [@keppens2020]. The same laboratories were also receiving EQA feedback each year, so the step reflects rule change and feedback together."""

S['results_its'] = """### Interrupted time-series estimates

The 2016 interruption is a level change, not a trend: the odds of a fully compliant description rose 4.8-fold in 2016 (OR 4.82, 95% CI 1.21–19.2 after over-dispersion correction; 1.93–12.0 under a plain binomial), about +15 percentage points against the projected pre-2016 trend, with no detectable slope before (OR 1.11 per year) or change in slope after (OR 1.07 per year) (Table 3). Pooled, 3.9% of 933 entries were compliant in 2012–2015 and 22.2% of 779 in 2016–2018 (risk ratio 5.76, 95% CI 4.07–8.14); by 2018 the fitted series sits 19.8 points above the counterfactual."""

S['results_sens'] = """**Sensitivity.** Refitting the main model with the break at each year from 2014 to 2018 gives residual deviances of 25.3, 24.2, 6.8, 10.8 and 11.2 (Supplementary Figure S2): the data place the break in 2016, the first scheme year after version 15.11. With the break forced to 2017 the effect dissolves into a steep pre-trend (OR 1.85 per year) with no level change (1.17, 0.46–2.99). The control series, the share of reports citing a current-version LRG or RefSeq reference sequence, shows no 2016 step (level OR 0.84, 0.38–1.87; 30.0% before vs 34.2% after, risk ratio 1.14, 1.00–1.31): the update changed how variants were written, not how laboratories cited their reference sequence."""

S['results_repl'] = """**Replication across schemes.** The step is not a feature of one scheme or one tumour type: each of the four provider–indication sub-series rose between 4.0- and 17.8-fold from 2012–2015 to 2016–2018 (Figure 3), and the nine variants distributed both before and after 2016 improved within variant (Mantel–Haenszel OR 6.5, 95% CI 4.9–8.5; eight of nine improved; Supplementary Figure S4). In a panel model with scheme intercepts the level change is 3.0 (0.6–14.2), imprecise because each sub-series has only five or six points and the Gen&Tiss series end in 2017."""

S['results_attrib'] = """**What the step can and cannot be attributed to.** The 2016 update redefined compliance (parentheses on predicted protein changes scored as required from 2016; Ter or * instead of X), so the post-2016 rates are measured against a stricter rule and still rose. The same laboratories were also receiving yearly EQA feedback: compliance rises with each successive participation (OR 1.65 per participation, 95% CI 1.38–1.98; 4.6% at a first participation, 36.2% at a fifth; Supplementary Figure S3), and a laboratory that was correct in one scheme was 5.0 times (3.9–6.4) as likely to be correct in the next [@keppens2020]. NGS adoption raised compliance on its own (OR 2.43, 1.82–3.23). A seven-point series cannot apportion the step among these; the shape still matters, because a one-year step followed by a flat trend is what a rule change produces, whereas cumulative learning alone would show a rising slope. The feedback gradient (OR 1.65 per participation) and the unsegmented calendar gradient (OR 1.65 per year) are the same size, as expected when laboratories accrue about one participation a year, so the two cannot be separated without laboratory-level data."""

S['results_read'] = """**Reading across to the literature.** No annual series exists for published articles, so the literature can only be anchored at points: in 2019, 60% of initial Human Mutation submissions with variants carried a checker file and 4 of 35 Genetics in Medicine revisions were returned for errors [@higgins2021]; in 2023–2024, after the HUGO guidance and VariantValidator integration, 0 of 52 Genetics in Medicine and GIM Open submissions were fully compliant [@lansdon2026]. Editorial mandates changed what authors attach, not what they write."""

S['results_errors'] = """### Nomenclature errors

Omitted context (reference sequence, version, genome build, g. level) is the dominant critical error in manuscripts [@lansdon2026]; clerical slips in the protein description dominate clinical reports [@keppens2020]; the 3′ rule and transcript versions dominate database and tool discordance [@yen2017; @chen2025] (Table 4). Frequencies are per audit and are not comparable across rows; the examples are those printed in the audits' own tables and text."""

S['discussion'] = """## Discussion

Across every peer-reviewed audit from 2011 to 2026, a minority of clinical variant descriptions are written correctly in HGVS nomenclature, and the failures are mostly omissions rather than syntax: the reference sequence, its version, the genome build or the genomic-level description is missing, or a legacy protein-only name stands alone. The one dated change in the standard that could be tested, the 2016 update, was followed by a single step in compliance in clinical reports that replicated across four independent EQA sub-series and within individual variants, had the best fit of any candidate break year, and was absent from a control measure. Later interventions aimed at the literature changed what authors attach to a submission, not what they write in it.

The step cannot be attributed to the rule change alone. The laboratories whose reports were scored were receiving individual EQA feedback every year, compliance rises monotonically with the number of participations, and laboratories that were correct once were five times as likely to be correct again [@keppens2020; @keppens2018; @tack2015; @dequeker2016]. Adoption of NGS pipelines, whose annotation software writes HGVS descriptions automatically [@callenberg2018; @wang2018], doubled the odds of compliance independently of year. What the time-series shape adds is that these mechanisms did not act gradually: compliance was flat for four scheme years and rose in the first year the updated recommendations were scored, which is the signature of a change in the target rather than of accumulating skill. A plausible reading is that the 2016 publication gave EQA providers, kit manufacturers and pipeline developers a single, citable specification to converge on, and that feedback then held the gain.

The findings agree with and extend the earlier EQA literature, which reported 22% HGVS-conforming cystic fibrosis reports [@berwouts2011], highly variable EGFR descriptions in the UK scheme [@deans2016] and improvement correlated with scheme duration [@tack2016], and with the editorial-office studies, which found that validation files are supplied when requested [@higgins2021] but that errors persist in essentially all submissions [@freeman2024; @lansdon2026]. They also connect the author-side problem to the tool-side one: the same elements that authors omit or misplace (reference version, 3′ shifting, protein syntax) are those on which annotation tools and databases disagree [@yen2017; @park2022; @chen2025], and the machine-readable grammar introduced in version 21.0.0 [@hart2024], the Variation Representation Specification [@wagner2021], allele identifiers [@pawliczek2018] and the MANE reference set [@morales2022] address exactly these ambiguities. The literature-mining evidence points the same way: when more than half of variant mentions in PubMed cannot be linked to a database record [@wei2022], the loss is on the author side, not the indexer's.

Three implications follow. For journals, author instructions and validation-file requirements are not enough; the Genetics in Medicine experience shows that a technical-editing step with VariantValidator or Mutalyzer output in the loop is what catches the omissions [@lansdon2026; @freeman2018; @lefter2021], and integration into submission systems removes the burden from editors [@hugorsv; @freeman2024]. For laboratories and EQA providers, scoring against the current version with a defined grace period [@emqn2024; @vankrieken2013; @deans2017] and passing reports through a checker before release are the measures with evidence behind them, and cancer reporting standards already require the elements most often missing [@li2017; @gulley2007]. For standards bodies, the 2024 re-foundation makes compliance machine-checkable for the first time; the audits summarized here provide the baseline against which the effect of versions 21.x can be measured when post-2024 EQA and editorial data become available."""

S['discussion_limits_intro'] = """### Limitations

The pooled figures summarize a small, heterogeneous set of audits, and the time series rests on one corpus; the direction and the order of magnitude are robust, the decimals are not."""

S['discussion_recs_intro'] = """### Recommendations

Automated validation at submission is the only intervention with a measured effect on the written description (NGS-pipeline users and fifth-time EQA participants reach 21–36% full compliance, against 4.6% at a first participation and 9.6–9.9% for non-NGS methods), while author instructions alone have none (100% of audited 2023–2024 manuscripts still failed). The actions below follow from the error catalogue."""

S['conclusions'] = """## Conclusions

Correct use of HGVS nomenclature in clinical variant descriptions has been the exception rather than the rule throughout 2010–2026, in manuscripts, clinical reports, checker inputs and databases alike. The 2016 revision of the standard coincided with a one-off, replicated improvement in clinical reports that feedback and automation sustained; the revisions and mandates that followed have so far changed attachments and metadata more than the descriptions themselves. Because version 21 of the nomenclature is now machine-checkable, the practical route to compliance is validation built into submission and reporting systems rather than reliance on authors, and the counts assembled here give the baseline against which that route can be evaluated."""

S['declarations'] = """## Declarations

**Data availability.** All counts analysed were extracted from the published papers cited and are provided, with their sources, in Supplementary Data (XLSX). No new patient or laboratory data were collected.

**Code availability.** The analysis scripts (Python 3; numpy, pandas, scipy, statsmodels, matplotlib), the extracted datasets and the scripts that rebuild the supplementary files are provided in the Supplementary Code and Figures archive.

**Funding.** No specific funding was received for this work.

**Competing interests.** The authors declare no competing interests.

**Author contributions.** A.K. and T.K. conceived and designed the study. A.K. performed the literature searches, data extraction, statistical analyses and visualization and wrote the first draft. T.K. verified the extracted data and the analyses and revised the manuscript critically for intellectual content. Both authors read and approved the final manuscript.

**Ethics approval.** Not applicable; the study analyses published aggregate data only.

**Declaration of generative AI and AI-assisted technologies in the manuscript preparation process.** During the preparation of this work, the authors used Claude Opus 5 Max (Anthropic) for drafting and for streamlining the analysis code. The authors reviewed and edited the output as needed and take full responsibility for the content of the published article."""

# ------------------------------------------------------------------ numbering
order = []
def number(key):
    if key not in REFS:
        raise KeyError(key)
    if key not in order:
        order.append(key)
    return order.index(key) + 1

def render(text):
    def rep(m):
        keys = [k.strip().lstrip('@') for k in m.group(1).split(';')]
        nums = sorted(number(k) for k in keys)
        # compress runs
        out, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
            out.append(str(nums[i]) if j == i else (f"{nums[i]},{nums[j]}" if j == i + 1 else f"{nums[i]}–{nums[j]}"))
            i = j + 1
        return '[' + ','.join(out) + ']'
    return re.sub(r'\[(@[^\]]+)\]', rep, text)

rendered = {}
for name, text in S.items():
    rendered[name] = render(text)
abs_words = len(re.sub(r'[#*]', '', rendered['abstract']).replace('Abstract', '').split())
main_words = sum(len(re.sub(r'[#*]', '', rendered[n]).split()) for n in rendered if n not in ('references', 'title_page', 'abstract'))
# the doc keeps the limitations bullets, recommendations checklist and figure/table captions outside these sections: add their approximate size
main_words_total = main_words + 700
rendered['title_page'] = rendered['title_page'].replace('{ABS_WORDS}', str(abs_words)).replace('{MAIN_WORDS}', f"{round(main_words_total, -2):,}")

refs_md = '## References\n\n' + '\n'.join(f"{i + 1}. {REFS[k]}" for i, k in enumerate(order))
rendered['references'] = refs_md
os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
with open(os.path.join(ROOT, 'results', 'manuscript_sections.json'), 'w', encoding='utf-8') as fh:
    json.dump({'sections': rendered, 'order': order}, fh, indent=1, ensure_ascii=False)
with open(os.path.join(ROOT, 'results', 'references.md'), 'w', encoding='utf-8') as fh:
    fh.write(rendered['references'])
print(len(order), 'references cited')
unused = [k for k in REFS if k not in order]
print('unused keys:', unused)
words = sum(len(re.sub(r'[#*]', '', rendered[n]).split()) for n in rendered if n not in ('references', 'title_page', 'abstract'))
print('main text words (sections here, excluding tables/legends/lists kept in doc):', words)
print('abstract words:', len(re.sub(r'[#*]', '', rendered['abstract']).split()))
