# Protocolo de aceitação do retreino — fixado antes de existir candidato

Data: 2026-09-04. Fixa o passo 3 de [`RETREINO_CONTROLADO.md`](RETREINO_CONTROLADO.md).

> **Porque é que este documento existe antes do candidato.** Um critério escrito depois de ver
> um resultado não é um critério: é uma descrição do resultado. Os limiares abaixo foram
> fixados a partir da dimensão da janela e do cálculo de potência, **sem nenhum modelo treinado
> e sem nenhuma métrica de candidato observada**. Baixá-los depois aparece no diff.

## 1. As datas, e o que elas deixam de fora

Defesa e artigo a **27/09/2026**, decidido pelo autor a 2026-09-04.

| | |
|---|---|
| Início da recolha de classe A | 2026-09-04 |
| Resultados congelados | ~2026-09-22 (deixa cinco dias para integrar em tese, figuras e slides) |
| Horizonte do rótulo | 3 dias de bolsa (`--primary-horizon 3`), ~5 de calendário |
| Última data de notícia rotulável | **~2026-09-17** |
| Dias de bolsa na janela | **10** |

## 2. O que a janela rende — medido, não estimado

Com a decisão R1 aplicada, um ciclo real registou **691 candidatas com *snapshot***, e a
distribuição por data de notícia dá o regime permanente: **~150 a 240 candidatas por dia** nos
dias completos, contra as **28** que o esquema anterior capturava.

**Mas o que conta não são as linhas.** O rótulo é o retorno anormal por `(ticker, dia)`, logo
todas as manchetes da mesma empresa no mesmo dia partilham o mesmo desfecho por construção. A
lição já custou uma correção a este projeto (sessão 55: 530 linhas eram 145 unidades).

> **12 empresas × 10 dias de bolsa = 120 unidades independentes.**

É esse o tamanho real do bloco de comparação, e não os milhares de linhas.

## 3. O cálculo de potência, que é o que decide o protocolo

Bootstrap de cluster por `(ticker, dia)`, 120 clusters, prevalência 0,38, score sem sinal:

> **meia-largura do IC 95% da ROC-AUC = 0,074.**

Ou seja, **só uma diferença acima de ~0,15 seria distinguível do acaso**. Para contexto, o
modelo atual mede **0,486** contra um acaso de **0,500**. Uma melhoria de 0,15 em ROC-AUC não é
um ajuste: seria uma mudança de natureza do sinal.

**Conclusão, escrita antes de haver candidato: esta janela não consegue sustentar a afirmação
«o candidato bate o modelo atual».** Nenhum resultado que apareça a 22/09 deve ser lido assim,
por mais favorável que pareça, porque o intervalo contê-lo-á.

## 4. O que a janela CONSEGUE sustentar, e é uma contribuição nova

A pós-validação publicada (ROC-AUC `0,486`, IC `[0,403; 0,571]`, ch5:1329) foi medida sobre
**239 pares empresa-dia que já tinham atravessado as portas**. Nunca foi medida sobre a
população que o modelo teria de triar se fosse ele a triar.

A decisão R1 dá essa população pela primeira vez. Portanto o resultado a produzir é:

> **Como é que o modelo implantado ordena a população real de candidatas, incluindo as que as
> portas elementares removem antes de ele ser invocado?**

Isto ataca diretamente a fraqueza que a dissertação já declara — quando o modelo é invocado, os
filtros elementares já removeram grande parte do que ele foi treinado para remover — e é a
medição que faltava para a fechar. **É avaliação, não retreino**, e não depende de haver dados
suficientes para treinar.

## 5. Regra de aceitação, pré-registada

Se ainda assim se treinar um candidato, a comparação é **emparelhada, no mesmo bloco temporal**,
contra **duas** referências e não uma:

1. o **modelo atual** (`triage_context_lr.joblib`, sha256 no `model_info` de cada linha);
2. a **linha de base de volatilidade** — que é quem ganha na dissertação, e por isso é a
   referência que interessa.

Métricas: **PR-AUC**, **Brier** e **ROC-AUC**, todas com **bootstrap de cluster por
`(ticker, dia)`**. Intervalos marginais não bastam; a comparação é de diferenças emparelhadas.

**O candidato só é promovido se as três condições valerem ao mesmo tempo:**

| # | Condição |
|---|---|
| A | O IC 95% da diferença emparelhada de PR-AUC contra o **modelo atual** exclui zero. |
| B | O IC 95% da diferença emparelhada de PR-AUC contra a **volatilidade** exclui zero. |
| C | O Brier não piora, e o esquema de features do candidato está registado no manifesto. |

Mínimo de dados para sequer avaliar: **≥ 80 clusters `(ticker, dia)` com rótulo maturado** e
**≥ 2 empresas em cada classe**. Abaixo disso o relatório diz «bloco insuficiente» e não emite
métrica de comparação — pela mesma razão que o `analyse_usefulness.py` se recusa a correr
abaixo de N=8.

## 6. Se o candidato perder

**O modelo atual permanece ativo e o resultado negativo é reportado.** Não se retreina até
ganhar, não se muda o critério, não se escolhe o bloco. Esta linha é a mesma que o plano final
já escreve, e está aqui repetida porque é a que mais tentação dá a três semanas da entrega.

Um resultado negativo aqui é coerente com o resto da dissertação, que já reporta três casos em
que a técnica mais simples ganhou. Um quarto não a enfraquece.

## 7. O que continua fora deste protocolo

- **Registar antes das portas não torna a população completa.** O filtro de relevância continua
  a montante e deita fora ~67% das manchetes; o que a decisão R1 recuperou foram as candidatas
  relevantes que o ciclo não escolhia, não as que a relevância rejeita.
- **A comparação mantidas vs suprimidas continua irrecuperável** nesta janela (R2: `kept`
  constante). O `stage` substitui-a, e é uma variável diferente — diz onde a candidata morreu,
  não se a porta acertou.

---

## 8. Correção do calendário e a regra que decide o que é treinável — 2026-09-04

### As duas datas não são a mesma coisa

O autor esclareceu: **27/09 é o prazo de submissão do DOCUMENTO**; a **defesa** (apresentação)
é em **outubro**.

Isto **não alarga** a janela útil — aperta-a, e por uma razão melhor do que a que eu tinha
assumido. Qualquer resultado que entre na dissertação tem de estar congelado antes de 27/09.
Os dias de outubro servem para a apresentação, não para o documento.

**O dimensionamento da secção 1 mantém-se, e o cálculo de potência da secção 3 também.** Nada
do que está pré-registado muda.

O que os dias extra permitem, e é legítimo: à data da defesa o sistema terá recolhido bastante
mais, e a apresentação pode dizer *«continuou a correr, e sobre uma janela maior o número é
este»*. É um acrescento oral sobre um documento cujo resultado ficou fechado a 27/09 — não uma
segunda versão do resultado.

### ⚠️ A regra que decide o que é treinável, e sem ela o retreino nascia viciado

Medido no registo real a 2026-09-04, sobre 977 linhas com *snapshot*:

| Etapa | `as_of` − `news_date` | Treinável? |
|---|---|---|
| `not_latest` | −1 a 0 dias | **Sim** |
| `sobreviveu` | −2 a −1 dias | **Sim** |
| `stale` | **+1 a +107 dias** | **Não** |

`score_latest` usa a **última barra disponível**. Para uma manchete fresca isso é a véspera ou
o próprio dia — a assimetria que a dissertação já declara. Para uma manchete de há dias, as
entradas passam a descrever um mercado **que já viu o desfecho** que o rótulo mede em
`(data, data+3]`. São **430 das 977 linhas**, e pareciam material de treino.

O defeito entrou pela porta que a decisão R1 abriu: registar toda a candidata relevante trouxe
também as velhas. O `as_of` é o que o torna detectável — foi para isto que o *snapshot* o
guarda.

**Fechado no ponto de escrita, e não por filtro a jusante:** as candidatas `stale` deixam de ser
pontuadas. A linha continua a ser registada, porque o funil precisa dela, mas sem `prob` e sem
`feature_snapshot`. Filtrar depois deixaria no ficheiro um *snapshot* que nunca pode ser usado, e
a auditoria contá-lo-ia como classe A.

**Regra para qualquer treino ou avaliação:** usar apenas linhas com `feature_snapshot.as_of`
**anterior ou igual** à data da notícia. As linhas anteriores a esta correção que tenham
`as_of` posterior ficam no registo como histórico e **não entram** em nenhum conjunto.
