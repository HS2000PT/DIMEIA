"use strict";
const MESES = { "1M":21, "3M":63, "6M":126, "1Y":252 };

function paleta() {
  const escuro = matchMedia("(prefers-color-scheme: dark)").matches;
  return {
    escuro,
    linha:   escuro ? "#2fd07f" : "#0a7f4f",
    sobe:    escuro ? "#5eead4" : "#0f766e",
    desce:   escuro ? "#f87171" : "#b3261e",
    alerta:  escuro ? "#f0a72e" : "#b45309",
    noticia: escuro ? "#8d96a3" : "#8a929c",
    grelha:  escuro ? "#1b1f26" : "#eeeeea",
    texto:   escuro ? "#8d96a3" : "#5b6472",
  };
}

function criarGrafico(alvo, altura, eixoOculto) {
  const P = paleta();
  return LightweightCharts.createChart(alvo, {
    localization: { locale: "en-GB" },
    width: alvo.clientWidth, height: altura || alvo.clientHeight,
    layout: { background:{ color:"transparent" }, textColor:P.texto,
              fontFamily:"IBM Plex Mono, monospace", fontSize:11 },
    grid: { vertLines:{ visible:false }, horzLines:{ color:P.grelha } },
    // ⚠️ `minimumWidth` fixo nas duas telas. Sem isto a escala do preço (três dígitos e duas
    // casas) e a do z (um dígito) têm larguras diferentes, as áreas de desenho ficam desalinhadas
    // por umas dezenas de pixeis, e «olhar para baixo para ver porque é que o dia foi
    // assinalado» — que é a razão de existir da faixa — deixa de funcionar.
    rightPriceScale: { borderVisible:false, minimumWidth:64 },
    timeScale: { borderVisible:false, fixLeftEdge:true, fixRightEdge:true,
                 timeVisible: S.intervalo === "1D", secondsVisible:false,
                 // Um só eixo do tempo para o par. Quando a faixa do z está no ar, é ela que o
                 // mostra, por estar por baixo; o de cima seria uma segunda régua a dizer o mesmo.
                 visible: !(eixoOculto && alvo.id === "graf") },
    crosshair: { mode:0 }, handleScale:false, handleScroll:false,
  });
}

function marcasDeAlertas(a, desdeTs, ate) {
  const P = paleta();
  return (a.alerts || []).map(al => {
    const iso = al.sent_at || (al.date ? `${al.date}T12:00:00Z` : "");
    if (!iso) return null;
    const ts = Math.floor(Date.parse(iso) / 1000);
    if (!Number.isFinite(ts) || ts < desdeTs || (ate && ts > ate)) return null;
    // ⚠️ Sem `text`. Onze alertas em seis meses agrupam-se nas mesmas semanas e as etiquetas
    // sobrepõem-se umas às outras — medido, não suposto, e é a mesma lição que as etiquetas do
    // z já tinham dado. A forma está na legenda e as datas estão nas fichas por baixo.
    return { tempo: S.intervalo === "1D" ? ts : (al.date || iso.slice(0, 10)),
             position:"aboveBar", color:P.alerta, shape:"circle", text:"" };
  }).filter(Boolean);
}

function mostraZ(a) {
  if (S.intervalo === "1D" || !S.camadas.zscore) return false;
  const desde = (a.closes || []).slice(-MESES[S.intervalo])[0]?.[0] || "";
  return (a.events || []).some(e => e[0] >= desde);
}

function desenharGrafico(a) {
  const alvo = $("#graf");
  if (!alvo || typeof LightweightCharts === "undefined") return;
  const P = paleta();
  S.desenhado = {};
  const umDia = S.intervalo === "1D";

  // ── os pontos da linha ────────────────────────────────────────────────────
  let pontos, desdeTs = 0, ateTs = 0;
  if (umDia) {
    const barras = a.intraday || [];
    if (barras.length < 2) {
      alvo.innerHTML = `<p class="vazio">No intraday series for ${esc(a.intraday_day || "today")}
        — the market may not have opened yet. Pick a longer range.</p>`;
      return;
    }
    pontos = barras.map(([t, v]) => ({ time:t, value:v }));
    desdeTs = barras[0][0]; ateTs = barras[barras.length - 1][0];
  } else {
    const fechos = (a.closes || []).slice(-MESES[S.intervalo]);
    if (fechos.length < 2) { alvo.innerHTML = '<p class="vazio">No price series.</p>'; return; }
    pontos = fechos.map(([t, v]) => ({ time:t, value:v }));
    desdeTs = Math.floor(Date.parse(fechos[0][0] + "T00:00:00Z") / 1000);
  }

  const c = criarGrafico(alvo, 0, mostraZ(a));
  // ⚠️ v5 do lightweight-charts: `addLineSeries` deixou de existir. A série cria-se com
  // `addSeries(LightweightCharts.LineSeries, ...)` e os marcadores com `createSeriesMarkers`,
  // que é uma função do módulo e não um método da série.
  const s = c.addSeries(LightweightCharts.LineSeries, {
    color:P.linha, lineWidth:2, priceLineVisible:false, lastValueVisible:false });
  s.setData(pontos);

  // ── a referência: o fecho de ontem ────────────────────────────────────────
  // Sem ela, uma linha intradiária não diz se o dia é de subida ou de descida — diz só a forma.
  if (S.camadas.referencia && umDia && a.prev_close != null) {
    s.createPriceLine({ price:a.prev_close, color:P.texto, lineWidth:1,
                        lineStyle:2, axisLabelVisible:true, title:"prev close" });
  }

  // ── as marcas ─────────────────────────────────────────────────────────────
  const marcas = [];
  if (S.camadas.assinalados && !umDia) {
    for (const [t, z, dir] of (a.events || [])) {
      if (t < pontos[0].time) continue;
      // Um dia assinalado que gerou alerta não se marca duas vezes: a marca do alerta manda,
      // porque a distinção que interessa é entre o que saiu e o que ficou por sair.
      if (S.camadas.alertas && (a.alerts || []).some(al => al.date === t)) continue;
      marcas.push({ tempo:t, position: dir > 0 ? "aboveBar" : "belowBar",
                    color: dir > 0 ? P.sobe : P.desce,
                    shape: dir > 0 ? "arrowUp" : "arrowDown", text:"" });
    }
  }
  if (S.camadas.noticias && !umDia) {
    const comAlerta = new Set((a.alerts || []).map(al => al.date));
    for (const n of (a.news || [])) {
      if (!n.date || n.date < pontos[0].time || comAlerta.has(n.date)) continue;
      marcas.push({ tempo:n.date, position:"belowBar", color:P.noticia,
                    shape:"square", text:"" });
    }
  }
  let fora = 0;
  if (S.camadas.alertas) {
    const dentro = marcasDeAlertas(a, desdeTs, ateTs);
    marcas.push(...dentro);
    // ⚠️ Um alerta pode ter saído fora da janela desenhada — tipicamente de madrugada, horas
    // antes da abertura. Não se arrasta o marcador para a borda, porque isso mentiria sobre a
    // hora; conta-se, e diz-se por baixo. É o mesmo facto que a secção da latência mede.
    if (umDia) {
      const hoje = (a.intraday_day || "").slice(0, 10);
      fora = (a.alerts || []).filter(al => (al.date || "") === hoje).length - dentro.length;
    }
  }
  S.desenhado = {
    alertas: marcas.filter(m => m.shape === "circle").length,
    assinalados: marcas.filter(m => m.shape !== "circle" && m.shape !== "square").length,
    noticias: marcas.filter(m => m.shape === "square").length,
    referencia: !!(S.camadas.referencia && umDia && a.prev_close != null),
    fora: Math.max(0, fora),
  };

  if (marcas.length) {
    LightweightCharts.createSeriesMarkers(s, marcas
      .sort((x, y) => (x.tempo > y.tempo ? 1 : -1))
      .map(m => ({ time:m.tempo, position:m.position, color:m.color,
                   shape:m.shape, text:m.text || "" })));
  }
  c.timeScale().fitContent();
  // ⚠️ O gráfico não se redimensiona sozinho. Sem isto, mudar a janela deixa-o cortado — e num
  // painel que se mostra ao vivo é o primeiro defeito que alguém vê.
  if (S.obs) S.obs.disconnect();
  S.obs = new ResizeObserver(() => c.applyOptions({ width: alvo.clientWidth }));
  S.obs.observe(alvo);
  // ── clicar no gráfico salta para o alerta ────────────────────────────────
  // O clique devolve a coordenada de tempo sob o cursor e não um marcador, por isso procura-se
  // o alerta mais próximo dessa data. Sem tolerância, isto pareceria partido quase sempre.
  c.subscribeClick(param => {
    if (!param || !param.time) return;
    const t = param.time;
    const data = typeof t === "string" ? t
      : (t && t.year ? `${t.year}-${String(t.month).padStart(2, "0")}-`
                       + `${String(t.day).padStart(2, "0")}`
                     : new Date(t * 1000).toISOString().slice(0, 10));
    const aviso = document.querySelector("#chartNotice");
    if (typeof focarAlertaEm === "function" && focarAlertaEm(data)) {
      if (aviso) aviso.textContent = "";
    } else if (aviso) {
      aviso.textContent = `No message within three days of ${data}.`;
    }
  });
  S.grafico = c;
}

function desenharZ(a) {
  const alvo = $("#grafZ");
  if (!alvo) return;
  if (S.intervalo === "1D" || !S.camadas.zscore) { alvo.hidden = true; alvo.innerHTML = ""; return; }
  alvo.hidden = false; alvo.innerHTML = "";
  if (typeof LightweightCharts === "undefined") return;

  const P = paleta();
  const fechos = (a.closes || []).slice(-MESES[S.intervalo]);
  const desde = fechos[0]?.[0] || "";
  const ev = (a.events || []).filter(e => e[0] >= desde);
  if (!ev.length) {
    alvo.innerHTML = '<p class="vazio" style="padding:10px 14px">No flagged day in this range.</p>';
    return;
  }
  const altZ = parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue('--z-alt'), 10) || 138;
  const c = criarGrafico(alvo, altZ, false);
  const lim = S.visao?.threshold ?? 1.5;
  // Uma série invisível que cobre o intervalo todo, para o eixo do tempo bater certo com o de
  // cima mesmo quando os dias assinalados são poucos e esparsos.
  const base = c.addSeries(LightweightCharts.LineSeries, {
    color:"rgba(0,0,0,0)", lineWidth:1, priceLineVisible:false, lastValueVisible:false });
  base.setData(fechos.map(([t]) => ({ time:t, value:0 })));
  // Sem `title`: o rótulo do eixo já diz o valor, e o título repeti-lo-ia ao lado.
  base.createPriceLine({ price: lim, color:P.sobe, lineWidth:1, lineStyle:2,
                         axisLabelVisible:true, title:"" });
  base.createPriceLine({ price:-lim, color:P.desce, lineWidth:1, lineStyle:2,
                         axisLabelVisible:true, title:"" });
  const sobe = c.addSeries(LightweightCharts.HistogramSeries, { color:P.sobe, priceLineVisible:false });
  const desce = c.addSeries(LightweightCharts.HistogramSeries, { color:P.desce, priceLineVisible:false });
  sobe.setData(ev.filter(e => e[1] >= 0).map(([t, z]) => ({ time:t, value:z })));
  desce.setData(ev.filter(e => e[1] < 0).map(([t, z]) => ({ time:t, value:z })));
  // ⚠️ O INTERVALO É FIXADO À MÃO, e a razão vê-se com um z grande. Deixada em automático,
  // a escala encosta a marca mais extrema à moldura e o rótulo do eixo sai CORTADO A MEIO —
  // «10.00» e «−3.02» impressos meios, numa faixa que existe justamente para se ler o valor.
  // Uma margem não chega: o gerador de marcas adapta-se à margem e volta a pôr uma no bordo.
  // Simétrico à volta de zero, porque a faixa mede distância à norma nos dois sentidos, e com
  // meia amplitude de folga para o rótulo mais alto ficar sempre dentro.
  const zMax = Math.max(1.5, ...ev.map(e => Math.abs(e[1]))) * 1.5;
  base.applyOptions({ autoscaleInfoProvider: () => ({
    priceRange: { minValue: -zMax, maxValue: zMax } }) });
  c.timeScale().fitContent();
  if (S.obsZ) S.obsZ.disconnect();
  S.obsZ = new ResizeObserver(() => c.applyOptions({ width: alvo.clientWidth }));
  S.obsZ.observe(alvo);
  S.graficoZ = c;
}

function pintarLegendaGrafico() {
  const el = $("#legGraf"); if (!el) return;
  const d = S.desenhado || {};
  const umDia = S.intervalo === "1D";
  const L = [];
  if (d.alertas)
    L.push(`<i><span class="p" style="background:var(--parou)"></span> an alert went out</i>`);
  if (d.assinalados) {
    L.push(`<i><span class="seta sobe"></span> flagged, closed up</i>`);
    L.push(`<i><span class="seta desce"></span> flagged, closed down</i>`);
    // ⚠️ Esta frase não é redundante com as duas de cima. Elas dizem o que a cor É; esta diz o
    // que a cor NÃO é. Verde num painel financeiro lê-se como «bom», e este sistema não emite
    // juízos sobre se um movimento é bom — nem sequer sobre se vai continuar.
    L.push(`<i>the colour is the direction of that day's move, and nothing more</i>`);
  }
  if (d.noticias)
    L.push(`<i><span class="quad"></span> historical headline, no alert in the loaded record</i>`);
  if (d.referencia)
    L.push(`<i><span class="tracejado"></span> previous session's close</i>`);
  if (S.camadas.zscore && !umDia && $("#grafZ") && !$("#grafZ").hidden)
    L.push(`<i>z = distance from this company's own ${S.visao?.window ?? 20}-day norm, in standard deviations</i>`);
  if (d.fora)
    L.push(`<i><b>${d.fora} alert${d.fora > 1 ? "s" : ""} today went out outside the plotted session</b>, so ${d.fora > 1 ? "they are" : "it is"} not on this chart — the times are below</i>`);
  el.innerHTML = L.join("");
  el.hidden = !L.length;
}

function pintarDias(a) {
  if (S.intervalo === "1D") {
    // No 1D as fichas passam a ser os alertas de hoje, com a hora a que saíram: é a única lista
    // do dia que existe, e é a que dá sentido às marcas do gráfico.
    const hoje = (a.intraday_day || "").slice(0, 10);
    const alertasHoje = (a.alerts || []).filter(al => (al.date || "") === hoje);
    $("#dias").innerHTML = alertasHoje.length ? alertasHoje.map((al, i) =>
      `<button class="dia-b" data-a="${i}">
        <span class="p" style="background:var(--parou)"></span>
        ${esc(horaDe(al.sent_at))} <span style="color:var(--fraco)">${esc(al.kind || "")}</span>
      </button>`).join("")
      : `<span class="vazio" style="padding:0">No alert for this company today.</span>`;
    $("#dias").querySelectorAll(".dia-b").forEach(b =>
      b.addEventListener("click", () => modalAlerta(alertasHoje[+b.dataset.a])));
    return;
  }
  const desde = (a.closes || []).slice(-MESES[S.intervalo])[0]?.[0] || "";
  const ev = (a.events || []).filter(e => e[0] >= desde).slice().reverse();
  $("#dias").innerHTML = ev.length ? ev.map(([t, z, dir]) =>
    `<button class="dia-b" data-d="${esc(t)}" data-z="${z}">
      <span class="p" style="background:var(--${dir > 0 ? "sobe" : "desce"})"></span>
      ${esc(t)} <span style="color:var(--fraco)">z ${z}</span></button>`).join("")
    : `<span class="vazio" style="padding:0">No flagged day in this range.</span>`;
  $("#dias").querySelectorAll(".dia-b").forEach(b =>
    b.addEventListener("click", () => modalDia(a, b.dataset.d, b.dataset.z)));
}
