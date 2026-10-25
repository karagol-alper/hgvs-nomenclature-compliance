export default () => <claude.Visualize data-claude-component='eqa-subseries-panel' sources={{rows:{kind:'data', data:[
{series:'ESP NSCLC', slug:'esp-nsclc', year:2013, k:5, n:86}, {series:'ESP NSCLC', slug:'esp-nsclc', year:2014, k:3, n:139}, {series:'ESP NSCLC', slug:'esp-nsclc', year:2015, k:2, n:110}, {series:'ESP NSCLC', slug:'esp-nsclc', year:2016, k:11, n:93}, {series:'ESP NSCLC', slug:'esp-nsclc', year:2017, k:14, n:92}, {series:'ESP NSCLC', slug:'esp-nsclc', year:2018, k:9, n:97},
{series:'ESP mCRC', slug:'esp-mcrc', year:2012, k:2, n:94}, {series:'ESP mCRC', slug:'esp-mcrc', year:2013, k:7, n:122}, {series:'ESP mCRC', slug:'esp-mcrc', year:2014, k:11, n:104}, {series:'ESP mCRC', slug:'esp-mcrc', year:2016, k:30, n:122}, {series:'ESP mCRC', slug:'esp-mcrc', year:2017, k:24, n:86}, {series:'ESP mCRC', slug:'esp-mcrc', year:2018, k:37, n:109},
{series:'Gen&Tiss NSCLC', slug:'gt-nsclc', year:2013, k:0, n:44}, {series:'Gen&Tiss NSCLC', slug:'gt-nsclc', year:2014, k:0, n:44}, {series:'Gen&Tiss NSCLC', slug:'gt-nsclc', year:2015, k:2, n:46}, {series:'Gen&Tiss NSCLC', slug:'gt-nsclc', year:2016, k:5, n:41}, {series:'Gen&Tiss NSCLC', slug:'gt-nsclc', year:2017, k:17, n:42},
{series:'Gen&Tiss mCRC', slug:'gt-mcrc', year:2013, k:0, n:49}, {series:'Gen&Tiss mCRC', slug:'gt-mcrc', year:2014, k:0, n:47}, {series:'Gen&Tiss mCRC', slug:'gt-mcrc', year:2015, k:4, n:48}, {series:'Gen&Tiss mCRC', slug:'gt-mcrc', year:2016, k:7, n:49}, {series:'Gen&Tiss mCRC', slug:'gt-mcrc', year:2017, k:19, n:48}
]}, cut:{kind:'data', data:[{year:2016}]}}}>{({rows, cut, datum}) => {
const slugs = rows.reduce((acc, r) => { if (acc.indexOf(r.slug) < 0) acc.push(r.slug); return acc; }, []);
const nameOf = s => rows.filter(r => r.slug === s).at(0).series;
const W = 340, H = 150, padL = 44, padT = 26, gapX = 30, gapY = 34, y0 = 70, ymax = 50;
const xOf = (yr, col) => 16 + col * (W + gapX) + padL + (yr - 2012) / 6 * (W - padL - 8);
const yOf = (v, row) => y0 + row * (H + gapY) + padT + (H - padT - 20) * (1 - v / ymax);
const wilson = (k, n) => { const z = 1.96, p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [Math.max(0, c - h), Math.min(1, c + h)]; };
const pct = r => 100 * r.k / r.n;
const path = (rs, col, row) => rs.map((r, i) => (i === 0 ? 'M' : 'L') + xOf(r.year, col) + ' ' + yOf(pct(r), row)).join(' ');
const summary = s => { const g = rows.filter(r => r.slug === s), pre = g.filter(r => r.year < cut.at(0).year), post = g.filter(r => r.year >= cut.at(0).year);
  const rate = a => 100 * a.reduce((t, r) => t + r.k, 0) / a.reduce((t, r) => t + r.n, 0); return [rate(pre), rate(post)]; };
const allPre = rows.filter(r => r.year < cut.at(0).year), allPost = rows.filter(r => r.year >= cut.at(0).year);
const ratio = a => a.reduce((t, r) => t + r.k, 0) / a.reduce((t, r) => t + r.n, 0);
const minRR = Math.min(...slugs.map(s => { const [a, b] = summary(s); return b / a; })), maxRR = Math.max(...slugs.map(s => { const [a, b] = summary(s); return b / a; }));
const ticks = [0, 25, 50];
return <svg viewBox='0 0 760 460' role='img' aria-label='The 2016 step appears in all four EQA sub-series' fontSize='11'>
<text data-claude-text-id='title' x='16' y='24' fontSize='15' fill='var(--cds-text-primary)'>The 2016 step appears in all four EQA sub-series</text>
<text x='16' y='44' fill='var(--cds-text-secondary)'>{`Fully compliant entries rose ${minRR.toFixed(1)}- to ${maxRR.toFixed(1)}-fold from 2012–2015 to 2016–2018 in each scheme (all four: ${(100 * ratio(allPre)).toFixed(1)}% → ${(100 * ratio(allPost)).toFixed(1)}%)`}</text>
{slugs.map((s, i) => { const col = i % 2, row = Math.floor(i / 2), g = rows.filter(r => r.slug === s), [pre, post] = summary(s), xc = xOf(cut.at(0).year - 0.5, col);
  return <g key={s} data-claude-anchor={`facet-${s}`}>
    <text x={16 + col * (W + gapX)} y={y0 + row * (H + gapY) + 12} fontWeight='600' fill='var(--cds-text-primary)'>{`${nameOf(s)}: ${pre.toFixed(1)}% → ${post.toFixed(1)}%`}</text>
    {ticks.map(t => <g key={t}><line x1={xOf(2012, col)} x2={xOf(2018, col)} y1={yOf(t, row)} y2={yOf(t, row)} stroke='var(--cds-chart-grid)' /><text x={xOf(2012, col) - 6} y={yOf(t, row) + 4} textAnchor='end' fill='var(--cds-text-secondary)' fontSize='10'>{t + '%'}</text></g>)}
    {[2012, 2013, 2014, 2015, 2016, 2017, 2018].map(yr => <text key={yr} x={xOf(yr, col)} y={yOf(0, row) + 16} textAnchor='middle' fill='var(--cds-text-secondary)' fontSize='10'>{yr}</text>)}
    <line x1={xc} x2={xc} y1={yOf(ymax, row) - 4} y2={yOf(0, row)} stroke='var(--cds-chart-reference)' strokeDasharray='3 3' />
    {slugs.filter(o => o !== s).map(o => <path key={o} d={path(rows.filter(r => r.slug === o), col, row)} fill='none' stroke='var(--cds-chart-grid)' strokeWidth='1.5' />)}
    <path d={path(g, col, row)} fill='none' stroke='var(--cds-chart-categorical-1)' strokeWidth='2' />
    {g.map(r => { const [lo, hi] = wilson(r.k, r.n); return <g key={r.year}><line x1={xOf(r.year, col)} x2={xOf(r.year, col)} y1={yOf(100 * lo, row)} y2={yOf(100 * hi, row)} stroke='var(--cds-chart-categorical-1)' strokeOpacity='0.45' />
      <circle cx={xOf(r.year, col)} cy={yOf(pct(r), row)} r='4' fill='var(--cds-chart-categorical-1)' stroke='var(--cds-surface, white)' strokeWidth='1.5' {...datum(r, 'k')}><title>{`${r.series}, ${r.year}: ${pct(r).toFixed(1)}% (${r.k}/${r.n}), 95% CI ${(100 * lo).toFixed(0)}–${(100 * hi).toFixed(0)}%`}</title></circle></g>; })}
  </g>; })}
<text data-claude-text-id='note' x='16' y='450' fill='var(--cds-text-secondary)'>Blue: the named scheme with Wilson 95% CIs; grey: the other three; dashed line: HGVS 15.11 / 2016 update. ESP ran no colorectal scheme in 2015; Gen&amp;Tiss data end in 2017.</text>
</svg>; }}</claude.Visualize>;
