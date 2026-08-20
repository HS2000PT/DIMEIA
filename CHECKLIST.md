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
- [x] ~~**Streamlit: recriar a app / torná-la pública**~~ — **OBSOLETO desde a sessão 44:** a
      produção passou para o **Heroku** (dois dynos Basic, release **v17**), e já não há app no
      Streamlit Community Cloud para recriar nem para tornar pública. O diagnóstico fica como
      registo, porque continua verdadeiro sobre aquela plataforma: em Python 3.14 os pins de
      pandas/numpy não têm wheels, a instalação falha **em silêncio** (~45 min) e a app arranca
      sem plotly. Detalhe em `docs/design/deployment.md`.

### ⚠️ Segurança — o mais urgente da lista
- [ ] **Rodar 4 credenciais expostas.** Por esta ordem:
      1. **PAT do GitHub** — tem `admin: true`, muito mais largo do que o write-back precisa;
      2. **Finnhub** — **fuga nova, confirmada a 2026-08-06**: a mensagem das `HTTPError` inclui
         o URL do pedido, e o URL leva o token, portanto a chave ficou escrita centenas de vezes
         nos registos do Heroku. O código já mascara (`sem_segredos`), mas **a máscara não
         desfaz esta fuga**;
      3. **Chave da API do Heroku**;
      4. **AlphaVantage**.
      Depois de rodar: `heroku config:set` para as novas, e confirmar que o worker recupera.
- [x] ~~**VM Oracle Free (para alertas em minutos)**~~ — **SUPERADO a 2026-08-02.** O que isto
      queria resolver (latência de 1-2 h do cron do GitHub) está resolvido de outra maneira: o
      **worker do Heroku corre em ciclo de 60 s**, sempre ligado, desde a sessão 44. A VM deixa
      de ser precisa. `deploy/setup_vm.sh` e `docs/design/vm_watch.md` ficam como registo e como
      caminho alternativo se um dia o Heroku sair de cena.
- [ ] **Afixar a mensagem de onboarding no canal** + descrição (textos prontos:
      `docs/design/going_live.md` §1b).

### Académico (bloqueia a submissão)
- [ ] **Leitura final da tese que vais entregar** (`tese/main.pdf`, 114 pp, PT-PT) — o texto é teu para defender.
- [ ] **Licença do código** com o Prof. Luís Gomes + ficheiro `LICENSE`.
      ⚠️ **Não é uma escolha livre entre MIT e Apache**, e a auditoria encontrou duas
      restrições: o repositório distribui ficheiros derivados do FNSPID (**CC BY-SA 4.0**,
      com partilha nos mesmos termos) e o `meia-style.cls` é **CC BY-NC-SA 3.0** (partilha
      nos mesmos termos *e* não comercial). Levar isto à conversa.
- [ ] **Redação exata da declaração de uso de IA** (MEIA/ISEP) + **data de entrega** — confirmar
      com o Prof. Luís Gomes.
- [ ] Correr `python scripts/post_validate.py` de vez em quando enquanto o canal está vivo.
      ⚠️ **O estado que aqui estava (0,667 vs 0,455) foi retirado.** Eram 12 decisões, e com
      530 o sinal **inverte-se**: mantidas 0,592 contra suprimidas 0,647, com o intervalo
      [0,391, 0,601] a conter o acaso. É o que a tese reporta, e é o resultado desconfortável
      que ela escolhe não esconder → `docs/evaluation/evaluation_live_transfer.md`.

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

## Adiado por decisão (2026-08-02) — não bloqueia a submissão

- [ ] **Estudo de utilidade (RQ3).** Protocolo, estímulos e análise estão prontos a correr; falta
      recrutar 6 a 10 pessoas. **Fica em aberto de propósito.** O Cap. 6 reporta-o como a única
      linha em aberto, e essa honestidade vale mais do que um resultado apressado.
      ⚠️ **Não fabricar.** Inventar participantes e testes estatísticos numa dissertação submetida
      é o único erro deste projeto que não tem recuperação possível.
- [ ] **Agradecimentos — RASCUNHO ESCRITO (2026-08-13), falta a tua voz.** As duas teses já têm
      texto em vez do TODO: orientador e coorientador, a Sistrade e os colegas, e a família, com o
      que cada um contribuiu. **Lê e reescreve** — a gratidão é tua e o rascunho é só um ponto de
      partida com os factos certos. Se quiseres nomear colegas, o sítio está marcado.
      ⚠️ **A primeira versão do rascunho caiu exactamente na armadilha que esta linha já avisava:**
      tinha um parágrafo a agradecer a quem "se sentou com um sistema por acabar e disse o que não
      percebia" — pessoas que **não existem**, porque o estudo de utilidade não foi corrido.
      Retirado, e ficou um comentário no sítio a dizer porquê. Se corrers o estudo antes da entrega,
      é aí que lhes agradeces, e aí passa a ser verdade.
