# Avaliação da guarda de ancoragem (camada de inteligência)

> Gerado por `scripts/evaluate_intelligence_guard.py` a 2026-08-11 00:28 UTC.
> Regenerável. Nenhum número deste ficheiro foi escrito à mão.

## ⚠️ Duas classes de número, e não se lêem da mesma maneira

Esta distinção existe porque metade destes números **reproduz exactamente** e a outra
metade **não**, e citar as duas como se fossem a mesma coisa seria afirmar uma
estabilidade que só uma delas tem.

| Classe | Quais | Reproduz? |
|---|---|---|
| **Determinística** | corpus de ataques, controlos | **Sim, exactamente.** A guarda é pura e o corpus é fixo: a mesma versão do código dá sempre o mesmo resultado. |
| **Amostrada** | secções geradas e conformes | **Não.** Dependem de quantos relatórios se geraram e do que o modelo escreveu nessa corrida. A **taxa** é a grandeza a citar; a contagem é da corrida. |
| **Invariante** | secções entregues com violação | **Tem de ser 0 em TODAS as corridas.** Não é uma estatística de amostra: é uma propriedade a verificar. Um valor diferente de zero é um defeito do caminho de entrega. |

## O que se mede, e porquê são três coisas

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

## Geração real (AMOSTRADA — ver a tabela das classes acima)

**Corrida única de 6 relatórios.** As contagens abaixo são desta corrida e
**não reproduzem exactamente**: o número de secções depende de quantos relatórios se
geram, e o que o modelo escreve varia entre chamadas. O que se deve citar é a
**taxa** — e o zero da última coluna, que é um invariante e não uma estatística.

| Relatórios | Secções | Conformes | Taxa | Entregues com violação |
|---|---|---|---|---|
| 6 | 27 | 27 | 1.000 | **0** |

Latência mediana do relatório: **1.6 s**.

Origem do texto: `{'groq': 3, 'groq+guarded': 3}`.

Motivos de rejeição observados: `{'aconselha': 3, 'afirma causa': 1}`.

> A coluna **entregues com violação** tem de ser zero **em todas as corridas**, por
> construção: uma secção que a guarda rejeita é substituída pela composição
> determinística antes de chegar ao ecrã. **Esta métrica é circular** — o mesmo
> verificador decide e avalia. É por isso que o corpus de ataques existe ao lado.

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
