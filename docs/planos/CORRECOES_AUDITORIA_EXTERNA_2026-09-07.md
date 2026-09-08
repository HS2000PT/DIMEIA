# Aplicação da auditoria externa de 7 de setembro de 2026

Pedido do autor: aplicar as correções da auditoria ao PDF de 123 páginas. A implementação
parte de `36939547a`, após sincronizar a redução entretanto aprovada pelo autor. Mantém
`openany`, as margens alternadas, a dedicatória e a remoção do Apêndice B e da antiga §A.6.

## Disposição dos 24 achados

| ID | Tratamento na versão atual |
|---|---|
| A01 | Corrigida a sobreposição: oito das nove empresas de teste são conhecidas, com 82,9% das linhas. A mudança de composição e de prevalência não é descrita como quase ausência de empresas comuns. |
| A02 | QI2 delimitada aos comparadores avaliados. Explicado que o filtro pelo setor conhecido satisfaz a aproximação de relevância quando existem candidatos suficientes; não se inventou uma nova medição desse filtro. |
| A03 | A distância ao oráculo refere-se à seleção de grupos empresa-dia. Permutar títulos com o mesmo rótulo não altera a precisão. Retirada a localização do erro na distinção intradiária de títulos. |
| A04 | Seleção com o dia completo apresentada como política diferida, sem garantia sobre a precisão online. Só o oráculo mantém a interpretação de máximo neste conjunto. |
| A05 | Conferida a máscara de `evaluate_retrieval_causal.py`: exige datas anteriores, sem impor maturação de oito dias. Texto, legendas, gráfico, artigo, slides e quizz passam a distinguir os dois protocolos. |
| A06 | Mantidos os votos e Wilson, com dependências por pessoa e por alerta explicitadas. Corrigido o gerador e regenerados os dois fragmentos com os mesmos dados locais: 86 registos, 81 válidos, 42 efetivos, 41 úteis, três pessoas e 29 alertas. |
| A07 | Descrição coerente com o alerta e o formatador: casos individuais acompanhados de amplitude e média descritiva. O alerta histórico permanece verbatim. |
| A08 | O residual positivo deixa de provar que a ação subiu ou que não existe causa interna. A decomposição é descritiva, sem inferência causal. |
| A09 | A figura do ciclo distingue teste reservado de teste usado uma única vez; remete para a reutilização declarada na avaliação. |
| A10 | Quatro resumos, conclusão, artigo e respostas de defesa distinguem as três técnicas comparadas com linhas de base da avaliação do ajuste da decomposição. |
| A11 | Brier inclui referência constante igual à prevalência de treino, cerca de 0,235; cálculo descrito abaixo. O valor 0,622 de anunciar sempre um mantém-se identificado como referência fraca. |
| A12 | O limiar de evidência 0,45 deixa de ser apresentado como o principal eliminador atual. |
| A13 | FNSPID descrito como tendo sido usado pela sua componente de notícias, sem negar a existência de preços no conjunto original. |
| A14 | Publicadas as sementes por protocolo em §3.7, em ambas as línguas, em vez de uma promessa genérica no apêndice. |
| A15 | Corrigidas referências às questões do investidor e de investigação, às duas modalidades de avaliação e à secção do acréscimo textual, agora com label próprio. |
| A16 | Robertson e Zaragoza (2009): volume 3, número 4, páginas 333–389, nas duas bibliografias. DOI preservado e metadados conferidos na primeira página do editor. |
| A17 | Criadas âncoras próprias antes das entradas das quatro listas no índice. Destinos a conferir no PDF compilado. |
| A18 | Formatação decimal dos eixos em português definida no estilo comum; inglês mantém ponto. |
| A19 | Nota inferior da figura dos nove pontos ancorada abaixo do traço, sem a atravessar. |
| A20 | A data de 15/08 não é preservada pelo artefacto da decomposição: o gerador elimina os índices de data. Retirada a atribuição a uma sessão concreta e declarada a limitação, sem substituir por uma data presumida nem alterar retornos. |
| A21 | Beta de referência setorial zero justificado como opção de regularização, não deduzido de média zero. Símbolo do fator setorial identificado como ortogonalizado. |
| A22 | Retiradas as autoqualificações indicadas. O órfão final já não existia após a redução sincronizada. |
| A23 | Mantidos os campos do júri: a memória atual esclarece que os nomes só são designados depois da submissão. Não é uma correção factual que se possa preencher agora. |
| A24 | Retirada a garantia de que corrigir o retorno do dia só reforçaria o resultado negativo. A direção do efeito exige novo treino e avaliação; as conclusões atuais ficam limitadas ao protocolo executado. |

## Cálculos e proveniência

O complemento de 17,1% é 82,9%; a interseção das empresas é 13−5 = 9−1 = 8.
As contagens e a mudança de prevalência da Apple já constam dos resultados congelados.

Para uma previsão constante `q = 0.3854`, a prevalência do treino, e prevalência de teste
`pi = 0.3781`, o Brier é `pi*(1-q)**2 + (1-pi)*q**2 = 0.23519368`, arredondado a 0,235.
As duas prevalências estão impressas na figura da deriva e em
`docs/evaluation/evaluation_drift.md`. É um cálculo sobre prevalências arredondadas, não uma
nova execução nem um resultado exato reconstruído das linhas. As métricas dos modelos permanecem
inalteradas.

Metadados de Robertson e Zaragoza verificados no
[PDF do editor](https://www.nowpublishers.com/article/DownloadEBook/INR-019),
DOI `10.1561/1500000019`: *Foundations and Trends in Information Retrieval* 3(4), 333–389.

## Verificação

Corrida a 2026-09-07, depois de aplicadas as vinte e quatro correções.

| Porta | Resultado |
|---|---|
| `tese-pt/main.pdf` | **122 páginas**, 0 erros, 0 referências ou citações indefinidas |
| `tese-eng/main.pdf` | **121 páginas**, 0 erros, 0 referências ou citações indefinidas |
| Overfull máximo | **5,68 pt** (PT) e **8,61 pt** (EN) — iguais ao registo anterior às correções |
| Materiais | slides 22 + 22 · guia 25 · guia de construção 16 · artigo 11, todos a 0 erros |
| `scripts/check_entrega.py` | **19 verificadores verdes**, 0 por resolver |
| `pytest` | **1027 passaram**, 6 saltados, 2 excluídos |
| `ruff check` sobre `scripts/ investigator/ tests/ api/ app/ web/` | limpo |

As únicas ocorrências de `undefined` nos dois registos de compilação são avisos de **forma de
fonte** (`T1/cmbr/m/sc`, `T1/cmtl/b/n`), cosméticos e pré-existentes. Não há uma única referência
cruzada nem citação por resolver.

**A17 conferido no PDF compilado, e não por leitura do `.tex`.** Resolvidos os destinos das
ligações do índice com `pypdf`: as cinco entradas das listas apontam para as páginas físicas
**11, 13, 15, 17 e 18**, que são exatamente onde a Lista de Figuras, de Tabelas, de Excertos, de
Símbolos e de Acrónimos começam. Os fólios impressos nessas páginas são xi, xiii, xv, xvii e
xviii, que é o que o índice anuncia. As restantes 104 ligações do índice foram resolvidas na mesma
passagem e nenhuma aponta para uma página anterior à da secção que nomeia.

**A11 refeito à parte, e fecha.** Com `q = 0,3854` e `pi = 0,3781`,
`pi(1-q)² + (1-pi)q² = 0,23519368`, arredondado a 0,235 como o texto imprime.

**A01 refeito à parte, e fecha.** 13 − 5 = 8 e 9 − 1 = 8; o complemento de 17,1% é 82,9%.

**A16 conferido contra o editor.** Robertson e Zaragoza (2009), *Foundations and Trends in
Information Retrieval* **3**(4), 333–389, DOI `10.1561/1500000019`. A entrada anterior dizia
4(1–2), 1–174, que são os metadados de outro volume da mesma série. Corrigida nas duas
bibliografias.

⚠️ **O que esta passagem NÃO verifica, e fica dito em vez de suposto.** Nenhuma destas portas
compara um número da tese com o artefacto que o produziu — isso é o que o `check_tese_numeros` e o
`auditar_numeros` fazem, e os dois estão verdes, mas nem um nem outro sabe se a *leitura* de um
número está certa. As correções A03, A04, A08, A20, A21 e A24 são de **interpretação**: retiram ou
estreitam uma afirmação sobre números que não mudaram. Uma porta verde não é prova de que a
formulação nova é a certa; é prova de que não partiu nada.

Não se retreinou qualquer modelo, não se recolheram novos votos e não se alteraram mensagens
entregues. Permanecem humanas a confirmação de participação do autor nos votos, a sua leitura
integral e os nomes do júri. A identificação da sessão de mercado do exemplo AMD continua
indisponível no artefacto preservado; a tese passa a dizê-lo.
