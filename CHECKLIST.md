# CHECKLIST — o que FALTA (só isso)

> Lista viva, mínima de propósito: **apenas o que ainda não está feito.** O histórico completo
> do que já foi construído vive em `progress/SESSIONS.md` (por sessão) e `progress/TRACKER.md`
> (por fase); o estado técnico detalhado em `CLAUDE.md`; o resumo para o júri em
> `RELATORIO_FINAL.md`. Última limpeza: 2026-07-11.

## 🧑 Cliques só teus (ninguém pode fazer por ti)

### Produto ao vivo
- [x] ~~Chaves de preços~~ ✅ **FECHADO 13/07:** os 3 segredos existem no GitHub
      (`TIINGO_API_KEY` + `POLYGON_API_KEY` criados 13/07 19:10; `ALPHAVANTAGE_API_KEY` desde
      03/07) e uma corrida manual do Alerts às 19:27 confirmou-os visíveis no runner (`***`).
      **O mercado JÁ está vivo** — 1.º alerta de mercado de sempre a 13/07 (NVDA −3,53%,
      "notable", Sector check + Possible explanation). Nota: o yfinance está a responder nos
      runners neste momento, por isso a cadeia de fallback fica de reserva silenciosa — se o
      Yahoo voltar a bloquear, o log dirá `[precos …] servido por …`.
- [ ] **Streamlit: apagar e recriar a app com Python 3.12** (Advanced settings ao criar —
      NÃO é o defeito). Causa confirmada (2026-07-11): em Python 3.14 os pins pandas/numpy
      não têm wheels, a instalação falha em silêncio (~45 min) e a app arranca sem plotly
      no ambiente base da plataforma. Detalhe: `docs/design/deployment.md` (aviso no topo).
- [ ] **Streamlit: Sharing → público** — logo a seguir a recriar; verificar em janela anónima.
- [ ] **VM Oracle Free (para alertas em minutos)** — criar conta + VM e correr
      `bash deploy/setup_vm.sh` (guia passo-a-passo: `docs/design/vm_watch.md`). Até lá, o cron
      do GitHub cobre com latência ~1-2 h. *Testável já no teu PC:*
      `python scripts/run_alerts.py --watch`.
- [ ] **Afixar a mensagem de onboarding no canal** + descrição (textos prontos:
      `docs/design/going_live.md` §1b).

### Académico (bloqueia a submissão)
- [ ] **Leitura final das teses** (`thesis/main.pdf` 90 pp · `thesis-pt/main.pdf` 92 pp) — o texto é teu para defender.
- [ ] **Licença do código** com o Prof. Luís Gomes (MIT/Apache; política de IP do ISEP) +
      ficheiro `LICENSE`.
- [ ] **Redação exata da declaração de uso de IA** (MEIA/ISEP) + **data de entrega** — confirmar
      com o Prof. Luís Gomes.
- [ ] Correr `python scripts/post_validate.py` de vez em quando enquanto o canal está vivo
      (última corrida: 13/07 — 33 decisões maturadas; precisão das mantidas 0,667 vs base
      0,455; Brier 0,229 → `docs/evaluation/live_monitoring.md`).

### Opcional
- [ ] (Opcional) Renomear o repositório `DIMEIA`→`InvestiGator` (Settings → Rename; mantém a
      história e redireciona os URLs antigos).

## 🤖 Pendentes do código (nenhum bloqueia)
- [x] ~~Confirmar alertas de MERCADO~~ ✅ **CONFIRMADO 13/07** (verificação nos logs reais do
      Actions): 1.º alerta de mercado de sempre (NVDA −3,53% intradiário, z=−1,67 vs ±1,5,
      severidade "notable"), linha "Sector check" (AMD −4,1%, TSLA −3,8% → sector-wide),
      "Possible explanation (0d ago)", dedup ("já alertado hoje — sem repetição"), enviado ao
      Telegram; branch `alerts-history` a crescer (44 alertas: 43 news + 1 market).
- [ ] Confirmar o 1.º RESUMO DIÁRIO na corrida ≥21h UTC de um dia útil (13/07 à noite ou dia
      útil seguinte) — agora há resultados de mercado para o alimentar.
- [x] ~~17/07: confirmar maturação da KB viva~~ ✅ **CONFIRMADO 13/07 (4 dias antes do
      previsto)**: 13 casos maturados em `live_kb.jsonl` com impactos reais (JPM/NFLX de
      04-05/07, alinhados ao 1.º dia de negociação 06/07), 1.043 pendentes, e o log do scan
      diz "[kb-viva] 13 caso(s) recente(s) em uso" — os precedentes de 2026 já entram no
      retrieval.
- [ ] ~Agosto: quando a KB viva tiver semanas de casos, definir `news.max_precedent_age_days`
      (proposta: 730) no alerts.yaml — o corte duro de idade dos precedentes.
- [x] ~~Platt vs isotonic no PC do FNSPID~~ ✅ **FEITO 13/07** (afinal ESTE PC tem o dataset):
      `scripts/evaluate_calibration_ext.py` reproduz o protocolo congelado 5/5 ao milésimo e
      compara — **a Platt ganha ou empata no Brier em TODAS as famílias** (ECE misto, margens
      pequenas), mesmo com 17.710 pontos de calibração; a escolha da tese fica validada
      empiricamente → `docs/evaluation/calibration_platt_vs_isotonic.md`. Fica em aberto só
      o opcional: re-curadoria da KB light com peso maior em 2022-23.
- [ ] Polimento futuro (quando quiseres): cobertura `pytest --cov` no README; camada `logging`;
      CLI do Gatilho 2; de-dup de precedentes quase iguais.
