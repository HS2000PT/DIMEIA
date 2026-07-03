# Proposta de extensão à dissertação — componente de ML treinado (para o Prof. Luís Gomes)

> **De:** Henrique Santos (1180934) · **Assunto:** proposta de extensão — modelo treinado de triagem
> de alertas · **Pedido:** validação do âmbito antes de alterar o texto da dissertação.

## Motivação (1 parágrafo)

A dissertação (InvestiGator) integra e avalia componentes existentes — deteção estatística de anomalias
e recuperação semântica de precedentes com SBERT pré-treinado — num sistema explicável e reproduzível.
Para reforçar a componente de **engenharia de *machine learning*** (e antecipar a pergunta do júri
"onde está o modelo que *tu* treinaste?"), proponho acrescentar **um componente supervisionado treinado
por mim**, mantendo intactas as restrições da tese (sem previsão de preços/direção, APIs gratuitas,
XAI-first).

## O que proponho treinar

**Modelo de triagem/materialidade de notícias**: dado um título de notícia + contexto de mercado,
estimar a **probabilidade de se seguir um movimento anormal** (em qualquer direção) — ou seja,
*"esta notícia merece alerta?"*. Nova questão de investigação (rascunho):

> **RQ4 —** Pode um modelo supervisionado, treinado com notícias históricas e contexto de mercado,
> priorizar utilmente as notícias que merecem alerta, para além de baselines simples de volatilidade?

- **Rótulo** (dados históricos, sem anotação manual): `|retorno anormal em (d, d+3]| ≥ τ`, com retorno
  anormal = retorno do ticker − retorno do mercado (SPY); τ primário 2%, com análise de sensibilidade.
  Os rótulos saem do código de *event study* já validado na tese.
- **Features** (todas calculáveis no dia do evento — sem *lookahead*, testado): embedding SBERT do
  título + volatilidade pré-evento (20d) + retorno acumulado 5d + setor + comprimento do título.
- **Modelos:** regressão logística (interpretável, principal) e *gradient boosting* (comparação),
  contra *baselines* honestos (alertar-sempre; só-volatilidade). scikit-learn, CPU, seeds fixas.
- **Protocolo:** divisão **temporal** treino/validação/teste com embargo; calibração; PR-AUC como
  métrica principal (classes desequilibradas) + precision@N-alertas/dia; tudo regenerável por script.
- **XAI:** coeficientes e decomposição aditiva por alerta (regressão logística); SHAP no boosting
  (Lundberg & Lee, já citado).
- **Dados:** corpus Finnhub já usado na avaliação (3.714 títulos) para construir o pipeline;
  **FNSPID multi-ano (2018–2023)** para os números finais (pipeline de download já validado).

## O que explicitamente NÃO muda

- **Sem previsão de preços nem direção** — o modelo prioriza alertas ("é material?"), não aconselha
  transações; a redação do alerta di-lo ("evidência de triagem, não previsão").
- As avaliações e números já validados na tese ficam **congelados** (o novo estudo é aditivo).
- Restrições mantidas: APIs gratuitas, XAI-first, reprodutibilidade total (scripts + seeds).

## Impacto na dissertação (se aprovar)

RQ4 no Cap. 1; fundamentação curta no Cap. 2 (event study com ajuste de mercado; materialidade de
notícias — citações verificadas como as restantes 50); nova secção no Cap. 3 (tarefa, rótulos,
protocolo, ameaças à validade); novo componente no Cap. 4; novo estudo no Cap. 5; veredicto no Cap. 6.
Estimativa: +6 a 10 páginas. O código e as experiências avançam já (não tocam no texto); **os capítulos
só são alterados após a sua validação** desta proposta.

## Risco e honestidade

O resultado pode ser modesto (a *baseline* de volatilidade é forte). Compromisso: reportar o resultado
que der — se o modelo não bater a baseline, a tese discute porquê; o contributo metodológico
(rotulagem histórica sem anotação manual + protocolo temporal + integração explicável) mantém-se válido.
