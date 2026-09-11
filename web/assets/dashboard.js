"use strict";
const ETAPAS = [
  ["no_news",           "No news at all",         "the source returned nothing for this company",
                        "There was news"],
  ["none_relevant",     "Nothing relevant",       "news arrived, but none of it named the company",
                        "Some of it named this company"],
  ["stale",             "Too old",                "the newest relevant headline is past the freshness window",
                        "The headline was recent enough"],
  ["weak_precedent",    "No strong past case",    "no past headline was similar enough to be worth showing",
                        "A comparable past case existed"],
  ["triage_suppressed", "Below the volume floor", "the learned model scored it below the floor",
                        "It cleared the volume floor"],
  ["ladder_floor",      "Second alert cost more", "an extra alert for the same company must clear a higher bar",
                        "It cleared the bar for a second alert"],
  ["duplicate_story",   "Same story, other words","already sent today under a different headline",
                        "It was not the same story again"],
  ["already_sent",      "Already sent",           "this exact headline had already gone out today",
                        "It had not gone out already"],
  ["daily_budget",      "Daily budget spent",     "the five slots for the day were already used",
                        "A slot was still free"],
  ["error",             "Error",                  "something failed while processing this company",
                        "Nothing failed"],
  ["alerted",           "Alert sent",             "cleared every gate and was delivered",
                        "Alert sent"],
];
const ORDEM = new Map(ETAPAS.map(([k], i) => [k, i]));
const ROTULO = new Map(ETAPAS.map(([k, t]) => [k, t]));
const PORQUE = new Map(ETAPAS.map(([k, , p]) => [k, p]));

const DETALHE = [
  [/^melhor sim ([\d.]+) < ([\d.]+)$/, m => `best match ${m[1]}, floor ${m[2]}`],
  [/^P=([\d.]+) < ([\d.]+)$/,          m => `scored ${m[1]}, floor ${m[2]}`],
  [/^mais recente (\S+) > (\d+)d$/,    m => `newest is ${m[1]}, ${m[2]} days past the window`],
  [/^same story, other words$/,        () => "sent under another headline"],
  [/^budget (\d+)\/day spent$/,        m => `all ${m[1]} slots for the day were used`],
  [/^cap (\d+)\/day reached$/,         m => `cap of ${m[1]} reached`],
  [/^(\d+) manchete\(s\) brutas$/,     m => `${m[1]} headlines, none about this company`],
];
const legivel = d => { for (const [rx, f] of DETALHE) { const m = rx.exec(d || ""); if (m) return f(m); }
                       return d || ""; };

const esc = s => String(s ?? "").replace(/[&<>"]/g, c =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));
const pct = v => (v == null || Number.isNaN(v)) ? "—"
  : `${v >= 0 ? "+" : "−"}${Math.abs(v * 100).toFixed(2)}%`;
const cls = v => v > 0 ? "sobe" : v < 0 ? "desce" : "";
const $ = s => document.querySelector(s);

const LIGACAO = /&lt;a href=(?:&quot;|")([\s\S]*?)(?:&quot;|")&gt;([\s\S]*?)&lt;\/a&gt;/g;

function comLigacoes(escapado) {
  return String(escapado).replace(LIGACAO, (_, cru, rotulo) => {
    const url = cru.replace(/&amp;/g, "&");
    const seguro = /^https?:\/\//i.test(url) ? url : "";
    return seguro
      ? `<a href="${esc(seguro)}" target="_blank" rel="noopener noreferrer nofollow">${rotulo}</a>`
      : rotulo;
  });
}

const soRotulo = escapado => String(escapado).replace(LIGACAO, (_, __, rotulo) => rotulo);


const R2_MEDIANA = 0.46;

// Percentagem com sinal e duas casas, para as linhas da conta.
// Mesma grafia do sinal que o `pct`: o menos tipográfico e não o hífen. Os dois aparecem
// agora na MESMA linha — a conta ao lado do resultado — e a mistura via-se.
// Duas casas com o menos tipográfico. Um beta negativo — que é o caso interessante, porque
// um β negativo vezes um fator negativo dá contribuição positiva — saía com hífen ASCII ao
// lado de percentagens com menos tipográfico, na mesma linha.
const b2 = v => `${v < 0 ? "−" : ""}${Math.abs(Number(v)).toFixed(2)}`;
const pctc = v => (v == null || !isFinite(v)) ? "—"
  : `${v >= 0 ? "+" : "−"}${Math.abs(v * 100).toFixed(2)}%`;

/* ══ Desdobramento recursivo: clicar num valor e ver de onde ele vem, até ao dado base ══
   ⚠️ O AUTOR PEDIU ISTO EM TERMOS QUE NÃO DEIXAM MARGEM: «não quero só que substituas, agora
   quero poder clicar por exemplo sobre o 0.25 e ver como é que se chegou a este... sempre...
   até chegarmos mesmo ao valor base!!! uma pessoa que não saiba dos conceitos tem que ficar a
   percebê-los!!!»

   O QUE ISSO OBRIGA, E É A PARTE QUE IMPORTA: um desdobramento que pare numa fórmula pede ao
   leitor que acredite na fórmula. Para chegar ao fundo, o ecrã tem de mostrar (a) as constantes
   e de onde vêm, (b) as quantidades estimadas e a conta que as produz, e (c) **as séries de
   preços que a regressão consumiu**. As três estão agora no cliente: a da empresa já vinha, a
   do índice e as dos setores passaram a vir para isto.

   COMO FUNCIONA: cada valor explicável é um botão com `data-exp`. Um só ouvinte em `#detalhe`
   abre a explicação logo abaixo do valor — e como essa explicação também é feita de botões
   `data-exp`, o mecanismo é recursivo sem código extra: desce-se pelo mesmo caminho.

   ⚠️ E AS CONSTANTES SÃO AS DO PYTHON, não cópias: há um teste que as compara com o
   `investigator/correlation_engine/decomposition.py`. Duas cópias de uma constante separam-se
   sem ninguém reparar, e aqui a cópia estaria a ENSINAR o número errado. */
const PRIOR_SD = 0.5;                 // PRIOR_BETA_SD
const MIN_JANELA = 10;                // MIN_WINDOW

// Um valor clicável. `t` é o que se lê; `k` é a chave da explicação.
const val = (k, t, v = null) => `<button type="button" class="f-val" data-exp="${k}"${v == null ? "" : ` data-v="${v}"`} aria-expanded="false">${t}</button>`;

const n2 = v => (v == null || !isFinite(v)) ? "—" : b2(v);

/* Os retornos diários que a regressão consumiu, calculados no browser a partir das séries
   servidas. É o fundo: abaixo disto só há os preços de fecho de onde saíram. */
function retornosDaJanela(d, qual) {
  const a = S.asset; if (!a) return [];
  const fechos = qual === "empresa" ? (a.closes || [])
    : qual === "mercado" ? (S.visao?.market_closes || [])
    : ((S.visao?.sector_closes || {})[a.sector_etf] || []);
  const n = (d.window || 20) + 2;
  const ult = fechos.slice(-n);
  const out = [];
  for (let i = 1; i < ult.length - 1; i++)   // o último dia é o explicado: fica de fora
    out.push([ult[i][0], Math.log(ult[i][1] / ult[i - 1][1])]);
  return out.slice(-(d.window || 20));
}

function tabelaDeRetornos(d) {
  const emp = retornosDaJanela(d, "empresa");
  const mer = retornosDaJanela(d, "mercado");
  const set = retornosDaJanela(d, "setor");
  if (!emp.length || !mer.length) {
    return `<p class="f-passo">The price series for this window did not reach the browser, so the
      base rows cannot be listed here.</p>`;
  }
  const pm = new Map(mer.map(r => [r[0], r[1]]));
  const ps = new Map(set.map(r => [r[0], r[1]]));
  // A coluna do setor pode faltar sozinha: uma serie por ETF, e o instantaneo salta a que
  // falhar. Sem esta nota as vinte linhas a tracejado leem-se como «o setor esteve parado».
  const semSetor = !set.length;
  const linhas = emp.filter(r => pm.has(r[0])).map(([dia, r]) =>
    `<tr><td>${dataDe(dia)}</td><td>${pctc(Math.expm1(r))}</td>`
    + `<td>${pctc(Math.expm1(pm.get(dia)))}</td>`
    + `<td>${ps.has(dia) ? pctc(Math.expm1(ps.get(dia))) : "—"}</td></tr>`);
  return `<p class="f-passo"><b>The base rows.</b> These are the daily changes the regression
      consumed: one row per trading day of the window, for the company, for the index and for the
      sector fund. Under these there is nothing left but the closing prices they came from.</p>
    <div class="f-tab"><table><thead><tr><th>day</th>
      <th>${esc(S.asset?.ticker || "company")}</th>
      <th>${esc(S.visao?.market_index || "index")}</th>
      <th>${esc(S.asset?.sector_etf || "sector")}</th></tr></thead>
      <tbody>${linhas.join("")}</tbody></table></div>
    ${semSetor ? `<p class="f-passo">The sector fund's own series did not reach the browser for
      this company, so its column is empty here. That is a missing reading, not a flat sector: the
      sector share of the move above was computed from it on the server.</p>` : ""}
    <p class="f-passo">${linhas.length} day${linhas.length === 1 ? "" : "s"}. A day's change is the
      natural logarithm of its close divided by the previous close, which is the form that adds up
      across days; the percentages shown are that value turned back into a percentage to read.</p>`;
}

/* O registo. Cada entrada devolve HTML, e esse HTML pode conter mais valores clicáveis. */
const EXPLICA = {
  beta_final: d => `<p class="f-passo"><b>What this number is.</b> It is this company's
      sensitivity to the factor, and it is the one figure in the line that is <em>estimated</em>
      rather than observed: the market's move is a fact, and this says how much of it lands here.
      A value of 1 means moving one-for-one with the factor, 2 means twice as much, and a negative
      value means moving against it.</p>
    <p class="f-passo">It is not the raw result of the fit. The fit produced a slope, and that
      slope was pulled towards the typical value in proportion to how precisely it was measured.
      The panel below this line shows that whole calculation, and every number in it opens.</p>`,

  sigma_prior: () => `<p class="f-passo"><b>Where ${n2(PRIOR_SD * PRIOR_SD)} comes from.</b> It is
      ${val("prior_sd", n2(PRIOR_SD))} multiplied by itself: ${n2(PRIOR_SD)} × ${n2(PRIOR_SD)} =
      ${n2(PRIOR_SD * PRIOR_SD)}. The weighting compares two spreads against each other, and a
      spread enters such a comparison as a variance, which is a standard deviation times
      itself.</p>`,

  prior_sd: () => `<p class="f-passo"><b>Where ${n2(PRIOR_SD)} comes from, and what it is not.</b>
      It is how far apart the sensitivities of different companies typically sit. Most shares move
      between roughly half of the market's move and twice it, and ${n2(PRIOR_SD)} is that spread
      written as a standard deviation.</p>
    <p class="f-passo">It is an economic magnitude and not a cut-off: nothing is ever compared
      against it and nothing is discarded by it. It decides only <em>how much</em> the typical
      value is allowed to pull a noisy estimate, and another reasonable choice would move the
      weighting slightly without changing which way it leans.</p>`,

  se: (d, ds) => `<p class="f-passo"><b>Where ${n2(Number(ds.v))} comes from.</b> It is the standard error of
      the slope: how much that slope would be expected to wobble if the same fit ran on a
      different sample of days. It comes out of how far the
      ${val("janela", (d.window || 20) + " days")} of the window fell from the fitted line,
      measured against how widely the factor itself moved during them.</p>
    <p class="f-passo">Two things make it large: days the model failed to track, and a factor that
      barely moved — a factor that stays still carries almost no information about how strongly
      this company follows it. This is the quantity that decides how much of the measured slope
      survives the weighting.</p>
    ${tabelaDeRetornos(d)}`,

  beta_bruto: (d, ds) => `<p class="f-passo"><b>Where ${n2(Number(ds.v))} comes from.</b> It is the slope of
      a straight line fitted through the ${val("janela", (d.window || 20) + " days")} before the
      day being explained: on days when the factor moved one percent, this company moved about
      ${n2(Number(ds.v))} percent. The line is placed so that the total squared distance from it to
      the actual days is the smallest it can be.</p>
    <p class="f-eq">slope = (how company and factor moved together) ÷ (how much the factor moved)</p>
    <p class="f-passo">Both quantities in that division are read off the rows below, and nothing
      else enters it.</p>
    ${tabelaDeRetornos(d)}`,

  janela: d => `<p class="f-passo"><b>Where ${d.window || 20} comes from.</b> It is the number of
      trading days used to estimate the sensitivities, and it is the same window the rarity
      measure uses, so that the page does not carry two different notions of «recent».</p>
    <p class="f-passo"><b>And this is the part that decides whether any of it can be trusted:</b>
      the window ends the day <em>before</em> the one being explained. Not one price from the day
      under explanation, and none from after it, takes part in estimating the sensitivities. Below
      ${MIN_JANELA} usable days the estimate is refused outright instead of reported as weak.</p>`,

  prior_m: () => `<p class="f-passo"><b>Where 1.00 comes from.</b> It is the sensitivity of the
      market to itself. A perfectly typical company moves one-for-one with the index, so when a
      window is too noisy to say anything, «typical» is the honest place to fall back to. Nothing
      was fitted to obtain it.</p>`,

  prior_s: () => `<p class="f-passo"><b>Where 0.00 comes from.</b> The sector figure used here is
      what the sector did <em>beyond</em> the market, with the market's own movement already taken
      out of it. A company with no particular tie to its sector, past being in the market at all,
      has zero sensitivity to that leftover — so zero is the neutral fallback.</p>`,

  r2_falta: d => `<p class="f-passo"><b>What «variation the model missed» is.</b> For each of the
      ${val("janela", (d.window || 20) + " days")} of the window the model predicts a move from the
      index and the sector; the miss is the distance between that and what happened. The misses are
      squared, so that being wrong in either direction counts, and then averaged.</p>
    ${tabelaDeRetornos(d)}`,

  r2_total: d => `<p class="f-passo"><b>What «total variation» is.</b> How much this company moved
      from day to day over the same ${val("janela", (d.window || 20) + " days")}, measured against
      its own average. It is what a model that knew nothing but that average would miss, and it is
      the yardstick the misses are held against — which is why a model that tracked nothing scores
      zero and one that tracked everything scores one.</p>`,

  mediana: () => `<p class="f-passo"><b>Where 0.46 comes from.</b> The same split was run for each
      of the seventeen companies of the sector map, and 0.46 is the middle value of their fit
      coefficients: half came out above it and half below. It is a median rather than an average
      precisely so that one badly fitting company cannot drag it.</p>
    <p class="f-passo">It is here so that the coefficient above is read against something. On its
      own, a number like 0.44 says nothing about whether it is normal for this method.</p>`,

  fator_mercado: (d, ds) => `<p class="f-passo"><b>Where ${pctc(Number(ds.v))} comes from.</b> It is the change
      of ${esc(S.visao?.market_index || "the index")} on this day, from the previous close to this
      one — the same series the sensitivity was estimated against, so that both halves of the
      multiplication describe the same thing.</p>
    <p class="f-passo">This number is shared by every company on the page. What differs from one
      company to the next is the sensitivity it gets multiplied by.</p>
    ${tabelaDeRetornos(d)}`,

  fator_setor: (d, ds) => `<p class="f-passo"><b>Where ${pctc(Number(ds.v))} comes from.</b> It is what
      ${esc(S.asset?.sector_etf || "the sector fund")} did on this day <em>after</em> the market's
      own movement is taken out of it. Removing the market first is what stops the same movement
      from being counted twice, once as market and once as sector.</p>
    ${tabelaDeRetornos(d)}`,
};

/* Um só ouvinte, e é o que torna o mecanismo recursivo: o HTML que ele injecta também tem
   valores clicáveis, e volta a cair aqui. */
function ligarDesdobramento() {
  const raiz = $("#detalhe");
  if (!raiz || raiz.dataset.exp === "1") return;
  raiz.dataset.exp = "1";
  raiz.addEventListener("click", e => {
    const b = e.target.closest(".f-val");
    if (!b || !raiz.contains(b)) return;
    e.preventDefault();
    e.stopPropagation();          // não fechar o <details> que contém o valor
    const seg = b.nextElementSibling;
    if (seg && seg.classList.contains("f-mais")) {
      seg.remove(); b.setAttribute("aria-expanded", "false"); return;
    }
    const f = EXPLICA[b.dataset.exp];
    if (!f) return;
    const cx = document.createElement("div");
    cx.className = "f-mais";
    try {
      cx.innerHTML = f(S.asset?.decomp || {}, b.dataset);
    } catch {
      cx.innerHTML = '<p class="f-passo">This value cannot be broken down further from the data '
        + 'on this page.</p>';
    }
    b.after(cx);
    b.setAttribute("aria-expanded", "true");
  });
}

/* ── Uma parcela da repartição, com a conta na linha e o resto a desdobrar ───────────────
   ⚠️ ESTA FUNÇÃO EXISTE POR CAUSA DE UMA PERGUNTA DO AUTOR, e a pergunta apanhou um RÓTULO
   ENGANADOR e não uma explicação em falta: «porque é que para as empresas a percentagem do
   mercado é diferente?». A linha dizia «Market −0,42%», e isso lê-se naturalmente como *o
   mercado caiu 0,42%* — que seria o mesmo número para as doze empresas. O que ali está é
   `β_mercado × retorno do mercado`, ou seja a fatia do movimento DESTA empresa que o mercado
   explica; o retorno do mercado é partilhado e o β é dela.

   A correção é mostrar a multiplicação na própria linha, porque é isso que faz a pergunta
   responder-se a si mesma sem um clique. A conta já existia atrás de um `<details>` único
   para a repartição inteira, e a pergunta é a prova de que ali não era encontrada.

   E desdobra-se em dois níveis, como o autor pediu: nível 1 diz o que a parcela é, nível 2
   diz de onde vem o β — com o estimado em bruto, o erro-padrão e o peso de Vasicek, para o
   encolhimento poder ser refeito por quem lê em vez de aceito. */
const PRIOR_SD2 = 0.25;           // σ²_prior do encolhimento (PRIOR_BETA_SD = 0,5)
const PRIOR_BETA = {market: 1, sector: 0};

function betaDesdobrado(chave, bruto, se, beta, nome) {
  if (bruto == null || !isFinite(bruto)) return "";
  const prior = PRIOR_BETA[chave];
  const temSe = se != null && isFinite(se) && se > 0;
  const w = temSe ? PRIOR_SD2 / (PRIOR_SD2 + se * se) : 1;
  return `<details class="f-nivel"><summary>Where does β = ${b2(beta)} come from?</summary>
    <p class="f-passo">β is measured, not chosen. A regression over the window above asks how much
      ${esc(nome)} moved on days when this factor moved, which came out at
      <b>${val("beta_bruto", b2(bruto), bruto)}</b>.</p>
    ${temSe ? `<p class="f-passo">A slope estimated from a few weeks is noisy, so it is pulled
      towards the typical value of ${val(chave === "market" ? "prior_m" : "prior_s", b2(prior))} in proportion to how precisely it was
      measured — the noisier the estimate, the less of it is kept:</p>
    <p class="f-eq">weight = σ²<sub>prior</sub> ÷ (σ²<sub>prior</sub> + standard error²)
      = ${val("sigma_prior", PRIOR_SD2.toFixed(2))} ÷ (${val("sigma_prior", PRIOR_SD2.toFixed(2))} + ${val("se", se.toFixed(2), se)}²)
      = ${w.toFixed(2)}</p>
    <p class="f-eq">β = ${w.toFixed(2)} × ${val("beta_bruto", b2(bruto), bruto)}
      + ${(1 - w).toFixed(2)} × ${val(chave === "market" ? "prior_m" : "prior_s", b2(prior))} = ${b2(beta)}</p>
    <p class="f-passo">So ${Math.round(w * 100)}% of what this window measured is kept. Nothing is
      capped or discarded: a clean fit keeps its slope, a noisy one falls back towards the typical
      value. Every figure above is rounded to two places while the weighting runs on the full
      values, so redoing the line by hand can land a little off the β shown.</p>`
      : `<p class="f-passo">The fit left no room for error in this window, so the measured slope was
        kept as it stands.</p>`}</details>`;
}

function parcela(d, chave, rotulo, valor, max, nome) {
  const motor = d.driver === chave;
  const beta = chave === "market" ? d.beta_market : chave === "sector" ? d.beta_sector : null;
  const rFator = (beta && valor != null) ? valor / beta : null;
  // A conta na linha: é o que responde, sem clique, a «porque é que isto difere por empresa?».
  const conta = chave === "company" ? "the remainder"
    : (beta && !d.fallback)
      ? `β ${val("beta_final", b2(beta))} × ${val(chave === "market" ? "fator_mercado" : "fator_setor", pctc(rFator), rFator)}`
      : "";
  const barra = `<span class="d-pista"><i style="width:${Math.abs(valor || 0) / max * 50}%;` +
    `${valor < 0 ? "right" : "left"}:50%;background:var(--${valor < 0 ? "desce" : "sobe"})"></i></span>`;
  const porque = chave === "company"
    ? `<p class="f-passo">This one has no formula. Market and sector are products — a sensitivity
        times what that factor did today. The company figure is whatever those two do not account
        for, obtained by subtraction, which is why the three always add up to the move exactly and
        why anything the model missed lands here.</p>`
    : `<p class="f-passo">This is not what the ${chave} did. It is the part of ${esc(nome)}'s move
        that the ${chave} accounts for: ${chave === "market" ? "the market" : "the sector"} moved
        ${pctc(rFator)}, and ${esc(nome)} carries a sensitivity of ${b2(beta)} to it,
        so the two multiply to ${pctc(valor)}. <b>The factor return is shared by every company; the
        sensitivity is this company's own</b> — which is why this line differs from one company to
        the next even on the same day.</p>
       ${betaDesdobrado(chave, chave === "market" ? d.beta_market_raw : d.beta_sector_raw,
                        chave === "market" ? d.beta_market_se : d.beta_sector_se,
                        Number(beta), nome)}`;
  return `<details class="d-parc"><summary class="d-lin">
      <span class="rot ${motor ? "motor" : ""}">${rotulo}</span>
      <span class="d-meio">${barra}${conta ? `<span class="d-conta">${conta}</span>` : ""}</span>
      <span class="val ${cls(valor)}">${pct(valor)}</span>
    </summary><div class="f-corpo">${porque}</div></details>`;
}


/* O R2 explicado do zero: o que mede, como se calcula, e o que ESTE valor quer dizer. */
function explicarR2(d, nome) {
  if (!d) return "";
  if (d.fallback) {
    return `<p class="f-passo"><b>Reliability.</b> The sensitivities could not be estimated from
      the past year, so this split assumes ${esc(nome)} moves one-for-one with the market. Read it
      as a placeholder, not a measurement.</p>`;
  }
  const r = d.r2;
  if (r === null || r === undefined || !isFinite(r)) return "";
  const pc = Math.round(r * 100);
  if (r <= 0) {
    return `<p class="f-passo"><b>4. How much to trust it.</b> R² came out at or below zero, which
      means that over the past ${d.window} days this market-and-sector model described
      ${esc(nome)} no better than a flat line would. The split above still adds up, but it rests on
      a fit that does not describe the data.</p>`;
  }
  const acima = r >= R2_MEDIANA;
  return `
    <p class="f-passo"><b>4. How much to trust it: R².</b> R² answers one question — over the
      ${val("janela", d.window + " trading days")} before this one, how much of ${esc(nome)}'s day-to-day movement did
      this same market-and-sector model manage to track?</p>
    <p class="f-eq">R² = 1 − ${val("r2_falta", "(variation the model missed)")} ÷ ${val("r2_total", "(total variation)")}</p>
    <p class="f-passo">A model that tracked every day perfectly would leave nothing missed and score
      1. A model that tracked nothing would score 0. Here it is
      <b>${r.toFixed(2)}</b>, so the model followed about <b>${pc}%</b> of ${esc(nome)}'s daily
      movement and missed the other ${100 - pc}%. ${acima
        ? `That is at or above the ${val("mediana", Math.round(R2_MEDIANA * 100) + "% median")} measured across the
           seventeen companies of the sector map, so the split above is on the firmer side of
           what this method achieves.`
        : `That is below the ${val("mediana", Math.round(R2_MEDIANA * 100) + "% median")} measured across the seventeen
           companies of the sector map. Treat the split as indicative: the weaker the fit, the
           more of the move ends up in the company line simply because the model could not
           place it.`}</p>`;
}


// Estado de navegação único. Dados remotos têm cache própria e não são copiados por vista.
const S = {modo:"hoje", ticker:null, intervalo:"1D", visao:null, asset:null,
  camadas:{alertas:true, assinalados:true, referencia:true, zscore:false, noticias:false},
  alertas:[], votos:{}, funil:[], feedLimite:12, feedTicker:"", feedKind:"", histIntervalo:"3M", next:null, remaining:0,
  total:0, diaHist:null, escolha:0, feedRequest:0, modalRequest:0, asOf:null};
const cache = new Map(), pending = new Map();
async function json(url, {ttl=30000, force=false}={}) {
  const hit = cache.get(url);
  if (!force && hit && Date.now()-hit.at < ttl) return hit.value;
  if (pending.has(url)) return pending.get(url);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  const task = (async () => {
    const response = await fetch(url, {signal:controller.signal, cache:"no-store"});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const value = await response.json();
    cache.set(url, {at:Date.now(), value});
    if (cache.size > 50) cache.delete(cache.keys().next().value);
    return value;
  })();
  pending.set(url, task);
  try { return await task; }
  finally { clearTimeout(timer); pending.delete(url); }
}
const horaDe = iso => {
  const d = new Date(iso);
  return !iso || Number.isNaN(+d) ? "—" : d.toLocaleTimeString("en-GB",
    {hour:"2-digit", minute:"2-digit", timeZone:"UTC"}) + " UTC";
};
const dataDe = day => day ? new Date(day.slice(0,10)+"T12:00:00Z").toLocaleDateString("en-GB",
  {day:"numeric", month:"short", year:"numeric", timeZone:"UTC"}) : "date unavailable";
const tipo = kind => ({news:"News",market:"Price move",summary:"Session summary",open:"Market open"}[kind] || "Message");
function retry(target, text, action) {
  target.innerHTML = `<p class="vazio">${esc(text)} <button class="text-button" data-retry>Try again</button></p>`;
  target.querySelector("[data-retry]").onclick = action;
}
function notice(text="") { $("#notice").hidden = !text; $("#notice").textContent = text; }
function updateStatus(v) {
  $("#estado").textContent = v.as_of ? `${v.fresh ? "Updated" : "Delayed"} ${v.age_label || Math.round(v.age_s || 0)+"s ago"}` : "Data unavailable";
  $("#pulso").className = "pulso"+(v.fresh ? "" : " frio");
}
function orderedRows() {
  return [...(S.visao?.rows || [])].sort((a,b) => Number(b.flagged)-Number(a.flagged)
    || Math.abs(b.z || 0)-Math.abs(a.z || 0) || a.ticker.localeCompare(b.ticker));
}
function pintarOverview() {
  const v=S.visao, rows=orderedRows(), flagged=rows.filter(r=>r.flagged);
  const day=rows.map(r=>r.price_day).filter(Boolean).sort().at(-1);
  $("#dataHoje").textContent = `LATEST CLOSE · ${dataDe(day)}`;
  $("#frase").textContent = !rows.length ? "No price snapshot available"
    : flagged.length ? `${flagged.length} unusual move${flagged.length===1 ? "" : "s"} to examine`
    : "No unusual moves at the latest close";
  $("#resumo").textContent = `${rows.length} companies monitored. Select one to see what moved and the evidence behind it.`;
  $("#mercado").textContent = v.market?.label || "Hours unavailable";
  $("#mercado").title = v.market?.detail || "";
  $("#notaMercado").innerHTML = v.market_move == null ? "" :
    `<span>${esc(v.market_index || "Market index")} · latest close</span><strong class="num ${cls(v.market_move)}">${pct(v.market_move)}</strong>`;
  $("#notaEmpresas").textContent = rows.length;
  // Não substituir a lista se os valores não mudaram: mantém foco e posição de rolagem.
  const signature = JSON.stringify(rows.map(r=>[r.ticker,r.name,r.move,r.flagged]));
  if (S.rowSignature !== signature) {
    $("#empresas").innerHTML = rows.map(r => `<button class="company" data-t="${esc(r.ticker)}" aria-pressed="${r.ticker===S.ticker}">
      <img src="/assets/logos/${esc(r.ticker)}.png" alt="" width="30" height="30">
      <span class="company-name"><b>${esc(r.name || r.ticker)}</b><small>${esc(r.ticker)}</small>${r.flagged ? '<span class="flag" title="Unusual move for this company"><span aria-hidden="true">\u25C6</span> Unusual</span>' : ""}</span>
      <span class="num ${cls(r.move)}">${pct(r.move)}</span></button>`).join("") || '<p class="vazio">No companies available.</p>';
    $("#empresas").querySelectorAll("button").forEach(b=>b.onclick=()=>abrirEmpresa(b.dataset.t));
    S.rowSignature=signature;
  }
  updateStatus(v);
}

let chartLibrary;
function loadCharts() {
  if (typeof LightweightCharts !== "undefined") return Promise.resolve();
  if (!chartLibrary) chartLibrary = new Promise((resolve,reject)=>{
    const script=document.createElement("script"); script.src="/assets/vendor/lightweight-charts.js";
    script.onload=resolve; script.onerror=()=>{script.remove(); chartLibrary=null; reject(new Error("chart unavailable"));};
    document.head.append(script);
  });
  return chartLibrary;
}
function disposeCharts() {
  S.obs?.disconnect(); S.obsZ?.disconnect();
  S.grafico?.remove(); S.graficoZ?.remove();
  S.grafico=null; S.graficoZ=null; S.obs=null; S.obsZ=null;
}
const INTERVALOS=["1D","1M","3M","6M","1Y"];
const TITULO_GRAFICO={"1D":"Intraday price","1M":"One month of closes","3M":"Three months of closes","6M":"Six months of closes","1Y":"One year of closes"};
const CAMADAS=[
  ["alertas","Delivered alerts"], ["referencia","Previous close"],
  ["assinalados","Flagged days"], ["zscore","Rarity scale (z)"], ["noticias","Historical news"]
];
function camadasHTML() {
  return CAMADAS.filter(([k])=>S.intervalo==="1D" ? ["alertas","referencia"].includes(k) : k!=="referencia")
    .map(([k,label])=>`<label class="cx"><input type="checkbox" data-c="${k}" ${S.camadas[k]?"checked":""}>${label}</label>`).join("");
}
function veredicto(a) { return S.visao?.rows.find(r=>r.ticker===a.ticker)?.verdict || "Rarity baseline unavailable."; }
/* Uma escolha governa a página: o detalhe E a lista de eventos. Antes havia um combobox
   separado, ou seja dois controlos para a mesma decisão, e a lista podia estar a mostrar uma
   empresa diferente daquela que o painel analisava. */
function sincronizarEscopo(t) {
  const todas = t === "";
  const b = $("#todasEmpresas");
  if (b) b.setAttribute("aria-pressed", String(todas));
  const e = $("#feedEscopo");
  if (e) e.textContent = todas ? "all companies" : t;
}
/* ── O âmbito «todas as empresas» passa a mostrar o MERCADO ──────────────────────────────
   ⚠️ O AUTOR APONTOU UMA INCOERÊNCIA DE ESTADO, e tinha razão: com «events from all
   companies» activo ficavam DUAS coisas activas ao mesmo tempo — a lista era do canal inteiro
   e o gráfico continuava a ser de uma empresa, que ficava com o botão marcado. Ou seja o
   controlo dizia «todas» e a metade de cima da página dizia «esta».

   Das três saídas que ele nomeou — minimizar o gráfico, removê-lo, ou mostrar o mercado — a
   terceira é a única que responde à pergunta em vez de a apagar: com o âmbito no conjunto, o
   que interessa é o que o conjunto fez.

   ⚠️ E O ÍNDICE É O SPY, NÃO O NASDAQ. O autor escreveu «o mercado, nasdaq no caso», e a
   maioria das doze empresas é mesmo cotada no NASDAQ — mas o fator de mercado deste sistema é
   o SPY, em toda a decomposição e em toda a dissertação. Desenhar o SPY com o rótulo NASDAQ
   seria falso; e trocar o fator invalidaria os números congelados. Fica o SPY, dito pelo nome.

   E CONSTRÓI-SE UM PSEUDO-ATIVO em vez de um segundo caminho de gráfico. Reimplementar o
   desenho aqui deixaria dois desenhos a divergir sem nada os comparar, que é a classe de
   defeito que este projeto pagou na política de alertas e nas frases do veredicto. */
/* A frase do cabeçalho quando o âmbito é o conjunto. Conta o que a grelha já mediu — quantas
   empresas foram assinaladas hoje — em vez de interpretar o movimento do índice, que é
   precisamente o que este trabalho recusa fazer. */
function frasedoMercado() {
  const rows = S.visao?.rows || [];
  const n = rows.filter(r => r.flagged).length;
  const idx = S.visao?.market_index || "the market";
  if (!rows.length) return `${idx}, the market factor used throughout this system.`;
  return n === 0
    ? `${idx}, the market factor used throughout this system. None of the ${rows.length} `
      + "companies monitored moved unusually for its own past today."
    : `${idx}, the market factor used throughout this system. ${n} of the ${rows.length} `
      + `compan${rows.length === 1 ? "y" : "ies"} monitored moved unusually for its own past `
      + "today.";
}


function ativoDoMercado() {
  const v = S.visao; if (!v || !(v.market_closes || []).length) return null;
  const closes = v.market_closes;
  return {
    ticker: v.market_index || "SPY",
    name: `${v.market_index || "SPY"} · the market factor this system uses`,
    mercado: true,
    move: v.market_move, z: null, flagged: false, rarity: null, decomp: null,
    vol_ratio: null, closes, events: [], alerts: [], alertsLoaded: true,
    alertsRemaining: 0, intraday: null, intraday_day: null, prev_close: null,
    price_day: closes[closes.length - 1][0],
  };
}

function mostrarMercado() {
  const a = ativoDoMercado();
  S.ticker = null;
  document.querySelectorAll(".company").forEach(b => b.setAttribute("aria-pressed", "false"));
  if (!a) {   // falha aberto: sem série, diz-se, e não se finge um gráfico
    S.asset = null;
    $("#detalhe").innerHTML = '<p class="vazio">The market series is unavailable in this ' +
      'snapshot. Select a company to see its own chart.</p>';
    disposeCharts();
    return;
  }
  S.asset = a;
  // O intervalo intradiário não existe para o índice neste instantâneo: cai no diário em vez
  // de abrir numa vista vazia, que foi um defeito real da v3.
  if (S.intervalo === "1D") S.intervalo = "1M";
  pintarDetalhe();
  void renderChart();
}


async function abrirEmpresa(t, {focus=true, force=false, url=true}={}) {
  if (!S.visao?.rows.some(r=>r.ticker===t)) return;
  const request=++S.escolha;
  S.ticker=t;
  if (S.feedTicker !== t) { S.feedTicker = t; void carregarFeed(); }
  sincronizarEscopo(t);
  document.querySelectorAll(".company").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.t===t)));
  if(matchMedia("(max-width:760px)").matches){const b=$('.company[aria-pressed="true"]');if(b)b.scrollIntoView({block:"nearest",inline:"center"});}
  if (url) {const u=new URL(location.href); u.searchParams.set("t",t); history.replaceState(null,"",u);}
  disposeCharts(); S.asset=null;
  $("#detalhe").innerHTML=`<div class="d"><h2>${esc(S.visao.rows.find(r=>r.ticker===t)?.name || t)}</h2><p class="vazio" role="status">Loading the analysis…</p></div>`;
  if (focus && matchMedia("(max-width:760px)").matches) $("#detalhe").scrollIntoView({block:"start",behavior:"smooth"});
  try {
    const a=await json(`/api/asset/${encodeURIComponent(t)}`,{force});
    if (request!==S.escolha) return;
    S.asset={...a,alerts:[],news:[]};
    pintarDetalhe();
    void companyAlerts(request,t);
  } catch {
    if (request!==S.escolha) return;
    retry($("#detalhe"),`The analysis for ${t} is unavailable.`,()=>abrirEmpresa(t,{focus:false,force:true}));
  }
}
async function companyAlerts(request,t) {
  try {
    const result=await json("/api/alerts"+`?ticker=${encodeURIComponent(t)}&limit=200`);
    if(request!==S.escolha || !S.asset) return;
    S.asset.alerts=result.rows || []; S.asset.alertsRemaining=result.remaining || 0;
    S.asset.alertsLoaded=true;
    if (S.modo==="hoje") await renderChart();
  } catch {
    if(request===S.escolha && $("#chartNotice")) $("#chartNotice").textContent="Alert markers unavailable. Price data is still shown.";
  }
}
function pintarDetalhe() {
  const a=S.asset; if(!a) return;
  const d=a.decomp, max=d ? Math.max(...[d.market,d.sector,d.company].map(v=>Math.abs(v || 0)),0.000001) : 1;
  const line=(label,value,key)=>`<div class="d-lin"><span class="rot ${d?.driver===key?"motor":""}">${label}</span>
    <span class="d-pista"><i style="width:${Math.abs(value || 0)/max*50}%;${value<0?"right":"left"}:50%;background:var(--${value<0?"desce":"sobe"})"></i></span>
    <span class="val ${cls(value)}">${pct(value)}</span></div>`;
  const rep = d ? parcela(d, "market", "Market", d.market, max, a.name || a.ticker)
                + parcela(d, "sector", "Sector", d.sector, max, a.name || a.ticker)
                + parcela(d, "company", "Company", d.company, max, a.name || a.ticker)
              : "";
  $("#detalhe").innerHTML=`<div class="d">
    <div class="d-cab">${a.mercado ? "" :
      `<img src="/assets/logos/${esc(a.ticker)}.png" alt="" width="44" height="44">`}
      <div><p class="eyebrow">${esc(a.ticker)} · ${dataDe(a.price_day)}</p><h2>${esc(a.name || a.ticker)}</h2></div>
      <span class="mv num ${cls(a.move)}">${pct(a.move)}<small>latest close</small></span></div>
    <p class="d-ver">${esc(a.mercado ? frasedoMercado() : veredicto(a))}</p>
    <div class="explanation"><h3>${a.mercado
      ? "Why there is no split here" : "What contributed to the move?"}</h3>
      ${a.mercado ? `<p class="d-nota">This is the market factor itself, so there is nothing to
          split: every company&rsquo;s market line is this series multiplied by that company's own
          sensitivity to it. Select a company to see its share of today's move.</p>`
        : d ? `<div class="d-rep">${rep}</div>
        <p class="d-nota">Contributions add up to the close-to-close move. This is a statistical split, not a causal attribution.</p>
        <p class="fit-summary">${d.fallback?"Fallback estimate":d.r2==null?"Fit unavailable":`Model fit R² ${Number(d.r2).toFixed(2)}`}${d.fallback || d.r2<R2_MEDIANA ? " · Indicative split" : ""}</p>
        <details class="fit-details"><summary>How reliable is this split?</summary><div class="f-corpo">${explicarR2(d, a.name || a.ticker) || "<p class=\"f-passo\">No fit statistic is available for this estimate.</p>"}</div></details>`
        : '<p class="summary-note">No decomposition is available for this session.</p>'}
    </div>
    <div class="chart-header"><h3 id="chartTitle">${TITULO_GRAFICO[S.intervalo]}</h3><div class="intervalos" id="intervalos" role="group" aria-label="Chart range">${INTERVALOS.map(r=>`<button data-r="${r}" aria-pressed="${r===S.intervalo}">${r}</button>`).join("")}</div></div>
    <p class="summary-note" id="chartDate"></p>
    <div class="d-graf" id="graf" role="img" aria-label="Price chart"></div>
    <div class="d-z" id="grafZ" hidden role="img" aria-label="Daily rarity scale"></div>
    <p id="chartNotice" class="summary-note" role="status"></p>
    <details class="chart-options"><summary>Chart options</summary><div class="camadas" id="camadas">${camadasHTML()}</div></details>
    <p class="legenda legenda-graf" id="legGraf" aria-label="Chart legend"></p>
    <details class="evidence" id="chartDays"><summary>Explore events on this chart</summary><div class="d-dias" id="dias"></div></details>
    <div class="evidence-actions"><button id="decision" class="quiet">Recorded news decisions</button><button id="news" class="quiet">Historical news & sources</button></div>
    </div>`;
  ligarDesdobramento();
  $("#intervalos").onclick=e=>{const b=e.target.closest("[data-r]"); if(!b) return;
    S.intervalo=b.dataset.r; $("#intervalos").querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));
    pintarFiltroTipos(); pintarFeed();  // o intervalo governa a página inteira, não só o gráfico
    $("#camadas").innerHTML=camadasHTML(); void renderChart();};
  $("#camadas").onchange=e=>{const k=e.target.dataset.c;if(!k)return;S.camadas[k]=e.target.checked;
    if(k==="noticias" && e.target.checked) void loadNews(false); else void renderChart();};
  $("#decision").onclick=()=>modalEmpresa(a.ticker);
  $("#news").onclick=()=>loadNews(true);
  void renderChart();
}
let renderId=0;
/* ── A linha da data, e porque e' que ela tinha de mudar ─────────────────────────────────
   ⚠️ O AUTOR PERGUNTOU «hoje e' dia 11 de setembro e nao vejo no grafico o 11 de setembro».
   O ecrã dizia «Session 10 Sept 2026 · times in UTC», que é verdade e **não responde à
   pergunta**. A resposta é que a bolsa americana ainda não abriu: às 10:53 UTC de dia 11 a
   sessão de hoje não existe, logo a série intradiária mais recente é a de ontem.

   Um ecrã que mostra o dia anterior sem dizer porquê ensina o leitor a desconfiar dos dados
   quando os dados estão certos. Passa a dizer as duas coisas: que sessão está desenhada, e
   que a de hoje ainda não começou — usando o estado do mercado que a API já serve e que o
   cabeçalho já mostra, em vez de um segundo cálculo de horários no cliente. */
function legendaDaData(a) {
  if (S.intervalo !== "1D") return `Daily closes through ${dataDe(a.price_day)}`;
  const sessao = (a.intraday_day || "").slice(0, 10);
  const hoje = (S.visao?.as_of || "").slice(0, 10);
  const base = `Session ${dataDe(sessao)} · times in UTC`;
  if (!sessao || !hoje || sessao === hoje) return base;
  const estado = S.visao?.market?.label || "";
  return `${base} — today's session has not produced data yet`
    + (estado ? ` (${estado.toLowerCase()})` : "") + ".";
}

async function renderChart() {
  const id=++renderId, a=S.asset;
  if(!a || S.modo!=="hoje") return;
  try {
    await loadCharts();
    if(id!==renderId || a!==S.asset || S.modo!=="hoje") return;
    disposeCharts(); $("#graf").replaceChildren(); $("#grafZ").replaceChildren();
    $("#chartTitle").textContent=TITULO_GRAFICO[S.intervalo];
    $("#chartDate").textContent=legendaDaData(a);
    desenharGrafico(a); desenharZ(a); pintarLegendaGrafico(); pintarDias(a);
    if(!a.alertsLoaded) $("#chartNotice").textContent="Loading delivered alerts…";
    else $("#chartNotice").textContent=a.alertsRemaining ? `${a.alertsRemaining} older messages are available in History; their markers are outside this loaded record.` : "";
  } catch {if(id===renderId) retry($("#graf"),"The chart could not load.",()=>renderChart());}
}

function abrirModal(title,html) {
  ++S.modalRequest;
  $("#mTit").textContent=title; $("#mCorpo").innerHTML=html;
  if(!$("#modal").open) $("#modal").showModal();
}
$("#mFechar").onclick=()=>$("#modal").close();
$("#modal").addEventListener("close",()=>++S.modalRequest);
$("#modal").onclick=e=>{if(e.target===$("#modal"))$("#modal").close();};
function modalAlerta(a) {
  if(!a)return;
  abrirModal(`${a.ticker} · ${tipo(a.kind)}`,`<p class="eyebrow">${dataDe(a.date)} · ${horaDe(a.sent_at)}</p>
    <p>${soRotulo(esc(a.text.split("\n").filter(Boolean).slice(0,3).join(" · ")))}</p>
    <p class="summary-note">Values recorded when this message was sent. The company view shows the latest close.</p>
    <details class="evidence"><summary>Original message & evidence</summary><pre class="m-exato">${comLigacoes(esc(a.text))}</pre></details>
    ${a.event_at?`<p class="summary-note">Source published: ${esc(a.event_at)}</p>`:""}
    <div id="readerVotes"></div>
    ${S.visao?.rows.some(r=>r.ticker===a.ticker)?'<button class="quiet" id="openCompany">Open company analysis</button>':""}`);
  const request=S.modalRequest;
  if($("#openCompany"))$("#openCompany").onclick=()=>{$("#modal").close();trocarModo("hoje");void abrirEmpresa(a.ticker);};
  // Votos são evidência secundária, pedida só quando se abre uma mensagem.
  json("/api/feedback",{ttl:60000}).then(result=>{
    if(request!==S.modalRequest)return;
    S.votos=result.por_alerta || {}; const v=S.votos[a.key];
    $("#readerVotes").innerHTML=v?`<p class="summary-note">Reader feedback: ${v[0]} useful · ${v[1]} did not help. One vote per person per alert.</p>`:"";
  }).catch(()=>{if(request===S.modalRequest)$("#readerVotes").textContent="Reader feedback unavailable.";});
}
/* ── O piloto de feedback dos leitores, em agregado ──────────────────────────────────────
   ⚠️ ISTO ERA UMA QUANTIDADE MEDIDA, SERVIDA E INVISÍVEL — a classe de defeito que este
   projeto já encontrou na repartição do movimento, no veredicto em palavras e no coeficiente
   de ajuste. Os votos apareciam só dentro de cada mensagem («2 useful · 0 did not help») e o
   agregado vivia apenas no relatório de avaliação: quem abria a aplicação não tinha como
   saber que os alertas entregues foram classificados por quem os recebeu.

   O NÚMERO NUNCA APARECE SOZINHO, e é essa a parte que o torna defensável. Vem com o número
   de PESSOAS — sem ele, noventa e um votos leem-se como noventa e um leitores — e com a
   salvaguarda do votante dominante quando ela dispara. Mostrar 95% sem dizer que um leitor
   forneceu 58% dos votos é mostrar meia medição, e é a primeira coisa que um arguente pergunta.

   E não se chama a isto uma prova de utilidade, porque não é: são três pessoas, ninguém
   recebeu a variação de preço sem explicação, e utilidade percebida não é decisão melhor. A
   dissertação diz exatamente isto no Cap. 6, e a aplicação não pode afirmar mais do que ela. */
function textoVotos(r) {
  if (!r || !r.votos_efetivos) return null;
  const pessoas = r.pessoas === 1 ? "1 reader" : `${r.pessoas} readers`;
  const curto = r.reportavel
    ? `${r.uteis} of ${r.votos_efetivos} ratings called an alert useful`
    : `${r.uteis} of ${r.votos_efetivos} ratings called an alert useful (too few to state a rate)`;
  return {curto: `Readers rated ${r.alertas_votados} delivered alerts: ${curto} — from ${pessoas}.`,
          pessoas};
}

function pintarVotos(r) {
  const txt = textoVotos(r);
  const linha = $("#votosLinha"), caixa = $("#votosCx");
  if (!txt) { if (linha) linha.hidden = true; if (caixa) caixa.hidden = true; return; }
  if (linha) {
    linha.hidden = false;
    linha.innerHTML = `<button class="text-button" id="votosAbrir">${esc(txt.curto)}</button>`;
    $("#votosAbrir").onclick = () => abrirModal("What readers said", modalVotos(r));
  }
  if (caixa) {
    caixa.hidden = false;
    caixa.innerHTML = `<div class="titulo"><h2>What readers said</h2>
        <span class="nota">two buttons on every message</span></div>
      <div class="votos-num"><strong class="num">${r.reportavel
          ? Math.round(r.proporcao * 100) + "%" : r.uteis + "/" + r.votos_efetivos}</strong>
        <span>${esc(txt.curto)}</span></div>
      <details class="votos-det"><summary>How this number should be read</summary>
        <div class="f-corpo">${modalVotos(r)}</div></details>`;
  }
}

function modalVotos(r) {
  const ic = r.intervalo && r.intervalo[0] != null
    ? ` The 95% Wilson interval runs from ${Math.round(r.intervalo[0] * 100)}% to
        ${Math.round(r.intervalo[1] * 100)}%.` : "";
  return `<p>Every alert carries two buttons. ${r.votos_brutos} presses were recorded and count as
      <b>${r.votos_efetivos} ratings</b>, because only the latest press by the same person on the
      same alert counts. Along the way a rating was changed ${r.mudancas_de_voto} times and a
      button was pressed again without changing anything ${r.repeticoes_iguais} times.</p>
    <p><b>${r.uteis} of ${r.votos_efetivos}</b> ratings, spread over ${r.alertas_votados} alerts,
      called the alert useful.${r.reportavel ? ic
        : ` No rate is stated: the rules fixed before any vote existed require at least
            ${r.n_minimo} ratings before a proportion is reported.`}</p>
    ${r.dominante_excede ? `<p>⚠️ One reader supplied
      ${Math.round(r.dominante_fracao * 100)}% of the ratings. In a channel this small a single
      enthusiastic reader can decide the result on their own, so the evaluation report repeats the
      calculation without that person.</p>` : ""}
    <p>This is a pilot with <b>${esc(r.pessoas === 1 ? "one reader" : r.pessoas + " readers")}</b>,
      and it is not proof that the explanations work. Whoever wants to votes, which pushes the
      sample towards the extremes; nobody received the price move without an explanation, so
      nothing here credits the usefulness to the explanation itself; and a reader can find an
      alert agreeable and still make a worse decision. What these buttons measure is perceived
      usefulness, in a real setting, and no more than that.</p>`;
}


async function modalEmpresa(t) {
  abrirModal(`${t} · recorded news decisions`,'<p class="vazio">Reading the decision record…</p>');
  const request=S.modalRequest;
  try {
    const result=await json("/api/screener",{ttl:120000}); if(request!==S.modalRequest)return;
    const rows=(result.rows || []).filter(r=>r.ticker===t);
    $("#mCorpo").innerHTML=`<p class="summary-note">These are recorded decisions about news. A price move can generate a separate alert.</p>
      ${result.stale?'<p class="notice">The source is unavailable. Showing the last successful reading.</p>':""}
      <ul class="decision-list">${rows.map(r=>`<li><b>${esc(ROTULO.get(r.stage) || r.stage)}</b><time>${esc(r.date)}</time><p>${esc(legivel(r.detail) || PORQUE.get(r.stage) || "")}</p></li>`).join("")}</ul>
      ${!rows.length?'<p>No decision is recorded for this company in the available window.</p>':""}
      <p class="summary-note">Silence is a decision this system makes. The record does not imply that every gate was traversed.</p>`;
  } catch {if(request===S.modalRequest)retry($("#mCorpo"),"Decision record unavailable.",()=>modalEmpresa(t));}
}
async function loadNews(openModal) {
  const a=S.asset;if(!a)return;
  if(openModal)abrirModal(`${a.ticker} · historical news`,'<p class="vazio">Reading sources…</p>');
  const request=S.modalRequest;
  try {
    const result=await json(`/api/news/${encodeURIComponent(a.ticker)}`,{ttl:900000});
    if(a!==S.asset)return;
    a.news=result.rows || [];
    if(openModal && request===S.modalRequest) {
      let shown=20;
      const paint=()=>{
        $("#mCorpo").innerHTML=`<p class="summary-note">Historical headlines with observed outcomes. These cases do not establish the cause of the latest move.</p>${result.stale?'<p class="notice">Showing the last successful reading.</p>':""}
          ${a.news.slice(0,shown).map(n=>`<article class="news-item"><time>${esc(n.date)}</time><p>${esc(n.headline)}</p><p>${sourceLink(n.url,n.source || "Open source")}</p><p class="summary-note">Observed: +1 session ${pct(n.d1)} · +5 sessions ${pct(n.d5)}</p>${n.n>1?`<details><summary>${n.n-1} other headline${n.n>2?"s":""} that day</summary><ul>${(n.others || []).map(h=>`<li>${esc(h)}</li>`).join("")}</ul><p class="summary-note">Up to five additional titles shown; outcomes are shared by company and day.</p></details>`:""}</article>`).join("") || '<p>No historical news available.</p>'}
          ${a.news.length>shown?`<button class="quiet" id="moreNews">${a.news.length-shown} older days — load 20 more</button>`:""}`;
        if($("#moreNews"))$("#moreNews").onclick=()=>{const top=$("#mCorpo").scrollTop;shown+=20;paint();$("#mCorpo").scrollTop=top;};
      };
      paint();
    }
    if(S.camadas.noticias)await renderChart();
  } catch {
    if(openModal && request===S.modalRequest)retry($("#mCorpo"),"Historical sources are unavailable.",()=>loadNews(true));
    else if(a===S.asset){S.camadas.noticias=false;const input=$("[data-c=noticias]");if(input)input.checked=false;$("#chartNotice").textContent="Historical news unavailable. Try again from Chart options.";}
  }
}
function sourceLink(url,label) { return /^https?:\/\//i.test(url || "")?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer nofollow">${esc(label)}</a>`:"Source link unavailable"; }
function modalDia(a,day,z) {
  const alerts=(a.alerts || []).filter(x=>x.date===day), news=(a.news || []).find(x=>x.date===day);
  abrirModal(`${a.ticker} · ${day}`,`<h4>Observed rarity</h4><p>The move was ${esc(z)} standard deviations from the previous ${S.visao.window} closes. The threshold is ±${S.visao.threshold}.</p>
    ${news?`<h4>Historical source</h4><p>${esc(news.headline)}</p>${sourceLink(news.url,news.source || "Open source")}`:""}
    ${alerts.length?alerts.map(x=>`<details class="evidence"><summary>${tipo(x.kind)} · ${horaDe(x.sent_at)}</summary><pre class="m-exato">${comLigacoes(esc(x.text))}</pre></details>`).join(""):"<p>No delivered alert for this day in the loaded record. The reason cannot be inferred from this chart.</p>"}`);
}

async function carregarFeed(more=false) {
  const request=++S.feedRequest, chosen=S.feedTicker;
  const params=new URLSearchParams({limit:String(S.feedLimite)});
  if(chosen)params.set("ticker",chosen);
  if(more && S.next)params.set("before",S.next);
  const old=S.alertas;
  if(!more){S.alertas=[];S.diaHist=null;$("#feed").innerHTML='<p class="vazio" role="status">Loading messages…</p>';}
  try {
    const result=await json("/api/alerts"+"?"+params,{force:more});
    if(request!==S.feedRequest)return;
    S.alertas=more?[...(result.rows || []),...old]:(result.rows || []);
    S.next=result.next_before;S.remaining=result.remaining || 0;S.total=result.total || 0;
    $("#rodape").textContent=`${S.total} messages ${chosen?"for "+chosen:"on record"}`;
    $("#feedNota").textContent=result.stale?"Source unavailable. Showing the last successful reading.":"The exact text that reached the phone is available inside each event.";
    pintarFiltroTipos();pintarFeed();if(S.modo==="hist")pintarHistorico();
  } catch {if(request===S.feedRequest){if(more){S.alertas=old;pintarFeed();$("#feedNota").textContent="Older messages could not load. Try the load button again.";}else retry($("#feed"),"Messages unavailable. Company data is still available.",()=>carregarFeed());}}
}

/* ── O intervalo do gráfico governa também a lista ────────────────────────────
   Antes o intervalo governava só o gráfico: com "1M" escolhido o gráfico mostrava um mês e a
   lista por baixo mostrava meio ano, na mesma página. É o invariante que a v3 tinha e a v5
   perdeu. Não se aplica no modo history, onde a navegação é por dia. */
const DIAS_INTERVALO = {"1D":1, "1M":31, "3M":93, "6M":186, "1Y":366};
function dentroDoIntervalo(a) {
  // ⚠️ NO MODO HISTÓRICO O INTERVALO PASSA A SER O DELE. Antes esta função devolvia sempre
  // `true` fora do modo «hoje», porque o histórico não tinha intervalo nenhum; agora tem, e
  // se a lista o ignorasse voltaria o defeito que esta função existe para corrigir — o gráfico
  // a mostrar três meses e a lista por baixo a mostrar tudo, na mesma página.
  if (S.modo !== "hoje") return dentroDoHist(a.date);
  const dias = DIAS_INTERVALO[S.intervalo];
  if (!dias || !a.date) return true;
  const corte = new Date(Date.now() - dias * 864e5).toISOString().slice(0, 10);
  return a.date >= corte;
}

/* Salta para o alerta mais próximo de uma data e dá-lhe foco.
   ⚠️ Com tolerância, e não por igualdade: ninguém acerta no pixel de um marcador, e um clique
   que só funcionasse em cima da data exacta pareceria partido quase sempre. */
/* ── Um clique no gráfico e TODAS as mensagens daquele dia ───────────────────────────────
   ⚠️ DOIS DEFEITOS DO AUTOR, e o primeiro era real: «quando há várias bolas na mesma coluna, o
   clique só vai para uma delas». Esta função escolhia a mensagem MAIS PRÓXIMA da data clicada,
   logo num dia com três alertas duas eram inalcançáveis pelo gráfico — e nada no ecrã dizia que
   existiam.

   A correção não é distinguir as bolas: num intervalo diário elas partilham a MESMA posição no
   eixo, porque a coluna é um dia. O que o clique pode fazer é honrar o que a coluna significa —
   revelar as mensagens desse dia, todas, e dizer quantas são.

   ⚠️ E O SEGUNDO: «se clicarmos num alerta do gráfico que estivesse no show more, a lista
   deveria ir para essa linha». Ia falhar em silêncio — a data existia no gráfico e não na lista
   carregada, e a função devolvia `false` sem nada acontecer, que se lê como um clique morto.
   Passa a carregar mais páginas até alcançar o dia, com um tecto para não varrer o histórico
   inteiro por causa de um clique. */
const PAGINAS_MAX = 6;

async function focarAlertaEm(data, toleranciaDias = 3) {
  if (!data) return false;
  for (let volta = 0; volta <= PAGINAS_MAX; volta++) {
    const itens = [...document.querySelectorAll("#feed .f-item")];
    const exactas = itens.filter(el => el.dataset.date === data);
    if (exactas.length) return realcar(exactas, data);

    // Nada exacto nesta página. Se o dia é ANTERIOR ao mais antigo carregado e há mais para
    // carregar, a mensagem está atrás do «show more» — é o caso do autor.
    const datas = itens.map(el => el.dataset.date).filter(Boolean).sort();
    const maisAntiga = datas[0];
    if (S.remaining && (!maisAntiga || data < maisAntiga) && volta < PAGINAS_MAX) {
      const nota = $("#chartNotice");
      if (nota) nota.textContent = "Loading the messages from that day…";
      await carregarFeed(true);
      continue;
    }
    // Sem mais páginas: cai na aproximação de antes, que cobre o alerta sem barra onde pousar.
    let melhor = null, menor = Infinity;
    for (const el of itens) {
      const d = el.dataset.date;
      if (!d) continue;
      const dist = Math.abs((new Date(d) - new Date(data)) / 864e5);
      if (dist < menor) { menor = dist; melhor = el; }
    }
    if (!melhor || menor > toleranciaDias) return false;
    return realcar([melhor], data, menor);
  }
  return false;
}

function realcar(alvos, data, distancia = 0) {
  alvos[0].scrollIntoView({behavior:"smooth", block:"center"});
  alvos[0].focus({preventScroll:true});
  for (const el of alvos) {
    el.classList.add("f-alvo");
    setTimeout(() => el.classList.remove("f-alvo"), 2600);
  }
  const nota = $("#chartNotice");
  if (nota) {
    nota.textContent = alvos.length > 1
      ? `${alvos.length} messages went out on ${dataDe(data)} — all of them are highlighted below.`
      : distancia
        ? `No message is recorded on ${dataDe(data)}; the nearest one is highlighted below.`
        : `Highlighted the message from ${dataDe(data)} below.`;
  }
  return true;
}

/* ── Filtro por tipo de mensagem ──────────────────────────────────────────────
   Os quatro tipos já existiam no modelo e a lista mostrava-os todos sem os poder separar. A nota
   de abertura e o resumo de fecho saem todos os dias úteis, portanto são justamente as que enchem
   a lista de quem procura outra coisa. Os rótulos usam as palavras do leitor, não as do modelo. */
const TIPOS = [["", "All"], ["news", "News"], ["market", "Price move"],
               ["open", "Market open"], ["summary", "Market close"]];
function pintarFiltroTipos() {
  const alvo = $("#feedKinds");
  if (!alvo) return;
  // ⚠️ As contagens obedecem ao MESMO filtro de intervalo que a lista. Contá-las sobre todas as
  // mensagens carregadas dava um número que não correspondia ao que o clique mostrava — a marca
  // dizia «News 8» e a lista mostrava duas —, e um número que mente é pior do que nenhum.
  const visiveis = S.alertas.filter(dentroDoIntervalo);
  const contagem = new Map();
  for (const a of visiveis) contagem.set(a.kind, (contagem.get(a.kind) || 0) + 1);
  alvo.innerHTML = TIPOS.map(([v, r]) => {
    const n = v ? (contagem.get(v) || 0) : visiveis.length;
    return `<button class="kind" data-k="${v}" aria-pressed="${S.feedKind === v}"`
         + `${!n && v ? " disabled" : ""}>${r}<span class="kind-n">${n}</span></button>`;
  }).join("");
  alvo.querySelectorAll("button").forEach(b => b.onclick = () => {
    S.feedKind = b.dataset.k; pintarFiltroTipos(); pintarFeed();
  });
}

function pintarFeed() {
  let rows=S.alertas.slice().reverse();
  if(S.modo==="hist" && S.diaHist)rows=rows.filter(a=>a.date===S.diaHist);
  const antesDoIntervalo=rows.length;
  rows=rows.filter(dentroDoIntervalo);
  const escondidos=antesDoIntervalo-rows.length;
  if(S.feedKind)rows=rows.filter(a=>a.kind===S.feedKind);
  $("#feed").innerHTML=rows.map((a,i)=>`<button class="f-item" data-i="${i}" data-date="${esc(a.date)}"><span class="f-cab"><b>${esc(a.ticker)}</b><span class="event-kind">${tipo(a.kind)}</span><time>${esc(a.date)} · ${horaDe(a.sent_at)}</time></span><p>${soRotulo(esc(a.text.split("\n").filter(Boolean).slice(0,3).join(" · ")))}</p><span class="read-event">Read explanation & evidence →</span></button>`).join("") || `<p class="vazio">${escondidos
      ? `No messages inside the ${S.intervalo} window. `
        + `${escondidos} older ${escondidos === 1 ? "message is" : "messages are"} hidden by it.`
      : "No messages in this selection."}</p>`;
  $("#feed").querySelectorAll(".f-item").forEach(b=>b.onclick=()=>modalAlerta(rows[+b.dataset.i]));
  if(escondidos && rows.length) {
    $("#feed").insertAdjacentHTML("beforeend",
      `<p class="f-corte">${escondidos} older ${escondidos === 1 ? "message" : "messages"} outside the ${S.intervalo} window ${escondidos === 1 ? "is" : "are"} not shown.</p>`);
  }
  if(S.remaining) {
    $("#feed").insertAdjacentHTML("beforeend",`<button class="f-mais" id="fMais">${S.remaining} older messages not shown — load ${Math.min(S.feedLimite,S.remaining)} more</button>`);
    $("#fMais").onclick=async()=>{const b=$("#fMais");b.disabled=true;b.textContent="Loading older messages…";await carregarFeed(true);};
  }
}
/* ── O intervalo do histórico ────────────────────────────────────────────────────────────
   ⚠️ O AUTOR PEDIU «filtro de datas melhor, como temos no chart», e a razão é concreta: o
   modo «hoje» tem cinco botões de intervalo que governam a página inteira, e o modo histórico
   não tinha nenhum — mostrava tudo o que estivesse carregado e a única maneira de estreitar
   era clicar num dia. Dois modos da mesma página com controlos de tempo diferentes obrigam o
   leitor a aprender duas interfaces.
   Os intervalos são os mesmos do gráfico, para não haver um segundo vocabulário de tempo. */
const HIST_INTERVALOS = [["1M", 31], ["3M", 93], ["6M", 186], ["1Y", 366], ["All", null]];

function dentroDoHist(iso) {
  const dias = (HIST_INTERVALOS.find(([r]) => r === S.histIntervalo) || [])[1];
  if (!dias || !iso) return true;
  const d = new Date(iso);
  return isFinite(d) && (Date.now() - d) / 864e5 <= dias;
}

function pintarHistorico() {
  const counts=new Map();
  for(const a of S.alertas) if(dentroDoHist(a.date)) counts.set(a.date,(counts.get(a.date)||0)+1);
  const days=[...counts.entries()].sort(), max=Math.max(1,...counts.values());
  const cx=$("#histIntervalos");
  if(cx) cx.innerHTML=HIST_INTERVALOS.map(([r])=>
    `<button data-hr="${r}" aria-pressed="${r===S.histIntervalo}">${r}</button>`).join("");
  const mostradas=S.alertas.filter(a=>dentroDoHist(a.date)).length;
  $("#histNota").textContent=`${mostradas} of ${S.alertas.length} loaded messages in this range`
    + ` (${S.total} in the record)${days.length?` · ${dataDe(days[0][0])} to ${dataDe(days.at(-1)[0])}`:""}.`
    + " Load older messages to extend the record.";
  // ⚠️ As marcas do eixo dos y são inteiras: contam-se mensagens, e «2,5 mensagens» seria
  // falso sobre a própria grandeza. Escolhe-se um passo que dê 3 a 5 marcas.
  const passo=Math.max(1,Math.ceil(max/4));
  const marcas=[];for(let v=0;v<=max;v+=passo)marcas.push(v);
  if(marcas.at(-1)!==max)marcas.push(max);
  const topo=marcas.at(-1);
  $("#histEixoY").innerHTML=marcas.slice().reverse().map(v=>
    `<span style="bottom:${v/topo*96}px">${v}</span>`).join("");
  $("#histBarras").innerHTML=days.map(([d,n])=>`<button class="hist-d" data-d="${d}" aria-label="${d}: ${n} messages" aria-pressed="${S.diaHist===d}"><i style="height:${Math.max(3,n/topo*96)}px;background:var(--acento)"></i><span class="n">${n}</span></button>`).join("");
  // ⚠️ O EIXO DOS X NOMEAVA SÓ O PRIMEIRO E O ÚLTIMO DIA, e o autor apontou-o: com sessenta
  // barras entre dois rótulos, nenhuma barra tem data — o leitor vê uma forma e não sabe
  // quando. Passa a nomear até cinco dias, POSICIONADOS pela fração do índice da barra, para
  // o rótulo cair debaixo da barra que nomeia em vez de ficar distribuído a espaço igual.
  // Com sete ou menos dias nomeiam-se todos, porque aí cabem e a leitura fica exacta.
  const eixoX=$("#histEixoX");
  if(eixoX){
    const n=days.length;
    if(n===0){ eixoX.innerHTML=""; }
    else if(n<=7){
      eixoX.innerHTML=days.map(([d])=>`<span>${dataDe(d)}</span>`).join("");
    }else{
      const quantos=Math.min(5,n);
      const idx=[...new Set(Array.from({length:quantos},(_,i)=>
        Math.round(i*(n-1)/(quantos-1))))];
      eixoX.innerHTML=idx.map(i=>{
        const frac=n>1 ? i/(n-1) : 0;
        // O alinhamento acompanha a posição: o primeiro encosta à esquerda, o último à
        // direita, e os do meio centram-se — senão os das pontas saem fora do eixo.
        const t=frac<=0 ? "translateX(0)" : frac>=1 ? "translateX(-100%)" : "translateX(-50%)";
        return `<span style="left:${(frac*100).toFixed(2)}%;transform:${t}">`
             + `${dataDe(days[i][0])}</span>`;
      }).join("");
    }
    eixoX.classList.toggle("esparso", n>7);
  }
  $("#histFiltro").textContent=S.diaHist?`Showing ${dataDe(S.diaHist)}. Select the same day to clear.`:"Counts cover the loaded messages, including session summaries and market-open notes.";
  $("#histBarras").querySelectorAll("button").forEach(b=>b.onclick=()=>{S.diaHist=S.diaHist===b.dataset.d?null:b.dataset.d;pintarHistorico();pintarFeed();});
  if(cx) cx.onclick=e=>{
    const b=e.target.closest("[data-hr]"); if(!b) return;
    S.histIntervalo=b.dataset.hr;
    S.diaHist=null;          // um dia escolhido fora do novo intervalo seria um filtro invisível
    pintarHistorico(); pintarFeed();
  };
}
function trocarModo(mode) {
  S.modo=mode;const today=mode==="hoje";
  $("#mHoje").setAttribute("aria-pressed",String(today));$("#mHist").setAttribute("aria-pressed",String(!today));
  $("#secHoje").hidden=!today;$("#secHist").hidden=today;$("#colEsq").hidden=!today;$("#detalhe").hidden=!today;
  $("#workspace").classList.toggle("history-mode",!today);$("#feedTitle").textContent=today?"Recent events":"Delivered messages";
  S.diaHist=null;
  if(today){void renderChart();}else{disposeCharts();pintarHistorico();}
  pintarFeed();
}
$("#mHoje").onclick=()=>trocarModo("hoje");$("#mHist").onclick=()=>trocarModo("hist");
$("#todasEmpresas").onclick=()=>{
  // ⚠️ ANTES ALTERNAVA SÓ O ÂMBITO DA LISTA e deixava a empresa em análise no gráfico, com o
  // botão dela marcado: o controlo dizia «todas» e a metade de cima da página dizia «esta».
  // Agora governa a página inteira — só um âmbito activo de cada vez.
  const paraTodas = !!S.feedTicker || !S.asset;
  S.feedTicker = paraTodas ? "" : (S.ticker || S.anterior || "");
  if (paraTodas) { S.anterior = S.ticker; mostrarMercado(); }
  else if (S.feedTicker) void abrirEmpresa(S.feedTicker);
  sincronizarEscopo(S.feedTicker);
  void carregarFeed();
};
$("#about").onclick=()=>abrirModal("About the evidence",`<p>This research application monitors US stocks and connects observed moves with recorded evidence.</p><ul><li>Rarity compares a daily move with the company's past.</li><li>The split estimates market, sector and company contributions; R² describes the historical fit.</li><li>News and similar past cases provide context, not proof of causation.</li><li>Messages preserve what was sent, including historical model estimates. These are not a confidence score for today's explanation.</li></ul><p>Sources and timestamps remain attached to the evidence. No price forecasts or investment recommendations are produced by this interface.</p>`);

let refreshing=false,pollTimer,polling=false,lastFeedCheck=0;
async function refresh(force=false) {
  if(refreshing)return;
  refreshing=true;$("#refresh").disabled=true;
  try {
    const v=await json("/api/overview",{force});
    const changed=S.asOf!==v.as_of;
    S.visao=v;S.asOf=v.as_of;pintarOverview();
    notice(!v.rows?.length?"Price data is unavailable. Retrying automatically.":!v.fresh?"The latest snapshot is delayed. Check the session dates before interpreting the values.":"");
    if(!S.ticker){const wanted=new URL(location.href).searchParams.get("t");S.ticker=v.rows.some(r=>r.ticker===wanted)?wanted:orderedRows()[0]?.ticker;}
    if(S.ticker && (!S.asset || force))void abrirEmpresa(S.ticker,{focus:false,force});
    else if(changed)notice("A newer snapshot is available. Refresh to update the open analysis.");
  } catch {notice("Connection interrupted. Keeping any previously loaded data; retrying automatically.");$("#estado").textContent="Connection interrupted";$("#pulso").className="pulso frio";}
  finally{refreshing=false;$("#refresh").disabled=false;}
}
async function checkMessages() {
  // Contagem independente do instantâneo; nunca interrompe a leitura do histórico.
  const chosen=S.feedTicker, request=S.feedRequest;
  const params=new URLSearchParams({limit:"1"});if(chosen)params.set("ticker",chosen);
  const result=await json("/api/alerts"+"?"+params,{force:true});
  lastFeedCheck=Date.now();
  if(chosen!==S.feedTicker || request!==S.feedRequest)return;
  if(result.total!==S.total) {
    $("#feedNota").innerHTML='New messages are available. <button class="text-button" id="newMessages">Show latest messages</button>';
    $("#newMessages").onclick=()=>carregarFeed();
    if(S.asset)void companyAlerts(S.escolha,S.ticker);
  }
}
async function poll() {
  clearTimeout(pollTimer);
  if(polling)return;polling=true;
  if(!document.hidden) {
    try {
      const h=await json("/api/health",{force:true});
      if(!S.visao || !S.asset || h.as_of!==S.asOf)await refresh(); else updateStatus(h);
      if(Date.now()-lastFeedCheck>60000)await checkMessages();
    } catch {notice("Connection interrupted. Retrying automatically.");$("#estado").textContent="Connection interrupted";$("#pulso").className="pulso frio";}
  }
  polling=false;
  if(!document.hidden)pollTimer=setTimeout(poll,30000);
}
$("#refresh").onclick=()=>{void refresh(true);void carregarFeed();};
document.addEventListener("visibilitychange",()=>{clearTimeout(pollTimer);if(!document.hidden)void poll();});
window.addEventListener("online",()=>{void refresh(true);void carregarFeed();});
window.addEventListener("pagehide",()=>{clearTimeout(pollTimer);disposeCharts();});
window.addEventListener("pageshow",e=>{if(e.persisted){void renderChart();void poll();}});
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>{if(S.asset)void renderChart();});
// O agregado dos votos é evidência da própria operação e não muda de minuto a minuto:
// pedido uma vez no arranque, com a mesma cache de 60 s que o detalhe já usava, e falha em
// silêncio — a página inteira funciona sem ele e os blocos ficam escondidos.
void json("/api/feedback",{ttl:60000}).then(r=>pintarVotos(r && r.resumo)).catch(()=>{});
void refresh();void carregarFeed();pollTimer=setTimeout(poll,30000);
