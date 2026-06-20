# evaluation_design.md — Plano de avaliação por componente

> **Fase C.** Definir a avaliação ANTES de a correr (sem "pescar" bons números). Cada método defensável e explicável.

- **Detetor de anomalias:** precision/recall contra uma noção clara de "anomalia verdadeira"; explicitar a regra de rotulagem e os seus limites.
- **Motor de correlação / precedentes (núcleo):** qualidade da recuperação (os precedentes são mesmo análogos?) + impacto medido (event-study +1/+3 dias); incluir baseline (aleatório/recência) e pequena ablação (métrica/janela).
- **Motor de explicação (XAI):** noção clara de qualidade da explicação (fidelidade à lógica real; utilidade para o investidor); protocolo humano pequeno e honesto (rubrica em N exemplos).
- **Rigor:** sem lookahead; seeds fixas; reportar variância onde importa; um resultado modesto e honesto é válido.

*(A detalhar na Fase C.)*
