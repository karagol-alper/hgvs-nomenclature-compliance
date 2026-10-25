export default () => <claude.Visualize data-claude-component='eqa-hgvs-compliance-its' sources={{rows:{kind:'data', data:[
{year:2012, series:'Variant description', slug:'nomen', obs:2.1, fit:3.2, cf:3.2, n:94},
{year:2013, series:'Variant description', slug:'nomen', obs:4.0, fit:3.6, cf:3.6, n:301},
{year:2014, series:'Variant description', slug:'nomen', obs:4.2, fit:4.0, cf:4.0, n:334},
{year:2015, series:'Variant description', slug:'nomen', obs:3.9, fit:4.4, cf:4.4, n:204},
{year:2016, series:'Variant description', slug:'nomen', obs:17.4, fit:19.6, cf:4.8, n:305},
{year:2017, series:'Variant description', slug:'nomen', obs:27.6, fit:22.5, cf:5.3, n:268},
{year:2018, series:'Variant description', slug:'nomen', obs:22.3, fit:25.7, cf:5.9, n:206},
{year:2012, series:'Current-version reference sequence cited', slug:'refseq', obs:16.7, fit:24.3, cf:24.3, n:102},
{year:2013, series:'Current-version reference sequence cited', slug:'refseq', obs:33.0, fit:27.6, cf:27.6, n:330},
{year:2014, series:'Current-version reference sequence cited', slug:'refseq', obs:27.5, fit:31.1, cf:31.1, n:356},
{year:2015, series:'Current-version reference sequence cited', slug:'refseq', obs:35.9, fit:34.8, cf:34.8, n:206},
{year:2016, series:'Current-version reference sequence cited', slug:'refseq', obs:34.3, fit:34.7, cf:38.7, n:306},
{year:2017, series:'Current-version reference sequence cited', slug:'refseq', obs:35.0, fit:34.1, cf:42.8, n:286},
{year:2018, series:'Current-version reference sequence cited', slug:'refseq', obs:33.0, fit:33.6, cf:46.9, n:206}
]}, cut:{kind:'data', data:[{year:2016, label:'HGVS version 15.11 / 2016 update'}]}}}>{({rows, cut, datum}) => {
const left = 64, right = 700, y0 = 92, bottom = 310, ymax = 40;
const x = yr => left + (yr - 2012) / 6 * (right - left);
const y = v => bottom - v / ymax * (bottom - y0);
const nom = rows.filter(r => r.slug === 'nomen'), ref = rows.filter(r => r.slug === 'refseq');
const path = (rs, key) => rs.map((r, i) => (i === 0 ? 'M' : 'L') + x(r.year) + ' ' + y(key === 'fit' ? r.fit : key === 'cf' ? r.cf : r.obs)).join(' ');
const pre = nom.filter(r => r.year < cut.at(0).year), post = nom.filter(r => r.year >= cut.at(0).year);
const cfRows = nom.filter(r => r.year >= cut.at(0).year - 1);
const preMean = pre.reduce((s, r) => s + r.obs * r.n, 0) / pre.reduce((s, r) => s + r.n, 0);
const postMean = post.reduce((s, r) => s + r.obs * r.n, 0) / post.reduce((s, r) => s + r.n, 0);
const ticks = [0, 10, 20, 30, 40];
const labelled = nom.filter(r => r.year === 2012 || r.year === 2015 || r.year === 2016 || r.year === 2018);
const refLabelled = ref.filter(r => r.year === 2012 || r.year === 2018);
const xc = x(cut.at(0).year - 0.5);
return <svg viewBox='0 0 760 364' role='img' aria-label='Variant descriptions jumped after the 2016 HGVS update; reference sequences did not' fontSize='12'>
<text data-claude-text-id='title' x='16' y='24' fontSize='15' fill='var(--cds-text-primary)'>Variant descriptions jumped after the 2016 HGVS update; reference sequences did not</text>
<text x='16' y='44' fill='var(--cds-text-secondary)'>{`HGVS-compliant variant descriptions: ${preMean.toFixed(1)}% of entries in 2012–2015 vs ${postMean.toFixed(1)}% in 2016–2018 (n = ${nom.reduce((s, r) => s + r.n, 0).toLocaleString('en-US')})`}</text> <text data-claude-text-id='subtitle2' x='16' y='62' fill='var(--cds-text-secondary)'>ESP and Gen&amp;Tiss EQA schemes, % per scheme year; grey = control series (current-version reference sequence cited).</text>
<g data-claude-anchor='y-axis'>{ticks.map(t => <g key={t}><line x1={left} x2={right} y1={y(t)} y2={y(t)} stroke='var(--cds-chart-grid)' /><text x={left - 8} y={y(t) + 4} textAnchor='end' fill='var(--cds-text-secondary)'>{t + '%'}</text></g>)}</g>
<g data-claude-anchor='x-axis'>{nom.map(r => <text key={r.year} x={x(r.year)} y={bottom + 18} textAnchor='middle' fill='var(--cds-text-secondary)'>{r.year}</text>)}</g>
<g data-claude-anchor='interruption'><line x1={xc} x2={xc} y1={y0 - 10} y2={bottom} stroke='var(--cds-chart-reference)' strokeDasharray='3 3' /><text x={xc + 6} y={y0 - 2} fill='var(--cds-text-secondary)'>{cut.at(0).label}</text></g>
<g data-claude-anchor='counterfactual'><path d={path(cfRows, 'cf')} fill='none' stroke='var(--cds-chart-reference)' strokeWidth='1.5' strokeDasharray='6 4' /><text data-claude-text-id='cf-label' x={x(2017.3)} y={y(cfRows.at(-1).cf) - 10} textAnchor='middle' fill='var(--cds-text-secondary)'>pre-2016 trend, projected</text></g>
<g data-claude-anchor='series-refseq'><path d={path(ref, 'obs')} fill='none' stroke='var(--cds-chart-muted)' strokeWidth='1.5' />{ref.map(r => <circle key={r.year} cx={x(r.year)} cy={y(r.obs)} r='3.5' fill='var(--cds-chart-muted)' {...datum(r, 'obs')}><title>{`${r.series}, ${r.year}: ${r.obs}% of ${r.n}`}</title></circle>)}{refLabelled.map(r => <text key={r.year} x={x(r.year) + (r.year === 2012 ? -8 : 8)} y={y(r.obs) + 4} textAnchor={r.year === 2012 ? 'end' : 'start'} fill='var(--cds-text-secondary)' {...datum(r, 'obs')}>{r.obs + '%'}</text>)}<text x={x(2014)} y={y(ref.at(2).obs) + 24} textAnchor='middle' fill='var(--cds-text-secondary)'>{ref.at(0).series}</text></g>
<g data-claude-anchor='series-nomen'><path d={path(pre, 'fit')} fill='none' stroke='var(--cds-chart-categorical-1)' strokeWidth='2' strokeOpacity='0.6' /><path d={path(post, 'fit')} fill='none' stroke='var(--cds-chart-categorical-1)' strokeWidth='2' strokeOpacity='0.6' />{nom.map(r => <circle key={r.year} cx={x(r.year)} cy={y(r.obs)} r='4.5' fill='var(--cds-chart-categorical-1)' {...datum(r, 'obs')}><title>{`${r.series}, ${r.year}: ${r.obs}% of ${r.n} entries (model ${r.fit}%, no-change projection ${r.cf}%)`}</title></circle>)}{labelled.map(r => <text key={r.year} x={x(r.year) + (r.year === 2018 ? 8 : 0)} y={y(r.obs) + (r.year === 2016 ? 20 : -9)} textAnchor={r.year === 2018 ? 'start' : 'middle'} fill='var(--cds-text-primary)' {...datum(r, 'obs')}>{r.obs + '%'}</text>)}<text x={x(2017)} y={y(nom.at(5).obs) - 14} textAnchor='middle' fill='var(--cds-chart-categorical-1)'>{nom.at(0).series}</text></g>
<text data-claude-text-id='note' x='16' y='350' fill='var(--cds-text-secondary)'>Solid blue = segmented logit fit (level change at 2016: OR 4.8, 95% CI 1.2–19); dashed grey = pre-2016 trend projected forward.</text>
</svg>; }}</claude.Visualize>;
