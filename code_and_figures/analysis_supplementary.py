"""Supplementary analyses for: HGVS nomenclature compliance in clinical variant literature, 2010-2026.

Inputs : data/*.csv (counts extracted from the included audits; see Supplementary Table S2)
Outputs: out/supp_results.json, out/*.csv (per-analysis tables), figs/S*.png
Run    : python3 analysis_supplementary.py   (Python 3.11+, numpy, pandas, scipy, statsmodels, matplotlib)
"""
import json, math, os
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda f: os.path.join(HERE, 'data', f)
O = lambda f: os.path.join(HERE, 'out', f)
F = lambda f: os.path.join(HERE, 'figs', f)
os.makedirs(O(''), exist_ok=True); os.makedirs(F(''), exist_ok=True)

# ---------------- palette (dataviz reference instance, light mode) ----------------
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#fcfcfb'
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.edgecolor': AXIS, 'axes.linewidth': 0.8,
                     'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK,
                     'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'savefig.dpi': 300,
                     'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False})

def style(ax):
    ax.grid(axis='y', color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    ax.tick_params(length=0)

# ---------------- helpers ----------------
def wilson(k, n, z=1.959964):
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0, c - h), min(1, c + h)

def rr_ci(k1, n1, k0, n0):
    rr = (k1 / n1) / (k0 / n0); se = math.sqrt(1 / k1 - 1 / n1 + 1 / k0 - 1 / n0)
    return rr, math.exp(math.log(rr) - 1.96 * se), math.exp(math.log(rr) + 1.96 * se)

def or_ci(k1, n1, k0, n0):
    a, b, c, d = k1, n1 - k1, k0, n0 - k0
    o = (a * d) / (b * c); se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return o, math.exp(math.log(o) - 1.96 * se), math.exp(math.log(o) + 1.96 * se)

def kcount(pct, n):
    return int(round(pct / 100 * n))

expit = lambda x: 1 / (1 + math.exp(-x))
logit = lambda p: math.log(p / (1 - p))

results = {}

# =====================================================================================
# S-A  Per-provider / per-indication ITS panel (replication of the 2016 break)
# =====================================================================================
pv = pd.read_csv(D('eqa_provider_yearly.csv'))
pv['series'] = pv.provider + ' ' + pv.indication
pv['k'] = [kcount(p, n) for p, n in zip(pv.nomen_pct, pv.nomen_n)]
pv['prop'] = pv.k / pv.nomen_n
pv['t'] = pv.year - 2012; pv['post'] = (pv.year >= 2016).astype(int); pv['tpost'] = np.where(pv.post == 1, pv.year - 2016, 0)
panel = {}
# common-break model with series fixed effects
m_common = smf.glm('prop ~ C(series) + t + post + tpost', data=pv, family=sm.families.Binomial(), var_weights=pv.nomen_n).fit(scale='X2')
ci = m_common.conf_int()
panel['common_break_model'] = {k: dict(OR=float(math.exp(m_common.params[k])), lo=float(math.exp(ci.loc[k, 0])), hi=float(math.exp(ci.loc[k, 1])), p=float(m_common.pvalues[k]))
                               for k in ['t', 'post', 'tpost']}
panel['common_break_model']['scale'] = float(m_common.scale); panel['common_break_model']['deviance'] = float(m_common.deviance); panel['common_break_model']['df_resid'] = int(m_common.df_resid)
# series-specific level change (interaction)
m_int = smf.glm('prop ~ C(series) + t + C(series):post + tpost', data=pv, family=sm.families.Binomial(), var_weights=pv.nomen_n).fit(scale='X2')
ci2 = m_int.conf_int()
panel['series_specific_level_change'] = {k.replace('C(series)[', '').replace(']:post', ''): dict(OR=float(math.exp(m_int.params[k])), lo=float(math.exp(ci2.loc[k, 0])), hi=float(math.exp(ci2.loc[k, 1])), p=float(m_int.pvalues[k]))
                                        for k in m_int.params.index if ':post' in k}
# simple pre/post per series
rows = []
for s, g in pv.groupby('series', sort=False):
    pre, post = g[g.post == 0], g[g.post == 1]
    kp, np_ = int(pre.k.sum()), int(pre.nomen_n.sum()); kq, nq = int(post.k.sum()), int(post.nomen_n.sum())
    rr, lo, hi = rr_ci(max(kq, 0.5), nq, max(kp, 0.5), np_)
    rows.append(dict(series=s, years=f"{g.year.min()}-{g.year.max()}", pre_k=kp, pre_n=np_, pre_pct=100 * kp / np_, post_k=kq, post_n=nq, post_pct=100 * kq / nq, RR=rr, RR_lo=lo, RR_hi=hi,
                     fisher_p=stats.fisher_exact([[kq, nq - kq], [kp, np_ - kp]])[1]))
panel['per_series_pre_post'] = rows
pd.DataFrame(rows).to_csv(O('S_per_series_pre_post.csv'), index=False)
results['A_per_provider_panel'] = panel

# =====================================================================================
# S-B  Interruption-year sweep on the total series
# =====================================================================================
eqa = pd.read_csv(os.path.join(HERE, '..', 'eqa_yearly.csv'))
eqa['k'] = [kcount(p, n) for p, n in zip(eqa.nomen_pct, eqa.nomen_n)]; eqa['prop'] = eqa.k / eqa.nomen_n; eqa['t'] = eqa.year - 2012
sweep = []
for cut in range(2014, 2019):
    d = eqa.copy(); d['post'] = (d.year >= cut).astype(int); d['tpost'] = np.where(d.post == 1, d.year - cut, 0)
    formula = 'prop ~ t + post + tpost' if d.tpost.abs().sum() > 0 else 'prop ~ t + post'
    m = smf.glm(formula, data=d, family=sm.families.Binomial(), var_weights=d.nomen_n).fit()
    mq = smf.glm(formula, data=d, family=sm.families.Binomial(), var_weights=d.nomen_n).fit(scale='X2')
    c = mq.conf_int()
    sweep.append(dict(cut=cut, deviance=float(m.deviance), aic=float(m.aic), df_resid=int(m.df_resid), level_OR=float(math.exp(m.params['post'])),
                      level_lo=float(math.exp(c.loc['post', 0])), level_hi=float(math.exp(c.loc['post', 1])), level_p_quasi=float(mq.pvalues['post'])))
results['B_interruption_sweep'] = sweep
pd.DataFrame(sweep).to_csv(O('S_interruption_sweep.csv'), index=False)

# =====================================================================================
# S-C  Feedback dose-response: compliance by number of EQA participations
# =====================================================================================
pp = pd.read_csv(D('eqa_participations.csv'))
pp['k'] = [kcount(p, n) for p, n in zip(pp.nomen_pct, pp.nomen_n)]; pp['prop'] = pp.k / pp.nomen_n
pp['rk'] = [kcount(p, n) for p, n in zip(pp.refseq_pct, pp.refseq_n)]; pp['rprop'] = pp.rk / pp.refseq_n
dose = {}
for label, sub in [('all_1_to_6', pp), ('excluding_6th', pp[pp.participations <= 5])]:
    m = smf.glm('prop ~ participations', data=sub, family=sm.families.Binomial(), var_weights=sub.nomen_n).fit(scale='X2')
    c = m.conf_int()
    dose[label] = dict(OR_per_participation=float(math.exp(m.params['participations'])), lo=float(math.exp(c.loc['participations', 0])), hi=float(math.exp(c.loc['participations', 1])), p=float(m.pvalues['participations']))
mr = smf.glm('rprop ~ participations', data=pp, family=sm.families.Binomial(), var_weights=pp.refseq_n).fit(scale='X2'); c = mr.conf_int()
dose['reference_sequence_all'] = dict(OR_per_participation=float(math.exp(mr.params['participations'])), lo=float(math.exp(c.loc['participations', 0])), hi=float(math.exp(c.loc['participations', 1])), p=float(mr.pvalues['participations']))
# calendar-year gradient for comparison (pre-2016 slope and overall linear trend)
my = smf.glm('prop ~ t', data=eqa, family=sm.families.Binomial(), var_weights=eqa.nomen_n).fit(scale='X2'); c = my.conf_int()
dose['calendar_year_linear_trend'] = dict(OR_per_year=float(math.exp(my.params['t'])), lo=float(math.exp(c.loc['t', 0])), hi=float(math.exp(c.loc['t', 1])), p=float(my.pvalues['t']))
dose['first_vs_fifth'] = dict(zip(['RR', 'lo', 'hi'], rr_ci(pp.k[4], pp.nomen_n[4], pp.k[0], pp.nomen_n[0])))
pp['wlo'] = [wilson(k, n)[1] for k, n in zip(pp.k, pp.nomen_n)]; pp['whi'] = [wilson(k, n)[2] for k, n in zip(pp.k, pp.nomen_n)]
results['C_dose_response'] = dose
pp.to_csv(O('S_participations.csv'), index=False)

# =====================================================================================
# S-D  Transition analysis: compliance conditional on the previous scheme's result
# =====================================================================================
tr = pd.read_csv(D('eqa_transitions.csv'))
trans = {}
for outcome in ['nomenclature', 'reference sequence']:
    g = tr[tr.outcome == outcome].reset_index(drop=True)
    k1, n1 = kcount(g.pct_compliant[0], g.n[0]), int(g.n[0]); k0, n0 = kcount(g.pct_compliant[1], g.n[1]), int(g.n[1])
    rr, lo, hi = rr_ci(k1, n1, k0, n0); o, olo, ohi = or_ci(k1, n1, k0, n0)
    trans[outcome] = dict(correct_prev=f"{k1}/{n1}", error_prev=f"{k0}/{n0}", RR=rr, RR_lo=lo, RR_hi=hi, OR=o, OR_lo=olo, OR_hi=ohi, chi2_p=float(stats.chi2_contingency([[k1, n1 - k1], [k0, n0 - k0]])[1]))
results['D_transitions'] = trans

# =====================================================================================
# S-E  Meta-analysis sensitivities (full compliance; k = 3)
# =====================================================================================
studies = {'Berwouts 2011': (139, 631), 'Keppens 2020': (490, 4053), 'Lansdon 2026': (0, 52)}

def dl_pool(ev, ns, cc=0.5):
    ys, vs = [], []
    for k, n in zip(ev, ns):
        kk, nn = (k + cc, n + 2 * cc) if (k == 0 or k == n) else (k, n)
        p = kk / nn; ys.append(logit(p)); vs.append(1 / (nn * p * (1 - p)))
    ys, vs = np.array(ys), np.array(vs); w = 1 / vs
    yfix = (w * ys).sum() / w.sum(); Q = float((w * (ys - yfix) ** 2).sum()); df = len(ys) - 1
    C = w.sum() - (w ** 2).sum() / w.sum(); tau2 = max(0.0, (Q - df) / C)
    wr = 1 / (vs + tau2); yre = (wr * ys).sum() / wr.sum(); se = math.sqrt(1 / wr.sum())
    sefix = math.sqrt(1 / w.sum())
    # Hartung-Knapp
    q_hk = float((wr * (ys - yre) ** 2).sum() / df) if df > 0 else float('nan')
    se_hk = se * math.sqrt(max(q_hk, 1.0)) if df > 0 else float('nan')
    tcrit = stats.t.ppf(0.975, df) if df > 0 else float('nan')
    out = dict(re=expit(yre), re_lo=expit(yre - 1.96 * se), re_hi=expit(yre + 1.96 * se), tau2=tau2, I2=100 * max(0, (Q - df) / Q) if Q > 0 else 0, Q=Q, df=df,
               fe=expit(yfix), fe_lo=expit(yfix - 1.96 * sefix), fe_hi=expit(yfix + 1.96 * sefix),
               hk_lo=expit(yre - tcrit * se_hk) if df > 0 else float('nan'), hk_hi=expit(yre + tcrit * se_hk) if df > 0 else float('nan'))
    if df >= 2:  # prediction interval (t with k-2 df)
        tp = stats.t.ppf(0.975, df - 1); sp = math.sqrt(tau2 + se ** 2)
        out['pi_lo'] = expit(yre - tp * sp); out['pi_hi'] = expit(yre + tp * sp)
    return out

def ft_pool(ev, ns):
    """Freeman-Tukey double-arcsine random-effects pooling, harmonic-mean back-transform."""
    ys = np.array([0.5 * (math.asin(math.sqrt(k / (n + 1))) + math.asin(math.sqrt((k + 1) / (n + 1)))) for k, n in zip(ev, ns)])
    vs = np.array([1 / (4 * n + 2) for n in ns]); w = 1 / vs
    yfix = (w * ys).sum() / w.sum(); Q = float((w * (ys - yfix) ** 2).sum()); df = len(ys) - 1
    C = w.sum() - (w ** 2).sum() / w.sum(); tau2 = max(0.0, (Q - df) / C)
    wr = 1 / (vs + tau2); yre = (wr * ys).sum() / wr.sum(); se = math.sqrt(1 / wr.sum())
    nh = len(ns) / sum(1 / n for n in ns)
    back = lambda t: 0.5 * (1 - np.sign(math.cos(2 * t)) * math.sqrt(1 - (math.sin(2 * t) + (math.sin(2 * t) - 1 / math.sin(2 * t)) / nh) ** 2)) if 0 < t < math.pi / 2 else (0.0 if t <= 0 else 1.0)
    return dict(re=float(back(yre)), re_lo=float(back(yre - 1.96 * se)), re_hi=float(back(yre + 1.96 * se)), tau2=tau2, I2=100 * max(0, (Q - df) / Q) if Q > 0 else 0)

ev, ns, names = [v[0] for v in studies.values()], [v[1] for v in studies.values()], list(studies)
meta = {'main_logit_cc0.5': dl_pool(ev, ns, 0.5), 'logit_cc0.1': dl_pool(ev, ns, 0.1), 'logit_cc1.0': dl_pool(ev, ns, 1.0), 'freeman_tukey': ft_pool(ev, ns)}
loo = {}
for i, nm in enumerate(names):
    e2 = [e for j, e in enumerate(ev) if j != i]; n2 = [n for j, n in enumerate(ns) if j != i]
    loo['without ' + nm] = dl_pool(e2, n2, 0.5)
meta['leave_one_out'] = loo
results['E_meta_sensitivity'] = meta

# =====================================================================================
# S-F  Version omission among descriptions that do cite a reference sequence
# =====================================================================================
k_no_version_eqa = kcount(10.0, 1792); n_with_ref_eqa = kcount(56.2, 1792)
vo = dict(eqa=dict(k=k_no_version_eqa, n=n_with_ref_eqa, p=k_no_version_eqa / n_with_ref_eqa, ci=wilson(k_no_version_eqa, n_with_ref_eqa)[1:]),
          manuscripts=dict(k=5, n=27, p=5 / 27, ci=wilson(5, 27)[1:]))
vo['fisher_p'] = float(stats.fisher_exact([[k_no_version_eqa, n_with_ref_eqa - k_no_version_eqa], [5, 22]])[1])
vo['pooled'] = dl_pool([k_no_version_eqa, 5], [n_with_ref_eqa, 27])
results['F_version_omission'] = vo

# =====================================================================================
# S-G  Returning variants: stratified (Mantel-Haenszel) pre/post-2016 comparison
# =====================================================================================
rv = pd.read_csv(D('eqa_returning_variants.csv'))
rv['k'] = [kcount(p, n) for p, n in zip(rv.pct, rv.n)]; rv['post'] = (rv.year >= 2016).astype(int)
strata = []
for v, g in rv.groupby('variant', sort=False):
    pre, post = g[g.post == 0], g[g.post == 1]
    if len(pre) and len(post):
        strata.append(dict(variant=v, gene=g.gene.iloc[0], pre_k=int(pre.k.sum()), pre_n=int(pre.n.sum()), post_k=int(post.k.sum()), post_n=int(post.n.sum())))
st = pd.DataFrame(strata); st['pre_pct'] = 100 * st.pre_k / st.pre_n; st['post_pct'] = 100 * st.post_k / st.post_n
tables = np.array([[[r.post_k, r.post_n - r.post_k], [r.pre_k, r.pre_n - r.pre_k]] for r in st.itertuples()])
sttab = sm.stats.StratifiedTable(list(tables))
mh = dict(n_variants=len(st), OR_MH=float(sttab.oddsratio_pooled), OR_lo=float(sttab.oddsratio_pooled_confint()[0]), OR_hi=float(sttab.oddsratio_pooled_confint()[1]),
          RR_MH=float(sttab.riskratio_pooled),
          breslow_day_p=float(sttab.test_equal_odds().pvalue), improved=int((st.post_pct > st.pre_pct).sum()),
          sign_test_p=float(stats.binomtest(int((st.post_pct > st.pre_pct).sum()), len(st), 0.5).pvalue))
results['G_returning_variants'] = dict(summary=mh, strata=st.to_dict('records'))
st.to_csv(O('S_returning_variants_strata.csv'), index=False)

# =====================================================================================
# S-H  Findability, S-I tool agreement, S-J genes, S-K methods, S-L journal pilot
# =====================================================================================
fd = pd.read_csv(D('findability.csv')); fd['p'] = fd.found / fd.n
fd['lo'] = [wilson(k, n)[1] for k, n in zip(fd.found, fd.n)]; fd['hi'] = [wilson(k, n)[2] for k, n in zip(fd.found, fd.n)]
results['H_findability'] = fd.to_dict('records'); fd.to_csv(O('S_findability.csv'), index=False)

ta = pd.read_csv(D('tool_agreement.csv')); ta['p'] = ta.agree / ta.n
ta['lo'] = [wilson(k, n)[1] for k, n in zip(ta.agree, ta.n)]; ta['hi'] = [wilson(k, n)[2] for k, n in zip(ta.agree, ta.n)]
yen_c, yen_p = (100, 108), (81, 108)
results['I_tool_agreement'] = dict(rows=ta.to_dict('records'), yen_c_vs_p_mcnemar_note='paired data not available; chi-square on independent proportions',
                                   yen_c_vs_p_chi2_p=float(stats.chi2_contingency([[100, 8], [81, 27]])[1]))
ta.to_csv(O('S_tool_agreement.csv'), index=False)

ge = pd.read_csv(D('eqa_genes.csv'))
comp = [[kcount(p, n), n - kcount(p, n)] for p, n in zip(ge.pct_compliant, ge.n)]
ser = [[kcount(p, n), n - kcount(p, n)] for p, n in zip(ge.pct_serious_error, ge.n_serious)]
results['J_genes'] = dict(compliance_chi2_p=float(stats.chi2_contingency(comp)[1]), serious_error_chi2_p=float(stats.chi2_contingency(ser)[1]),
                          EGFR_vs_KRAS_serious_RR=dict(zip(['RR', 'lo', 'hi'], rr_ci(ser[0][0], ge.n_serious[0], ser[1][0], ge.n_serious[1]))))

me = pd.read_csv(D('eqa_methods.csv')); mn = me[me.outcome == 'nomenclature'].reset_index(drop=True)
k_ngs = kcount(20.9, 447); n_ngs = 447; k_non = kcount(9.6, 768) + kcount(9.9, 717); n_non = 1485   # 20.9% is the paper's overall NGS figure
results['K_methods'] = dict(NGS_vs_nonNGS=dict(ngs=f"{k_ngs}/{n_ngs}", non=f"{k_non}/{n_non}", **dict(zip(['OR', 'lo', 'hi'], or_ci(k_ngs, n_ngs, k_non, n_non))), chi2_p=float(stats.chi2_contingency([[k_ngs, n_ngs - k_ngs], [k_non, n_non - k_non]])[1])),
                            noncommercial_vs_commercial_NGS=dict(zip(['OR', 'lo', 'hi'], or_ci(kcount(24.6, 300), 300, kcount(17.2, 147), 147))),
                            noncommercial_vs_commercial_nonNGS=dict(zip(['OR', 'lo', 'hi'], or_ci(kcount(9.9, 717), 717, kcount(9.6, 768), 768))))

jp = pd.read_csv(D('journal_pilot.csv'))
results['L_journal_pilot'] = [dict(journal=r.journal, stage=r.stage, attached=f"{r.with_validation_file}/{r.with_variants}", p=r.with_validation_file / r.with_variants, ci=wilson(r.with_validation_file, r.with_variants)[1:]) for r in jp.itertuples()]

# =====================================================================================
# S-M  Manuscript criteria (Lansdon 2026 Table 1) with CIs
# =====================================================================================
mc = pd.read_csv(D('manuscript_criteria.csv')); mc['p_any'] = mc.any_error / mc.n
mc['lo'] = [wilson(k, n)[1] for k, n in zip(mc.any_error, mc.n)]; mc['hi'] = [wilson(k, n)[2] for k, n in zip(mc.any_error, mc.n)]
mc.to_csv(O('S_manuscript_criteria.csv'), index=False); results['M_manuscript_criteria'] = mc.to_dict('records')

with open(O('supp_results.json'), 'w') as f:
    json.dump(results, f, indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))

# =====================================================================================
# FIGURES
# =====================================================================================
# S1: per-provider small multiples
fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=True, sharey=True)
order = ['ESP NSCLC', 'ESP mCRC', 'Gen&Tiss NSCLC', 'Gen&Tiss mCRC']
for ax, s in zip(axes.flat, order):
    for s2, g2 in pv.groupby('series'):
        if s2 != s: ax.plot(g2.year, 100 * g2.prop, color=GRID, lw=1.2, zorder=1)
    g = pv[pv.series == s]
    ax.plot(g.year, 100 * g.prop, color=BLUE, lw=2, marker='o', ms=6, mec=SURF, mew=1.2, zorder=3)
    for r in g.itertuples():
        lo, hi = wilson(r.k, r.nomen_n)[1:]
        ax.plot([r.year, r.year], [100 * lo, 100 * hi], color=BLUE, lw=1, alpha=0.5, zorder=2)
    ax.axvline(2015.5, color=MUTED, lw=1, ls=(0, (3, 3)))
    row = next(x for x in rows if x['series'] == s)
    ax.set_title(f"{s}: {row['pre_pct']:.1f}% → {row['post_pct']:.1f}%", fontsize=9.5, loc='left')
    style(ax); ax.set_ylim(0, 60); ax.set_xticks(range(2012, 2019)); ax.tick_params(axis='x', labelsize=8)
for ax in axes[:, 0]: ax.set_ylabel('HGVS-compliant entries, %')
fig.suptitle('The 2016 step appears in all four EQA sub-series (dashed line: HGVS 15.11 / 2016 update)', fontsize=10, x=0.02, ha='left')
fig.text(0.02, 0.005, 'Points: laboratory-level compliance per scheme year with Wilson 95% CI; grey: the other three series. Data: Keppens et al. 2020, Table 3.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 0.96)); fig.savefig(F('S1_per_provider_panel.png')); plt.close(fig)

# S2: interruption-year sweep
sw = pd.DataFrame(sweep)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
a1.bar(sw.cut, sw.deviance, width=0.6, color=[BLUE if c == 2016 else GRID for c in sw.cut]); style(a1)
a1.set_title('Residual deviance by candidate break year', loc='left', fontsize=9.5); a1.set_ylabel('deviance (lower = better fit)')
for r in sw.itertuples(): a1.text(r.cut, r.deviance + 0.3, f"{r.deviance:.1f}", ha='center', fontsize=8, color=INK2)
a2.errorbar(sw.cut, sw.level_OR, yerr=[sw.level_OR - sw.level_lo, sw.level_hi - sw.level_OR], fmt='o', color=BLUE, ms=6, capsize=0, lw=1.2)
a2.set_yscale('log'); a2.axhline(1, color=AXIS, lw=0.8); style(a2); a2.set_title('Level-change OR (quasi-binomial 95% CI)', loc='left', fontsize=9.5)
for ax in (a1, a2): ax.set_xticks(sw.cut); ax.set_xlabel('break year')
fig.text(0.02, 0.005, 'Segmented logit model refitted with the break at each year; the 2018 model has no post-break slope term.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S2_interruption_sweep.png')); plt.close(fig)

# S3: dose-response by participations
fig, ax = plt.subplots(figsize=(7.2, 3.4))
ax.errorbar(pp.participations, 100 * pp.prop, yerr=[100 * (pp.prop - pp.wlo), 100 * (pp.whi - pp.prop)], fmt='o-', color=BLUE, ms=7, mec=SURF, mew=1.2, lw=2, capsize=0, label='Variant description fully compliant')
ax.plot(pp.participations, 100 * pp.rprop, 'o-', color=MUTED, ms=6, mec=SURF, mew=1.2, lw=1.5, label='Reference sequence given (LRG/NM with version)')
for r in pp.itertuples(): ax.text(r.participations, 100 * r.whi + 2, f"n={r.nomen_n}", ha='center', fontsize=7.5, color=INK2)
style(ax); ax.set_xlabel('number of successive EQA participations by the laboratory'); ax.set_ylabel('% compliant'); ax.set_ylim(0, 60)
ax.set_title(f"Compliance rises with each EQA participation: OR {dose['all_1_to_6']['OR_per_participation']:.2f} per participation (1–6; {dose['excluding_6th']['OR_per_participation']:.2f} for 1–5)", loc='left', fontsize=9.5)
ax.legend(loc='upper left', fontsize=8)
fig.text(0.02, 0.005, 'Wilson 95% CIs; the sixth participation has 41 entries. Data: Keppens et al. 2020, Table 3.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S3_dose_response.png')); plt.close(fig)

# S4: returning variants slope chart
fig, ax = plt.subplots(figsize=(7.2, 4.4))
# label positions: sort by post value and push apart so no two labels sit closer than 2.6 points
lab = sorted([(r.post_pct, f"{r.variant} ({r.gene})") for r in st.itertuples()])
ypos = []
for v, _ in lab:
    y = v if not ypos else max(v, ypos[-1] + 2.6)
    ypos.append(y)
for i, r in enumerate(st.itertuples()):
    ax.plot([0, 1], [r.pre_pct, r.post_pct], color=BLUE if r.gene == 'EGFR' else (ORANGE if r.gene == 'KRAS' else AQUA), lw=2, marker='o', ms=6, mec=SURF, mew=1.2)
for (v, name), y in zip(lab, ypos):
    ax.plot([1.01, 1.04], [v, y], color=GRID, lw=0.8)
    ax.text(1.05, y, name, fontsize=7.5, va='center', color=INK2)
ax.set_xlim(-0.2, 2.2); ax.set_ylim(0, 50); ax.set_xticks([0, 1]); ax.set_xticklabels(['before 2016', '2016 and after']); style(ax); ax.set_ylabel('% compliant')
ax.set_title(f"{mh['improved']} of {mh['n_variants']} variants distributed before and after 2016 improved; MH OR {mh['OR_MH']:.1f} ({mh['OR_lo']:.1f}–{mh['OR_hi']:.1f})", loc='left', fontsize=9.5)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], color=BLUE, lw=2, label='EGFR'), Line2D([], [], color=ORANGE, lw=2, label='KRAS'), Line2D([], [], color=AQUA, lw=2, label='NRAS')], loc='upper left', fontsize=8)
fig.text(0.02, 0.005, 'Pooled entries per variant across its pre- and post-2016 scheme years. Data: Keppens et al. 2020, Table 2.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S4_returning_variants.png')); plt.close(fig)

# S5: manuscript criteria stacked bars
mcs = mc.sort_values('p_any', ascending=True)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
y = np.arange(len(mcs)); pc = 100 * mcs.critical / mcs.n; ps = 100 * mcs.small / mcs.n
ax.barh(y, pc, color=BLUE, height=0.55); ax.barh(y, ps, left=pc + 0.6, color=BLUE, alpha=0.35, height=0.55)
ax.set_yticks(y); ax.set_yticklabels([f"{c} (n={n})" for c, n in zip(mcs.criterion, mcs.n)], fontsize=8); style(ax); ax.grid(axis='x', color=GRID); ax.grid(axis='y', visible=False)
ax.set_xlim(0, 105); ax.set_xlabel('% of manuscripts with the error')
for yi, (a, b) in enumerate(zip(pc, ps)): ax.text(a + b + 2, yi, f"{a + b:.0f}%", va='center', fontsize=8, color=INK2)
ax.set_title('Manuscript errors by criterion, GIM 2023–2024 (dark: critical; light: small)', loc='left', fontsize=9.5)
fig.text(0.02, 0.005, 'Data: Lansdon et al. 2026, Table 1; n varies because some criteria apply only to NGS or CNV manuscripts.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S5_manuscript_criteria.png')); plt.close(fig)

# S6: findability
fig, ax = plt.subplots(figsize=(7.2, 3.2))
short = {'exact nomenclature as published': 'as published', 'published nomenclature with p. dropped': 'p. dropped', 'gene symbol + c. only': 'gene + c. only', 'any search form': 'any form'}
lab = [f"{t}\n{short[s]}" for t, s in zip(fd.tool, fd.search_form)]
x = np.arange(len(fd)); ax.bar(x, 100 * fd.p, color=[BLUE if 'exact' in s else GRID for s in fd.search_form], width=0.6)
ax.errorbar(x, 100 * fd.p, yerr=[100 * (fd.p - fd.lo), 100 * (fd.hi - fd.p)], fmt='none', ecolor=INK2, lw=1)
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=7.5); style(ax); ax.set_ylabel('% of 18 variants found'); ax.set_ylim(0, 105)
for xi, p in zip(x, fd.p): ax.text(xi, 100 * p + 9, f"{100 * p:.0f}%", ha='center', fontsize=8, color=INK2)
ax.set_title('Findability of published variants by search tool (blue: nomenclature exactly as published)', loc='left', fontsize=9.5)
fig.text(0.02, 0.005, 'Data: Lansdon et al. 2026; 18 variants from four Genetics in Medicine articles; Wilson 95% CI.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S6_findability.png')); plt.close(fig)

# S7: meta-analysis sensitivity forest
labels, est, lo, hi = [], [], [], []
for nm, key in [('Main: DL random effects, logit, cc 0.5', 'main_logit_cc0.5'), ('Continuity correction 0.1', 'logit_cc0.1'), ('Continuity correction 1.0', 'logit_cc1.0'), ('Freeman–Tukey double arcsine', 'freeman_tukey')]:
    r = meta[key]; labels.append(nm); est.append(r['re']); lo.append(r['re_lo']); hi.append(r['re_hi'])
labels.append('Fixed effect (inverse variance)'); r = meta['main_logit_cc0.5']; est.append(r['fe']); lo.append(r['fe_lo']); hi.append(r['fe_hi'])
labels.append('Hartung–Knapp CI'); est.append(r['re']); lo.append(r['hk_lo']); hi.append(r['hk_hi'])
labels.append('95% prediction interval'); est.append(r['re']); lo.append(r['pi_lo']); hi.append(r['pi_hi'])
for nm, r in loo.items(): labels.append('Leave-one-out: ' + nm); est.append(r['re']); lo.append(r['re_lo']); hi.append(r['re_hi'])
fig, ax = plt.subplots(figsize=(7.2, 4.0)); y = np.arange(len(labels))[::-1]
ax.hlines(y, 100 * np.array(lo), 100 * np.array(hi), color=BLUE, lw=2); ax.plot(100 * np.array(est), y, 'o', color=BLUE, ms=6, mec=SURF, mew=1.2)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8); style(ax); ax.grid(axis='x', color=GRID); ax.grid(axis='y', visible=False); ax.set_xlim(0, 100); ax.set_xlabel('% fully HGVS-compliant (pooled)')
for yi, e, l, h in zip(y, est, lo, hi): ax.text(102, yi, f"{100 * e:.1f} ({100 * l:.1f}–{100 * h:.1f})", va='center', fontsize=7.5, color=INK2, clip_on=False)
ax.set_title('Pooled full compliance under alternative methods (k = 3)', loc='left', fontsize=9.5)
fig.subplots_adjust(left=0.36, right=0.80, top=0.92, bottom=0.13); fig.savefig(F('S7_meta_sensitivity.png')); plt.close(fig)

# S8: method and gene effects
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={'width_ratios': [1.3, 1]})
mn2 = mn.copy(); mn2['k'] = [kcount(p, n) for p, n in zip(mn2.pct_compliant, mn2.n)]
mn2['lo'] = [wilson(k, n)[1] for k, n in zip(mn2.k, mn2.n)]; mn2['hi'] = [wilson(k, n)[2] for k, n in zip(mn2.k, mn2.n)]
y = np.arange(len(mn2))[::-1]
a1.hlines(y, 100 * mn2.lo, 100 * mn2.hi, color=[BLUE if 'NGS' in m and 'non-NGS' not in m else MUTED for m in mn2.method], lw=2)
a1.plot(mn2.pct_compliant, y, 'o', color=INK2, ms=5, mec=SURF, mew=1.0); a1.set_yticks(y); a1.set_yticklabels([f"{m} (n={n})" for m, n in zip(mn2.method, mn2.n)], fontsize=8)
style(a1); a1.grid(axis='x', color=GRID); a1.grid(axis='y', visible=False); a1.set_xlim(0, 35); a1.set_xlabel('% fully compliant'); a1.set_title('By test method', loc='left', fontsize=9.5)
ge2 = ge.copy(); ge2['k'] = [kcount(p, n) for p, n in zip(ge2.pct_serious_error, ge2.n_serious)]
ge2['lo'] = [wilson(k, n)[1] for k, n in zip(ge2.k, ge2.n_serious)]; ge2['hi'] = [wilson(k, n)[2] for k, n in zip(ge2.k, ge2.n_serious)]
y2 = np.arange(len(ge2))[::-1]
a2.hlines(y2, 100 * ge2.lo, 100 * ge2.hi, color=BLUE, lw=2); a2.plot(ge2.pct_serious_error, y2, 'o', color=INK2, ms=5, mec=SURF, mew=1.0)
a2.set_yticks(y2); a2.set_yticklabels([f"{g} (n={n})" for g, n in zip(ge2.gene, ge2.n_serious)], fontsize=8); style(a2); a2.grid(axis='x', color=GRID); a2.grid(axis='y', visible=False)
a2.set_xlim(0, 45); a2.set_xlabel('% with a type 2 or 3 error'); a2.set_title('Serious errors by gene', loc='left', fontsize=9.5)
fig.text(0.02, 0.005, 'Wilson 95% CIs. Data: Keppens et al. 2020 (Figure 1, Table S1 as reported in text).', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S8_method_gene.png')); plt.close(fig)

# S9: error composition (EQA) and Mutalyzer assessments
et = pd.read_csv(D('eqa_error_types.csv')); mu = pd.read_csv(D('mutalyzer_assessments.csv'))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
for ax, df, col, title in [(a1, et, 'category', 'EQA entries by outcome (n = 4,053)'), (a2, mu, 'assessment', 'Mutalyzer assessments (26 M unique inputs)')]:
    y = np.arange(len(df))[::-1]; ax.barh(y, df.pct, color=[BLUE if ('compliant' in c or 'Correct' in c) else GRID for c in df[col]], height=0.55)
    ax.set_yticks(y); ax.set_yticklabels([c if len(c) < 46 else c[:44] + '…' for c in df[col]], fontsize=7.5); style(ax); ax.grid(axis='x', color=GRID); ax.grid(axis='y', visible=False)
    for yi, p in zip(y, df.pct): ax.text(p + 1, yi, f"{p:.1f}%", va='center', fontsize=8, color=INK2)
    ax.set_xlim(0, 80); ax.set_title(title, loc='left', fontsize=9.5); ax.set_xlabel('% of entries')
fig.text(0.02, 0.005, 'Data: Keppens et al. 2020 (text) and Lefter et al. 2021 (Figure 3); categories as defined by each study.', fontsize=7, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(F('S9_error_composition.png')); plt.close(fig)

# ---------------- console summary ----------------
print('A common-break panel:', {k: (round(v['OR'], 2), round(v['lo'], 2), round(v['hi'], 2), round(v['p'], 4)) for k, v in panel['common_break_model'].items() if isinstance(v, dict)})
print('A series-specific level ORs:', {k: round(v['OR'], 2) for k, v in panel['series_specific_level_change'].items()})
for r in rows: print('  ', r['series'], f"{r['pre_pct']:.1f}% ({r['pre_k']}/{r['pre_n']}) -> {r['post_pct']:.1f}% ({r['post_k']}/{r['post_n']}) RR {r['RR']:.2f} ({r['RR_lo']:.2f}-{r['RR_hi']:.2f}) p={r['fisher_p']:.2g}")
print('B sweep:', [(s['cut'], round(s['deviance'], 2), round(s['level_OR'], 2)) for s in sweep])
print('C dose:', {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in dose.items()})
print('D transitions:', {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in trans.items()})
print('E meta:', {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in meta.items() if k != 'leave_one_out'})
print('E LOO:', {k: (round(v['re'], 3), round(v['re_lo'], 3), round(v['re_hi'], 3)) for k, v in loo.items()})
print('F version omission:', vo)
print('G MH:', mh)
print('I yen chi2 p:', results['I_tool_agreement']['yen_c_vs_p_chi2_p'])
print('J genes:', results['J_genes']); print('K methods:', results['K_methods']); print('L pilot:', results['L_journal_pilot'])
