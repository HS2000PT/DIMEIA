/* InvestiGator v5 — cliente
 *
 * A REGRA QUE GOVERNA ESTE FICHEIRO: um pedido pinta a aplicação; depois disso, interagir
 * não toca na rede. Trocar de intervalo é um `slice` de um vector que já está em memória.
 * Foi essa a conclusão do estudo de percursos, e a razão de o Streamlit ter saído:
 * "No CSS fixes this; a client-side interaction layer does."
 *
 * O QUE FICA FORA DO CAMINHO CRÍTICO: precedentes e triagem (custam ~7 s a frio, porque
 * carregam o modelo semântico e a base de casos) e o texto gerado. Os três pedem-se DEPOIS
 * da primeira pintura e entram quando chegam. A v4 teve de RETIRAR os precedentes do produto
 * por causa desse custo; aqui a capacidade volta sem o utilizador pagar a espera.
 */

const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const S = {
  overview: null, assets: new Map(), prec: new Map(), triage: new Map(),
  route: { view: 'home', ticker: null },
  range: '1D', series: { events: true, news: true },
  chart: null, chartApi: null, markers: null,
  rail: { open: false, tab: 'report', report: null, chat: [], busy: false },
  bundleFacts: new Map(),
};

/* ── rede ── */
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok && r.status !== 404) throw new Error(`${path} → ${r.status}`);
  return r.json();
}
const post = (p, body) => api(p, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });

/* ── formatação ── */
const pct = (v, d = 2) => v == null ? '—' : `${v >= 0 ? '+' : ''}${(v * 100).toFixed(d)}%`;
const sgn = v => v == null ? '' : v > 0 ? 'up' : v < 0 ? 'down' : '';
const arrow = v => v == null ? '' : v > 0 ? '▲' : v < 0 ? '▼' : '—';
const money = v => v == null ? '—' : `$${v.toFixed(2)}`;
const shortDate = d => { const [y, m, dd] = String(d).split('-'); return `${dd} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m - 1]}`; };

/* ── router ────────────────────────────────────────────────────────────────
 * URLs reais. O botão "voltar" do browser tem de funcionar e um alerta do
 * Telegram tem de poder apontar directamente ao detalhe (?t=NVDA). */
function readURL() {
  const p = new URLSearchParams(location.search);
  const v = p.get('view');
  S.route = { view: p.get('t') ? 'asset' : (v || 'home'), ticker: (p.get('t') || '').toUpperCase() || null };
  S.range = p.get('r') || S.range;
}
function go(route, replace = false) {
  const p = new URLSearchParams();
  if (route.ticker) p.set('t', route.ticker);
  else if (route.view && route.view !== 'home') p.set('view', route.view);
  if (route.ticker && S.range !== '1D') p.set('r', S.range);
  const url = p.toString() ? `/?${p}` : '/';
  history[replace ? 'replaceState' : 'pushState']({}, '', url);
  readURL();
  render();
}
addEventListener('popstate', () => { readURL(); render(); });

/* ── esqueleto (nunca um viewport vazio) ── */
function skeleton() {
  const cards = Array.from({ length: 12 }, () => `
    <div class="card">
      <div class="card-top"><div class="sk" style="width:26px;height:26px;border-radius:4px"></div>
        <div style="flex:1"><div class="sk sk-line" style="width:60%"></div><div class="sk sk-line" style="width:34%;height:8px"></div></div></div>
      <div class="sk" style="width:44%;height:26px"></div>
      <div><div class="sk sk-line"></div><div class="sk sk-line" style="width:76%"></div></div>
      <div class="sk" style="height:13px"></div>
    </div>`).join('');
  return `<div class="situation"><div class="sk sk-line" style="width:120px;height:9px"></div>
    <div class="sk sk-line" style="width:82%;height:18px;margin-top:14px"></div>
    <div class="sk sk-line" style="width:58%;height:18px"></div></div>
    <div class="grid">${cards}</div>`;
}

/* ── cabeçalho ── */
function paintHeader() {
  const o = S.overview; if (!o) return;
  const m = o.market || {};
  const pill = $('#mkt');
  pill.className = `pill ${m.open ? 'live' : 'shut'}`;
  $('#mkt-t').textContent = m.open ? `Market open · ${m.detail || ''}` : `Market closed · ${m.detail || ''}`;

  // A idade dos dados é obrigatória no ecrã: um número sem idade é um número que o leitor
  // assume actual. Uma pessoa leu o fecho de ontem como o preço de agora, às 08:02, porque
  // nada no ecrã a desmentia.
  $('#asof').textContent = o.as_of ? `data ${o.age_label}${o.fresh ? '' : ' · stale'}` : '';
  $('#asof').style.color = o.fresh ? 'var(--ink-3)' : 'var(--warn)';
}

/* ── SVG utilitários ── */
function strip(count, n) {
  if (!n) return '';
  const marks = 60, on = Math.max(0, Math.min(marks, Math.round(marks * count / n))), w = 100 / marks;
  let s = `<svg class="strip" viewBox="0 0 100 13" preserveAspectRatio="none" aria-hidden="true">`;
  for (let i = 0; i < marks; i++)
    s += `<rect x="${(i * w).toFixed(2)}" y="0" width="${(w - .28).toFixed(2)}" height="13" rx=".4" fill="${i < on ? 'var(--line-2)' : 'var(--warn)'}" opacity="${i < on ? .5 : 1}"/>`;
  return s + '</svg>';
}
function spark(closes, colour) {
  if (!closes || closes.length < 2) return '';
  const v = closes.map(c => c[1]), lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1;
  const pts = v.map((y, i) => `${(i / (v.length - 1) * 100).toFixed(2)},${(26 - (y - lo) / r * 22).toFixed(2)}`).join(' ');
  return `<svg class="spark" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true">
    <polyline points="${pts}" fill="none" stroke="${colour}" stroke-width="1.4" vector-effect="non-scaling-stroke"/></svg>`;
}
const logoOf = (t, n) => `<div class="logo-fb">${esc((n || t).slice(0, 2).toUpperCase())}</div>`;

/* ══ VISTA: home ══════════════════════════════════════════════════════════ */
function viewHome() {
  const o = S.overview, rows = o.rows || [];
  const flagged = rows.filter(r => r.flagged);
  const sorted = [...rows].sort((a, b) => Math.abs(b.z ?? 0) - Math.abs(a.z ?? 0));

  const cards = sorted.map(r => {
    const s = sgn(r.move), c = s === 'up' ? 'var(--up)' : s === 'down' ? 'var(--down)' : 'var(--ink-3)';
    const chips = [];
    if (r.flagged) chips.push(`<span class="chip w">z ${(r.z >= 0 ? '+' : '') + r.z.toFixed(2)} vs 20-day norm</span>`);
    if (r.vol_ratio) chips.push(`<span class="chip">${r.vol_ratio.toFixed(1)}× usual volume</span>`);
    if (r.decomp?.driver) chips.push(`<span class="chip i">${esc(r.decomp.driver)}-driven</span>`);
    return `<button class="card ${r.flagged ? 'flag' : ''}" data-t="${esc(r.ticker)}">
      <div class="card-top">${logoOf(r.ticker, r.name)}
        <div class="card-id"><div class="card-name">${esc(r.name || r.ticker)}</div>
          <div class="card-tick">${esc(r.ticker)}</div></div></div>
      <div class="card-move"><span class="card-pct ${s}">${pct(r.move)}</span>
        <span class="card-arrow ${s}">${arrow(r.move)}</span></div>
      <div class="verdict">${esc(r.verdict || '')}</div>
      ${r.rarity ? strip(r.rarity.count, r.rarity.n) : ''}
      ${spark(r.closes?.slice(-30), c)}
      <div class="chips">${chips.join('')}</div>
    </button>`;
  }).join('');

  return `
  <section class="situation" id="situation">
    <div class="sit-head">
      <span class="sit-title">Situation</span>
      <span class="tag det" id="sit-tag">deterministic</span>
      <span class="spacer" style="flex:1"></span>
      <button class="tbtn ai" id="gen-report">Generate report</button>
    </div>
    <div class="sit-body" id="sit-body"><p>${esc(deterministicSituation(rows, flagged))}</p></div>
  </section>
  <div class="grid">${cards}</div>`;
}

/* O chão da situação, sem LLM. Existe para a página nunca abrir vazia e para o produto
 * funcionar com zero chaves de API — que é uma restrição fundadora, não um detalhe. */
function deterministicSituation(rows, flagged) {
  if (!rows.length) return 'No data yet.';
  const up = rows.filter(r => (r.move ?? 0) > 0).length, down = rows.length - up;
  const drivers = rows.map(r => r.decomp?.driver).filter(Boolean);
  const market = drivers.filter(d => d === 'market').length;
  let s = flagged.length === 0
    ? `Nothing stood out today. All ${rows.length} names moved within their usual range.`
    : `${flagged.length} of ${rows.length} stood out today: ${flagged.map(r => r.ticker).join(', ')}.`;
  s += ` ${up} up, ${down} down.`;
  if (market) s += ` The market itself was the largest component for ${market} of ${drivers.length}.`;
  return s;
}

/* ══ VISTA: activo ════════════════════════════════════════════════════════ */
function viewAsset(t) {
  const a = S.assets.get(t);
  if (!a) return `<div class="panel"><div class="panel-body"><div class="sk" style="height:420px"></div></div></div>`;
  const s = sgn(a.move);
  const last = a.closes?.length ? a.closes[a.closes.length - 1][1] : null;

  return `
  <div class="crumb"><button data-nav-home>Overview</button><span class="sep">/</span>
    <span class="muted">${esc(a.name || t)}</span></div>

  <div class="asset-head">
    <div class="asset-id">${logoOf(t, a.name)}
      <div><div class="asset-name">${esc(a.name || t)}</div>
        <div class="asset-tick">${esc(t)}${a.sector_etf ? ` · sector ${esc(a.sector_etf)}` : ''}</div></div></div>
    <div class="asset-price"><div class="asset-pct ${s}">${pct(a.move)}</div>
      <div class="asset-last">${money(last)} · last completed session</div></div>
  </div>

  <div class="panel">
    <div class="panel-head">
      <div class="seg" id="ranges" role="group" aria-label="Time range">
        ${['1D', '5D', '1M', '3M', '6M', '1Y'].map(r =>
          `<button data-r="${r}" aria-pressed="${S.range === r}">${r}</button>`).join('')}
      </div>
      <div class="toggles">
        <button class="tog ev" id="tog-ev" aria-pressed="${S.series.events}"><i class="sw"></i>Events</button>
        <button class="tog nw" id="tog-nw" aria-pressed="${S.series.news}"><i class="sw"></i>News</button>
      </div>
      <span class="spacer" style="flex:1"></span>
      <span class="dim" style="font-size:var(--t-xs)" id="chart-note"></span>
      <button class="tbtn ai" id="ask-chart">Ask about this view</button>
    </div>
    <div id="chart"></div>
  </div>

  <div class="q3">
    <div class="q">
      <h4>1 · What happened</h4>
      <div class="ans">${esc(rowVerdict(t))}</div>
      ${a.rarity ? `<div class="muted" style="font-size:var(--t-sm)">
        ${a.rarity.count} of the last ${a.rarity.n} trading days moved at least this much.</div>
        ${strip(a.rarity.count, a.rarity.n)}` : ''}
    </div>
    <div class="q">
      <h4>2 · Where it came from</h4>
      ${decompHTML(a.decomp)}
    </div>
    <div class="q" id="prec-q">
      <h4>3 · Has this happened before</h4>
      <div class="dim" style="font-size:var(--t-sm)">Searching 80k archived headlines…
        <div class="sk sk-line" style="margin-top:10px"></div>
        <div class="sk sk-line" style="width:70%"></div></div>
    </div>
  </div>

  <div class="panel" style="margin-top:var(--s4)">
    <div class="panel-head"><span class="panel-title">Captured news · ${a.news?.length || 0} days</span>
      <span class="dim" style="font-size:var(--t-xs)">outcome measured 5 trading days later, never projected</span></div>
    <div class="rows" id="news-rows">${newsRows(a.news)}</div>
  </div>

  ${a.alerts?.length ? `<div class="panel" style="margin-top:var(--s4)">
    <div class="panel-head"><span class="panel-title">Alerts actually sent · ${a.alerts.length}</span></div>
    <div class="rows">${a.alerts.slice(0, 12).map(al => `
      <div class="row"><span class="row-date">${esc(shortDate(al.date))}</span>
        <div class="row-main"><div class="row-title">${esc((al.text || '').split('\n')[0])}</div>
          <div class="row-meta"><span>${esc(al.kind)}</span>${al.sent_at ? `<span>sent ${esc(al.sent_at.slice(11, 16))} UTC</span>` : ''}</div>
        </div></div>`).join('')}</div></div>` : ''}`;
}

function rowVerdict(t) {
  const r = (S.overview.rows || []).find(x => x.ticker === t);
  return r?.verdict || '';
}

function decompHTML(d) {
  if (!d) return `<div class="dim" style="font-size:var(--t-sm)">Not available for this name — the
    market or sector series could not be estimated.</div>`;
  const parts = [['Market', d.market], ['Sector', d.sector], ['Company', d.company]];
  const max = Math.max(...parts.map(p => Math.abs(p[1] || 0)), 1e-9);
  const bars = parts.map(([lab, v]) => {
    const isDriver = lab.toLowerCase().startsWith(String(d.driver || '').slice(0, 6).toLowerCase());
    const w = Math.abs(v || 0) / max * 50;
    const c = (v || 0) >= 0 ? 'var(--up)' : 'var(--down)';
    const side = (v || 0) >= 0 ? `left:50%;width:${w}%` : `right:50%;width:${w}%`;
    return `<div class="dec-row ${isDriver ? 'driver' : ''}">
      <span class="dec-lab">${lab}</span>
      <div class="dec-track"><div class="dec-bar" style="${side};background:${c}"></div></div>
      <span class="dec-val ${sgn(v)}">${pct(v)}</span></div>`;
  }).join('');
  // As componentes que puxaram AO CONTRÁRIO são ditas, não escondidas: é a informação que
  // distingue "caiu com o mercado" de "caiu apesar do mercado".
  const against = parts.filter(([, v]) => v != null && Math.sign(v) !== Math.sign(d.market + d.sector + d.company)).map(p => p[0]);
  return `<div class="dec">${bars}</div>
    <div class="muted" style="font-size:var(--t-sm);margin-top:var(--s3)">
      Largest component: <b>${esc(d.driver || '—')}</b>.
      ${against.length ? `${against.join(' and ')} pulled the other way.` : ''}
      <span class="dim">Two-factor, sector orthogonalised, betas shrunk toward 1 (Vasicek) from prior data only.</span>
    </div>`;
}

function newsRows(news) {
  if (!news?.length) return `<div class="empty">No headlines captured for this name yet.</div>`;
  return news.slice(0, 60).map((n, i) => `
    <button class="row" data-news="${i}">
      <span class="row-date">${esc(shortDate(n.date))}</span>
      <div class="row-main"><div class="row-title">${esc(n.headline)}</div>
        <div class="row-meta">${n.source ? `<span>${esc(n.source)}</span>` : ''}
          ${n.n > 1 ? `<span>+${n.n - 1} more that day</span>` : ''}</div></div>
      <span class="row-val ${sgn(n.d5)}">${n.d5 == null ? '<span class="dim">pending</span>' : pct(n.d5)}</span>
    </button>`).join('');
}

/* ══ GRÁFICO ══════════════════════════════════════════════════════════════ */
const RANGE_BARS = { '5D': 5, '1M': 22, '3M': 66, '6M': 126, '1Y': 260 };

function buildChart(t) {
  const a = S.assets.get(t); if (!a) return;
  const box = $('#chart'); if (!box) return;
  box.innerHTML = '';

  const LWC = window.LightweightCharts;
  const css = getComputedStyle(document.documentElement);
  const ink3 = css.getPropertyValue('--ink-3').trim(), line = css.getPropertyValue('--line').trim();

  const chart = LWC.createChart(box, {
    layout: { background: { type: 'solid', color: 'transparent' }, textColor: ink3,
              fontFamily: css.getPropertyValue('--font'), fontSize: 11, attributionLogo: false },
    grid: { vertLines: { visible: false }, horzLines: { color: line, style: 1 } },
    rightPriceScale: { borderVisible: false, scaleMargins: { top: .14, bottom: .12 } },
    timeScale: { borderVisible: false, timeVisible: S.range === '1D', secondsVisible: false,
                 rightOffset: 3, barSpacing: 8 },
    crosshair: { mode: LWC.CrosshairMode.Normal,
      vertLine: { color: ink3, width: 1, style: 2, labelBackgroundColor: line },
      horzLine: { color: ink3, width: 1, style: 2, labelBackgroundColor: line } },
    handleScroll: true, handleScale: true, autoSize: true,
  });

  const intraday = S.range === '1D' && a.intraday?.length > 1;
  const up = css.getPropertyValue('--up').trim(), down = css.getPropertyValue('--down').trim();

  let data, base;
  if (intraday) {
    data = a.intraday.map(([ts, v]) => ({ time: ts, value: v }));
    base = a.prev_close ?? data[0].value;
  } else {
    const bars = RANGE_BARS[S.range] || 260;
    data = (a.closes || []).slice(-bars).map(([d, v]) => ({ time: d, value: v }));
    base = data.length ? data[0].value : 0;
  }
  if (!data.length) { box.innerHTML = `<div class="empty">No series for this range.</div>`; return; }

  const rising = data[data.length - 1].value >= base;
  const colour = rising ? up : down;

  const series = chart.addSeries(LWC.AreaSeries, {
    lineColor: colour, lineWidth: 2,
    topColor: colour.replace(')', ', .22)').replace('rgb', 'rgba'),
    bottomColor: 'rgba(0,0,0,0)',
    priceLineVisible: false, lastValueVisible: true,
    priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
  });
  series.setData(data);

  // A referência contra a qual a variação do dia faz sentido. Sem ela, uma linha
  // intradiária é um preço sem baseline.
  if (intraday && a.prev_close) {
    series.createPriceLine({ price: a.prev_close, color: ink3, lineWidth: 1, lineStyle: 2,
                             axisLabelVisible: true, title: 'prev close' });
  }

  // ── MARCADORES: eventos (detector) e notícias (captadas) ──
  // Os eventos NÃO são decoração: são o replay do MESMO detector sobre cada dia da série
  // (a RQ1 aplicada ao passado), não uma marcação escolhida à mão.
  const marks = [];
  const inRange = new Set(data.map(d => d.time));
  if (S.series.events && !intraday) {
    for (const [d, z] of (a.events || [])) {
      if (!inRange.has(d)) continue;
      marks.push({ time: d, position: z >= 0 ? 'aboveBar' : 'belowBar', color: css.getPropertyValue('--warn').trim(),
                   shape: z >= 0 ? 'arrowUp' : 'arrowDown', text: `z ${z >= 0 ? '+' : ''}${z}`, size: 1 });
    }
  }
  if (S.series.news && !intraday) {
    const seen = new Set();
    for (const n of (a.news || [])) {
      // Uma notícia de sábado não tem barra onde pousar: ancora-se na primeira sessão
      // >= à data, que é a MESMA regra com que o impacto foi medido.
      const anchor = nearestSession(n.date, data);
      if (!anchor || seen.has(anchor)) continue;
      seen.add(anchor);
      marks.push({ time: anchor, position: 'belowBar', color: css.getPropertyValue('--info').trim(),
                   shape: 'circle', size: 0.7 });
    }
  }
  marks.sort((x, y) => String(x.time) < String(y.time) ? -1 : 1);
  S.markers = marks.length ? LWC.createSeriesMarkers(series, marks) : null;

  chart.timeScale().fitContent();
  S.chart = chart; S.chartApi = series;

  const note = $('#chart-note');
  if (note) note.textContent = intraday
    ? `${a.intraday.length} five-minute bars · ${a.intraday_day || ''}`
    : `${data.length} sessions · ${marks.filter(m => m.shape !== 'circle').length} flagged · ${marks.filter(m => m.shape === 'circle').length} news days`;

  // Clicar num marcador abre a evidência. É o "overview → detail → source" pedido.
  chart.subscribeClick(p => {
    if (!p.time) return;
    const key = typeof p.time === 'number' ? p.time : String(p.time);
    openDayDrawer(t, key);
  });

  addEventListener('resize', () => chart.applyOptions({}), { passive: true });
}

function nearestSession(date, data) {
  for (const d of data) if (String(d.time) >= date) return d.time;
  return null;
}

/* ══ GAVETA (drill-down) ══════════════════════════════════════════════════ */
function drawer(title, bodyHTML) {
  closeDrawer();
  const scrim = el('div', 'scrim'); scrim.onclick = closeDrawer;
  const d = el('div', 'drawer');
  d.innerHTML = `<div class="drawer-head"><b style="flex:1">${title}</b>
      <button class="x" aria-label="Close">✕</button></div>
    <div class="drawer-body">${bodyHTML}</div>`;
  d.querySelector('.x').onclick = closeDrawer;
  $('#portal').append(scrim, d);
  addEventListener('keydown', escClose);
}
const escClose = e => { if (e.key === 'Escape') closeDrawer(); };
function closeDrawer() { $('#portal').innerHTML = ''; removeEventListener('keydown', escClose); }

function openDayDrawer(t, time) {
  const a = S.assets.get(t); if (!a) return;
  const day = typeof time === 'number' ? new Date(time * 1000).toISOString().slice(0, 10) : String(time);
  const ev = (a.events || []).find(([d]) => d === day);
  const news = (a.news || []).filter(n => n.date <= day).slice(0, 1)
    .concat((a.news || []).filter(n => n.date === day));
  const uniq = [...new Map(news.map(n => [n.headline, n])).values()];

  drawer(`${esc(t)} · ${esc(day)}`, `
    ${ev ? `<div class="ev" style="border-color:color-mix(in srgb, var(--warn) 40%, transparent);background:var(--warn-soft)">
      <div class="ev-lab">Flagged by the rolling z-score detector</div>
      <div class="ev-val">z ${ev[1] >= 0 ? '+' : ''}${ev[1]} against its own 20-day norm (threshold ±1.5)</div>
      <div class="ev-src"><span class="tag measured">computed</span>
        <span class="dim">Same rule as the live detector, replayed over this day.</span></div></div>`
      : `<p class="dim" style="font-size:var(--t-sm)">The detector did not flag this day.</p>`}

    <h5 style="margin:var(--s5) 0 var(--s2);font-size:var(--t-xs);letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3)">Headlines on or before this day</h5>
    ${uniq.length ? uniq.map(n => `
      <div style="padding:var(--s3) 0;border-bottom:1px solid var(--line)">
        <div style="font-size:var(--t-sm);line-height:1.5">${esc(n.headline)}</div>
        <div class="row-meta" style="margin-top:6px">
          <span class="tag measured">source</span>
          ${n.source ? `<span>${esc(n.source)}</span>` : '<span class="dim">source not recorded</span>'}
          <span>${esc(n.date)}</span>
          ${n.d5 != null ? `<span class="${sgn(n.d5)}">${pct(n.d5)} after 5 sessions</span>`
            : '<span class="dim">outcome not yet measurable</span>'}
        </div>
        ${n.url ? `<a href="${esc(n.url)}" target="_blank" rel="noopener" style="font-size:var(--t-xs)">Open source ↗</a>` : ''}
      </div>`).join('')
      : '<p class="dim" style="font-size:var(--t-sm)">No captured headline for this day.</p>'}

    <div style="margin-top:var(--s5)">
      <button class="tbtn ai" data-ask="What happened with ${esc(t)} around ${esc(day)}?">Ask the analyst about this day</button>
    </div>
    <p class="dim" style="font-size:var(--t-xs);margin-top:var(--s4)">
      A headline appearing near a move is <b>temporal proximity</b>. This system does not measure
      causation, and does not claim it.</p>`);
}

/* ══ PAINEL DE INTELIGÊNCIA ═══════════════════════════════════════════════ */
function railHTML() {
  return S.rail.tab === 'report' ? reportHTML() : chatHTML();
}

function reportHTML() {
  const r = S.rail.report;
  if (S.rail.busy && !r) return `<div class="dim" style="font-size:var(--t-sm)">Gathering evidence and synthesising…</div>
    ${'<div class="sk sk-line"></div><div class="sk sk-line" style="width:80%"></div><div class="sk sk-line" style="width:64%"></div>'.repeat(3)}`;
  if (!r) return `<div class="dim" style="font-size:var(--t-sm)">
    <p>A situation report gathers everything the system measured for the current scope and
    synthesises it into prose. Every sentence carries the identifiers of the facts it rests on —
    click one to open the evidence.</p>
    <button class="tbtn ai" id="gen-report-2" style="margin-top:var(--s3)">Generate report</button></div>`;

  const src = r.generated ? `<span class="tag gen">AI-generated · ${esc(r.source)}</span>`
                          : `<span class="tag det">composed from facts</span>`;
  return `<div style="display:flex;align-items:center;gap:var(--s2);margin-bottom:var(--s4);flex-wrap:wrap">
      ${src}<span class="dim" style="font-size:var(--t-xs)">${r.latency_s ? r.latency_s + 's' : ''}</span>
      <span class="spacer" style="flex:1"></span>
      <button class="tbtn" id="regen" style="height:26px;font-size:var(--t-xs)">Regenerate</button></div>
    ${r.guarded ? `<div class="ev" style="border-color:color-mix(in srgb,var(--warn) 40%,transparent);background:var(--warn-soft);margin-bottom:var(--s4)">
      <div class="ev-lab">The fidelity guard rejected part of the model's output and replaced it
        with the deterministic composition.</div></div>` : ''}
    ${r.sections.map(s => `<div class="report-sec"><h5>${esc(s.title)}</h5>
      <p>${anchorize(s.text)}</p></div>`).join('')}
    <p class="dim" style="font-size:var(--t-xs);border-top:1px solid var(--line);padding-top:var(--s3)">
      The generator receives only the facts listed above; it cannot query the market. Numbers are
      checked against those facts before this text is shown.</p>`;
}

function chatHTML() {
  if (!S.rail.chat.length) return `<div class="dim" style="font-size:var(--t-sm)">
    <p>Ask about what the system measured. The analyst reads the same evidence you can see,
    and will move the dashboard to show you the answer.</p>
    <div class="suggest">
      ${['What stood out today?', 'Why did NVDA move?', 'Which names did the market explain?',
         'Why was the system quiet on Apple?', 'Show me the last month for Tesla']
        .map(q => `<button data-ask="${esc(q)}">${esc(q)}</button>`).join('')}
    </div></div>`;
  return S.rail.chat.map(m => m.role === 'you'
    ? `<div class="msg msg-you"><div class="bubble">${esc(m.text)}</div></div>`
    : `<div class="msg msg-ai">
        <div class="msg-head">${m.pending ? '<span class="dim" style="font-size:var(--t-xs)">thinking…</span>'
          : `<span class="tag ${m.generated ? 'gen' : 'det'}">${m.generated ? 'AI · ' + esc(m.source) : 'composed from facts'}</span>
             ${m.action ? `<span class="dim" style="font-size:var(--t-xs)">moved the view</span>` : ''}`}</div>
        <div class="bubble">${m.pending ? '<div class="sk sk-line"></div><div class="sk sk-line" style="width:70%"></div>' : anchorize(m.text)}</div>
      </div>`).join('');
}

/* Transforma [f3] em chips clicáveis. É isto que torna "AI explicável" verificável em vez
 * de prometida: cada frase abre os factos de que saiu. */
function anchorize(text) {
  return esc(text).replace(/\[(f\d+)\]/g, (_, id) =>
    `<button class="anchor" data-fact="${id}" title="Show the evidence">${id}</button>`);
}

function showFact(id, near) {
  const f = S.bundleFacts.get(id);
  document.querySelectorAll('.ev.fact').forEach(n => n.remove());
  document.querySelectorAll('.anchor.on').forEach(n => n.classList.remove('on'));
  if (!f) return;
  near.classList.add('on');
  const origin = { measured: 'measured', computed: 'computed', model: 'model output' }[f.origin] || f.origin;
  const box = el('div', 'ev fact', `
    <div class="ev-lab">${esc(f.label)}</div>
    <div class="ev-val">${esc(String(f.value))}</div>
    <div class="ev-src"><span class="tag measured">${esc(origin)}</span>
      ${f.detail?.method ? `<span class="dim">${esc(f.detail.method)}</span>` : ''}
      ${f.detail?.similarity != null ? `<span class="dim">cosine ${f.detail.similarity}</span>` : ''}
      ${f.detail?.source ? `<span class="dim">${esc(f.detail.source)}</span>` : ''}</div>`);
  near.closest('p, .bubble')?.after(box);
}

async function generateReport() {
  S.rail.busy = true; S.rail.report = null; paintRail();
  try {
    const body = S.route.ticker ? { scope: 'asset', ticker: S.route.ticker } : { scope: 'market' };
    const r = await post('/api/report', body);
    (r.facts || []).forEach(f => S.bundleFacts.set(f.id, f));
    S.rail.report = r;
    if (!S.route.ticker) paintSituation(r);
  } catch (e) {
    S.rail.report = { sections: [{ title: 'Unavailable', text: 'The report could not be generated right now.' }], generated: false, source: 'error' };
  }
  S.rail.busy = false; paintRail();
}

/* A situação gerada substitui a determinística na faixa do topo — e a etiqueta muda com ela,
 * porque um texto gerado e um texto composto não valem o mesmo. */
function paintSituation(r) {
  const body = $('#sit-body'), tag = $('#sit-tag'); if (!body) return;
  const sit = r.sections.find(s => s.key === 'situation');
  const mov = r.sections.find(s => s.key === 'movement');
  body.innerHTML = `<p>${anchorize(sit?.text || '')}</p>` + (mov ? `<p class="sit-sub">${anchorize(mov.text)}</p>` : '');
  if (tag) { tag.className = `tag ${r.generated ? 'gen' : 'det'}`; tag.textContent = r.generated ? `AI-generated · ${r.source}` : 'composed from facts'; }
}

async function askAnalyst(q) {
  if (!q.trim() || S.rail.busy) return;
  S.rail.tab = 'chat'; openRail();
  S.rail.chat.push({ role: 'you', text: q }, { role: 'ai', pending: true });
  S.rail.busy = true; paintRail();
  try {
    const ctx = { ticker: S.route.ticker, range: S.range, view: S.route.view };
    const r = await post('/api/ask', { question: q, context: ctx });
    (r.facts || []).forEach(f => S.bundleFacts.set(f.id, f));
    const act = r.plan?.action;
    S.rail.chat[S.rail.chat.length - 1] = { role: 'ai', text: r.text, generated: r.generated,
      source: r.source, action: act && act.type !== 'none' ? act : null };
    if (act) applyAction(act);
  } catch (e) {
    S.rail.chat[S.rail.chat.length - 1] = { role: 'ai', text: 'The analyst is unavailable right now.', generated: false, source: 'error' };
  }
  S.rail.busy = false; paintRail();
  $('#rail-body').scrollTop = $('#rail-body').scrollHeight;
}

/* Linguagem natural -> estado da aplicação. É o que faz da conversa uma SEGUNDA INTERFACE
 * para os mesmos dados, em vez de uma caixa de texto ao lado do produto. */
function applyAction(a) {
  if (a.type === 'select_ticker' && a.ticker) { go({ view: 'asset', ticker: a.ticker }); return; }
  if (a.type === 'set_range' && a.range) {
    S.range = a.range;
    // Pedir "o último mês da Tesla" a partir da vista do mercado são DUAS mudanças de estado.
    if (a.ticker && a.ticker !== S.route.ticker) { go({ view: 'asset', ticker: a.ticker }); return; }
    if (S.route.ticker) render();
    return;
  }
  if (a.type === 'toggle_series' && a.series) {
    if (a.series === 'events') S.series.events = !S.series.events;
    if (a.series === 'news') S.series.news = !S.series.news;
    if (S.route.ticker) render();
    return;
  }
  if (a.type === 'open_screener') go({ view: 'screener' });
  if (a.type === 'open_method') go({ view: 'method' });
}

function paintRail() {
  $('#rail-body').innerHTML = railHTML();
  $('#rail-foot').hidden = S.rail.tab !== 'chat';
  $('#tab-report').setAttribute('aria-selected', S.rail.tab === 'report');
  $('#tab-chat').setAttribute('aria-selected', S.rail.tab === 'chat');
}
function openRail() { S.rail.open = true; $('#rail').hidden = false; paintRail(); }

/* ══ VISTAS SECUNDÁRIAS ═══════════════════════════════════════════════════ */
async function viewScreener() {
  const d = await api('/api/screener');
  const rows = d.rows || [];
  const by = {};
  rows.forEach(r => { by[r.stage] = (by[r.stage] || 0) + 1; });
  const label = { no_news: 'No headline found', none_relevant: 'Nothing named the company',
    stale: 'Headline too old', weak_precedent: 'No strong past case',
    triage_suppressed: 'Below the volume-control floor', alerted: 'Alert sent', error: 'Error' };
  return `<div class="crumb"><button data-nav-home>Overview</button><span class="sep">/</span><span class="muted">Screener</span></div>
    <h2 style="margin:0 0 var(--s2);font-size:var(--t-2xl);letter-spacing:-.03em">Why the system stayed quiet</h2>
    <p class="muted" style="max-width:70ch;margin:0 0 var(--s5)">Nine in ten scans send nothing. Silence
      is a decision this system makes, so it has to be inspectable — every name the scan looked at,
      the gate that stopped it, and <b>the margin it missed by</b>.</p>
    <div class="chips" style="margin-bottom:var(--s4)">
      ${Object.entries(by).sort((a, b) => b[1] - a[1]).map(([k, v]) =>
        `<span class="chip ${k === 'alerted' ? 'i' : ''}">${esc(label[k] || k)} · ${v}</span>`).join('')}</div>
    <div class="panel"><div class="rows">
      ${rows.slice(0, 120).map(r => `<div class="row">
        <span class="row-date">${esc(shortDate(r.date))}</span>
        <div class="row-main"><div class="row-title"><b>${esc(r.ticker)}</b> — ${esc(label[r.stage] || r.stage)}</div>
          ${r.detail ? `<div class="row-meta"><span class="num">${esc(r.detail)}</span></div>` : ''}</div>
      </div>`).join('') || '<div class="empty">No gate log available.</div>'}
    </div></div>`;
}

async function viewMethod() {
  const d = await api('/api/method');
  return `<div class="crumb"><button data-nav-home>Overview</button><span class="sep">/</span><span class="muted">Method</span></div>
    <h2 style="margin:0 0 var(--s2);font-size:var(--t-2xl);letter-spacing:-.03em">How this was evaluated</h2>
    <p class="muted" style="max-width:70ch;margin:0 0 var(--s5)">Every number below was produced by a
      script in this repository and is tied to the file that generated it. The negative results are
      here too — a product that showed only the wins of its own evaluation would be doing marketing
      with academic numbers.</p>
    ${(d.blocks || []).map(b => `<div class="panel" style="margin-bottom:var(--s4)">
      <div class="panel-head"><span class="panel-title">${esc(b.title)}</span>
        <span class="dim" style="font-size:var(--t-xs)">${esc(b.metric)}</span></div>
      <div class="rows">${b.numbers.map(n => `<div class="row">
        <div class="row-main"><div class="row-title">${esc(n.label)}</div>
          <div class="row-meta"><span>${esc(n.source)}</span>${n.note ? `<span>${esc(n.note)}</span>` : ''}</div></div>
        <span class="row-val num">${esc(n.value)}</span></div>`).join('')}</div>
      ${b.verdict ? `<div class="panel-body" style="border-top:1px solid var(--line)">
        <p class="muted" style="margin:0;font-size:var(--t-sm)">${esc(b.verdict)}</p></div>` : ''}
    </div>`).join('')}`;
}

/* ══ RENDER ═══════════════════════════════════════════════════════════════ */
async function render() {
  const v = $('#view');
  paintHeader();

  if (S.route.view === 'screener') { v.innerHTML = '<div class="sk" style="height:300px"></div>'; v.innerHTML = await viewScreener(); return; }
  if (S.route.view === 'method') { v.innerHTML = '<div class="sk" style="height:300px"></div>'; v.innerHTML = await viewMethod(); return; }

  if (S.route.view === 'asset' && S.route.ticker) {
    const t = S.route.ticker;
    v.innerHTML = viewAsset(t);
    if (!S.assets.has(t)) {
      const a = await api(`/api/asset/${t}`);
      if (a.error) { v.innerHTML = `<div class="empty">${esc(a.error)}</div>`; return; }
      // O instantâneo já traz o intradiário; junta-se ao detalhe para o cliente ter tudo.
      const row = (S.overview.rows || []).find(r => r.ticker === t) || {};
      S.assets.set(t, { ...a, intraday: row.intraday, intraday_day: row.intraday_day, prev_close: row.prev_close });
      v.innerHTML = viewAsset(t);
    }
    buildChart(t);
    loadPrecedents(t);
    return;
  }

  v.innerHTML = viewHome();
}

/* Fora do caminho crítico: carrega e injecta quando chegar. */
async function loadPrecedents(t) {
  const slot = $('#prec-q'); if (!slot) return;
  try {
    const p = S.prec.get(t) || await api(`/api/precedents/${t}`);
    S.prec.set(t, p);
    if (!p.available) {
      slot.innerHTML = `<h4>3 · Has this happened before</h4>
        <div class="dim" style="font-size:var(--t-sm)">${esc(p.reason || 'Not available.')}</div>`;
      return;
    }
    const framing = p.up && p.down
      ? `These cases moved in <b>both directions</b> (${p.up} up, ${p.down} down).`
      : p.down ? `All ${p.down} of these moved down.` : `All ${p.up} of these moved up.`;
    slot.innerHTML = `<h4>3 · Has this happened before</h4>
      <div class="dim" style="font-size:var(--t-xs);margin-bottom:var(--s3)">
        ${p.semantic ? 'Semantic retrieval (MiniLM, 384-d)' : 'Word-overlap fallback'} ·
        query: “${esc((p.query || '').slice(0, 70))}”</div>
      ${p.cases.map(c => `<div class="row" style="padding:var(--s2) 0">
        <div class="row-main"><div class="row-title" style="font-size:var(--t-xs)">${esc(c.headline.slice(0, 96))}</div>
          <div class="row-meta"><span>${esc(c.ticker)}</span><span>${esc(c.date)}</span>
            <span>cos ${c.similarity}</span></div></div>
        <span class="row-val ${sgn(c.impact_pct)}">${c.impact_pct == null ? '—' : (c.impact_pct >= 0 ? '+' : '') + c.impact_pct + '%'}</span>
      </div>`).join('')}
      <div class="muted" style="font-size:var(--t-sm);margin-top:var(--s3)">${framing}
        <span class="dim">Retrieval matches <b>theme</b>, not direction. Measured outcomes, not a forecast.</span></div>`;
  } catch { /* fail-open: a secção fica com o estado de carregamento e nada parte */ }
}

/* ══ EVENTOS ══════════════════════════════════════════════════════════════ */
document.addEventListener('click', e => {
  const card = e.target.closest('.card[data-t]');
  if (card) return go({ view: 'asset', ticker: card.dataset.t });

  if (e.target.closest('[data-nav-home]')) return go({ view: 'home' });
  if (e.target.closest('[data-nav]')) { e.preventDefault(); return go({ view: 'home' }); }

  const r = e.target.closest('#ranges button[data-r]');
  if (r) { S.range = r.dataset.r; history.replaceState({}, '', S.route.ticker ? `/?t=${S.route.ticker}${S.range !== '1D' ? '&r=' + S.range : ''}` : '/');
           document.querySelectorAll('#ranges button').forEach(b => b.setAttribute('aria-pressed', b.dataset.r === S.range));
           return buildChart(S.route.ticker); }

  if (e.target.closest('#tog-ev')) { S.series.events = !S.series.events; $('#tog-ev').setAttribute('aria-pressed', S.series.events); return buildChart(S.route.ticker); }
  if (e.target.closest('#tog-nw')) { S.series.news = !S.series.news; $('#tog-nw').setAttribute('aria-pressed', S.series.news); return buildChart(S.route.ticker); }

  const nrow = e.target.closest('[data-news]');
  if (nrow) { const a = S.assets.get(S.route.ticker); const n = a?.news?.[+nrow.dataset.news];
              if (n) return openDayDrawer(S.route.ticker, n.date); }

  const anch = e.target.closest('.anchor[data-fact]');
  if (anch) return showFact(anch.dataset.fact, anch);

  const ask = e.target.closest('[data-ask]');
  if (ask) { closeDrawer(); return askAnalyst(ask.dataset.ask); }

  if (e.target.closest('#gen-report') || e.target.closest('#gen-report-2') || e.target.closest('#regen')) {
    S.rail.tab = 'report'; openRail(); return generateReport();
  }
  if (e.target.closest('#ask-chart')) { S.rail.tab = 'chat'; openRail();
    return askAnalyst(`What is happening with ${S.route.ticker} over the ${S.range} view?`); }

  if (e.target.closest('#toggle-rail')) { S.rail.open ? ($('#rail').hidden = true, S.rail.open = false) : openRail(); return; }
  if (e.target.closest('#close-rail')) { $('#rail').hidden = true; S.rail.open = false; return; }
  if (e.target.closest('#tab-report')) { S.rail.tab = 'report'; return paintRail(); }
  if (e.target.closest('#tab-chat')) { S.rail.tab = 'chat'; return paintRail(); }
  if (e.target.closest('#nav-screener')) return go({ view: 'screener' });
  if (e.target.closest('#nav-method')) return go({ view: 'method' });
  if (e.target.closest('#theme')) {
    const now = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', now);
    localStorage.setItem('ig-theme', now);
    if (S.route.ticker) buildChart(S.route.ticker);
  }
});

$('#ask-form').addEventListener('submit', e => {
  e.preventDefault();
  const i = $('#ask-input'); const q = i.value; i.value = ''; i.style.height = 'auto';
  askAnalyst(q);
});
$('#ask-input').addEventListener('input', e => {
  e.target.style.height = 'auto'; e.target.style.height = Math.min(140, e.target.scrollHeight) + 'px';
});
$('#ask-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#ask-form').requestSubmit(); }
});

/* ══ ARRANQUE ═════════════════════════════════════════════════════════════ */
(async function boot() {
  const saved = localStorage.getItem('ig-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  readURL();
  $('#view').innerHTML = skeleton();
  try {
    S.overview = await api('/api/overview');
  } catch {
    $('#view').innerHTML = `<div class="empty">The service is unavailable. Nothing here is cached
      client-side on purpose — showing stale numbers without saying so is the failure this product
      is built to avoid.</div>`;
    return;
  }
  render();

  // Actualização silenciosa: o worker corre a 60 s. Repinta só se os dados mudaram, e nunca
  // reordena a grelha debaixo do polegar de quem está a fazer scroll.
  setInterval(async () => {
    if (document.hidden || S.route.view !== 'home') return;
    try {
      const o = await api('/api/overview');
      if (o.as_of !== S.overview.as_of) { S.overview = o; S.assets.clear(); render(); }
      else { S.overview = o; paintHeader(); }
    } catch { /* offline: mantém o que está e o carimbo de idade denuncia-o */ }
  }, 60000);
})();
