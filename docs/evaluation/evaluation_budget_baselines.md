# evaluation_budget_baselines.md — o chão da precisão@orçamento

> Gerado por `scripts/evaluate_budget_baselines.py`. **Não editar à mão.** Sementes fixas (0–39); re-correr sobre o mesmo dataset reproduz.

- Bloco de teste: **32649** linhas · **221** dias · prevalência **0.3781**
- Orçamento: **5** alertas/dia · métrica: `precision_at_daily_budget`
- Porta de reprodução: o modelo só-contexto dá **0.6317** contra o congelado **0.632** ⇒ mesmo protocolo.

## 1. O achado

O ficheiro de teste está ordenado por `(date, ticker)`: **True**. Com o score constante de `alertar-sempre`, o `argsort` estável não ordena nada — devolve a ordem do ficheiro. O chão publicado não escolhe ao acaso, escolhe por **ordem alfabética**.

Das **1105** linhas que ele selecciona, **1105** são de **AAPL** (100%), o nome alfabeticamente primeiro.
A taxa-base do AAPL no teste é **0.1831** — abaixo da prevalência global de 0.3781, e é essa a origem do número.

## 2. As quatro ordenações

| ordenação | precisão@5 | o que é |
|---|---|---|
| alertar-sempre (chão publicado) | **0.1629** | ordem alfabética do ticker, não uma escolha cega |
| aleatória, 40 sementes | **0.3790** ± 0.0170 | o que "às cegas" quer dizer |
| prior de volatilidade por ticker (só treino) | **0.6624** | 13 constantes, sem manchete e sem modelo |
| modelo só-contexto (implantado) | **0.6317** | o congelado |

## 3. Leitura

1. **O ganho reivindicado encolhe.** Contra um chão que escolhe mesmo às cegas, a triagem sobe de 0.379 para 0.632 — um factor de **1.67×**, não de 3.9×. O ganho continua a existir e continua a ser real; o que era falso era a sua dimensão.
2. **Uma tabela de 13 constantes bate o modelo treinado** (0.662 vs 0.632) nesta métrica. É a terceira vez que o método simples ganha neste trabalho, depois do z-score contra o Isolation Forest e da volatilidade contra o texto — e é coerente com o que já se sabia: o score do modelo é dominado por `vol20`.
3. **A prevalência é 0.3781 e o aleatório dá 0.3790.** Coincidirem é a verificação de sanidade da própria métrica: seleccionar ao acaso tem de render a taxa-base.

## 4. O que isto NÃO diz

- **Não invalida** o PR-AUC, o ROC-AUC nem o Brier da linha `alertar-sempre` (0.378 / 0.500 / 0.622). Essas três não dependem da ordem entre empates; só a coluna da precisão@orçamento depende.
- **Não altera** o resultado negativo da RQ4 (nenhum modelo com texto bate a volatilidade). Esse não passa por esta métrica.
- **Não diz** que o prior por ticker deva ser implantado: 5581 linhas de teste pertencem a nomes sem prior no treino e receberam a mediana global, e um prior estático não reage a nada. O que ele mostra é o custo de comparar contra o chão errado.
