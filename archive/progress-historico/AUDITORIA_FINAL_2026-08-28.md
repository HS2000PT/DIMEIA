# Auditoria final — 2026-08-28

## Âmbito fixado pelo aluno

- Fonte canónica: `tese/main.pdf`, 136 páginas, gerado em 2026-08-26.
- `thesis/main.pdf` é uma versão inglesa distinta e não é a fonte atual.
- Ordem: verdade científica e técnica; compressão e organização da tese; produto e implantação;
  apresentação; material visual de estudo.
- Não mover nem arquivar ficheiros antes de mapear dependências.

## Primeira medição do documento

- 24 páginas físicas de matéria inicial antes do Capítulo 1.
- 102 páginas numeradas de corpo, da Introdução ao fim das Conclusões.
- Bibliografia nas páginas 103–106; Apêndice A nas páginas 107–111.
- 35 figuras, 33 tabelas e 2 excertos de código.
- O problema visual não é uma ausência absoluta de figuras: é a alternância entre muitas páginas
  densas e diagramas pequenos que nem sempre retiram carga à prosa.

| Parte | Palavras no `.tex` | Figuras | Tabelas | Subsecções |
|---|---:|---:|---:|---:|
| Cap. 1 | 1 978 | 2 | 0 | 0 |
| Cap. 2 | 6 744 | 3 | 5 | 0 |
| Cap. 3 | 11 848 | 12 | 6 | 26 |
| Cap. 4 | 8 701 | 7 | 7 | 5 |
| Cap. 5 | 14 559 | 8 | 12 | 29 |
| Cap. 6 | 4 800 | 3 | 0 | 0 |
| Apêndice A | 2 493 | 0 | 3 | 0 |

O Capítulo 5 é o primeiro candidato a compressão estrutural. O Capítulo 3 vem a seguir. O
apêndice tem apenas cinco páginas impressas; a sensação de desorganização vem de concentrar cinco
funções diferentes, não de ser longo.

## Portas que já passam

- `check_entrega.py`: todos os verificadores passam.
- `auditar_numeros.py`: 246 números; 26 sem ocorrência automática, todos já rastreados e
  justificados; zero sem origem conhecida.
- O PDF compila limpo e é mais recente do que as fontes.

Isto prova coerência e proveniência, não prova ainda necessidade, clareza ou validade da
interpretação. A leitura humana continua necessária.

## Bibliografia: estado real e risco real

- 65 entradas.
- 48 DOI resolvidos e conferidos.
- 4 pré-publicações sem versão publicada encontrada no registo atual:
  `araci2019finbert`, `yang2020finbert`, `doshivelez2017rigorous` e `wu2023bloomberggpt`.
- 59 das 65 fontes têm PDF local; as seis restantes são páginas web.
- Há uma dependência entre árvores: `tese/main.tex` importa `../thesis/references.bib`.

Conclusão provisória: a bibliografia não é dominada por arXiv, mas as quatro pré-publicações são
um risco específico perante a preferência declarada do orientador. Cada uma deve ser mantida,
substituída ou retirada por uma razão explícita; não se troca uma fonte apenas para esconder o
suporte em que foi publicada.

## Próxima passagem

1. Ler QI1, QI2, QI3 e as conclusões como um arguente: pergunta, protocolo, comparador, resultado,
   limitação e frase final.
2. Marcar afirmações cuja prova existe apenas no repositório e não junto do texto.
3. Identificar repetições entre Métodos, Avaliação e Conclusões que possam ser cortadas.
4. Só depois propor cortes e novos visuais, com ganho estimado de páginas.

## Achados confirmados na leitura QI1--QI3

### F1 — contradição na justificação da variante implantada — corrigida

O Capítulo 5 prova que a variante implantada (`0.538`) não tinha a melhor PR-AUC entre as que
cabiam no contentor: só volatilidade obtém `0.542` e sem indicadores de setor obtém `0.543`.
Contudo, o Capítulo 6 voltava a afirmar a justificação já refutada. A conclusão foi alinhada com a
prova: a razão defensável era conseguir mostrar as contribuições no alerta, com um preço medido de
`0.005` de PR-AUC. O PDF foi recompilado e a página 98 foi inspecionada visualmente.

### F2 — a formulação da QI2 prometia mais do que o rótulo media — corrigida

A pergunta dizia “genuinamente parecidas/relacionadas”, mas o protocolo define relevância como
“outra empresa do mesmo setor” e admite corretamente que duas notícias do mesmo setor podem tratar
assuntos diferentes. A formulação forte foi estreitada no Capítulo 1, na abertura da avaliação e
na conclusão. O resultado continua positivo, mas agora responde exatamente ao proxy medido.

### Estado provisório das três perguntas

- **QI1:** protocolo e limitações estão explícitos; o argumento principal é consistência entre
  empresas e não depende do rótulo aproximado. A falta de intervalos é reconhecida. Não foi
  encontrado nesta passagem um erro que altere o veredicto.
- **QI2:** o resultado é sólido para o proxy de setor, incluindo restrição temporal e comparação
  por setor. Não demonstra semelhança factual ou causal; a formulação foi corrigida.
- **QI3:** é a avaliação mais completa e também a maior fonte de extensão. O resultado negativo,
  a ablação, a transferência para produção, a deriva e o pequeno acréscimo do texto são distintos,
  mas há repetição editorial entre diagnóstico, autocorreção e conclusão. É possível comprimir sem
  remover resultados.

### F3 — critério de diferença prática aparecia depois dos resultados — corrigido

A regra editorial que trata diferenças de PR-AUC inferiores a `0.02` como indistinguíveis foi
movida para «Como foi medido», antes da apresentação dos resultados da QI3. A regra deixa assim de
parecer escolhida depois de observados os números.

## Primeira compactação do Capítulo 5

- 14 559 para 13 703 palavras (`-856`).
- Foram condensadas explicações repetidas sobre precisão, revocação e F1, a história da variante
  implantada, a adição do texto e as alternativas de recuperação.
- Mantiveram-se as fórmulas, um exemplo calculado, todos os protocolos, resultados e limitações.
- O PDF passou de 136 para 134 páginas.

Uma compilação interrompida deixou o PDF e os auxiliares incompletos. Foram limpos apenas os
artefactos gerados e feita uma reconstrução integral. A versão final tem 134 páginas e zero
referências indefinidas.

## Portas depois da compactação

- 53/53 números conferidos contra as fontes que os produzem.
- `git diff --check` limpo.
- `check_entrega.py`: 11 verificações a zero, quando corrido com o Python do projeto.

O primeiro ensaio com o Python global encontrou apenas 584 dos 754 testes porque nesse ambiente
faltava `python-dotenv` e seis módulos não podiam ser importados. Não era uma queda da suite; o
ambiente do projeto recolheu a contagem integral.

### F4 — priors de Vasicek e convenções de retorno estavam incompletos — corrigido

A descrição da decomposição dizia apenas que os betas eram encolhidos para valores fixos de `1.0`
e `0.5`. O código não faz isso: encolhe o beta de mercado para `1.0`, o beta do setor já
ortogonalizado para `0.0`, e usa `0.5` como desvio-padrão comum do prior, isto é, variância `0.25`.
O Capítulo 3 passa a distinguir estes quatro números e a declarar os dois desvios face à formulação
original de Vasicek: os priors são escolhas do autor, não estimativas transversais, e não foi feita
uma análise de sensibilidade ao desvio-padrão. Portanto, o mecanismo de ponderação pela precisão é
fundamentado, mas os valores concretos da repartição dependem desta escolha de modelação.

Ficou também separada uma convenção que o texto confundia. O detetor e a decomposição usam retornos
logarítmicos; os resultados históricos dos precedentes usam a variação simples
`P_(d+h) / P_d - 1`, que o utilizador consegue conferir diretamente. No caso da AMD, o retorno
logarítmico de `+6.2944%` corresponde a uma variação simples de `+6.50%`. A tese já não afirma que
uma única definição rege todos os números do capítulo.

A correção foi sincronizada com o gerador e o relatório da decomposição, o guia da tese e os dois
materiais de estudo. As páginas físicas 54 e 58 da tese e as páginas afetadas dos guias foram
renderizadas e inspecionadas. A primeira renderização revelou uma palavra colada na legenda da
Tabela 3.4; foi corrigida e a página 54 voltou a ser renderizada limpa.

## Portas depois da correção da decomposição

- Tese canónica: 134 páginas, compilação limpa e zero referências indefinidas.
- `check_entrega.py`: 11 verificações a zero; 53/53 números conferidos.
- Suite completa: 754 testes passaram, 2 foram desselecionados.
- Ruff e `git diff --check`: limpos; os únicos avisos do Git são de normalização CRLF/LF.
