# evaluation_retrieval_causal.md — a recuperação só com o passado (QI2)

> Gerado por `scripts/evaluate_retrieval_causal.py` a 2026-08-20 13:08 UTC. **Não editar à mão.**
> Aditivo: não toca em `evaluation_retrieval_fnspid.md`, que é o congelado citado pela
> dissertação.

## A pergunta

O protocolo da dissertação proíbe o candidato de ser da mesma empresa, e mais nada — em
particular, não o proíbe de ser **posterior** à consulta. O sistema em produção não tem
essa liberdade: a base de precedentes só recebe um caso oito dias depois, quando o
impacto já é observável. Este documento mede a mesma tarefa **com a restrição da**
**produção**, para que o número que a dissertação reporta se possa ler pelo que é.

## Resultado

Corpus: **79753** manchetes com embedding e setor conhecido, de 2018-01-01 a 2023-12-16. 5 repetições de 500 consultas, semente 42, precisão@5.

| protocolo | o que o recuperador pode ver | precisão@5 | chão de acaso |
|---|---|---|---|
| simétrico (o da dissertação) | tudo menos a própria empresa | **0.595** ± 0.024 | 0.333 |
| causal (o da produção) | só o que é anterior à consulta | **0.513** ± 0.024 | 0.259 |

**Diferença em precisão bruta: -0.082.** Mas o chão de acaso também desce, porque restringir os candidatos aos anteriores muda a composição do conjunto de onde se escolhe. A quantidade comparável é a **margem sobre o acaso**:

| protocolo | precisão@5 | chão | **margem** |
|---|---|---|---|
| simétrico | 0.595 | 0.333 | **+0.262** |
| causal | 0.513 | 0.259 | **+0.254** |

**A margem muda -0.008.**

Consultas sem passado suficiente, excluídas da linha causal: 0 em 2500 (0.0%). São as primeiras do corpus, que não têm $k$ candidatos anteriores; deixá-las dentro mediria uma tarefa impossível.

## Leitura honesta

Esta comparação **não** existe para descobrir uma fuga: o rótulo da métrica é
*pertence ao mesmo setor*, e o setor não muda com o tempo, portanto a direcção temporal
não tem por onde inflacionar a precisão. Existe porque a afirmação da dissertação é
sobre **encontrar casos passados**, e um número medido sem essa restrição descreve uma
tarefa ligeiramente diferente da que o produto executa.

E há uma segunda lição, que é de método e vale mais do que o número: a precisão bruta
desce, mas o **chão desce quase o mesmo**, e a margem sobre o acaso fica praticamente
onde estava. Ler só a primeira coluna desta tabela levaria à conclusão errada — que é
exactamente o erro que esta dissertação já cometeu uma vez, e corrigiu, com o chão da
precisão no orçamento.
