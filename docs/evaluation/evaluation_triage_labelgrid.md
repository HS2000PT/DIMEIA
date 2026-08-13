# evaluation_triage_labelgrid.md — o negativo da RQ4 sobrevive à definição de rótulo?

> Gerado por `scripts/evaluate_triage_labelgrid.py` (ADITIVO; não altera congelados). Embedder **sbert**, seed 42. **Não editar à mão.**

As nove colunas de rótulo já eram escritas pelo `build_dataset.py` e nunca tinham sido lidas. Cada célula treina as três famílias que decidem a comparação, sob o mesmo split temporal, a mesma calibração de Platt e a mesma métrica do congelado.

- Porta de reprodução: a célula (τ=0.02, h=3) dá **vol 0.542**, **context 0.538**, **full 0.496** contra os congelados 0.542, 0.538, 0.496.

## A grelha (PR-AUC no teste)

| τ | h | prevalência | só-volatilidade | só-contexto | contexto+texto | vol ≥ full? |
|---|---|---|---|---|---|---|
| 0.015 | 1 | 0.277 | 0.449 | 0.449 | 0.420 | **sim** |
| 0.015 | 3 | 0.483 | 0.613 | 0.612 | 0.572 | **sim** |
| 0.015 | 5 | 0.597 | 0.716 | 0.718 | 0.689 | **sim** |
| 0.02 | 1 | 0.183 | 0.334 | 0.317 | 0.294 | **sim** |
| 0.02 | 3 | 0.378 | 0.542 | 0.538 | 0.496 | **sim** ← |
| 0.02 | 5 | 0.487 | 0.620 | 0.617 | 0.590 | **sim** |
| 0.03 | 1 | 0.082 | 0.228 | 0.214 | 0.174 | **sim** |
| 0.03 | 3 | 0.232 | 0.402 | 0.404 | 0.369 | **sim** |
| 0.03 | 5 | 0.324 | 0.489 | 0.485 | 0.461 | **sim** |

## Veredicto

A volatilidade bate ou iguala o contexto+texto em **9 de 9** células.

O negativo da RQ4 **não depende da definição de rótulo**: vale nas três amplitudes e nos três horizontes, com prevalências entre 0.082 e 0.597. A escolha (τ=0,02, h=3) deixa de ser um ponto de ataque.

## O que isto NÃO diz

- Não é uma re-avaliação do modelo implantado: as famílias são re-treinadas por célula, e o congelado continua a ser a célula (τ=0,02, h=3).
- Não corrige a dimensionalidade do bloco de texto (isso é o re-teste justo, `evaluation_triage_fairtext.md`); mede apenas a sensibilidade ao **alvo**.
