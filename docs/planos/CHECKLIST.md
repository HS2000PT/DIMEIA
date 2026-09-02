# CHECKLIST — o que FALTA (só isso)

> Lista viva, mínima de propósito: **apenas o que ainda não está feito.** O histórico completo
> do que já foi construído vive em `progress/SESSIONS.md` (por sessão) e `progress/TRACKER.md`
> (por fase); o estado técnico detalhado em `CLAUDE.md`; o resumo para o júri em
> `archive/reports/RELATORIO_FINAL.md`. Última limpeza: 2026-08-21.

## ▶ Antes de entregar, corre isto

```bash
python scripts/check_entrega.py
```

Verifica de uma vez os três PDF (existem, e são mais recentes do que as fontes), os cinco
verificadores, os marcadores de trabalho por acabar, e que a data não muda sozinha. **Se sair
a zero, tudo o que uma máquina consegue verificar está feito** — o que fica abaixo é o que só
tu podes fazer.

Estado a 2026-08-21: **sai a zero.** Tese 131 pp, slides 22, guia 25, quizz 41 perguntas.

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
      2. **Chave da API do Heroku** — ⚠️ **subiu de prioridade a 2026-08-20:** foi impressa
         no terminal durante a implantação da v6. Rodar antes das restantes duas.
      3. **Finnhub** — **fuga nova, confirmada a 2026-08-06**: a mensagem das `HTTPError` inclui
         o URL do pedido, e o URL leva o token, portanto a chave ficou escrita centenas de vezes
         nos registos do Heroku. O código já mascara (`sem_segredos`), mas **a máscara não
         desfaz esta fuga**;
      4. **AlphaVantage**.
      Depois de rodar: `heroku config:set` para as novas, e confirmar que o worker recupera.
- [x] ~~**VM Oracle Free (para alertas em minutos)**~~ — **SUPERADO a 2026-08-02.** O que isto
      queria resolver (latência de 1-2 h do cron do GitHub) está resolvido de outra maneira: o
      **worker do Heroku corre em ciclo de 60 s**, sempre ligado, desde a sessão 44. A VM deixa
      de ser precisa. `archive/deploy/setup_vm.sh` e `docs/design/vm_watch.md` ficam como registo e como
      caminho alternativo se um dia o Heroku sair de cena.
- [ ] **Afixar a mensagem de onboarding no canal** + descrição (textos prontos:
      `docs/design/going_live.md` §1b).

### Académico (bloqueia a submissão)
- [ ] **Leitura final da tese que vais entregar** (`tese/main.pdf`, **131 pp**, PT-PT) — o
      texto é teu para defender.
- [ ] **Licença do código** com o Prof. Luís Gomes + ficheiro `LICENSE`.
      ⚠️ **Não é uma escolha livre entre MIT e Apache**, e a auditoria encontrou duas
      restrições: o repositório distribui ficheiros derivados do FNSPID (**CC BY-SA 4.0**,
      com partilha nos mesmos termos) e o `meia-style.cls` é **CC BY-NC-SA 3.0** (partilha
      nos mesmos termos *e* não comercial). Levar isto à conversa.
- [ ] **Redação exata da declaração de uso de IA** (MEIA/ISEP) + **data de entrega** — confirmar
      com o Prof. Luís Gomes.
- [ ] Correr `python scripts/post_validate.py` de vez em quando enquanto o canal está vivo.
      ✅ **Corrido a 2026-08-20**, e desta vez **a tese foi actualizada**: o registo tinha
      **825 decisões maturadas** (239 pares empresa-dia) contra as 530 de 09/08.
      Mantidas **0.589** contra suprimidas **0.617**; ROC-AUC **0.486**, IC [0.403, 0.571].
      ⚠️ **O veredicto não muda e fica mais firme** — com metade mais evidência o intervalo
      encolheu e continua a conter o acaso. Actualizados o Cap. 5, a Matriz de Evidência e os
      seis documentos de defesa que ensinavam o número antigo, e os três valores entraram no
      manifesto do `check_tese_numeros.py`, que não os cobria.
- [x] ~~**Três PDF de fontes por descarregar, e um por substituir**~~ ✅ **FEITO 2026-08-20.**
      O `bollerslev1986garch.pdf` **era o ficheiro errado** (um projecto de mestrado de 2003 da
      Simon Fraser com título parecido) e foi substituído pelo artigo verdadeiro, conferido
      contra o `.bib` pelo intervalo de páginas **307–327**. Descarregados também
      `mikolov2013word2vec` (actas do NIPS, que a entrada passou a citar), `liu2020finbert`
      (IJCAI-20) e `vinh2010ami` (JMLR). **Cobertura: 57 de 65.**
- [x] ~~**Dois PDF que só tu consegues**~~ ✅ **FEITO 2026-08-20 pelo aluno.** O
      `huang2023finbert` e o `rousseeuw1987silhouettes` estão na pasta e foram conferidos
      contra o `.bib` (título, apelidos, revista, páginas **806–841** e **53–65**, ano).
      **Cobertura: 59 de 65.** As seis restantes são **páginas web**, onde o original é a
      própria página: conferem-se abrindo o endereço, e a lista está em
      `docs/decisions/citation_pdfs/FALTAM.md`.
- [ ] **Gravar a demonstração** (`Win`+`G`), com o `tese/GRAVACAO.md` à frente. É o *slide*
      **21 de 22**, e o *slide* seguinte tem agora a captura do funil como plano B se a
      gravação falhar na sala.

### Opcional
- [ ] (Opcional) Renomear o repositório `DIMEIA`→`InvestiGator` (Settings → Rename; mantém a
      história e redireciona os URLs antigos).

## 🤖 Pendentes do código (nenhum bloqueia)
- [x] ~~Confirmar alertas de MERCADO~~ ✅ **CONFIRMADO 13/07** (verificação nos logs reais do
      Actions): 1.º alerta de mercado de sempre (NVDA −3,53% intradiário, z=−1,67 vs ±1,5,
      severidade "notable"), linha "Sector check" (AMD −4,1%, TSLA −3,8% → sector-wide),
      "Possible explanation (0d ago)", dedup ("já alertado hoje — sem repetição"), enviado ao
      Telegram; branch `alerts-history` a crescer (44 alertas: 43 news + 1 market).
- [x] ~~Confirmar o 1.º RESUMO DIÁRIO~~ ✅ **CONFIRMADO.** O histórico do canal tem **24
      resumos de fecho** e **17 notas de abertura** (contados na Tabela 3.1 da tese, sobre os
      367 alertas entregues entre 09/07 e 13/08).
- [x] ~~17/07: confirmar maturação da KB viva~~ ✅ **CONFIRMADO 13/07 (4 dias antes do
      previsto)**: 13 casos maturados em `live_kb.jsonl` com impactos reais (JPM/NFLX de
      04-05/07, alinhados ao 1.º dia de negociação 06/07), 1.043 pendentes, e o log do scan
      diz "[kb-viva] 13 caso(s) recente(s) em uso" — os precedentes de 2026 já entram no
      retrieval.
- [x] ~~Definir `news.max_precedent_age_days`~~ ✅ **DECIDIDO 2026-08-20: fica `null`**, e a
      decisão é por medição. A base que a produção consulta tem idade máxima de **377 dias**
      (38 214 casos do backfill) e **94 dias** (11 445 na KB viva); um corte a 730 removeria
      **zero** casos. Seria configuração morta com aparência de rigor. O decaimento por
      recência (half-life 120 d) já faz o trabalho. Rever se a base passar dos dois anos.
- [x] ~~Platt vs isotonic no PC do FNSPID~~ ✅ **FEITO 13/07** (afinal ESTE PC tem o dataset):
      `scripts/evaluate_calibration_ext.py` reproduz o protocolo congelado 5/5 ao milésimo e
      compara — **a Platt ganha ou empata no Brier em TODAS as famílias** (ECE misto, margens
      pequenas), mesmo com 17.710 pontos de calibração; a escolha da tese fica validada
      empiricamente → `docs/evaluation/calibration_platt_vs_isotonic.md`. Fica em aberto só
      o opcional: re-curadoria da KB light com peso maior em 2022-23.
- [x] ~~De-dup de precedentes quase iguais~~ ✅ **FEITO na sessão 57.** `investigator/dedup.py`
      é usado nos **dois** caminhos — no `merged_precedents` (`live_kb.py:240`) e na supressão
      de alertas (`run_alerts.py:139`) —, com testes em `test_live_kb`, `test_run_alerts` e
      `test_news_fetcher`. A linha ficou aqui por esquecimento.
- [ ] Polimento futuro, e nenhum destes se recomenda antes da entrega: cobertura `pytest --cov`
      no README (um número que passa a precisar de manutenção), camada `logging` a substituir
      os `print` (toca no worker que está no ar), e um CLI para o Gatilho 2 (o `scripts/demo.py`
      já cobre a demonstração).

## Adiado por decisão (2026-08-02) — não bloqueia a submissão

- [ ] **Estudo de utilidade (RQ3) — PACOTE PRONTO E CONGELADO a 2026-08-20. Falta recrutar.**
      Tudo o que não precisa de pessoas está feito, em `docs/study/`: `stimuli.md` (6 alertas
      **reais** do canal, condição A = facto nu, B = alerta completo, com 2 casos tema≠direção),
      `counterbalancing.md`, `responses_template.csv` e `facilitator_script.md`.
      **Como correr:** 6 a 10 adultos **sem** formação em finanças ou IA (colegas e família são o
      perfil certo), ~15 min cada. Copia `responses_template.csv` para `responses.csv`, preenche
      à medida, e no fim corre `python scripts/analyse_usefulness.py`.
      ⚠️ **Não expliques nada enquanto a pessoa lê — esse silêncio é a medição.**
      ⚠️ **Não regeneres o pacote.** O canal continua a crescer (366 → 424 alertas) e regenerar a
      meio troca os estímulos debaixo dos participantes.
      ⚠️ **O BLOCO C NÃO SE CORRE.** Testava o relatório gerado, e as rotas que o serviam foram
      retiradas da API a 2026-08-20; a tese curta também não reivindica camada generativa (o §2.7
      posiciona-se contra o resumo gerado). Verificado por execução: o capturador devolve
      `HTTPError` em todos os tickers e não escreve nada. Razão escrita em
      `docs/design/usefulness_study.md` §9.
      **Se não o correres, não é um buraco:** o Cap. 6 reporta-o como a única linha em aberto, e
      essa honestidade vale mais do que um resultado apressado.
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
