"""Meta-analysis of HGVS-compliance proportions and interrupted time-series (ITS) analysis.

Inputs : studies.csv (per-study events/n), eqa_yearly.csv (Keppens et al. 2020, Table 3 totals)
Outputs: results.json, forest_data.csv, its_data.csv (printed summary to stdout)
"""
import json, math
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

# ---------- helpers ----------
def wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)

def logit(p):
    return math.log(p / (1 - p))

def expit(x):
    return 1 / (1 + math.exp(-x))

def re_pool(events, ns, labels):
    """DerSimonian-Laird random-effects pooling of proportions on the logit scale.
    Zero cells get a 0.5 continuity correction (standard practice for logit pooling)."""
    ys, vs = [], []
    for k, n in zip(events, ns):
        kk, nn = (k + 0.5, n + 1.0) if (k == 0 or k == n) else (k, n)
        p = kk / nn
        ys.append(logit(p)); vs.append(1 / (nn * p * (1 - p)))
    ys, vs = np.array(ys), np.array(vs)
    w = 1 / vs
    yfix = np.sum(w * ys) / np.sum(w)
    Q = float(np.sum(w * (ys - yfix) ** 2))
    df = len(ys) - 1
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    wr = 1 / (vs + tau2)
    yre = np.sum(wr * ys) / np.sum(wr)
    se = math.sqrt(1 / np.sum(wr))
    I2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0
    return dict(pooled=expit(yre), lo=expit(yre - 1.96 * se), hi=expit(yre + 1.96 * se),
                tau2=tau2, Q=Q, df=df, I2=I2, k=len(ys), labels=labels,
                p_het=float(1 - stats.chi2.cdf(Q, df)) if df > 0 else float('nan'))

# ---------- per-study estimates ----------
st = pd.read_csv('studies.csv')
rows = []
for _, r in st.iterrows():
    p, lo, hi = wilson(r.events, r.n)
    rows.append(dict(study=r.study, stratum=r.stratum, outcome=r.outcome, period=r.period,
                     events=int(r.events), n=int(r.n), pct=100 * p, lo=100 * lo, hi=100 * hi, source=r.source))
forest = pd.DataFrame(rows)
forest.to_csv('forest_data.csv', index=False)

# ---------- pooled estimates by stratum ----------
pools = {}
def pool(name, names):
    sub = st[st.study.isin(names)]
    pools[name] = re_pool(sub.events.tolist(), sub.n.tolist(), sub.study.tolist())

pool('Full compliance, clinical reports (EQA)', ['Berwouts 2011', 'Keppens 2020'])
pool('Full compliance, all document-level audits (reports + manuscripts)', ['Berwouts 2011', 'Keppens 2020', 'Lansdon 2026'])
pool('Reference sequence provided (reports + manuscripts)', ['Keppens 2020 (ref seq)', 'Lansdon 2026 (ref seq)'])
pool('Protein-level description correct (manuscripts + tools)', ['Lansdon 2026 (p.)', 'Yen 2017 (p.)'])
pool('Tool-to-tool c. agreement (Yen 2017, Chen 2025)', ['Yen 2017 (c.)', 'Chen 2025 (c.)'])
pool('Tool-to-tool p. agreement (Yen 2017, Chen 2025)', ['Yen 2017 (p.)', 'Chen 2025 (p.)'])

# ---------- ITS on the EQA annual series ----------
eqa = pd.read_csv('eqa_yearly.csv')
eqa['nomen_k'] = (eqa.nomen_pct / 100 * eqa.nomen_n).round().astype(int)
eqa['refseq_k'] = (eqa.refseq_pct / 100 * eqa.refseq_n).round().astype(int)

def its(df, kcol, ncol, cut):
    d = df.copy()
    d['t'] = d.year - d.year.min()
    d['post'] = (d.year >= cut).astype(int)
    d['tpost'] = np.where(d.post == 1, d.year - cut, 0)   # 0 in the first post year, 1 the next ...
    d['fail'] = d[ncol] - d[kcol]
    # binomial GLM, logit link; pre-trend, level change at `cut`, slope change after `cut`
    d['prop'] = d[kcol] / d[ncol]
    # binomial GLM on proportions with n as variance weights (identical fit to the successes/failures form)
    m = smf.glm('prop ~ t + post + tpost', data=d, family=sm.families.Binomial(), var_weights=d[ncol]).fit()
    # quasi-binomial (scale = Pearson chi2 / df) to allow over-dispersion
    mq = smf.glm('prop ~ t + post + tpost', data=d, family=sm.families.Binomial(), var_weights=d[ncol]).fit(scale='X2')
    # counterfactual: pre-period model only, projected forward
    pre = d[d.post == 0]
    mpre = smf.glm('prop ~ t', data=pre, family=sm.families.Binomial(), var_weights=pre[ncol]).fit()
    d['fitted'] = m.predict(d)
    d['counterfactual'] = mpre.predict(d)
    d['observed'] = d[kcol] / d[ncol]
    out = dict(cut=cut, n_total=int(d[ncol].sum()), deviance=float(m.deviance), df_resid=int(m.df_resid),
               pearson_chi2=float(m.pearson_chi2), scale_quasi=float(mq.scale))
    for name, mod in [('binomial', m), ('quasibinomial', mq)]:
        ci = mod.conf_int()
        out[name] = {k: dict(coef=float(mod.params[k]), lo=float(ci.loc[k, 0]), hi=float(ci.loc[k, 1]),
                            OR=float(math.exp(mod.params[k])), OR_lo=float(math.exp(ci.loc[k, 0])),
                            OR_hi=float(math.exp(ci.loc[k, 1])), p=float(mod.pvalues[k]))
                     for k in ['t', 'post', 'tpost']}
    # absolute effects in the first post year and the last year
    first_post = d[d.year == cut].iloc[0]
    last = d.iloc[-1]
    out['level_change_pp_first_post_year'] = float(100 * (first_post.fitted - first_post.counterfactual))
    out['gap_pp_last_year'] = float(100 * (last.fitted - last.counterfactual))
    out['series'] = d[['year', kcol, ncol, 'observed', 'fitted', 'counterfactual']].round(4).to_dict('records')
    # pre vs post pooled rates, chi-square
    pre_k, pre_n = int(pre[kcol].sum()), int(pre[ncol].sum())
    post_k, post_n = int(d[d.post == 1][kcol].sum()), int(d[d.post == 1][ncol].sum())
    chi2, pval, _, _ = stats.chi2_contingency([[pre_k, pre_n - pre_k], [post_k, post_n - post_k]])
    out['pre_rate'] = pre_k / pre_n; out['post_rate'] = post_k / post_n
    out['pre_n'] = pre_n; out['post_n'] = post_n; out['chi2_p'] = float(pval)
    # risk ratio post/pre with CI
    rr = (post_k / post_n) / (pre_k / pre_n)
    se_lrr = math.sqrt(1 / post_k - 1 / post_n + 1 / pre_k - 1 / pre_n)
    out['RR'] = rr; out['RR_lo'] = math.exp(math.log(rr) - 1.96 * se_lrr); out['RR_hi'] = math.exp(math.log(rr) + 1.96 * se_lrr)
    return out

results = dict(pooled=pools,
               its_nomenclature_2016=its(eqa, 'nomen_k', 'nomen_n', 2016),
               its_nomenclature_2017=its(eqa, 'nomen_k', 'nomen_n', 2017),
               its_refseq_2016=its(eqa, 'refseq_k', 'refseq_n', 2016))

# Durbin-Watson on deviance residuals of the main model (autocorrelation check, 7 points only)
d = eqa.copy(); d['t'] = d.year - 2012; d['post'] = (d.year >= 2016).astype(int); d['tpost'] = np.where(d.post == 1, d.year - 2016, 0)
d['prop'] = d.nomen_k / d.nomen_n
m = smf.glm('prop ~ t + post + tpost', data=d, family=sm.families.Binomial(), var_weights=d.nomen_n).fit()
res = m.resid_deviance.values
results['its_nomenclature_2016']['durbin_watson'] = float(np.sum(np.diff(res) ** 2) / np.sum(res ** 2))

pd.DataFrame(results['its_nomenclature_2016']['series']).to_csv('its_data.csv', index=False)
with open('results.json', 'w') as f:
    json.dump(results, f, indent=1, default=float)

# ---------- print summary ----------
print(forest[['study', 'events', 'n', 'pct', 'lo', 'hi']].round(1).to_string(index=False))
print()
for k, v in pools.items():
    print(f"{k}: {100*v['pooled']:.1f}% (95% CI {100*v['lo']:.1f}-{100*v['hi']:.1f}); k={v['k']}; I2={v['I2']:.1f}%; tau2={v['tau2']:.3f}; Q={v['Q']:.1f} p={v['p_het']:.3g}")
print()
for key in ['its_nomenclature_2016', 'its_nomenclature_2017', 'its_refseq_2016']:
    r = results[key]
    print(key, 'cut', r['cut'], 'N', r['n_total'])
    for name in ['binomial', 'quasibinomial']:
        b = r[name]
        print(f"  {name}: pre-slope OR/yr {b['t']['OR']:.2f} ({b['t']['OR_lo']:.2f}-{b['t']['OR_hi']:.2f}) p={b['t']['p']:.3g}; "
              f"level OR {b['post']['OR']:.2f} ({b['post']['OR_lo']:.2f}-{b['post']['OR_hi']:.2f}) p={b['post']['p']:.3g}; "
              f"slope change OR/yr {b['tpost']['OR']:.2f} ({b['tpost']['OR_lo']:.2f}-{b['tpost']['OR_hi']:.2f}) p={b['tpost']['p']:.3g}")
    print(f"  deviance {r['deviance']:.2f} on {r['df_resid']} df; quasi scale {r['scale_quasi']:.2f}; level change first post year {r['level_change_pp_first_post_year']:.1f} pp; gap last year {r['gap_pp_last_year']:.1f} pp")
    print(f"  pre rate {100*r['pre_rate']:.1f}% (n={r['pre_n']}), post rate {100*r['post_rate']:.1f}% (n={r['post_n']}), RR {r['RR']:.2f} ({r['RR_lo']:.2f}-{r['RR_hi']:.2f}), chi2 p={r['chi2_p']:.2g}")
    if 'durbin_watson' in r: print('  Durbin-Watson', round(r['durbin_watson'], 2))
    print('  series:', [(s['year'], round(100*s['observed'],1), round(100*s['fitted'],1), round(100*s['counterfactual'],1)) for s in r['series']])
