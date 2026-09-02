# O que foi alterado na tese — plano pré-defesa executado

Base: `main.pdf` de 2026-08-30 11:43 (135 pp). Alterações de **texto e uma figura**;
nenhum resultado foi recorrido, nenhum número existente foi alterado.
Ficheiros tocados: `tese/cap3`, `tese/cap4`, `tese/cap5`, `tese/cap6`,
`tese/frontmatter`, `thesis/references.bib` (+202 linhas, −12).

**Portas:** compila a **0 erros**, 0 referências e citações indefinidas, overfull máximo
$5.19$ pt (inalterado). `check_escrita`, `check_floats`, `check_tex_escapes`,
`auditar_numeros`, `check_apendice_xref` e `check_tese_numeros` (53/53) passam todos.
**141 páginas** contra 135, ou seja **+6**.

> ⚠️ A compilação de verificação correu num TeX Live 2023 e não no MiKTeX desta máquina.
> **Recompilar localmente antes de entregar** — a contagem de páginas pode diferir por uma
> ou duas. `latexmk -pdf main.tex` em `tese/`.

---

## Primeiro: o que foi verificado no código, antes de escrever

Quatro pontos estavam marcados `[VERIFICAR NO CÓDIGO]` na auditoria. Todos verificados.

**1. `ret_event` na linha de base vencedora — NÃO ENTRA.**
`scripts/evaluate_triage_identity.py` constrói a variante ``só volatilidade'' com
`so_vol = [i for i,n in enumerate(nomes) if n == "vol20"]`: uma única coluna.
**Isto salva a resposta à pergunta mais técnica do júri** e está agora escrito na tese.

**2. Treze ou catorze empresas — as duas, e a tese dizia mal.**
Contado no conjunto congelado: o *dataset* tem **14** empresas, o **bloco de treino** tem
**13**. A tese dizia ``o treino cobre catorze'', o que é falso. A tabela de consulta
agrupa por `ticker` **dentro do treino**, logo treze constantes está certo.

**3. Deduplicação entre fontes de notícias — por título normalizado.**
`_norm()` passa a minúsculas e tira pontuação; não compara significado. A coluna
``exclusivas'' da Tabela 4.2 é por isso um limite superior, como a auditoria suspeitava.

**4. Prevalência de $47.0\%$ na validação — explicada, e o achado é maior do que a pergunta.**
Ver a secção seguinte.

---

## O achado novo, e é o mais importante desta ronda

**Os três blocos quase não partilham empresas.** Lido direto das colunas `split` e
`ticker` do conjunto congelado:

| bloco | período | empresas | prevalência |
|---|---|---|---|
| treino | 2018-01-02 a 2022-03-03 | **13** | $0.385$ |
| validação | 2022-03-11 a 2023-01-25 | **8** | $0.470$ |
| teste | 2023-02-02 a 2023-12-18 | **9** | $0.378$ |

- Cinco empresas do treino (BAC, GOOGL, JNJ, JPM, PFE) **não aparecem uma única vez** no teste.
- Uma empresa do teste (MSFT), que vale **$17.1\%$** das suas linhas, **nunca aparece** no treino.
- Para as que estão dos dois lados, a taxa de positivos desloca-se muito: a Apple passa de
  $0.448$ no treino para $0.183$ no teste.

**Não é uma fuga nem um erro de divisão** — o corte é por dia, e por dia a proporção é a
declarada. É a composição do corpus a mudar com o tempo, pela mesma razão que já tornava o
bloco de teste maior do que o de treino.

**Corta nos dois sentidos, e está escrito assim.** A favor do resultado negativo: um modelo
cujo sinal é a identidade da empresa estima essa identidade sobre empresas que mal existem
onde é avaliado, enquanto a volatilidade é medida no próprio dia e atravessa empresas — é
uma explicação mais concreta do que a que a tese tinha para a linha de base ganhar. Contra:
não separa *o modelo é pior* de *a identidade não transfere entre estes dois períodos*.
E explica a prevalência da validação sem recorrer ao acaso.

---

## Alterações, uma a uma

### Capítulo 3
1. **Tabela 3.3 nova, ``Os cinco conjuntos de empresas''**, com o parágrafo que a introduz.
   Reúne 17 / 15 / 15 / 14 / 13 / 9 / 12 e diz para que serve cada um. Diz em voz alta que
   **não são conjuntos encaixados**. Fecha a fragilidade F6.
2. **Tabela 3.2** passa a dizer ``14 empresas (13 no treino)''.
3. **Citação nova para fadiga de alertas** (§3.7.1): Ancker et al. (2017), BMC Medical
   Informatics and Decision Making 17(1):36, DOI `10.1186/s12911-017-0430-8`.
   **Verificada no Crossref**: título, seis autores, revista, volume, número, ano e número
   de artigo conferem. O parágrafo diz que o domínio é outro e que **o que se transfere é o
   mecanismo e não os valores** — a mesma disciplina que a tese já usa para Barber e Odean.
4. Dois `\label` novos (`sec:met_split`, `sec:met_calibracao`) para as remissões novas.

### Capítulo 4
5. **Legenda da Tabela 4.2**: a coluna ``exclusivas'' passa a estar declarada como limite
   superior, com a regra de comparação escrita e o ponteiro para o item 5 do trabalho futuro.
6. **Latência**: ``o ciclo comprou 53 minutos'' passa a ``as duas eras diferem em 53 minutos
   de mediana'', com as três razões pelas quais não é o efeito isolado do ciclo (não foram
   sorteadas, mudaram as fontes e o período, $n=28$ contra $73$, sem intervalo). A conclusão
   que interessa — o tempo está todo na descoberta — não depende dessa comparação e fica
   destacada como tal.

### Capítulo 5 — as correções científicas
7. **§5.3.2, o chão da amplitude de disparo.** Parágrafo novo: a medida principal da QI1 tem
   o zero como ótimo e o ótimo é atingível por um disparo aleatório calibrado. Passa a estar
   escrito que **nenhuma das duas medidas basta sozinha** e que só a regra deslizante passa
   nas duas. Fecha a fragilidade crítica F1.
8. **Figura 5.5 nova**: as duas medidas num plano, com as duas zonas de exclusão
   sombreadas e os três métodos posicionados. A posição do disparo aleatório está marcada a
   cinzento e a legenda diz que é consequência da construção e **não uma medição**.
9. **§5.6.1, a direção do enviesamento do `ret_event`.** Passa a dizer que a entrada pertence
   ao bloco de contexto, ou seja aos modelos que perdem, e que a linha de base vencedora usa
   uma única entrada fechada na véspera: **corrigir a assimetria só pode tornar o resultado
   negativo mais forte**. Fecha F3.
10. **§5.6.3, quarta verificação**: o achado da composição dos blocos, com os números e as
    duas leituras.
11. **§5.6.5**: ``o treino cobre catorze'' corrigido para ``o conjunto cobre catorze e o bloco
    de treino cobre treze'', com a ligação explícita às treze constantes. Fecha F5.
12. **§5.6.7**: a caixa destacada passa a abrir com **$48\%$** (títulos distintos), com os
    $84\%$ das decisões registadas ao lado e identificados como a contagem mais generosa.
13. **§5.6.10**: a legenda da Tabela 5.9 explica porque é que ``contexto + texto'' dá $0.533$
    ali e $0.496$ na Tabela 5.6 — é a redução a 32 dimensões, igual para todas as linhas
    daquela tabela. E o $+0.012$ passa a estar formulado como **limite superior de um efeito**,
    e não como descoberta.
14. **§5.6.12**: o $\beta = 1$ do rótulo passa a estar nomeado como **hipótese alternativa não
    excluída**, com o mecanismo (o erro do rótulo é maior nas ações mais sensíveis ao mercado,
    que são as mais voláteis, e a volatilidade é a linha de base que ganha) e a experiência que
    o resolveria. Fecha F7 pela via da assunção, que é a única disponível em três dias.
15. **§5.3.3**: fica dito porque é que a amplitude aparece como $0.017$ ali e $0.015$ na
    Tabela 5.2 — é o mesmo protocolo de região comum que já explicava o $F_1$.

### Capítulo 6
16. **Limitação nova**, antes de ``Os rótulos são aproximações'': os três blocos quase não
    partilham empresas, com as duas consequências e o que faria falta.

### Resumo e Abstract
17. ``A recuperação semântica supera as linhas de base lexical e triviais'' → **``supera a
    taxa-base dentro de cada um dos cinco setores, e mantém essa margem quando restringida a
    olhar apenas para o passado''**, nas duas línguas. Era a única contradição
    Resumo↔Capítulo, e a Tabela A.3 já a registava como estreitada. Fecha F4.

---

## O que ficou por fazer, e porquê

- **Nomes do júri na folha de rosto** continuam como `[Nome do Presidente, Categoria, Escola]`.
  É seu, não meu.
- **Análise de sensibilidade ao rótulo com betas encolhidos** — a experiência que fecharia F7.
  Não corri nenhuma experiência nova, por decisão: a três dias da defesa, um número novo obriga
  a propagar por seis capítulos.
- **Origem rolante** para a QI3 — mesma razão. Está declarada em falta em dois sítios.
- **Ressalva dos cinco pontos percentuais no texto do alerta** (F10) — é uma linha de código no
  produto, não na tese. Continua por fazer; a resposta oral está preparada na auditoria.
- **`main.pdf` não foi substituído**: recompile no MiKTeX.

---

## Dia 3 — o que resta é a defesa

Não abra o LaTeX. As cinco respostas que decidem a defesa estão redigidas na
`AUDITORIA_CRITICA_PRE_DEFESA.md`, §5: **Q1** (o chão da amplitude), **Q2** (o $\beta = 1$),
**Q3** (o mesmo bloco de teste), **Q4** (o `ret_event`) e **Q14** (onde está a engenharia).
As Q4, Q5 e Q6 já não são perigosas: o texto foi corrigido.

E acrescente uma sexta, que é nova e agora vai aparecer porque a tese a levanta sozinha:
**``o seu bloco de teste tem uma empresa que o modelo nunca viu. Isso não invalida tudo?''**
A resposta está no Capítulo 6 e no §5.6.3, e é a mesma que serve para tudo o resto neste
trabalho: reforça a conclusão negativa por um lado, limita-a por outro, e as duas metades
estão escritas.
