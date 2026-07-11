# Guia RÁPIDO de defesa — InvestiGator (versão simplificada)

> A versão de bolso: tudo o que tens de ter na cabeça, em 10 minutos de leitura.
> A versão DETALHADA (ensina do zero, 64 slides) é `slides/guia_estudo/main.pdf`;
> o guião oral completo (abertura de 3 min + 15 s por RQ) está no
> `docs/defence/caderno_de_defesa.md` §0. Todos os números abaixo são os congelados
> e reproduzíveis — nenhum é novo.

---

## 1. O pitch de 30 segundos

"O InvestiGator é um sistema de alertas financeiros **explicável** para o investidor de
retalho. Vigia o mercado US e, quando algo acontece — um movimento anormal ou uma notícia —
alerta no Telegram **com a explicação completa**: o que disparou, porquê, e o que aconteceu
no passado em casos semelhantes. **Nunca prevê preços**: mostra evidência histórica.
Está ao vivo, de graça, sem servidor próprio — e toda a estatística da tese é reproduzível
por scripts versionados."

## 2. O sistema em 5 linhas

1. **Gatilho 1 (mercado):** z-score móvel sobre retornos (janela 20d, limiar |z|≥3), sem lookahead → "movimento anormal PARA esta ação".
2. **Gatilho 2 (notícia):** embedding da manchete (SBERT MiniLM) → procura na KB histórica (FNSPID) os casos mais parecidos → mostra o impacto observado (+1/+3/+5d). É **CBR** (raciocínio baseado em casos).
3. **Triagem aprendida (RQ4):** regressão logística treinada por mim estima P(movimento anormal se segue) — filtra o ruído (fadiga de alertas); evidência, não previsão.
4. **Explicação (XAI):** cada alerta carrega todos os números que o justificam; testes de fidelidade garantem que nada se perde.
5. **Entrega:** canal Telegram (GitHub Actions, 30/30 min em horário de mercado) + dashboard público (Streamlit) que mostra **os mesmos alertas**.

## 3. Os números que TENHO de saber (mapa mínimo)

| Número | O que é | Onde |
|---|---|---|
| **P@5 0,514 ± 0,015** | Recuperação SBERT-MiniLM (5 seeds) vs **0,346 lexical / 0,240 acaso / 0,126 recência** | Cap. 5, `evaluation_results.md` |
| **0,538** | P@5 do SBERT-MPNet (melhor, mas mais pesado) | idem |
| **spread 0,015 vs 0,344** | Consistência da taxa de disparo: z-score vs limiar fixo (o z-score adapta-se a cada ação) | Cap. 5, `evaluation_anomaly.md` |
| **F1 0,530 vs 0,271** | z-score vs Isolation Forest causal (a escolha simples GANHA — validada por comparação) | idem |
| **z = +7,61** | Anomalia real detetada: TSLA, 24-10-2024 (exemplo trabalhado) | Cap. 5 (CS1) |
| **+6,46%** | Impacto médio +5d dos 3 precedentes do exemplo Nvidia/AI (demo offline reproduz) | Cap. 3, `scripts/demo.py` |
| **−1,97%** | CS3: manchete positiva recupera cluster de ameaça competitiva — **tema ≠ direção** (limitação assumida) | Cap. 5 |
| **PR-AUC 0,542 vs 0,496** | RQ4: a volatilidade-só BATE todos os modelos com texto (reportado tal como é) | Cap. 5 (CS4), `evaluation_triage.md` |
| **0,632 vs 0,163** | MAS: precisão@5-alertas/dia da triagem vs alertar-sempre (quase 4×) — o mecanismo vale | idem |
| **79.753 / 2.016** | Exemplos FNSPID 2018–23 do treino / fatia curada que serve a app pública | `kb_fnspid_build.md` |
| **0,992 / 96%** | Paridade ONNX↔SBERT na produção (cosseno médio; vizinhos top-3 comuns) | `onnx_minilm_validation.md` |
| **132 testes; 78 pp; 52/52** | Testes+ruff verdes; tese 0 erros; todas as citações verificadas | CI, `page_audit.md` |

## 4. Cada componente em 3 frases

- **z-score móvel:** comparo o retorno de hoje com a média e desvio dos últimos 20 dias *desta* ação; se está a mais de 3 desvios, é anormal *para ela*. Um limiar fixo (%) dispara demais nas voláteis e de menos nas calmas — medi isso (spread 0,344 vs 0,015). Sem lookahead: só uso o passado.
- **Embeddings/SBERT:** transformo a manchete num vetor onde textos com significado parecido ficam perto; a semelhança é o cosseno. O SBERT é pré-treinado (inferência) — não treino linguagem, uso-a. Comparei com um baseline lexical para provar o ganho semântico (0,514 vs 0,346).
- **KB histórica (CBR):** cada notícia do FNSPID vira um "caso": manchete + data + ticker + o que o preço fez depois (+1/+3/+5d). Dada uma notícia nova, devolvo os casos mais parecidos e o seu desfecho. É evidência do passado, nunca previsão.
- **Event study:** mede o impacto DEPOIS do evento (do fecho do dia do evento para a frente) — medir o desfecho não é prever; alinho a notícia ao 1.º dia de negociação seguinte.
- **Triagem (RQ4, o modelo que EU treinei):** rótulo = |retorno anormal vs SPY| ≥ 2% na janela (d, d+3]; features só do passado (teste anti-lookahead); split temporal com embargo; calibração Platt. O texto não bateu a volatilidade (digo-o), mas no orçamento de 5 alertas/dia a triagem quase quadruplica a precisão.
- **XAI:** a explicação É o cálculo (números exatos no alerta); testes de fidelidade partem se algum número desaparecer. Confiança apropriada: digo também o que o sistema NÃO sabe (tema ≠ direção).
- **Produto:** Actions (cron) + canal Telegram + app Streamlit + bot `/watch`; tudo opcional está off por defeito e falha aberto; anti-repetição no dia; segredos só em Secrets/.env.

## 5. As 8 perguntas mais prováveis (resposta curta)

1. **"Isto não é só usar bibliotecas?"** — É engenharia de IA: integração, metodologia notícia→impacto e avaliação honesta são a contribuição. E treinei um modelo próprio (RQ4) com protocolo anti-lookahead.
2. **"O vosso modelo perdeu para a volatilidade — é um fracasso?"** — Não: pré-comprometi-me com a comparação e reporto-a. A hipótese do texto falhou neste corpus; o mecanismo de triagem vale (0,632 vs 0,163 no orçamento diário). Ciência honesta > número bonito.
3. **"Porquê não prever o preço?"** — Decisão de desenho e ética (EMH; retalho): evidência explicável em vez de promessa de previsão. É restrição dura do sistema, escrita nos alertas.
4. **"P@5 de 0,51 é bom?"** — 2,1× o acaso, acima do lexical, desvio pequeno (5 seeds); e é honesto: corpus recente, proxy de setor como limitação explícita.
5. **"Porquê z-score e não ML na anomalia?"** — Comparei: o Isolation Forest causal perde (F1 0,271 vs 0,530). A escolha simples fica validada por comparação, não por fé.
6. **"A recuperação capta a direção da notícia?"** — Não — capta o TEMA (CS3: manchete positiva, cluster negativo, −1,97%). Assumo: a média dos precedentes é evidência sobre um tema, sinalizo discordância de direção.
7. **"Isto funciona mesmo?"** — Está ao vivo: canal Telegram alimentado por Actions de 30 em 30 min, app pública com os mesmos alertas, bot interativo. E a demo offline reproduz o exemplo da tese num comando.
8. **"O que fica por fazer?"** — Avaliação de retrieval multi-ano sobre a KB construída; estudo humano de confiança; webhook/host para o bot; multi-mercado. Tudo listado no Cap. 6.

## 6. Se algo falhar na defesa

- **Sem wifi/projetor:** `python scripts/demo.py` é offline e determinística (+6,46%); o guia detalhado tem o output real captado em slides.
- **App dormente/privada:** mostrar o canal Telegram no telemóvel (mensagens reais) ou os slides.
- **Branco sobre um número:** este ficheiro (§3) e o mapa completo no caderno §5.5.

## 7. Onde estudar mais

- **Detalhado (ensina do zero):** `slides/guia_estudo/main.pdf` (64 slides).
- **Guião oral + perguntas do júri completas:** `docs/defence/caderno_de_defesa.md` (§0 e §7).
- **A tese em si:** `thesis/main.pdf` (78 pp) — a leitura final é insubstituível.
