# Z3 — referências próximas, 2026-09-10

Quatro referências identificadas e integradas nas duas línguas. `[Cor21]` continua pendente:
a etiqueta e «relevância sem anotação humana» não identificam uma publicação. Os documentos
`claude/` citados no plano não estão neste checkout. Pedido ao autor o título ou a ligação.

## Identidades e fontes

| Etiqueta | Entrada verificada | Fonte primária e âmbito consultado |
|---|---|---|
| `[Nee25]` | `neela2025spa`: Sandeep Neela, 2025, arXiv 2512.15008 | [Texto](https://arxiv.org/html/2512.15008v1), metadados, §§4.4–4.5 e 5.1. Preprint; sem revista confirmada. |
| `[Cha22c]` | `chan2022deeptrust`: Pok Wah Chan, depósito 2022, arXiv 2203.08144 | [Texto](https://arxiv.org/html/2203.08144v1), capa, resumo, arquitetura e §4.1.1. Dissertação MSc do Imperial College London de setembro de 2021; 2022 é o depósito citado. |
| `[Fer19]` | `dang2020squawk`: Xuan-Hong Dang, Syed Yousaf Shah, Petros Zerfos, IJCAI 2020, pp. 4597–4603 | [Actas](https://www.ijcai.org/proceedings/2020/634), metadados e resumo. DOI 10.24963/ijcai.2020/634. Etiqueta corrigida; citada a publicação de 2020, em vez do preprint de 2019. |
| `[Fen21b]` | `feng2021hybrid`: Fuli Feng, Moxin Li, Cheng Luo, Ritchie Ng, Tat-Seng Chua, SIGIR 2021, pp. 233–243 | [Crossref](https://api.crossref.org/works/10.1145/3404835.3462969): campos; [resumo institucional](https://www.microsoft.com/en-us/research/publication/hybrid-learning-to-rank-for-financial-event-ranking/): âmbito. A página institucional duplica Cheng Luo; prevalecem os cinco autores das actas e do registo do editor. |

Consultados metadados e secções necessárias às afirmações introduzidas; **A10 não fecha
como leitura integral**. Não se compararam desempenhos entre protocolos diferentes.

## Alterações

- §2.2: Squawk Bot, DeepTrust e SPA entram na comparação académica.
- §2.9: retirada a afirmação universal de componentes académicos nunca integrados.
  «Explicar sem prever» deixa de distinguir o projeto perante toda a literatura.
- §2.9: a crítica à geração passa a referir frases sem ligação aos factos.
- §6.5: Feng sustenta a direção de ordenação; o benefício no orçamento diário permanece por medir.
- Bibliografias PT/EN: quatro entradas iguais; resultados experimentais intocados.

## Verificação — FECHADA a 2026-09-10

⚠️ **Esta secção dizia «Em curso» e isso é um defeito por si.** Um documento que se declara em
verificação e não a fecha lê-se, na sessão seguinte, como trabalho garantido — é a mesma classe
do `achados_citacoes_por_consumir.md` da sessão 61 e do `reorganizacao.md`, que se autodeclarou
«ainda não executado» durante nove dias com metade dele feito. Fica com o que foi corrido.

| verificação | resultado |
|---|---|
| `verify_bibliography.py` | **103/103 sem achados.** `dang2020squawk` e `feng2021hybrid` resolvem no Crossref campo a campo; as duas pré-publicações levam nota de que não têm registo no Crossref, o DOI resolve em `doi.org` e os campos foram conferidos à mão |
| compilação das duas árvores | **0 erros, 0 citações e 0 referências por resolver.** Linhas a transbordar: 6 na PT e 4 na EN, **iguais ao registo anterior a estas edições** |
| páginas | **141 físicas antes e depois** — o texto novo absorveu-se nas páginas existentes. **116 de 120** antes dos apêndices |
| paridade PT↔EN | **0 assimetrias em 139 chaves comparadas**, com os dois controlos negativos a disparar (tradução fiel: silêncio; *hedge* perdido: disparo) |
| `check_entrega.py` | **verde nos 23 verificadores** |
| suite | **1195 testes** |
| `ruff` | limpo |

⚠️ **E uma leitura errada minha, apanhada a medir.** A porta reportou «105 de 120 páginas antes
dos apêndices» num ponto anterior desta sessão e «116 de 120» depois destas edições, o que se
lê como um salto de onze páginas por causa de vinte e sete linhas de texto. Não é: a primeira
leitura veio do `tese-pt/main.pdf` da **raiz**, que é um artefacto versionado e estava
desatualizado. É a armadilha nº 1 do próprio *brief* — o PDF fresco está em `build/` — e a
diferença **não é atribuível a estas alterações**, cujo efeito medido na contagem física é zero.

### O que esta verificação NÃO garante

- **`A10` não fecha.** Foram lidos metadados e as secções que sustentam cada afirmação
  introduzida, não o texto integral das seis fontes.
- Uma porta verde prova que nada partiu, **não que a formulação nova é a certa**. As alterações
  da §2.9 são de interpretação: retiram uma afirmação de ausência universal e concedem que
  «explicar sem prever» é opção partilhada. Isso pede leitura, e é o passo 10 do plano.
- **Verificado o que mais preocupava:** nenhum outro sítio do documento reivindica «explicar sem
  prever» como novidade ou prioridade — procurado no Cap. 1, no Cap. 6 e no *front matter*, zero
  ocorrências a cruzar a expressão com «novidade», «contribuição», «primeiro», «inédito»,
  «distingue» ou «único». A concessão da §2.9 não abre contradição interna.
- **E o acrescento do §6.5 respeita a regra do §11.1 do *brief*:** diz que o trabalho de Feng
  «oferece uma formulação a explorar» e que o benefício sob o orçamento diário **continua por
  medir**. Não afirma que a reordenação por codificador cruzado (B6) foi feita, que era
  precisamente a armadilha desta fase.
