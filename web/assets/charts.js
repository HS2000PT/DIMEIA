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
    // ── Uma cor por TIPO de alerta ────────────────────────────────────────────────────────
    // ⚠️ O autor pediu «distintos icons para os tipos de alertas, em vez de só bolas
    // amarelas», e as FORMAS não dão: a biblioteca tem quatro (círculo, quadrado, seta para
    // cima, seta para baixo) e três já carregam sentido neste gráfico — o quadrado é notícia
    // captada, as setas são dias assinalados com a sua direção. Sobrava o círculo.
    // Logo a distinção é por cor e por uma letra, com a legenda a nomear as quatro. As cores
    // são escolhidas para não colidirem com as que já significam subida, descida e notícia.
    k_news:    escuro ? "#f0a72e" : "#b45309",   // notícia: mantém o âmbar de sempre
    k_market:  escuro ? "#7aa2f7" : "#2c5fb8",   // movimento de preço
    k_open:    escuro ? "#c4a7f7" : "#6b4fa8",   // nota de abertura
    k_summary: escuro ? "#9aa5b1" : "#5b6472",   // resumo de fecho
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
    // ⚠️ A MARGEM DE TOPO EXISTE PARA AS MARCAS EMPILHADAS, e o defeito era visível: a
    // biblioteca empilha verticalmente as marcas do MESMO dia — que é como se vê que um dia
    // teve vários alertas — e sem folga a letra da marca mais alta sai CORTADA pela moldura.
    // É a mesma classe do rótulo do z cortado a meio, que a sessão 67 pagou: um desacordo que
    // se manifesta como composição e não como exceção não tem quem o apanhe.
    //
    // Aqui a margem RESOLVE, ao contrário do que aconteceu no eixo do z: ali o gerador de
    // marcas do eixo adaptava-se à margem e voltava a pôr uma no bordo, e o que resolveu foi
    // fixar o intervalo. As marcas de alerta não se adaptam — assentam no preço do dia —,
    // logo dar folga acima do máximo é exatamente o que lhes dá sítio.
    // ⚠️ E O VALOR IMPORTA: o padrão da biblioteca já é `top: 0.2`, logo qualquer coisa abaixo
    // disso AGRAVA o corte em vez de o resolver — a minha primeira tentativa foi 0,18 e era
    // menos folga do que havia. As marcas empilham-se para cima do preço do dia, portanto a
    // folga tem de acomodar a pilha e não só o máximo da série.
    rightPriceScale: { borderVisible:false, minimumWidth:64,
                       scaleMargins: { top:0.26, bottom:0.08 } },
    timeScale: { borderVisible:false, fixLeftEdge:true, fixRightEdge:true,
                 timeVisible: S.intervalo === "1D", secondsVisible:false,
                 // Um só eixo do tempo para o par. Quando a faixa do z está no ar, é ela que o
                 // mostra, por estar por baixo; o de cima seria uma segunda régua a dizer o mesmo.
                 visible: !(eixoOculto && alvo.id === "graf") },
    crosshair: { mode:0 }, handleScale:false, handleScroll:false,
  });
}

// A inicial de cada tipo. As palavras são as do leitor — as mesmas do filtro da lista — e não
// as do modelo: «Price move» e não «market», «Market close» e não «summary».
const LETRA_ALERTA = {news:"N", market:"P", open:"O", summary:"C"};

/* ⚠️ UMA MARCA POR DIA E POR TIPO, e não uma por alerta — e isto foi decidido A OLHAR para o
   render, não no papel. Com uma marca por alerta, o intervalo de um mês da NVIDIA desenhava
   pilhas de cinco círculos na mesma coluna: a letra da marca mais alta saía cortada pela
   moldura mesmo com 32% de folga no topo, e o conjunto **tapava a linha de preço**, que é o
   objeto do gráfico. Um gráfico que esconde a sua própria série para mostrar anotações trocou
   o assunto pelo enfeite.

   E O COLAPSO NÃO PERDE INFORMAÇÃO, porque a coluna É um dia: num intervalo diário as marcas
   do mesmo dia partilham a MESMA posição no eixo, logo cinco círculos empilhados nunca foram
   cinco pontos distinguíveis — eram um dia desenhado cinco vezes. A marca passa a dizer que
   TIPOS de mensagem saíram nesse dia, e a lista por baixo diz quantas e quais: o clique
   realça-as todas e a nota diz o número.

   No intervalo de um dia não se colapsa: aí as marcas têm hora própria e sítio para ela. */
function marcasDeAlertas(a, desdeTs, ate) {
  const P = paleta();
  const vistos = new Set();
  return (a.alerts || []).map(al => {
    const iso = al.sent_at || (al.date ? `${al.date}T12:00:00Z` : "");
    if (!iso) return null;
    const ts = Math.floor(Date.parse(iso) / 1000);
    if (!Number.isFinite(ts) || ts < desdeTs || (ate && ts > ate)) return null;
    // ⚠️ UMA LETRA, e não uma etiqueta. O texto tinha sido retirado porque onze alertas em
    // seis meses se agrupam nas mesmas semanas e as etiquetas de data se sobrepunham — medido,
    // não suposto. Uma letra é uma fração dessa largura, e é o que permite distinguir os tipos
    // num intervalo diário, onde o tipo era invisível. Verificado a renderizar em 6M e 1Y.
    const k = al.kind || "news";
    const umDia = S.intervalo === "1D";
    const tempo = umDia ? ts : (al.date || iso.slice(0, 10));
    if (!umDia) {
      const chave = `${tempo}|${k}`;
      if (vistos.has(chave)) return null;   // o mesmo dia e o mesmo tipo: uma marca basta
      vistos.add(chave);
    }
    return { tempo, position:"aboveBar", color:P[`k_${k}`] || P.alerta,
             shape:"circle", text:(LETRA_ALERTA[k] || "") };
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
  let fora = 0, hojeFora = 0;
  if (S.camadas.alertas) {
    const dentro = marcasDeAlertas(a, desdeTs, ateTs);
    marcas.push(...dentro);
    // ⚠️ Um alerta pode ter saído fora da janela desenhada — tipicamente de madrugada, horas
    // antes da abertura. Não se arrasta o marcador para a borda, porque isso mentiria sobre a
    // hora; conta-se, e diz-se por baixo. É o mesmo facto que a secção da latência mede.
    if (umDia) {
      const sessao = (a.intraday_day || "").slice(0, 10);
      fora = (a.alerts || []).filter(al => (al.date || "") === sessao).length - dentro.length;
      // O dia corrente vem do carimbo do instantâneo e não do relógio do browser: o que
      // interessa é o dia dos dados servidos, e um browser com a hora errada não pode
      // inventar um dia que o sistema não viu.
      const hoje = (S.visao?.as_of || "").slice(0, 10);
      if (hoje && hoje !== sessao)
        hojeFora = (a.alerts || []).filter(al => (al.date || "") === hoje).length;
    }
  }
  // ⚠️ CONTADO A PARTIR DAS MARCAS DESENHADAS, e não da lista de alertas: um alerta fora da
  // janela do gráfico não tem marca, e nomeá-lo na legenda mandaria procurar no gráfico o que
  // lá não está. É a mesma disciplina das outras linhas da legenda, que só aparecem quando a
  // marca correspondente foi desenhada.
  const DE_LETRA = Object.fromEntries(Object.entries(LETRA_ALERTA).map(([k, v]) => [v, k]));
  const tipos = {};
  for (const m of marcas)
    if (m.shape === "circle" && DE_LETRA[m.text])
      tipos[DE_LETRA[m.text]] = (tipos[DE_LETRA[m.text]] || 0) + 1;
  S.desenhado = {
    tipos,
    alertas: marcas.filter(m => m.shape === "circle").length,
    assinalados: marcas.filter(m => m.shape !== "circle" && m.shape !== "square").length,
    noticias: marcas.filter(m => m.shape === "square").length,
    referencia: !!(S.camadas.referencia && umDia && a.prev_close != null),
    fora: Math.max(0, fora),
    hoje_fora: Math.max(0, hojeFora),
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
    // ⚠️ `focarAlertaEm` PASSOU A SER ASSÍNCRONA, porque pode ter de carregar páginas do
    // histórico para alcançar um dia que está atrás do «show more». Testar o valor de retorno
    // directamente deixaria de funcionar sem dar erro: uma Promise é sempre verdadeira, logo o
    // ramo de falha desapareceria e um clique sem mensagem nenhuma pareceria ter acertado.
    if (typeof focarAlertaEm !== "function") return;
    void Promise.resolve(focarAlertaEm(data)).then(acertou => {
      if (!acertou && aviso) aviso.textContent = `No message within three days of ${data}.`;
    });
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
  // ⚠️ A LEGENDA TEM DE NOMEAR OS TIPOS, senão as cores novas são um código sem chave — o que
  // é pior do que quatro bolas iguais. Nomeiam-se só os tipos DESENHADOS: uma legenda que
  // enumera categorias ausentes manda procurar no gráfico o que lá não está.
  if (d.alertas) {
    const P = paleta();
    for (const [k, rotulo] of [["news", "news alert"], ["market", "price-move alert"],
                               ["open", "market-open note"], ["summary", "market-close summary"]]) {
      if ((d.tipos || {})[k])
        L.push(`<i><span class="p" style="background:${P[`k_${k}`]}"></span> `
               + `<b>${LETRA_ALERTA[k]}</b> ${rotulo}</i>`);
    }
    // ⚠️ E a descoberta: o autor disse que «deveria ser mais intuitivo que podemos interagir
    // com o gráfico». Um gráfico clicável que não diz que o é não é clicado. A frase fica na
    // legenda, que é onde o olho já vai para decifrar as marcas.
    L.push(`<i>click any column to jump to that day's messages below</i>`);
  }
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
  // ⚠️ ESTA LINHA DIZIA «today» E ERA FALSO, e foi o que confundiu o autor: o «today» aqui
  // significava o dia da SESSÃO DESENHADA, que fora de horas é a sessão anterior. Numa página
  // cujo cabeçalho diz «latest close · 10 Sept» e num dia 11, chamar 10 de setembro «hoje» é
  // uma afirmação errada. Passa a nomear a data.
  if (d.fora) {
    const dia = dataDe((S.asset?.intraday_day || "").slice(0, 10));
    L.push(`<i><span><b>${d.fora} alert${d.fora > 1 ? "s" : ""} of ${dia} went out outside `
      + `that session's hours</b>, so ${d.fora > 1 ? "they are" : "it is"} not on this `
      + "chart — the times are in the list below</span></i>");
  }
  // ⚠️ E FALTAVA A OUTRA METADE, que é a pergunta que o autor fez: as mensagens de HOJE. O
  // contador `fora` só olha para o dia da sessão desenhada, logo num dia em que a bolsa ainda
  // não abriu as mensagens já enviadas hoje não eram contadas nem mencionadas em sítio nenhum —
  // o ecrã ficava calado sobre elas em vez de dizer que existem.
  if (d.hoje_fora)
    L.push(`<i><span><b>${d.hoje_fora} message${d.hoje_fora > 1 ? "s" : ""} went out today</b>, `
      + "before any session this chart can draw. Switch the range to place it in "
      + "context, or read it in the list below</span></i>");
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
