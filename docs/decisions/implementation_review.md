# implementation_review.md — Revisão crítica da implementação e do desenho (Fase D)

> Revisão de engenharia, honesta e crítica, em resposta a: *é mesmo o melhor caminho para o objetivo?*
> *funcionará na vida real e será útil?* *como se corre?* (o "como correr" está em
> [`how_to_run.md`](../design/how_to_run.md)). A auditoria página-a-página e a re-verificação de TODAS as
> citações são a Fase E.

**Data:** 2026-06-27 · **Versão:** 76 pp, 50 refs.

## 1. Validação da estatística (re-corrida HOJE, não apenas consistência de texto)

Os três scripts de avaliação foram **re-executados neste ambiente** (SBERT 5.6.0 + corpus real presente) e
reproduziram os números da tese **exatamente** (a única diferença nos ficheiros é o carimbo temporal
"Gerado:"):

| Avaliação | Resultado re-corrido | Estado |
|---|---|---|
| Recuperação (5 seeds) | MiniLM 0,514±0,015 · MPNet 0,538±0,011 · lexical 0,346 · recency 0,126 · random 0,240 (P@5) | ✅ idêntico à tese/`evaluation_results.md` |
| Anomalia | amplitude z-score 0,015 vs fixo 0,344 · F1 0,516 vs 0,218 · ablação 0,385/0,516/0,678 | ✅ idêntico |
| Por setor | tech 0,712 · energia 0,448 (lift +0,377) · saúde 0,419 · banca 0,272 · consumo 0,171 | ✅ idêntico |
| Testes | `pytest -m "not telegram"` = **42 verdes** (inclui o teste semântico `@sbert`) + ruff limpo | ✅ |

**Conclusão:** os números da tese são genuinamente **reprodutíveis a partir de scripts versionados**, não
apenas internamente consistentes. Esta é a garantia mais importante para o júri.

## 2. O desenho é o melhor caminho para o objetivo? (crítica)

Objetivo: alertas explicáveis para retalho, **sem previsão**, só recursos gratuitos, reprodutível.

- **Detetor z-score** — escolha certa. Transparente, normaliza a volatilidade, consistência validada. As
  alternativas (Isolation Forest, GARCH) acrescentam opacidade/complexidade não justificadas para uma
  série de retornos de baixa dimensão que tem de ser explicada a um não-especialista. Defensável.
- **Recuperação SBERT + event study** — altitude certa. Bate todas as baselines; enquadramento CBR
  (raciocínio baseado em casos) liga-se à explicabilidade. A alternativa (LLM) violaria as restrições de
  gratuito/transparente/reprodutível.
- **Explicação transparente** — fiel por construção (renderizada dos próprios objetos computados).
- **Fraqueza real:** o corpus é a janela recente do Finnhub, não o FNSPID multi-ano → a análise de
  impacto é **preliminar**. O pipeline de construção existe; o build completo é a principal lacuna (já
  declarada como trabalho futuro).

**Veredito:** nenhuma mudança de desenho é necessária para a dissertação. As escolhas são as mais
defensáveis para o objetivo declarado.

## 3. Funcionará na vida real e será útil? (viabilidade honesta)

**Provado de ponta a ponta:** gatilho de mercado (yfinance → z-score → explicação → Telegram; envio real
confirmado) e gatilho de notícias (título → SBERT → KB → precedentes → explicação).

**Limites honestos de protótipo (não de investigação):**
- Sem agendador nem alojamento (os pontos de entrada existem; cron/host fora de âmbito).
- *Tier* gratuito de notícias → KB recente e rasa → menos precedentes; o FNSPID completo dá profundidade.
- Sem persistência além do ficheiro da KB; sem contas de utilizador; sem recuperação de falha de provider.
- **Utilidade para um humano ainda não medida** (sem estudo de utilizador) — a principal validação em aberto.

**Veredito de utilidade:** já é genuinamente útil HOJE como apoio à decisão de um investidor de retalho
curioso — totalmente para o gatilho de mercado, e para o de notícias sobre o corpus recente. Para ser
robustamente útil falta a KB multi-ano + um estudo de usabilidade.

## 4. Riscos de engenharia / robustez

- **Limites de taxa das APIs** (Finnhub 60/min; yfinance não-oficial) → fallback previsto; produção
  exigiria cache + backoff.
- **yfinance é não-oficial** → fragilidade aceitável para um protótipo gratuito, sinalizada.
- **Coerência embedder–KB:** consultar com um embedder diferente do usado para construir a KB dá resultados
  errados silenciosamente (visto antes: dim-64 vs 384). Hoje é só por convenção — **um footgun**.
  → Recomendação R1 (abaixo).
- **Determinismo:** seeds fixas; inferência SBERT determinística em CPU. ✅

## 5. Recomendações

**Acionáveis (pequenas, opcionais):**
- **R1 — guarda de dimensão na KB:** `find_precedents` deve falhar com erro claro se a dimensão do
  embedding da consulta não coincidir com a dos registos (previne o footgun dim-64 vs 384). *Implementado
  nesta fase* (ver testes).
- **R2 — CLI para o gatilho de notícias** (hoje só programático) — conveniência; não essencial.

**Trabalho futuro (já reconhecido na tese):** KB FNSPID multi-ano; estudo humano de utilidade; impacto
ajustado ao mercado (CAR); índice ANN para escala; texto mais rico (corpo dos artigos).

## Veredito global da Fase D
O desenho é a forma certa e defensável de atingir o objetivo; as estatísticas são reprodutíveis (re-corridas
hoje); o sistema funciona de ponta a ponta como protótipo. As lacunas honestas (KB completa, estudo humano)
já estão declaradas como trabalho futuro. Sem mudanças de desenho necessárias; R1 implementado como reforço
de robustez.
