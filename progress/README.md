# `progress/` — continuidade entre sessões

Esta pasta existe por uma razão só: **o trabalho atravessa muitas sessões e mais do que uma
máquina**, e sem um sítio onde o estado fica escrito, cada sessão nova recomeça a perceber o
projecto do zero. Não é documentação do produto — isso vive em [`../docs/`](../docs/).

## O que está vivo

| ficheiro | para que serve |
|---|---|
| [`PLANO_V2.md`](PLANO_V2.md) | **O plano activo.** Duas pistas: a tese (aditiva, entrega 13/09) e a ambição de produto, que fica para depois da entrega. |
| [`TRACKER.md`](TRACKER.md) | Caixas por fase. É onde se marca o que ficou feito. |
| [`SESSIONS.md`](SESSIONS.md) | Registo por sessão. O histórico longo, em prosa. |
| [`DECISIONS.md`](DECISIONS.md) | As decisões com o **porquê** — o que se escolheu e o que se rejeitou. |
| [`BILINGUAL_PLAN.md`](BILINGUAL_PLAN.md) | Estado da paridade EN↔PT, capítulo a capítulo. |

> O estado mais recente **não** está aqui: está no [`../CLAUDE.md`](../CLAUDE.md), que é lido no
> início de cada sessão e actualizado no fim de todas, sem excepção.

## `_historico/` — planos superados

[`_historico/`](_historico/) guarda planos que já **não** dirigem trabalho nenhum. Estavam
misturados com os que estão vivos, e um plano superado ao lado de um plano activo é pior do que
não ter plano: as caixas por marcar nos superados incluem itens que foram **cortados por
decisão**, e alguém que os leia como pendências vai reconstruir coisas que se decidiu não fazer.

A cadeia de sucessão, do mais antigo para o actual:

```
MASTER_PLAN  →  PRODUCT_ROADMAP  →  PLANO_MELHORIAS  →  PLANO_V2  (activo)
```

**Não se apagam.** O `MASTER_PLAN` é onde estão as fases A–H que levaram a tese ao estado de
submissão, incluindo a Fase E (a porta de validação das citações), e as razões pelas quais cada
corte foi feito continuam a valer para a defesa. Um plano superado é registo, não lixo — a
diferença é só que deixou de dar ordens.
