# mapa_competencias.md — o que esta dissertação demonstra, e onde está a prova

> ⚠️ **Este documento foi escrito para a tese longa em inglês.** A que vais defender é a
> tese curta em português (`tese/`), que tem **três QI** e não quatro RQ, e onde alguns
> números foram corrigidos. Lê o [`LEIA-ME-PRIMEIRO.md`](LEIA-ME-PRIMEIRO.md) antes de
> estudares por aqui.

> **Para que serve.** Numa defesa, a pergunta *"onde é que isto mostra engenharia de IA?"* aparece
> quase sempre, e a pior resposta possível é uma lista de tecnologias. Esta página liga cada
> competência a **um artefacto concreto e a um número**, para a resposta ser verificável em vez de
> declarativa.
>
> ⚠️ **Uma coisa que tens de completar tu.** Os nomes exatos das unidades curriculares do MEIA não
> estão registados no repositório, e **não os inventei**. As colunas abaixo descrevem **áreas de
> competência** evidenciadas pelo trabalho. Antes da defesa, abre o plano de estudos e escreve o
> nome real de cada UC na primeira coluna. Só três nomes aparecem nos registos do projeto e por
> isso só esses vão escritos: *Knowledge Engineering*, *ANN/Deep Learning* e *Privacidade/
> Segurança*.

---

## 1. O mapa

| Área de competência | O que o trabalho demonstra | Prova (artefacto) | Número |
|---|---|---|---|
| **Knowledge Engineering** | Taxonomia de tipos de evento construída sobre o corpus, com rubrica **pré-registada** e dois controlos de validade | `historical_kb/taxonomy.py`, Caso 5 | AMI evento **0.358** vs ticker 0.188 |
| **ANN / Deep Learning** | Embeddings de frase (Sentence-BERT) em recuperação semântica; export **ONNX int8** com paridade provada e SHA256 fixado | Cap. 3–4, `onnx_minilm_validation.md` | cosseno **0.992**; top-3 igual em 20/23 |
| **Privacidade / Segurança** | Controlo da cadeia de fornecimento (hash fixado ⇒ download corrompido falha **fechado**); nenhum dado pessoal recolhido; recusa explícita de carteira | Cap. 4, Cap. 6 §exclusões | — |
| **Aprendizagem supervisionada** | Modelo de materialidade treinado, calibrado (Platt) e testado sob protocolo temporal com embargo | `triage/`, Caso 4 | PR-AUC **0.542** vs 0.496 |
| **Avaliação e metodologia experimental** | Linhas de base pré-comprometidas; ablações; multi-seed; bootstrap por cluster; resultados negativos reportados | Cap. 3 §avaliação, Casos 1–8 | 5 seeds; IC 95% por cluster |
| **Quantificação de incerteza** | Predição conformal split com garantia livre de distribuição, testada sob permutabilidade **e** sob divisão temporal | `triage/conformal.py`, Caso 6 | cobertura **0.902** vs 0.90 nominal |
| **MLOps / ML em produção** | Deriva medida com PSI+KS e bandas convencionadas; gatilho de re-treino verificável; log de gates; pós-validação ao vivo | `evaluation/drift.py`, Caso 7 | PSI **0.281** (significativa) |
| **Linguagem natural e IA generativa** | **Geração ancorada**: o gerador vê um pacote de evidência onde cada facto declara a origem (`measured`/`computed`/`model`), escreve prosa e **nunca um facto**; cada número que escreve tem de pertencer ao facto que a **própria frase** cita, e a interface resolve cada `[f3]` de volta ao registo | `intelligence/context.py`, `guard.py`, Cap. 4 §4.8 | **23/23** ataques bloqueados · **8/8** controlos fiéis · **0** secções entregues com violação |
| **XAI** | Fidelidade **por construção** (o texto é composto dos mesmos objetos calculados) + guarda de allowlist para linguagem gerada, com red team como regressão | `explanation_engine/`, `narrator/` | **0** violações entregues; 21/21 exploits bloqueados |
| **Recuperação de informação** | Recuperação vetorial com protocolo cross-ticker e precision@k contra três linhas de base | `correlation_engine/`, Caso 2 | P@5 **0.595** à escala |
| **PLN** | Comparação de representações: léxico → estáticos → contextuais; benchmark de encoders medido, não argumentado | Cap. 2, `evaluation_retrieval_embedders.md` | MiniLM 0.514 > FinBERT 0.420 |
| **Estatística / séries temporais** | z-score deslizante sem lookahead; decomposição de dois fatores com **encolhimento de Vasicek**; EWMA vs rolling | `anomaly_detector/`, `decomposition.py` | amplitude **0.015** vs 0.344 |
| **Engenharia de software** | 709 testes, ruff, CI, pacote instalável, artefactos congelados byte-iguais | `tests/`, `.github/workflows/` | **600+** testes |
| **Ética e IA responsável** | Recusa de prever preços como restrição de desenho; quatro capacidades cortadas **por princípio** e justificadas | Cap. 6 §"Posições Assumidas por Exclusão" | 5 posições escritas |

---

## 2. As três respostas que valem mais do que a tabela

Se só houver tempo para três frases, são estas.

**"Onde está a engenharia de IA, em vez de utilização de IA?"**
> No que foi **medido para decidir**, não no que foi usado. Quatro capacidades foram construídas e
> depois **não** ligadas à produção, porque a medição não as sustentou: taxonomia de eventos,
> score de convergência, e as extensões de features. A engenharia está em ter um critério que
> consegue dizer não. **E o exemplo mais forte é contra mim próprio:** ao verificar o que a minha
> própria linha de base media, descobri que ela ordenava por ordem alfabética e não ao acaso, e
> **reduzi o ganho que a tese anunciava de ~4× para 1,67×** — mais um prior de treze constantes que
> bate o modelo treinado. Um critério que só valida não é um critério.

**"Qual é a contribuição, se os modelos são todos pré-existentes?"**
> A integração avaliada. Nenhum algoritmo é novo; o que é novo é um sistema que responde às três
> perguntas de um investidor de retalho a custo zero, com cada afirmação rastreável ao procedimento que a
> produz, e com os resultados negativos reportados tal como caíram.

**"E o resultado negativo da RQ4 não enfraquece a tese?"**
> Fortalece-a, e agora há um segundo caminho independente a dizer o mesmo: a predição conformal
> mostra que, para garantir 90% de cobertura, o modelo só decide em **39,5%** dos casos. Dois
> métodos diferentes, sem partilhar suposições, chegam à mesma conclusão sobre a força do sinal.

> ⚠️ **NÃO dizer "quadruplica".** Essa versão foi retirada a 2026-08-13. O número certo é
> **0,379 → 0,632, um factor de 1,67×**, contra uma ordenação aleatória; o `0,163` que a tese
> citava era o chão de "alertar-sempre", que com pontuação constante desempata pela ordem do
> ficheiro e portanto escolhe **alfabeticamente** (as 1.105 linhas que escolhia eram todas AAPL).
> E há mais: um **prior de volatilidade por ticker, treze constantes**, dá **0,662** — bate o
> modelo. A leitura honesta é que *ordenar por volatilidade* compensa, não que *aprender* compensa.

---

## 3. Onde estão os buracos (dizer antes que perguntem)

| Lacuna | Estado honesto |
|---|---|
| **Estudo humano de utilidade** | Protocolo pronto a correr, ainda não corrido. É a única linha em aberto do Cap. 6. |
| **Aprendizagem por reforço** | Não existe no trabalho. Não a reivindicar. |
| **Sistemas multi-agente** | Não existe, e a recusa está **escrita** no Cap. 6: um LLM com cinco ferramentas não é multi-agente. |
| **Visão computacional** | Fora de âmbito por natureza do problema. |
| **Treino de modelos de raiz** | Um modelo treinado (a triagem). Os embeddings são pré-treinados, e isso está declarado em todo o lado. |
| **A garantia da camada generativa é mais fraca do que a dos alertas** | E está escrito: o alerta empurrado usa **allowlist** de vocabulário fechado; o texto puxado usa **blocklist**, que sobre linguagem natural perde no limite. Quatro riscos residuais declarados em `guard.RESIDUAL` e no Cap. 6. |
| **O red team da guarda está incompleto** | **2 de 6 lentes** correram (as outras morreram num limite de gasto), pelo que a força medida é um **limite inferior** — e a tese diz isso. |

Dizer isto primeiro tira ao júri a pergunta de armadilha e transforma-a numa demonstração de que
o âmbito foi escolhido em vez de acontecer.
