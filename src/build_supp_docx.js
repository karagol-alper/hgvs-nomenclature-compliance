// Builds supplementary/Supplementary_Information.docx from results/*.json, results/*.csv, data/*.csv and figures/*.png
// Run: node src/build_supp_docx.js  (needs the `docx` npm package: npm install)
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, AlignmentType,
  ImageRun, PageBreak, BorderStyle, ShadingType, Footer, PageNumber, LevelFormat
} = require('docx');

const ROOT = path.resolve(__dirname, '..');
const RES = f => path.join(ROOT, 'results', f), DATA = f => path.join(ROOT, 'data', f), FIG = f => path.join(ROOT, 'figures', f);
const R = JSON.parse(fs.readFileSync(RES('supp_results.json'), 'utf8'));
const MAIN = JSON.parse(fs.readFileSync(RES('results.json'), 'utf8'));

function csv(file) {
  const txt = fs.readFileSync(file, 'utf8').trim().split(/\r?\n/);
  const split = line => { const out = []; let cur = '', q = false; for (const ch of line) { if (ch === '"') q = !q; else if (ch === ',' && !q) { out.push(cur); cur = ''; } else cur += ch; } out.push(cur); return out; };
  const hd = split(txt[0]);
  return txt.slice(1).map(line => { const cells = split(line); const o = {}; hd.forEach((h, i) => o[h] = cells[i]); return o; });
}
const forest = csv(RES('forest_data.csv'));
const versions = csv(DATA('hgvs_versions.csv'));
const perSeries = csv(RES('S_per_series_pre_post.csv'));
const sweep = csv(RES('S_interruption_sweep.csv'));
const parts = csv(RES('S_participations.csv'));
const strata = csv(RES('S_returning_variants_strata.csv'));
const criteria = csv(RES('S_manuscript_criteria.csv'));
const findab = csv(RES('S_findability.csv'));
const tools = csv(RES('S_tool_agreement.csv'));
const pilot = csv(DATA('journal_pilot.csv'));

const f1 = x => (Math.round(Number(x) * 10) / 10).toFixed(1);
const f2 = x => (Math.round(Number(x) * 100) / 100).toFixed(2);
const pct = x => f1(100 * Number(x));
const pfmt = p => { p = Number(p); return p < 0.001 ? '< 0.001' : p.toFixed(3); };
const orci = (o) => `${f2(o.OR)} (${f2(o.lo)}–${f2(o.hi)})`;

// ---------- primitives ----------
const FONT = 'Arial';
const body = (text, opts = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, children: [new TextRun({ text, font: FONT, size: 20, ...opts })] });
const bodyRuns = (runs) => new Paragraph({ spacing: { after: 120, line: 276 }, children: runs.map(r => new TextRun({ font: FONT, size: 20, ...r })) });
const h1 = text => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 120 }, children: [new TextRun({ text, font: FONT, bold: true, size: 28 })] });
const h2 = text => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 }, children: [new TextRun({ text, font: FONT, bold: true, size: 24 })] });
const caption = (label, text) => new Paragraph({ spacing: { before: 80, after: 160, line: 260 }, children: [new TextRun({ text: label + ' ', font: FONT, bold: true, size: 19 }), new TextRun({ text, font: FONT, size: 19 })] });
const bullet = text => new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text, font: FONT, size: 20 })] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

const TABLE_W = 9638; // A4 text width at 2.54 cm margins ≈ 6.69 in = 9638 DXA
function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cols = widths.map(w => Math.round(w / total * TABLE_W));
  const cell = (text, i, head) => new TableCell({
    width: { size: cols[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: 'EEEEEE', color: 'auto' } : undefined,
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ spacing: { after: 0, line: 240 }, children: [new TextRun({ text: String(text), font: FONT, size: 16, bold: !!head })] })]
  });
  return new Table({
    width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: cols,
    borders: { top: { style: BorderStyle.SINGLE, size: 4, color: '999999' }, bottom: { style: BorderStyle.SINGLE, size: 4, color: '999999' }, left: { style: BorderStyle.NONE, size: 0 }, right: { style: BorderStyle.NONE, size: 0 }, insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'DDDDDD' }, insideVertical: { style: BorderStyle.NONE, size: 0 } },
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }), ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, i, false)) }))]
  });
}
function figure(file, widthIn = 6.5) {
  const buf = fs.readFileSync(FIG(file));
  // png dimensions
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = Math.round(widthIn * 96), hpx = Math.round(wpx * h / w);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, children: [new ImageRun({ type: 'png', data: buf, transformation: { width: wpx, height: hpx } })] });
}

// ---------- content ----------
const its = MAIN.its_nomenclature_2016, its17 = MAIN.its_nomenclature_2017, itsRef = MAIN.its_refseq_2016;
const panel = R.A_per_provider_panel, dose = R.C_dose_response, trans = R.D_transitions, meta = R.E_meta_sensitivity, vo = R.F_version_omission, mh = R.G_returning_variants.summary;

const children = [];
children.push(new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: 'Supplementary Information', font: FONT, bold: true, size: 32 })] }));
children.push(new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: 'Correct use of HGVS nomenclature in clinical variant reporting and literature, 2010–2026: a meta-analysis of published audits and an interrupted time-series analysis of nomenclature changes', font: FONT, size: 24 })] }));
// ---- authors
const affil = (runs, after = 40) => new Paragraph({ spacing: { after, line: 260 }, children: runs.map(r => new TextRun({ font: FONT, size: 18, ...r })) });
children.push(new Paragraph({ spacing: { before: 60, after: 60 }, children: [
  new TextRun({ text: 'Alper Karagöl', font: FONT, size: 22 }), new TextRun({ text: '1,†,*', font: FONT, size: 22, superScript: true }),
  new TextRun({ text: ', Taner Karagöl', font: FONT, size: 22 }), new TextRun({ text: '1,¶,*', font: FONT, size: 22, superScript: true })] }));
children.push(affil([{ text: '1', superScript: true }, { text: ' Istanbul University, Istanbul Medical Faculty, Istanbul, Turkey' }]));
children.push(affil([{ text: '†', superScript: true }, { text: ' Present address: Broad Institute of MIT and Harvard, Cambridge, MA, USA; Department of Mechanical Engineering, Massachusetts Institute of Technology, Cambridge, MA, USA' }]));
children.push(affil([{ text: '¶', superScript: true }, { text: ' Present address: McGovern Institute for Brain Research, Massachusetts Institute of Technology, Cambridge, MA, USA' }]));
children.push(affil([{ text: '*', superScript: true }, { text: ' To whom correspondence should be addressed: Alper Karagöl (akaragol@mit.edu; ORCID 0009-0001-7864-0732); Taner Karagöl (karagolt@mit.edu; ORCID 0009-0005-1011-7661)' }], 120));
children.push(body('Prepared 22 October 2026. Companion files: Supplementary_Data.xlsx (every count used, one sheet per dataset) and analysis code (analysis.py, analysis_supplementary.py).', { italics: true, color: '555555' }));
children.push(h2('Contents'));
['Supplementary Methods: S1 search and selection; S2 extraction and scoring; S3 statistical models',
 'Supplementary Figures S1–S9',
 'Supplementary Tables S1–S13',
 'Supplementary References'].forEach(t => children.push(bullet(t)));

// ---- Methods
children.push(h1('Supplementary Methods'));
children.push(h2('S1. Search strategy and study selection'));
children.push(body('Searches were run on 20 October 2026 with a general web search engine over the terms "HGVS nomenclature compliance", "HGVS external quality assessment", "variant nomenclature errors manuscripts", "Mutalyzer literature variant descriptions", "annotation discordance HGVS ClinVar", and the titles of papers cited by each retrieved study (citation chasing in both directions). PubMed, Europe PMC, Crossref and OpenAlex could not be queried from the analysis environment, so no database search with controlled vocabulary was possible and the search is not exhaustive; this is the principal limitation of the evidence base.'));
children.push(body('Inclusion: peer-reviewed publication (2010–2026) that scored variant descriptions against the HGVS recommendations current at the time and reported, or allowed recovery of, the number scored and the number compliant for a defined corpus (journal manuscripts, clinical reports, checker submissions, database or annotation-tool output). Exclusion: commentaries without counts; tool papers without usage audits; studies on gene-symbol nomenclature only.'));
children.push(body('Fourteen records were retrieved and read in full where the publisher page could be fetched; nine met the inclusion criteria (Table 2 of the main text), six of which report counts that enter Figure 1. Three records (Tack et al. 2016; Deans et al. 2016; Berwouts et al. 2011) could not be fetched from the publisher and are represented through the figures reported in Keppens et al. 2020; Hart et al. 2024 is represented through its abstract record and the official HGVS version pages. The HGVS version history was taken from hgvs-nomenclature.org (versions pages for the 21.0 and 21.1 series and the older-versions page) on 20 October 2026.'));

children.push(h2('S2. Extraction and scoring'));
children.push(body('A description was counted as fully compliant only when the audit scored it as complete and correct under the recommendations current at the time: a versioned reference sequence; the DNA level with its c. or g. prefix; the protein level with the p. prefix and, where the audit required it, parentheses around predicted changes; the 3′ rule; and the del, dup, ins and delins conventions. Legacy protein-only names (T790M, ΔF508) were non-compliant in every audit. Where a paper reports a percentage and a denominator but not the count, the count was recovered as round(percentage × n / 100); these cells are marked "back-computed" in Supplementary Data. Element-level outcomes (reference sequence given; version given; c. level; p. level; g. level; genome build) were extracted separately and never pooled with full-compliance outcomes.'));
children.push(body('Corpus strata, pooled only within a stratum: journal manuscripts and articles; clinical reports scored in external quality assessment (EQA) schemes; descriptions submitted to a nomenclature checker; database or annotation-tool outputs. The unit of analysis differs between strata (manuscript, report, variant entry, submitted string, variant) and is stated with every estimate.'));

children.push(h2('S3. Statistical models'));
children.push(body('Proportions. Wilson score 95% confidence intervals for every proportion. Random-effects pooling on the logit scale with DerSimonian–Laird τ²; zero cells received a continuity correction of 0.5 (sensitivity: 0.1 and 1.0, and a Freeman–Tukey double-arcsine transform with harmonic-mean back-transformation). Heterogeneity as Cochran Q and I². Hartung–Knapp confidence intervals and a 95% prediction interval (t distribution with k − 2 degrees of freedom) were computed for the main pooled estimate; leave-one-out estimates omit each study in turn.'));
children.push(body('Interrupted time series. For the annual EQA series (Keppens et al. 2020, Table 3, "Total" column; 2012–2018; 1,712 scored entries) a segmented binomial regression with logit link was fitted with the proportion compliant as outcome and the number of entries as variance weight: logit(p_t) = β0 + β1·t + β2·post_t + β3·(t − 2016)·post_t, where t = year − 2012 and post_t indicates 2016 or later; β2 is the level change and β3 the change in slope. Over-dispersion was allowed by a quasi-binomial scale (Pearson χ²/df). The counterfactual is the pre-break model projected forward. Autocorrelation was checked with the Durbin–Watson statistic on deviance residuals. Sensitivity: the break moved to each year 2014–2018 (the 2018 model has no post-break slope term); a control series (the share of reports citing a current-version LRG or RefSeq reference sequence, an element whose rules the 2016 update did not change) fitted identically; and a panel of the four provider–indication sub-series with scheme fixed effects and a common break, plus a model with scheme-specific level changes.'));
children.push(body('Other comparisons. Risk ratios and odds ratios with Wald 95% CIs; χ² or Fisher exact tests for 2 × 2 tables; a weighted logistic trend for compliance by number of EQA participations; a Mantel–Haenszel odds ratio stratified by variant for the nine variants distributed both before and after 2016, with the Breslow–Day test for homogeneity and an exact sign test on the direction of change. All computation in Python 3 with numpy, pandas, scipy and statsmodels 0.15; the scripts reproduce every number in the main text and this supplement.'));

// ---- Figures
children.push(pageBreak());
children.push(h1('Supplementary Figures'));
const figs = [
  ['S1_per_provider_panel.png', 'Supplementary Figure S1.', `Replication of the 2016 step in each EQA sub-series. Laboratory-level HGVS compliance per scheme year in the European Society of Pathology (ESP) and Gen&Tiss schemes for non-small-cell lung cancer (NSCLC) and metastatic colorectal cancer (mCRC), with Wilson 95% CIs; grey lines show the other three series. Pooled rates before and after 2016: ${perSeries.map(r => `${r.series} ${f1(r.pre_pct)}% → ${f1(r.post_pct)}% (RR ${f2(r.RR)}, ${f2(r.RR_lo)}–${f2(r.RR_hi)})`).join('; ')}. Data: Keppens et al. 2020, Table 3.`],
  ['S2_interruption_sweep.png', 'Supplementary Figure S2.', `Interruption-year sensitivity. The segmented logit model for the total EQA series refitted with the break placed at each year 2014–2018. Left: residual deviance (${sweep.map(s => `${s.cut}: ${f1(s.deviance)}`).join('; ')}); right: level-change odds ratio with quasi-binomial 95% CI. The 2016 break fits best; the 2018 model has no post-break slope term.`],
  ['S3_dose_response.png', 'Supplementary Figure S3.', `Feedback dose–response. Compliance by the number of successive EQA participations by a laboratory (1–6), with Wilson 95% CIs and the number of entries; grey: reference sequence given in LRG/NM format with version. Weighted logistic trend: OR ${f2(dose.all_1_to_6.OR_per_participation)} (${f2(dose.all_1_to_6.lo)}–${f2(dose.all_1_to_6.hi)}) per participation over 1–6 and ${f2(dose.excluding_6th.OR_per_participation)} (${f2(dose.excluding_6th.lo)}–${f2(dose.excluding_6th.hi)}) over 1–5; reference sequence OR ${f2(dose.reference_sequence_all.OR_per_participation)} (${f2(dose.reference_sequence_all.lo)}–${f2(dose.reference_sequence_all.hi)}). Data: Keppens et al. 2020, Table 3.`],
  ['S4_returning_variants.png', 'Supplementary Figure S4.', `Within-variant change for the nine variants distributed in EQA schemes both before and after 2016. Entries pooled per variant across its pre- and post-2016 scheme years. ${mh.improved} of ${mh.n_variants} improved (sign test p = ${pfmt(mh.sign_test_p)}); Mantel–Haenszel OR ${f2(mh.OR_MH)} (${f2(mh.OR_lo)}–${f2(mh.OR_hi)}), risk ratio ${f2(mh.RR_MH)}; Breslow–Day homogeneity p = ${pfmt(mh.breslow_day_p)}. Data: Keppens et al. 2020, Table 2.`],
  ['S5_manuscript_criteria.png', 'Supplementary Figure S5.', 'Manuscript-level errors by rubric criterion in 52 manuscripts submitted to Genetics in Medicine and Genetics in Medicine Open in 2023–2024 (dark: critical error; light: small error); n varies because genome-build criteria apply only to the 46 NGS manuscripts and CNV criteria to the 9 CNV manuscripts. Data: Lansdon et al. 2026, Table 1.'],
  ['S6_findability.png', 'Supplementary Figure S6.', 'Findability of 18 published variants from four Genetics in Medicine articles in ClinVar, LitVar2 and Franklin when searched with the nomenclature exactly as published (blue) or with a modified string (grey); Wilson 95% CIs. Data: Lansdon et al. 2026.'],
  ['S7_meta_sensitivity.png', 'Supplementary Figure S7.', `Sensitivity of the pooled full-compliance estimate (k = 3 document-level audits) to the pooling model, transform, continuity correction, confidence-interval method and leave-one-out exclusion. Main estimate ${pct(meta['main_logit_cc0.5'].re)}% (${pct(meta['main_logit_cc0.5'].re_lo)}–${pct(meta['main_logit_cc0.5'].re_hi)}); I² = ${f1(meta['main_logit_cc0.5'].I2)}%.`],
  ['S8_method_gene.png', 'Supplementary Figure S8.', `Full compliance by test method (left) and share of entries with a type 2 or 3 error (potential therapeutic impact) by gene (right), with Wilson 95% CIs. NGS vs non-NGS methods: OR ${f2(R.K_methods.NGS_vs_nonNGS.OR)} (${f2(R.K_methods.NGS_vs_nonNGS.lo)}–${f2(R.K_methods.NGS_vs_nonNGS.hi)}); compliance did not differ between genes (χ² p = ${pfmt(R.J_genes.compliance_chi2_p)}) but serious errors did (p < 0.001; EGFR vs KRAS RR ${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.RR)}, ${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.lo)}–${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.hi)}). Data: Keppens et al. 2020.`],
  ['S9_error_composition.png', 'Supplementary Figure S9.', 'Composition of outcomes in the EQA audit (left; Keppens et al. 2020: type 1 = clerical, type 2 = prefix omitted, legacy name or wrong amino-acid code, type 3 = one level only) and of Mutalyzer Name Checker assessments of 26 million unique submitted descriptions, September 2014 to October 2019 (right; Lefter et al. 2021, Figure 3).'],
];
figs.forEach(([file, label, legend], i) => { children.push(figure(file)); children.push(caption(label, legend)); if (i < figs.length - 1) children.push(pageBreak()); });

// ---- Tables
children.push(pageBreak());
children.push(h1('Supplementary Tables'));

children.push(caption('Supplementary Table S1.', 'Complete HGVS Nomenclature release log, 2000–2026, newest first (hgvs-nomenclature.org version pages, accessed 20 October 2026; den Dunnen et al. 2016 for version 15.11).'));
children.push(table(['Date', 'Version', 'Type', 'Change'], versions.map(v => [v.date, v.version, v.type, v.change]), [1.2, 1, 1, 6]));

children.push(caption('Supplementary Table S2.', 'Study-level estimates entering Figure 1 (Wilson 95% CIs; counts back-computed from published percentages where the paper reports no count) and the HUGO journal pilot (Higgins et al. 2021).'));
children.push(table(['Estimate', 'Stratum', 'Outcome', 'Period', 'Events / n', '% (95% CI)'],
  forest.map(r => [r.study, r.stratum, r.outcome, r.period, `${Number(r.events).toLocaleString('en-US')} / ${Number(r.n).toLocaleString('en-US')}`, `${f1(r.pct)} (${f1(r.lo)}–${f1(r.hi)})`]), [1.6, 1.5, 2.2, 1.8, 1.4, 1.4]));
children.push(body(''));
children.push(table(['Journal (HUGO pilot)', 'Stage', 'Period', 'Manuscripts with variants', 'With validation file (% , 95% CI)', 'Returned for errors'],
  R.L_journal_pilot.map((r, i) => [r.journal, r.stage, pilot[i].period, r.attached.split('/')[1], `${r.attached.split('/')[0]} (${pct(r.p)}; ${pct(r.ci[0])}–${pct(r.ci[1])})`, pilot[i].returned_for_errors || '—']), [1.6, 1.3, 1.8, 1.3, 2, 1]));

const coefRows = (label, m, keyset) => keyset.map(([k, name]) => [label, name, `${f2(m[k].OR)} (${f2(m[k].OR_lo)}–${f2(m[k].OR_hi)})`, pfmt(m[k].p)]);
const KEYS = [['t', 'Pre-break slope (per year)'], ['post', 'Level change at break'], ['tpost', 'Change in slope after break (per year)']];
children.push(caption('Supplementary Table S3.', `Interrupted time-series model outputs for the total EQA series (odds ratios with 95% CIs). Main model: break 2016, residual deviance ${f1(its.deviance)} on ${its.df_resid} df, over-dispersion φ = ${f2(its.scale_quasi)}, Durbin–Watson ${f2(its.durbin_watson)}; pre-period rate ${pct(its.pre_rate)}% (n = ${its.pre_n}), post-period ${pct(its.post_rate)}% (n = ${its.post_n}), risk ratio ${f2(its.RR)} (${f2(its.RR_lo)}–${f2(its.RR_hi)}); level change +${f1(its.level_change_pp_first_post_year)} percentage points in 2016 and a gap of ${f1(its.gap_pp_last_year)} points by 2018 against the projected pre-2016 trend.`));
children.push(table(['Model', 'Term', 'OR (95% CI)', 'p'], [
  ...coefRows('Variant description, break 2016, quasi-binomial', its.quasibinomial, KEYS),
  ...coefRows('Variant description, break 2016, binomial', its.binomial, KEYS),
  ...coefRows('Variant description, break 2017, quasi-binomial', its17.quasibinomial, KEYS),
  ...coefRows('Current-version reference sequence cited (control), break 2016, quasi-binomial', itsRef.quasibinomial, KEYS),
], [3, 3, 2, 1]));
children.push(body(''));
children.push(table(['Year', 'Compliant / n', 'Observed %', 'Fitted % (break 2016)', 'Projected % (no break)'], its.series.map(s => [s.year, `${s.nomen_k} / ${s.nomen_n}`, pct(s.observed), pct(s.fitted), pct(s.counterfactual)]), [1, 1.4, 1.2, 1.6, 1.6]));

children.push(caption('Supplementary Table S4.', `Per-scheme replication (Figure S1). Pooled compliance before (2012–2015) and after (2016–2018) the break in each provider–indication sub-series, with risk ratios and Fisher exact p; scheme-specific level-change odds ratios from the interaction model; and the common-break panel model with scheme fixed effects (${panel.common_break_model.df_resid} residual df, deviance ${f1(panel.common_break_model.deviance)}, φ = ${f2(panel.common_break_model.scale)}).`));
children.push(table(['Sub-series', 'Years', 'Before: compliant / n (%)', 'After: compliant / n (%)', 'RR (95% CI)', 'Fisher p', 'Scheme-specific level OR (95% CI)'],
  perSeries.map(r => { const sp = panel.series_specific_level_change[r.series]; return [r.series, r.years, `${r.pre_k} / ${r.pre_n} (${f1(r.pre_pct)})`, `${r.post_k} / ${r.post_n} (${f1(r.post_pct)})`, `${f2(r.RR)} (${f2(r.RR_lo)}–${f2(r.RR_hi)})`, pfmt(r.fisher_p), sp ? `${f2(sp.OR)} (${f2(sp.lo)}–${f2(sp.hi)})` : '—']; }), [1.5, 1, 1.6, 1.6, 1.4, 0.8, 1.8]));
children.push(body(''));
children.push(table(['Panel model term (common break, scheme intercepts)', 'OR (95% CI)', 'p'], KEYS.map(([k, name]) => [name, orci(panel.common_break_model[k]), pfmt(panel.common_break_model[k].p)]), [4, 2, 1]));

children.push(caption('Supplementary Table S5.', 'Interruption-year sweep for the total EQA series (Figure S2): fit statistics and level-change estimate with the break placed at each candidate year.'));
children.push(table(['Break year', 'Residual deviance', 'AIC', 'Residual df', 'Level OR (95% CI, quasi-binomial)', 'p'], sweep.map(s => [s.cut, f2(s.deviance), f1(s.aic), s.df_resid, `${f2(s.level_OR)} (${f2(s.level_lo)}–${f2(s.level_hi)})`, pfmt(s.level_p_quasi)]), [1, 1.3, 1, 1, 2.4, 0.8]));

children.push(caption('Supplementary Table S6.', `Feedback dose–response (Figure S3) and transitions between successive schemes. Transitions: a laboratory correct in the previous scheme was compliant in ${trans.nomenclature.correct_prev} cases vs ${trans.nomenclature.error_prev} after an error (RR ${f2(trans.nomenclature.RR)}, ${f2(trans.nomenclature.RR_lo)}–${f2(trans.nomenclature.RR_hi)}; OR ${f2(trans.nomenclature.OR)}, ${f2(trans.nomenclature.OR_lo)}–${f2(trans.nomenclature.OR_hi)}); for reference sequences ${trans['reference sequence'].correct_prev} vs ${trans['reference sequence'].error_prev} (RR ${f2(trans['reference sequence'].RR)}, ${f2(trans['reference sequence'].RR_lo)}–${f2(trans['reference sequence'].RR_hi)}). First vs fifth participation RR ${f2(dose.first_vs_fifth.RR)} (${f2(dose.first_vs_fifth.lo)}–${f2(dose.first_vs_fifth.hi)}); unsegmented calendar trend OR ${f2(dose.calendar_year_linear_trend.OR_per_year)} per year (${f2(dose.calendar_year_linear_trend.lo)}–${f2(dose.calendar_year_linear_trend.hi)}).`));
children.push(table(['Participations', 'Compliant / n', '% (95% CI)', 'Reference sequence: compliant / n', '%'], parts.map(p => [p.participations, `${p.k} / ${p.nomen_n}`, `${pct(p.prop)} (${pct(p.wlo)}–${pct(p.whi)})`, `${p.rk} / ${p.refseq_n}`, pct(p.rprop)]), [1.2, 1.3, 1.8, 2, 0.8]));

children.push(caption('Supplementary Table S7.', `Returning variants (Figure S4): entries pooled before and after 2016 for each variant distributed in both periods. Mantel–Haenszel OR ${f2(mh.OR_MH)} (${f2(mh.OR_lo)}–${f2(mh.OR_hi)}); Breslow–Day p = ${pfmt(mh.breslow_day_p)}.`));
children.push(table(['Gene', 'Variant', 'Before: compliant / n (%)', 'After: compliant / n (%)'], strata.map(s => [s.gene, s.variant, `${s.pre_k} / ${s.pre_n} (${f1(s.pre_pct)})`, `${s.post_k} / ${s.post_n} (${f1(s.post_pct)})`]), [0.8, 2.6, 1.8, 1.8]));

const mrow = (name, m) => [name, `${pct(m.re)} (${pct(m.re_lo)}–${pct(m.re_hi)})`, m.tau2 !== undefined ? f2(m.tau2) : '—', m.I2 !== undefined ? f1(m.I2) : '—'];
children.push(caption('Supplementary Table S8.', 'Meta-analytic sensitivity for the pooled full-compliance estimate (Figure S7). Main model: DerSimonian–Laird random effects on the logit scale with a 0.5 continuity correction for the zero cell (Lansdon 2026, 0/52).'));
children.push(table(['Method', 'Pooled % (95% CI)', 'τ² (logit)', 'I² (%)'], [
  mrow('Main: random effects, logit, cc 0.5', meta['main_logit_cc0.5']),
  mrow('Random effects, logit, cc 0.1', meta['logit_cc0.1']),
  mrow('Random effects, logit, cc 1.0', meta['logit_cc1.0']),
  mrow('Random effects, Freeman–Tukey double arcsine', meta.freeman_tukey),
  ['Fixed effect (inverse variance), logit', `${pct(meta['main_logit_cc0.5'].fe)} (${pct(meta['main_logit_cc0.5'].fe_lo)}–${pct(meta['main_logit_cc0.5'].fe_hi)})`, '—', '—'],
  ['Main estimate with Hartung–Knapp CI', `${pct(meta['main_logit_cc0.5'].re)} (${pct(meta['main_logit_cc0.5'].hk_lo)}–${pct(meta['main_logit_cc0.5'].hk_hi)})`, '—', '—'],
  ['Main estimate, 95% prediction interval', `${pct(meta['main_logit_cc0.5'].re)} (${pct(meta['main_logit_cc0.5'].pi_lo)}–${pct(meta['main_logit_cc0.5'].pi_hi)})`, '—', '—'],
  ...Object.entries(meta.leave_one_out).map(([k, m]) => mrow('Leave-one-out: ' + k, m)),
], [3.2, 2, 1, 1]));

children.push(caption('Supplementary Table S9.', 'Element-level and subgroup comparisons: version omission among descriptions that cite a reference sequence (EQA reports vs manuscripts), test-method and gene effects.'));
children.push(table(['Comparison', 'Group 1', 'Group 2', 'Effect (95% CI)', 'p'], [
  ['Reference cited without a version', `EQA reports: ${vo.eqa.k} / ${vo.eqa.n} (${pct(vo.eqa.p)}; ${pct(vo.eqa.ci[0])}–${pct(vo.eqa.ci[1])})`, `Manuscripts: ${vo.manuscripts.k} / ${vo.manuscripts.n} (${pct(vo.manuscripts.p)}; ${pct(vo.manuscripts.ci[0])}–${pct(vo.manuscripts.ci[1])})`, `pooled ${pct(vo.pooled.re)}% (${pct(vo.pooled.re_lo)}–${pct(vo.pooled.re_hi)}), I² = ${f1(vo.pooled.I2)}%`, `Fisher ${pfmt(vo.fisher_p)}`],
  ['Full compliance, NGS vs non-NGS methods', `NGS ${R.K_methods.NGS_vs_nonNGS.ngs}`, `non-NGS ${R.K_methods.NGS_vs_nonNGS.non}`, `OR ${orci(R.K_methods.NGS_vs_nonNGS)}`, pfmt(R.K_methods.NGS_vs_nonNGS.chi2_p)],
  ['Full compliance, non-commercial vs commercial NGS panels', '24.6% (n = 300)', '17.2% (n = 147)', `OR ${orci(R.K_methods.noncommercial_vs_commercial_NGS)}`, '—'],
  ['Full compliance, non-commercial vs commercial non-NGS methods', '9.9% (n = 717)', '9.6% (n = 768)', `OR ${orci(R.K_methods.noncommercial_vs_commercial_nonNGS)}`, '—'],
  ['Full compliance by gene', 'EGFR 12.0% (2,377); KRAS 12.4% (1,217)', 'NRAS 11.9% (459)', '—', `χ² ${pfmt(R.J_genes.compliance_chi2_p)}`],
  ['Type 2/3 (serious) errors by gene', 'EGFR 35.6% (2,377)', 'KRAS 18.1% (1,217); NRAS 16.8% (456)', `EGFR vs KRAS RR ${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.RR)} (${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.lo)}–${f2(R.J_genes.EGFR_vs_KRAS_serious_RR.hi)})`, `χ² ${pfmt(R.J_genes.serious_error_chi2_p)}`],
], [2, 2, 2, 2.2, 0.9]));

children.push(caption('Supplementary Table S10.', 'Manuscript rubric results, Genetics in Medicine and GIM Open submissions 2023–2024 (Lansdon et al. 2026, Table 1), with Wilson 95% CIs for any error.'));
children.push(table(['Criterion', 'Critical', 'Small', 'No error', 'n', 'Any error % (95% CI)'], criteria.map(c => [c.criterion, c.critical, c.small, c.none, c.n, `${pct(c.p_any)} (${pct(c.lo)}–${pct(c.hi)})`]), [3.4, 0.8, 0.8, 0.8, 0.6, 1.8]));

children.push(caption('Supplementary Table S11.', 'Findability of 18 published variants by tool and search string (Lansdon et al. 2026).'));
children.push(table(['Tool', 'Search string', 'Found / 18', '% (95% CI)'], findab.map(f => [f.tool, f.search_form, f.found, `${pct(f.p)} (${pct(f.lo)}–${pct(f.hi)})`]), [1.5, 3, 1, 1.8]));

children.push(caption('Supplementary Table S12.', `Agreement of HGVS descriptions between annotation tools and with ClinVar (Yen et al. 2017; Chen et al. 2025). Chen et al. counts are back-computed from reported match fractions on 164,549 ClinVar variants. In Yen et al., c. agreement exceeded p. agreement (χ² p = ${pfmt(R.I_tool_agreement.yen_c_vs_p_chi2_p)}).`));
children.push(table(['Study', 'Comparison', 'Level', 'Agree / n', '% (95% CI)'], tools.map(t => [t.study, t.comparison, t.level, `${Number(t.agree).toLocaleString('en-US')} / ${Number(t.n).toLocaleString('en-US')}`, `${pct(t.p)} (${pct(t.lo)}–${pct(t.hi)})`]), [1, 3, 0.7, 1.6, 1.6]));

children.push(caption('Supplementary Table S13.', 'Error-type composition of the 4,053 scored EQA entries (Keppens et al. 2020) and of 26 million unique Mutalyzer submissions (Lefter et al. 2021), as plotted in Figure S9.'));
children.push(table(['Source', 'Category', '%'], [
  ...csv(DATA('eqa_error_types.csv')).map(e => ['EQA entries (n = 4,053)', e.category, e.pct]),
  ...csv(DATA('mutalyzer_assessments.csv')).map(m => ['Mutalyzer Name Checker', m.assessment, m.pct]),
], [2, 5, 0.8]));

// ---- References
children.push(pageBreak());
children.push(h1('Supplementary References'));
[
  'Lansdon LA, Porath B, Mori M, Miller DT, Drexler DD, Wattenberg C, et al. Universal presence of gene/variant nomenclature errors in journal manuscript submissions. Clin Chem. 2026;72(6):652-661. doi:10.1093/clinchem/hvag010',
  'Keppens C, Tack V, Dufraing K, Rouleau E, Ligtenberg MJL, Schuuring E, et al. Variation in nomenclature of somatic variants for selection of oncological therapies: can we reach a consensus soon? Hum Mutat. 2020;41(1):7-16. doi:10.1002/humu.23926',
  'Higgins J, Dalgleish R, den Dunnen JT, Barsh G, Freeman PJ, Cooper DN, et al. Verifying nomenclature of DNA variants in submitted manuscripts: guidance for journals. Hum Mutat. 2021;42(1):3-7. doi:10.1002/humu.24144',
  'Freeman PJ, Wagstaff JF, Fokkema IFAC, Cutting GR, Rehm HL, Davies AC, et al. Standardizing variant naming in literature with VariantValidator to increase diagnostic rates. Nat Genet. 2024;56(11):2284-2286. doi:10.1038/s41588-024-01938-w',
  'Lefter M, Vis JK, Vermaat M, den Dunnen JT, Taschner PEM, Laros JFJ. Mutalyzer 2: next generation HGVS nomenclature checker. Bioinformatics. 2021;37(18):2811-2817. doi:10.1093/bioinformatics/btab051',
  'Wei CH, Allot A, Riehle K, Milosavljevic A, Lu Z. tmVar 3.0: an improved variant concept recognition and normalization tool. Bioinformatics. 2022;38(18):4449-4451. doi:10.1093/bioinformatics/btac537',
  'Yen JL, Garcia S, Montana A, Harris J, Chervitz S, Morra M, et al. A variant by any name: quantifying annotation discordance across tools and clinical databases. Genome Med. 2017;9:7. doi:10.1186/s13073-016-0396-7',
  'Chen YA, Yuan TH, Huang JH, Wang YB, Hung TM, Chen CY, et al. Toward streamline variant classification: discrepancies in variant nomenclature and syntax for ClinVar pathogenic variants across annotation tools. Hum Genomics. 2025;19:70. doi:10.1186/s40246-025-00778-x',
  'Conlin LK, Landrum MJ, Freimuth RR, Funke B. Standardization of genomic nomenclature across a diverse ecosystem of stakeholders: evolution and challenges. Clin Chem. 2025;71(1):45-53. doi:10.1093/clinchem/hvae195',
  'Berwouts S, Morris MA, Girodon E, Schwarz M, Stuhrmann M, Dequeker E. Mutation nomenclature in practice: findings and recommendations from the cystic fibrosis external quality assessment scheme. Hum Mutat. 2011;32(11):1197-1203. doi:10.1002/humu.21569 (Figures as reported by Keppens et al. 2020.)',
  'Tack V, Deans ZC, Wolstenholme N, Patton S, Dequeker EMC. What\'s in a name? A coordinated approach toward the correct use of a uniform nomenclature to improve patient reports and databases. Hum Mutat. 2016;37(6):570-575. doi:10.1002/humu.22975 (As reported by Keppens et al. 2020.)',
  'Deans ZC, Fairley JA, den Dunnen JT, Clark C. HGVS nomenclature in practice: an example from the United Kingdom National External Quality Assessment Scheme. Hum Mutat. 2016;37(6):576-578. doi:10.1002/humu.22978 (As reported by Keppens et al. 2020.)',
  'den Dunnen JT, Dalgleish R, Maglott DR, Hart RK, Greenblatt MS, McGowan-Jordan J, et al. HGVS recommendations for the description of sequence variants: 2016 update. Hum Mutat. 2016;37(6):564-569. doi:10.1002/humu.22981',
  'Hart RK, Fokkema IFAC, DiStefano M, Hastings R, Laros JFJ, Taylor R, et al. HGVS Nomenclature 2024: improvements to community engagement, usability, and computability. Genome Med. 2024;16(1):149. doi:10.1186/s13073-024-01421-5',
  'Richards S, Aziz N, Bale S, Bick D, Das S, Gastier-Foster J, et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genet Med. 2015;17(5):405-424. doi:10.1038/gim.2015.30',
  'HGVS Variant Nomenclature Committee. HGVS Nomenclature: versions (21.1 series, 21.0 series, older versions). https://hgvs-nomenclature.org/stable/versions/ (accessed 20 October 2026).',
  'EMQN CIC. EMQN CIC policy on variant nomenclature (DOC2702), version 13. Manchester: EMQN CIC; 2024. https://www.emqn.org/wp-content/uploads/2024/06/DOC2702-EMQN-Variant-Nomenclature-Policy.pdf (accessed 20 October 2026).',
].forEach((r, i) => children.push(new Paragraph({ spacing: { after: 80, line: 260 }, indent: { left: 400, hanging: 400 }, children: [new TextRun({ text: `${i + 1}. ${r}`, font: FONT, size: 18 })] })));

const doc = new Document({
  numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'Supplementary Information — HGVS nomenclature compliance 2010–2026 — page ', font: FONT, size: 16, color: '777777' }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: '777777' })] })] }) },
    children
  }]
});
const outDir = path.join(ROOT, 'supplementary'); fs.mkdirSync(outDir, { recursive: true });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(path.join(outDir, 'Supplementary_Information.docx'), buf); console.log('written', path.join(outDir, 'Supplementary_Information.docx'), buf.length); });
