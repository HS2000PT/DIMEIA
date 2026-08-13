# evaluation_similarity_floor.md — o chão de similaridade compra alguma coisa?

> Gerado por `scripts/evaluate_similarity_floor.py` (ADITIVO). Semente 42; 1500 consultas × top-10. **Não editar à mão.**

- Corpus: **79553** registos com impacto a +5 dias e embedding.
- Protocolo: vizinho de **outra** empresa e **estritamente anterior** à consulta.
- Utilidade = **concordância de direcção** do impacto a +5 dias.
- **Chão de acaso medido: 0.5069** (emparelhamento aleatório sob as mesmas restrições). Não é 0,5, e assumir que era teria enviesado tudo.

## Concordância de direcção por faixa de cosseno

| cosseno | pares | concordância | IC 95% |
|---|---|---|---|
| 0.00–0.30 | 50 | **0.6200** | ±0.1345 |
| 0.30–0.40 | 658 | **0.4878** | ±0.0382 |
| 0.40–0.45 | 900 | **0.5122** | ±0.0327 |
| 0.45–0.50 | 1308 | **0.5092** | ±0.0271 |
| 0.50–0.60 | 3295 | **0.5041** | ±0.0171 |
| 0.60–1.01 | 8789 | **0.5038** | ±0.0105 |

## O chão actual (0.45)

| lado | pares | concordância |
|---|---|---|
| cosseno ≥ 0.45 | 13392 | **0.5044** |
| cosseno < 0.45 | 1608 | **0.5056** |
| diferença | — | **-0.0012** (±0.0259) |

## Veredicto

⚠️ **A similaridade não separa.** A diferença entre estar acima e abaixo do chão é -0.0012 com intervalo a incluir zero, e a coluna da concordância não sobe de forma monótona com o cosseno. Sobre este corpus, **o chão de 0.45 não está a comprar concordância de direcção**.

Isto **não** quer dizer que o chão seja inútil: ele também controla o *volume* de alertas, e a coerência **temática** que um leitor vê não é a mesma coisa que a concordância de direcção — a tese já mede e afirma que a recuperação capta **tema, não direcção** (Caso 3). Quer dizer que a justificação honesta do 0,45 é *controlo de volume e coerência temática*, e **não** que os precedentes acima do chão predizem melhor o que se seguiu.

## O que isto NÃO diz

- Não mede se o precedente **ajuda um humano** a decidir: isso é o estudo de utilidade.
- A concordância de direcção é uma medida de utilidade entre várias; um precedente pode ser útil por enquadrar o tema mesmo quando a direcção diverge.
- O corpus é o FNSPID (2018–2023). A KB viva é curta demais para esta medição.

⚠️ **Não comparar o número desta página com o `0.708` do Caso 3.** São medidas diferentes com chãos de acaso diferentes, e pô-las lado a lado seria o erro que este projecto já cometeu uma vez ao comparar purezas com cardinalidades diferentes. O Caso 3 mede a **coerência interna do conjunto recuperado** (que fracção do cluster se move no mesmo sentido), cujo chão de acaso é ~0,69 porque uma maioria é ≥0,5 por construção. Aqui mede-se a concordância **par a par entre o precedente e a consulta**, cujo chão é ~0,5 — e medido, 0.5069. As duas dizem a mesma coisa por caminhos distintos: a recuperação capta tema, não direcção.
