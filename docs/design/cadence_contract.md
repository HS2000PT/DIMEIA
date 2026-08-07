# cadence_contract.md — O que o InvestiGator promete enviar (e nunca enviar)

> **Estado:** v1, 2026-07-29. Documento de produto, não de avaliação.
> Acompanha `config/alerts.yaml`; qualquer alteração de gate tem de se refletir aqui.

## Porque é que este documento existe

Até aqui a cadência do canal **emergia** de quatro gates independentes espalhados pelo
runner — limiar de mercado `1.5`, chão de similaridade `0.45`, teto `2/ticker/dia` e gate de
materialidade `0.5`. Nenhum deles é errado, mas juntos produziam um comportamento que
**ninguém, nem o autor, conseguia enunciar numa frase**. É a raiz de duas queixas reais:
"o conteúdo dos alertas é mau" e "isto está dessincronizado do mundo".

Um utilizador não consegue confiar num canal cujo silêncio é ambíguo. Se não souber o que o
sistema promete, não sabe se o silêncio significa "está tudo calmo" ou "está partido".

---

## A promessa

**Todos os dias úteis, mesmo que não aconteça nada, recebes pelo menos uma mensagem.**
É o que torna o silêncio legível: se não chegou nada, algo está avariado — não é calmaria.

| Quando | O quê | Garantido? |
|---|---|---|
| Abertura US (~14–15 UTC) | Como a watchlist abriu vs o fecho de ontem | **Sim**, 1×/dia útil |
| Fecho US (≥21 UTC) | Resumo do dia: movimentos e anomalias | **Sim**, 1×/dia útil |
| Durante a sessão | Movimento abrupto (z-score fora de ±1,5) | Só quando acontece |
| Durante a sessão | Notícia relevante com precedente forte | Só quando acontece |

## O que NUNCA é enviado

1. **Previsões de preço.** Nem direção, nem alvo, nem "vai subir". Restrição fundadora,
   não uma opção de configuração.
2. **Conselho de investimento.** Nada de comprar/vender/manter. O sistema descreve o que
   observou e o que aconteceu em casos passados semelhantes.
3. **Previsões de terceiros.** Price targets e recomendações de analistas ficam **de fora
   por princípio**: importar a previsão de outra pessoa para um sistema que se define por não
   prever seria auto-contradição.
4. **Mais de 2 alertas de notícia por ticker por dia.** Teto rígido contra fadiga.
5. **Alertas sem evidência.** Sem um precedente com cosseno ≥ 0,45, não há alerta — mesmo
   que a notícia pareça importante. Preferimos calar do que parecer aleatório.
6. **A mesma notícia duas vezes.** Dedup por chave partilhada entre produtores (VM + Actions).

---

## Os gates, por ordem, e o que cada um custa

Uma notícia atravessa cinco filtros. A medição ao vivo de 2026-07-29 (10 tickers, uma
varredura) mostra onde morrem — e as margens são apertadas:

| # | Gate | Constante | Onde vive | Efeito medido |
|---|---|---|---|---|
| 1 | Relevância (menção à empresa, sem boilerplate) | — | `news_fetcher/relevance.py` | mata manchetes mal etiquetadas |
| 2 | Frescura (notícia ≤ N dias) | `max_age_days: 2` | `run_alerts.py` | anti-repetição |
| 3 | Chão de similaridade | `min_similarity: 0.45` | `config/alerts.yaml` | **7 de 10 tickers** |
| 4 | Triagem aprendida | `min_materiality: 0.5` | `config/alerts.yaml` | **2 de 10 tickers** |
| 5 | Teto + dedup | `max_per_ticker_per_day: 2` | `config/alerts.yaml` | anti-fadiga |

**As margens (mesma varredura):** MSFT 0,42 · NFLX 0,41 · GOOGL 0,44 · META 0,44 contra um
chão de 0,45. AAPL P=0,43 e NVDA P=0,48 contra um gate de 0,50. **Quatro tickers falham por
≤0,04.** Estas constantes estão a fazer quase todo o trabalho de filtragem e, até agora,
nunca tinham sido medidas contra a distribuição real.

O funil acumula em `gate_log.jsonl` (ver `investigator/gate_log.py`), por isso a tabela acima
deixa de ser um instantâneo e passa a ser uma série.

---

## De onde vem cada número

- **`min_materiality: 0.5`** — deixou de ser arbitrário. `docs/evaluation/evaluation_policy_sweep.md`
  mostra que corresponde a um **rácio de custo implícito ≈ 0,9**: o sistema assume que perder
  um movimento real custa quase o mesmo que incomodar com um falso alarme. Sob custos iguais
  (R=1) o limiar ótimo é 0,49 — ou seja, o 0,5 estava quase certo, mas agora é **derivado e
  discutível** em vez de adivinhado.
- **`threshold: 1.5`** (mercado) — decisão de implantação, divulgada, distinta do 3,0
  congelado que a tese avalia. Compensada por níveis de severidade no texto do alerta.
- **`min_similarity: 0.45`** e **`max_per_ticker_per_day: 2`** — ainda **postos à mão**.
  São a próxima coisa a derivar. Declarado aqui em vez de escondido.

---

## Latência: o que é honesto prometer

O sistema **não** promete tempo real. Promete o seguinte, e agora sabe medi-lo
(`HistoryEntry.event_at → sent_at`, ver `investigator/alerts_history.py`):

Até 2026-07-29 o sistema **não conseguia produzir um único número de latência**, nem
retroativamente: só guardava a data ao dia e descartava a hora exata de publicação que o
Finnhub devolve. Passou a guardá-la. As afirmações de latência assentam em medição,
não em estimativa.

⚠️ **Esta secção tinha uma tabela que prometia "~1 min" para o ciclo de 60 s, e a promessa era
minha, não uma medição.** Medida a 2026-08-07 sobre 101 alertas entregues
([`evaluation_latency.md`](../evaluation/evaluation_latency.md)):

| componente | mediana | de quem é |
|---|---|---|
| publicação → deteção | ~158 min | da fonte (limite inferior) |
| deteção → entrega | **~1 s** | nosso |
| **total, era do cron** (best-effort 1,5–2 h) | 196 min | — |
| **total, era do worker 60 s** | 143 min | — |

Encurtar o ciclo de 1,5–2 h para 60 s moveu a mediana **53 minutos**, não duas horas: o ciclo
nunca foi a restrição dominante. O que é honesto prometer é **"entregamos em segundos o que a
fonte nos dá"** — e não uma latência total, porque a maior parte dela não é nossa para prometer.

---

## O que muda quando um gate muda

Mexer numa constante muda a promessa. O procedimento é:

1. Alterar em `config/alerts.yaml` (ou via `settings_overrides` para ajuste ao vivo).
2. Atualizar a tabela deste documento.
3. Re-correr `scripts/evaluate_policy_sweep.py` se o gate for o de materialidade.
4. Registar a decisão e a data — o padrão já usado para `threshold 3.0 → 1.5`.

Os números **congelados** da tese (`docs/evaluation/evaluation_*.md`, `models/`) nunca mudam
com decisões de produto: a avaliação e a implantação são deliberadamente separadas, e é isso
que permite ajustar o produto sem invalidar a ciência.
