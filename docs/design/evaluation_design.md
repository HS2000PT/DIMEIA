# evaluation_design.md — Plano de avaliação por componente

> **Fase C.** Definir a avaliação **ANTES** de a correr (sem "pescar" bons números — §16). Cada método
> defensável e explicável. Resultados modestos mas **honestos** são válidos; nunca inflacionar nem inventar (§6.5).
> Regras transversais aplicam-se a tudo: **sem lookahead**, **seeds fixas**, reportar **variância** onde importa,
> e nunca apresentar um número que não se consiga **reproduzir e explicar**.

## 0. Princípios e dados
- **Fonte de avaliação histórica:** FNSPID (subconjunto definido em `data_card.md`). Separar claramente o que é
  *in-sample* (construção) do que é *avaliação*.
- **Sem lookahead:** features e impacto medidos só com informação no instante do evento ou posterior à janela
  definida; documentar a regra em cada experiência.
- **Reprodutibilidade:** seeds fixas; figuras de resultados geradas por script (§6.7); ambiente fixado (§7).

## 1. Detetor de anomalias
- **Pergunta de avaliação:** o detetor assinala movimentos que correspondem a anomalias "reais"?
- **Rótulo de "anomalia verdadeira" (explícito):** dias com movimento confirmado grande (ex.: |retorno| acima de
  um limiar pré-definido, p.ex. percentil alto da distribuição histórica) e/ou coincidentes com eventos
  conhecidos. **Limitação assumida:** é uma definição operacional (proxy), não uma verdade absoluta.
- **Métricas:** precision, recall, F1; opcionalmente curva precision–recall ao variar o limiar de z-score.
- **Baseline:** limiar fixo simples (ex.: |retorno| > k%) vs. z-score com janela móvel.
- **Ablação:** tamanho da janela móvel (ex.: 10/20/60 dias) e limiar de z-score.
- **Rigor:** o limiar é escolhido sem olhar para o conjunto de teste; reportar por vários tickers (variância).

## 2. Motor de correlação / precedentes (NÚCLEO)
- **Pergunta A — qualidade da recuperação:** os precedentes recuperados são **mesmo análogos**?
  - **Métricas:** precision@k (k=5/10) com julgamento de relevância (rubrica humana num conjunto pequeno de
    consultas); opcionalmente concordância por categoria/setor/tipo de evento como proxy automática.
  - **Baselines:** recuperação **aleatória** e por **recência** (notícias mais recentes), para mostrar que os
    embeddings acrescentam valor sobre alternativas triviais.
  - **Ablação:** métrica de similaridade (cosseno vs. outra) e modelo de embeddings (1 alternativo, se houver tempo).
- **Pergunta B — impacto medido (event-study):** o impacto associado aos precedentes é coerente e bem medido?
  - **Métricas:** retorno (anormal) médio a +1d/+3d/+5d; dispersão (desvio/IC); % de casos com direção consistente.
  - **Janela:** documentar a janela de estimação e a janela de evento (decisão nossa = parte da contribuição).
  - **Rigor:** estritamente pós-evento; sem usar o futuro além da janela; reportar variância entre eventos.

## 3. Motor de explicação (XAI)
- **Pergunta de avaliação:** a explicação é **fiel** à lógica real do sistema e **útil** ao investidor de retalho?
- **Fidelidade (faithfulness):** verificar que a explicação reflete de facto as entradas/regra/medida usadas
  (ex.: se a explicação cita um precedente, esse precedente foi mesmo o recuperado; se cita um fator SHAP, é o
  de maior peso). Verificação programática onde possível.
- **Utilidade:** **protocolo humano pequeno e honesto** — uma **rubrica** (ex.: clareza, completude,
  acionabilidade, 1–5) aplicada a **N exemplos** (ex.: 15–20 alertas) pelo aluno (e, se possível, 1–2 pessoas).
  Reportar média e exemplos; assumir a subjetividade como limitação.

## 4. Avaliação ponta-a-ponta (thin slice e sistema)
- **Smoke test:** o caminho completo corre e um alerta Telegram é enviado (teste automatizado — §8.1).
- **Estudo de caso qualitativo:** 2–3 episódios reais/históricos descritos ponta-a-ponta (evento → deteção →
  precedentes → explicação → alerta), como evidência demonstrável (à semelhança dos "Case Studies" das
  dissertações de referência).

## 5. O que NÃO avaliamos (fora de âmbito — §5.2)
- Não há previsão de preços nem trading → **não** se avalia "lucro", "accuracy de previsão" nem retornos de
  estratégia. O foco é deteção, qualidade de precedentes e qualidade das explicações.

> Referências metodológicas verificadas (ver `citation_log.md`): Chandola et al. 2009 (anomalias);
> Brown & Warner 1985 (event study); Reimers & Gurevych 2019 (embeddings); Lundberg & Lee 2017 (SHAP);
> Arrieta 2020 / Adadi & Berrada 2018 (XAI).
