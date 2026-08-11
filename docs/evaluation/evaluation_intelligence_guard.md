# Avaliação da guarda de ancoragem (camada de inteligência)

> Gerado por `scripts/evaluate_intelligence_guard.py` a 2026-08-11 00:14 UTC.
> Regenerável. Nenhum número deste ficheiro foi escrito à mão.

## O que se mede, e porquê são duas coisas

- **Corpus de ataques** — mede a GUARDA contra texto adversário conhecido.
- **Controlos** — mede se a guarda deixa passar o texto FIEL. Sem eles, uma guarda
  que rejeitasse tudo obtinha 100% no corpus e parecia perfeita.
- **Geração real** — mede o MODELO (com que frequência escreve texto conforme) e
  verifica que nenhuma secção com violação é ENTREGUE.

## Corpus de ataques

| Ataques | Bloqueados | Taxa |
|---|---|---|
| 23 | 23 | 1.000 |

| Controlos (texto fiel) | Passaram | Taxa |
|---|---|---|
| 8 | 8 | 1.000 |

Nenhum ataque do corpus escapou.

## Geração real

| Secções geradas | Conformes | Taxa | Entregues com violação |
|---|---|---|---|
| 27 | 27 | 1.000 | **0** |

Latência mediana do relatório: **1.52 s**.

Origem do texto: `{'groq': 2, 'groq+guarded': 3, 'gemini+guarded': 1}`.

Motivos de rejeição observados: `{'aconselha': 3, 'limits': 1, 'afirma causa': 1}`.

> A coluna **entregues com violação** tem de ser zero por construção: uma secção
> que a guarda rejeita é substituída pela composição determinística antes de
> chegar ao ecrã. **Esta métrica é circular** — o mesmo verificador decide e
> avalia. É por isso que o corpus de ataques existe ao lado dela.

## Risco residual declarado

```
Risco residual desta guarda, depois do red team de seis lentes (114 ataques, 21 reproduzidos):

1. RELEVÂNCIA DA ÂNCORA. Verifica-se que o facto citado EXISTE e que os números da frase são
   dele. Não se verifica que o facto SUSTENTA a afirmação em linguagem natural. Uma frase
   pode citar um facto verdadeiro e caracterizá-lo mal sem usar números.
2. PARÁFRASE. A defesa linguística é uma blocklist, e uma blocklist de linguagem natural
   perde sempre no limite. É por isso que o alerta empurrado usa a allowlist do narrador e
   este caminho não: aqui o texto aparece ao lado da evidência e o utilizador pode abri-la.
3. QUALIFICADORES. "unusually large", "relatively rare" são juízos sem número. Ficam
   permitidos porque proibi-los tornaria o texto ilegível; são verificáveis pelo leitor
   contra o facto citado ao lado.
4. OMISSÃO. Nada obriga o gerador a mencionar um facto desfavorável. A composição
   determinística cobre isto por construção; o texto gerado não.
```
