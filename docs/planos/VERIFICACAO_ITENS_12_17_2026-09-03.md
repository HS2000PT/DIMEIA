# Verificação dos itens 12–17 da matriz — evidência ficheiro a ficheiro

Data: 2026-09-03. Executa a «próxima ação» de
[`REVISAO_PRIORITARIA_ANEXOS.md`](REVISAO_PRIORITARIA_ANEXOS.md): aprofundar os itens 12 a 17.

**O que esta passagem é.** Inspeção de código e artefactos congelados, mais uma medição nova que
não usa dados de produção nem toca no modelo ativo. **O que não é.** Não houve treino, deploy,
descarregamento de dados, alteração de números da tese nem recompilação do PDF. Nenhuma linha da
tese foi alterada; as correções propostas ficam listadas por localizar, para decisão.

Estados usados: **A — confirmado agora** (input identificado, verificação corrida nesta
passagem); **B — histórico rastreável** (artefacto e origem existem, não reproduzidos hoje);
**C — insuficiente**.

## Resumo

| Item | Veredicto | Estado |
|---|---|---|
| 12 | Ambos os números existem, mas são **artefactos diferentes** e não podem ser reunidos numa frase. Dois defeitos menores encontrados na tese. | A |
| 13 | Anexo a corrigir, e agora com o número que o fecha: a capacidade de ordenação **foi** medida e não se distingue do acaso. | A |
| 14 | Nove entradas: confirmado. «Sete estáticas»: errado — são cinco. A formulação correta é **mais forte** do que a do anexo. | A |
| 15 | À letra falso, na substância correto — e passa aqui de afirmação a **medição**. | A |
| 16 | Confirmado nos números; a inferência do anexo («prova bug do ciclo») é errada e o defeito real já está diagnosticado e corrigido na tese. | A |
| 17 | Confirmado, com um âmbito que muda a leitura: os dezanove dias são do ciclo de maturação, não da entrega de alertas. | A |

---

## Item 12 — «0,486; amplitudes 0,072 e 0,392»

**São três números de duas medições distintas.** A matriz avisava para conferir artefactos,
períodos e denominadores antes de os reunir. Conferidos, não se podem reunir.

| | Amplitudes | Capacidade de ordenação |
|---|---|---|
| Valor | dentro `0,072` · entre `0,392` · razão `5,4×` | ROC-AUC `0,486`, IC `[0,403; 0,571]` |
| Mede | dispersão da pontuação | capacidade de separar material de não material |
| Denominador | 36 925 decisões pontuadas | 239 pares empresa-dia independentes (de 825 decisões maturadas) |
| Período | 2026-07-22 a 2026-08-20 | decisões maturadas até à leitura |
| Fonte | `origin/alerts-history:predictions_log.jsonl`, piso 0,5 | registo de pós-validação |
| Artefacto | `docs/evaluation/evaluation_gate_selectivity_unicos.md` | `tese-v2/ch5/chapter5.tex:1325–1335` |
| Na tese | `ch5:1194–1196` | `ch5:1329` |

Uma frase que os junte afirma uma relação entre uma dispersão e uma discriminação, medidas em
janelas, unidades e denominadores diferentes. Cada um é defensável sozinho.

### Dois defeitos encontrados na tese

1. **O denominador dos 48% não está escrito em lado nenhum.** `ch5:1210–1212` diz «contada uma
   vez por título distinto, sobre uma janela mais ampla de $36\,925$ decisões, a fração é de
   $48\%$». Os 48% são sobre **982 títulos distintos**; as 36 925 são as decisões dessa janela.
   O artefacto tem os dois números (`evaluation_gate_selectivity_unicos.md`, secção 2); a tese
   só tem um, e é o do outro denominador. Um arguente que pergunte «48% de quê?» não encontra o
   número na tese. Verificado: `982` não ocorre em `ch4` nem em `ch5`.
   **Correção mínima:** nomear os 982 títulos distintos na frase.
2. **A distinção entre as duas contagens é feita duas vezes.** `ch5:1194–1200` e `ch5:1207–1213`
   dizem a mesma coisa por outras palavras. Candidato de corte limpo (~9 linhas) para a frente
   de redução, sem perder protocolo, comparador nem limitação. A frase «Cita-se a primeira» em
   `ch5:1198` fica sem antecedente claro quando o segundo parágrafo desaparece — reescrever.

---

## Item 13 — «Mudar o nome para *ranking* salva o componente»

**Não salva, e o número que o fecha já está na tese.** A ordenação não é uma capacidade por
medir a que se possa recuar: **foi medida, sobre a população que o modelo efetivamente observa
em produção**, e o resultado é ROC-AUC `0,486` com intervalo `[0,403; 0,571]`, num intervalo em
que o acaso vale exatamente `0,500` (`ch5:1325–1335`). Repetida com 825 decisões maturadas
contra as 530 da primeira leitura, passou de `0,494` para `0,486` e o intervalo encolheu.

Renomear a porta para ordenação troca a palavra, não a medição. A leitura correta continua a ser
a que a tese já faz: esta amostra não distingue o modelo do acaso, o que não é o mesmo que
provar ausência de benefício.

⚠️ **Uma afirmação a manter fora da tese.** A secção 4 de
`evaluation_gate_selectivity_unicos.md` diz que a pontuação «serve para ordenar entre empresas,
que é para o que tem informação». Essa utilidade **não está medida em lado nenhum**. Verificado
que ainda não migrou para o corpo (`ch4`/`ch5` não a contêm). Não deve migrar sem medição.

---

## Item 14 — «Nove entradas, sete estáticas, tabela de consulta»

| Afirmação do anexo | Verificação |
|---|---|
| Nove entradas | **Confirmado.** `investigator/triage/features.py:17–18`: quatro numéricas (`vol20`, `mom5`, `ret_event`, `headline_len`) mais os cinco indicadores de setor. Vetor montado em `infer.py:100–105`. |
| Sete estáticas | **Errado. São cinco.** Estáticos por ticker são apenas os indicadores de setor. `headline_len` varia com cada notícia; `vol20`, `mom5` e `ret_event` são recalculados da série de preços a cada dia. |
| Sem *embedding* | **Confirmado** para o caminho implantado: a produção usa a variante só-contexto (`infer.py:1–11`), porque o modelo com texto exige o codificador SBERT, que não corre nessa configuração. |
| «Tabela de consulta» | Metáfora, não descrição literal. O modelo é uma regressão logística calibrada e a sua saída muda ao longo do tempo. |

**A formulação correta é mais forte do que a do anexo, e é esta:** fixados o ticker e o dia,
**oito das nove entradas são constantes**, e a nona é o número de caracteres do título. Dizer
«sete estáticas» é ao mesmo tempo inexato e mais fraco do que o que se passa.

---

## Item 15 — «Dez notícias recebem exatamente o mesmo score»

**À letra é falso; na substância é correto — e deixa de ser inferência.** Foi medido nesta
passagem, contra o artefacto congelado do modelo, sem dados de produção:

| O que varia, com tudo o resto igual | Amplitude da probabilidade calibrada |
|---|---:|
| A manchete (20 → 200 caracteres) | `0,0064` |
| O setor | `0,1612` (25×) |
| A volatilidade diária (1% → 4%) | `0,2016` (31×) |

**Entre duas notícias da mesma empresa no mesmo dia, a pontuação não pode diferir mais do que
0,6 pontos percentuais, e o que as separa é o comprimento do título, não o seu significado.**

- Script: `scripts/check_headline_sensitivity.py` (novo) · Artefacto:
  `docs/evaluation/sensibilidade_headline.md` (novo) · Entrada: `models/triage_context_lr.joblib`,
  sha256 `2432e44e95417222…`.
- Reproduzível em qualquer máquina com o repositório; não lê registos de produção, não treina,
  não altera o modelo ativo nem nenhum número da tese.
- ⚠️ Correu num ambiente com scikit-learn 1.8.0 e o artefacto foi gravado com 1.9.0. Os
  coeficientes são matrizes simples e a inferência é determinística, mas **o número a citar deve
  ser o da execução no venv do projeto**. Correr `python scripts/check_headline_sensitivity.py`
  antes de qualquer utilização na tese.

Isto é o mecanismo, medido no artefacto, do que
`evaluation_gate_selectivity_unicos.md` observa nos registos: a amplitude média dentro de cada
empresa é `0,072`, e a maior parte dela vem de a volatilidade mudar de dia para dia.

Nota de âmbito, para não sobre-afirmar: isto **não** demonstra que dez mensagens foram enviadas.
As portas e o orçamento diário decidem entregas, e a afirmação do anexo sobre «poluir o canal»
continua por reproduzir no comportamento real.

---

## Item 16 — «333 aprovações e cinco entregas provam um bug do ciclo»

**Os números estão certos; a inferência não.** Ambos são do dia 2026-08-15
(`docs/evaluation/funil_por_porta.md`), citados na Figura `fig:sis_funil`
(`tese-v2/ch4/chapter4.tex:366–405`):

- `333` = **avaliações** que atravessaram todas as portas, e o sistema reavalia os mesmos
  títulos de 60 em 60 segundos;
- `5` = **mensagens entregues**, que é o orçamento diário.

Não são a mesma unidade, e a própria figura o diz (`ch4:396`: «5 mensagens entregues ≠ 333
passagens pelas portas»).

O defeito real existiu e é de **instrumentação**, não do ciclo de entrega: a verificação de
duplicação impedia o reenvio no fim mas, ao contrário de todas as outras, não estava registada
como etapa, pelo que a vista de inspeção mostrava aprovações que nunca seriam entregues. Está
escrito em `ch4:408–418`, já corrigido, e com um teste automático que falha caso a etapa volte a
ser omitida. Os dias 19, 20 e 21 de agosto já mostram a etapa «Já avisei hoje» com identificação
própria.

**Nada a alterar na tese.** O item fecha como resolvido antes de ter sido levantado.

---

## Item 17 — «Interrupção de 19 dias»

**Confirmado, e o âmbito muda a leitura.** `ch4:723–728`: o que esteve interrompido durante
dezanove dias, sem registo de erro, foi o **ciclo de maturação da base de casos** — a atualização
da evidência exibida —, e não a entrega de alertas. Causa: os dois processos correm em máquinas
cujo sistema de ficheiros é reinicializado a cada arranque, e os ficheiros intermédios de
maturação não estavam a ser publicados no repositório de dados. A tese classifica-o como
dependência de dados não declarada, na aceção de Sculley et al. (2015), e o capítulo de
conclusões retoma-o como limitação.

**Não dizer** «dezanove dias sem alertas». A afirmação verdadeira é mais estreita e continua a
ser um bom caso de MLOps.

**Fica pendente**, e não é verificável a partir do repositório: se a correção está ativa em
produção e se existe monitorização que apanhasse uma repetição. Exige inspeção do sistema no ar.

---

## O que fica pendente destes seis itens

| # | Pendência | Quem |
|---|---|---|
| 12 | Nomear os 982 títulos distintos em `ch5:1210–1212`; cortar a repetição de `ch5:1207–1213` | frente de escrita |
| 15 | Correr o script no venv do projeto e fixar o número antes de o citar | uma execução |
| 15 | Reproduzir o comportamento real de entregas (a alínea «poluir o canal») | inspeção do sistema no ar |
| 17 | Confirmar correção ativa e monitorização em produção | inspeção do sistema no ar |
