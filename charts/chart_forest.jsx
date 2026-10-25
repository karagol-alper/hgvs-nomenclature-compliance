export default () => <claude.Visualize data-claude-component='hgvs-compliance-forest' sources={{rows:{kind:'data', data:[
{group:'Journal manuscripts', study:'Lansdon 2026 (GIM 2023–24)', outcome:'no critical error', pct:0.0, lo:0.0, hi:6.9, n:52, full:1, pooled:0, slug:'lansdon-full'},
{group:'Journal manuscripts', study:'Lansdon 2026', outcome:'c. compliant', pct:30.8, lo:19.9, hi:44.3, n:52, full:0, pooled:0, slug:'lansdon-c'},
{group:'Journal manuscripts', study:'Lansdon 2026', outcome:'p. error-free', pct:25.0, lo:15.2, hi:38.2, n:52, full:0, pooled:0, slug:'lansdon-p'},
{group:'Journal manuscripts', study:'Lansdon 2026', outcome:'reference sequence given', pct:51.9, lo:38.7, hi:64.9, n:52, full:0, pooled:0, slug:'lansdon-ref'},
{group:'Clinical reports (EQA)', study:'Berwouts 2011 (CF EQA)', outcome:'fully compliant', pct:22.0, lo:19.0, hi:25.4, n:631, full:1, pooled:0, slug:'berwouts-full'},
{group:'Clinical reports (EQA)', study:'Keppens 2020 (EQA 2012–18)', outcome:'fully compliant', pct:12.1, lo:11.1, hi:13.1, n:4053, full:1, pooled:0, slug:'keppens-full'},
{group:'Clinical reports (EQA)', study:'Keppens 2020', outcome:'reference sequence given', pct:56.2, lo:53.9, hi:58.5, n:1792, full:0, pooled:0, slug:'keppens-ref'},
{group:'Clinical reports (EQA)', study:'Keppens 2020', outcome:'current reference version', pct:31.9, lo:29.8, hi:34.1, n:1792, full:0, pooled:0, slug:'keppens-refcur'},
{group:'Checker submissions', study:'Lefter 2021 (Mutalyzer 2014–19)', outcome:'correct as submitted', pct:50.4, lo:50.4, hi:50.4, n:26000000, full:1, pooled:0, slug:'mutalyzer'},
{group:'Databases and annotation tools', study:'Yen 2017 (SnpEff vs VEP)', outcome:'same c. description', pct:92.6, lo:86.1, hi:96.2, n:108, full:0, pooled:0, slug:'yen-c'},
{group:'Databases and annotation tools', study:'Yen 2017 (SnpEff vs VEP)', outcome:'same p. description', pct:75.0, lo:66.1, hi:82.2, n:108, full:0, pooled:0, slug:'yen-p'},
{group:'Databases and annotation tools', study:'Chen 2025 (ClinVar, 3 tools)', outcome:'same c. description', pct:58.5, lo:58.3, hi:58.8, n:164549, full:0, pooled:0, slug:'chen-c'},
{group:'Databases and annotation tools', study:'Chen 2025 (ClinVar, 3 tools)', outcome:'same p. description', pct:84.0, lo:83.9, hi:84.2, n:164549, full:0, pooled:0, slug:'chen-p'},
{group:'Pooled (random effects)', study:'Pooled, 3 audits', outcome:'fully compliant', pct:14.2, lo:7.5, hi:25.1, n:4736, full:1, pooled:1, slug:'pooled-full'},
{group:'Pooled (random effects)', study:'Pooled, 2 audits', outcome:'reference sequence given', pct:56.1, lo:53.8, hi:58.3, n:1844, full:0, pooled:1, slug:'pooled-ref'}
]}}}>{({rows, datum}) => {
const labelW = 330, x0 = labelW + 10, x1 = 712, y0 = 82, rowH = 22;
const x = v => x0 + v / 100 * (x1 - x0);
const groups = rows.reduce((acc, r) => { if (acc.indexOf(r.group) < 0) acc.push(r.group); return acc; }, []);
let cursor = y0; const placed = [];
groups.forEach(g => { placed.push({kind:'head', group:g, y:cursor}); cursor += rowH; rows.filter(r => r.group === g).forEach(r => { placed.push({kind:'row', r:r, y:cursor}); cursor += rowH; }); cursor += 6; });
const H = cursor + 40;
const heads = placed.filter(p => p.kind === 'head'), items = placed.filter(p => p.kind === 'row');
const ticks = [0, 25, 50, 75, 100];
const fullRows = rows.filter(r => r.full === 1 && r.pooled === 0);
const fullMin = Math.min(...fullRows.map(r => r.pct)), fullMax = Math.max(...fullRows.map(r => r.pct));
return <svg viewBox={'0 0 760 ' + H} role='img' aria-label='Full HGVS compliance ranged from 0% (journal manuscripts) to 50% (checker inputs)' fontSize='12'>
<text data-claude-text-id='title' x='16' y='24' fontSize='15' fill='var(--cds-text-primary)'>Full HGVS compliance ranged from 0% (journal manuscripts) to 50% (checker inputs)</text>
<text x='16' y='44' fill='var(--cds-text-secondary)'>{`Fully compliant descriptions (blue) span ${fullMin.toFixed(0)}% to ${fullMax.toFixed(0)}% of the units audited; single elements and tool-to-tool agreement do better.`}</text> <text data-claude-text-id='subtitle2' x='16' y='62' fill='var(--cds-text-secondary)'>Point = estimate, bar = Wilson 95% CI; grey = one element of a description or agreement between tools.</text>
<g data-claude-anchor='x-axis'>{ticks.map(t => <g key={t}><line x1={x(t)} x2={x(t)} y1={y0 - 6} y2={cursor} stroke='var(--cds-chart-grid)' /><text x={x(t)} y={cursor + 16} textAnchor='middle' fill='var(--cds-text-secondary)'>{t + '%'}</text></g>)}</g>
<g data-claude-anchor='group-headings'>{heads.map(h => <text key={h.group} x='16' y={h.y + 15} fontWeight='600' fill='var(--cds-text-primary)'>{h.group}</text>)}</g>
{items.map(p => { const r = p.r, cy = p.y + 11, isFull = r.full === 1, col = isFull ? 'var(--cds-chart-categorical-1)' : 'var(--cds-chart-muted)'; return <g key={r.slug} data-claude-anchor={`row-${r.slug}`}>
<text x='24' y={cy + 4} fill='var(--cds-text-secondary)'><tspan fill='var(--cds-text-primary)'>{r.study}</tspan>{' — ' + r.outcome}</text>
<line x1={x(r.lo)} x2={x(r.hi)} y1={cy} y2={cy} stroke={col} strokeWidth='2' {...datum(r, 'pct')}><title>{`${r.study}: ${r.outcome} ${r.pct}% (95% CI ${r.lo}–${r.hi}), n = ${r.n.toLocaleString('en-US')}`}</title></line>
{r.pooled === 1 ? <polygon points={`${x(r.pct)},${cy - 6} ${x(r.pct) + 6},${cy} ${x(r.pct)},${cy + 6} ${x(r.pct) - 6},${cy}`} fill={col} {...datum(r, 'pct')}><title>{`${r.study}: ${r.outcome} ${r.pct}% (95% CI ${r.lo}–${r.hi})`}</title></polygon> : <circle cx={x(r.pct)} cy={cy} r='4' fill={col} {...datum(r, 'pct')}><title>{`${r.study}: ${r.outcome} ${r.pct}% (95% CI ${r.lo}–${r.hi}), n = ${r.n.toLocaleString('en-US')}`}</title></circle>}
<text x={x(r.hi) + 6} y={cy + 4} fill='var(--cds-text-secondary)' {...datum(r, 'pct')}>{`${r.pct.toFixed(1)}%`}</text>
</g>; })}
<text data-claude-text-id='note' x='16' y={H - 8} fill='var(--cds-text-secondary)'>Units differ by corpus (manuscript, report, variant entry, submitted description); diamonds = DerSimonian–Laird pooled estimates.</text>
</svg>; }}</claude.Visualize>;
