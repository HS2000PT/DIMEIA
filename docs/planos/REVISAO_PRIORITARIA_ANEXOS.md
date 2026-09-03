# Revisão prioritária — quatro anexos, ponto a ponto

Atualizado: 2026-09-03. Pedido direto do autor: ler todos os anexos, verificar cada ponto e
preservar a prioridade entre plataformas. Os quatro foram lidos integralmente nesta passagem.
Leitura completa não significa validação completa. A matriz abaixo distingue ambas.

## Autoridade e decisões

Este registo complementa a secção 0 do plano final e prevalece sobre o adiamento histórico da
auditoria integral para depois da defesa. Primeiro verificar as críticas que afetam arquitetura,
dados, método e calendário; depois implementar e medir; só depois finalizar a escrita.
O retreino continua autorizado, mas não deve cristalizar um contrato de dados antes de verificar
as críticas à semântica e à disponibilidade temporal das suas entradas.

- Todas as figuras serão refeitas em inglês, para reutilização no artigo. Não basta trocar a
  língua dos rótulos; composição, finalidade e legibilidade serão revistas.
- Tese em português por agora; eventual tradução integral para inglês é decisão final do autor.
- Piloto Figma rejeitado. A dissertação não herda as cores/mascote do software. Seguir modelo
  oficial e apresentação académica sóbria, vetorial e legível em cinzentos.
- Propostas dos anexos não se tornam factos por terem sido reenviadas. Não atribuir superioridade,
  garantias jurídicas, eficácia humana ou significância estatística sem evidência adequada.
- Feedback humano exclusivamente real; declaração de IA fiel às tarefas efetivamente assistidas.
- Não adiar automaticamente o artigo para depois da defesa: confirmar prazo e regra de avaliação
  relatada pelo autor, que refere dois valores associados ao artigo.

## Fontes preservadas integralmente

Os textos originais, incluindo afirmações incorretas ou ainda não verificadas, estão guardados
sem os promover a instruções científicas:

1. [Plano sistémico](anexos-revisao-2026-09-03/anexo-1.txt).
2. [Mitos e riscos](anexos-revisao-2026-09-03/anexo-2.txt).
3. [Análise crítica](anexos-revisao-2026-09-03/anexo-3.txt).
4. [Comparação e investigação](anexos-revisao-2026-09-03/anexo-4.txt).

## Matriz de verificação

Estados: **decidido** = instrução do autor; **confirmado localmente** = evidência inspecionada;
**parcial** = apenas parte comprovada; **corrigir anexo** = extrapolação ou contradição encontrada;
**pendente** = requer investigação/medição. Nenhuma linha pendente pode ser marcada como resolvida
apenas por estar mencionada na tese. Os caminhos referem-se à raiz do repositório.

| ID / origem | Ponto | Estado, evidência e ação |
|---|---|---|
| 01 · A1§1 | 62 biliões e data 2025/2026 | Pendente: distinguir ano de publicação de ano observado; ch1 usa série até 2024. Conferir fonte primária antes de atualizar. |
| 02 · A1§1, A3§2, A4§2 | Alto valor, velocidade e democratização institucional | Corrigir anexo: benefícios propostos não são benefícios medidos. Mediana de 353 min consta de ch4:656; não prova ausência de toda a utilidade, nem vantagem competitiva. |
| 03 · A1§1 | Três títulos/lemas propostos | Pendente editorial: não adotar promessa de alta velocidade. Nome/título final depende de âmbito e resultados; não reabrir marca por automatismo. |
| 04 · A1§2, A2§2 | Comparação com Cortex e Google Finance | Parcial: produtos existem; tabela de capacidades, datas, países e planos exige verificação por funcionalidade. Ver fontes abaixo. |
| 05 · A1§2 | Cortex gratuito e transparência baixa; Investigator total | Corrigir anexo: suporte oficial dos EUA associa Digests a Gold. Não classificar transparência total/baixa sem critérios observáveis; não generalizar entre mercados. |
| 06 · A1§2 | BERT/FinBERT usados por superioridade | Pendente: distinguir alternativas avaliadas do codificador implantado e dos resultados. Não escrever superioridade porque é especializado em finanças. |
| 07 · A1§2, A3/A4 literatura | Retrieval equivale a RAG; ausência de geração elimina alucinações | Corrigir anexo: recuperação sem geração não é RAG completo; templates não garantem associação correta ou dados verdadeiros. Conferir cadeia de geração e verificações. |
| 08 · A1§2 | SHAP/LIME rejeitados por transparência intrínseca | Pendente: conferir ch2 e contribuições reais do modelo. Uma explicação do score não é explicação causal do mercado. |
| 09 · A1§2, A2§2, A3§5, A4§4 | Conformal impossível em séries temporais | Parcial: ch2:565 discute variante corrente; não extrapolar exclusão a todas as variantes. Verificar pressupostos e literatura publicada. |
| 10 · A1§2 | Vasicek/Platt garantem incerteza honesta | Corrigir anexo: procedimentos não são garantia empírica de calibração. Conferir métricas e separar encolhimento de betas de calibração probabilística. |
| 11 · A1§3, A2§2 | Generalizações sobre concorrentes e 100 passagens | Parcial: ch1:45 contém generalização sem fonte no parágrafo. Contagem de 100 não verificada. Inventariar alegações e fonte, não substituir dogmatismo por vaguidade. |
| 12 · A1§4, A2§1 | 0,486; amplitudes 0,072 e 0,392 | **Confirmado localmente (2026-09-03), mas são duas medições distintas e não podem ser reunidas numa frase.** Amplitudes `0,072`/`0,392`/`5,4×`: 36 925 decisões, 2026-07-22 a 2026-08-20, `evaluation_gate_selectivity_unicos.md`, citadas em ch5:1194–1196. `0,486`: ROC-AUC da pós-validação sobre 239 pares empresa-dia, IC `[0,403; 0,571]`, ch5:1329. Denominadores, períodos e quantidades diferentes. Dois defeitos encontrados na tese — o denominador dos 48% (982 títulos distintos) não está escrito, e a distinção entre contagens aparece duas vezes. Detalhe em `VERIFICACAO_ITENS_12_17_2026-09-03.md`. |
| 13 · A1§4, A2§1 | Mudar nome para ranking salva o componente | **Corrigir anexo, e o número que o fecha já está na tese.** A capacidade de ordenação foi medida sobre a população que o modelo observa em produção: ROC-AUC `0,486`, IC `[0,403; 0,571]`, acaso `0,500` (ch5:1325–1335). Renomear troca a palavra, não a medição. ⚠️ A afirmação de que a pontuação «serve para ordenar entre empresas» (secção 4 de `evaluation_gate_selectivity_unicos.md`) não está medida e ainda não migrou para o corpo — não deve migrar sem medição. Retreino continua a exigir comparação emparelhada de candidato, atual e baseline. |
| 14 · A3§1, A4§1 | Nove entradas, sete estáticas e tabela de consulta | **Verificado (2026-09-03).** Nove entradas: confirmado (features.py:17–18; vetor em infer.py:100–105). «Sete estáticas»: errado, são **cinco** (só os indicadores de setor). A formulação correta é mais forte: **fixados o ticker e o dia, oito das nove entradas são constantes**. «Tabela de consulta» é metáfora, não descrição literal. Sem embedding no caminho implantado: confirmado (variante só-contexto, infer.py:1–11). |
| 15 · A4§1 | Dez notícias recebem exatamente o mesmo score e poluem canal | **Medido (2026-09-03), e passa de afirmação a número.** Com tudo o resto igual, a manchete move a probabilidade `0,0064`; o setor move-a `0,1612` (25×) e a volatilidade `0,2016` (31×). Entre duas notícias da mesma empresa no mesmo dia a pontuação não difere mais de 0,6 pontos percentuais, e o que as separa é o comprimento do título. À letra a afirmação é falsa; na substância é correta. Novo: `scripts/check_headline_sensitivity.py` → `docs/evaluation/sensibilidade_headline.md`; correr no venv do projeto antes de citar. A parte «poluem canal» continua por reproduzir: portas e orçamento decidem entregas. |
| 16 · A1§4 | 333 aprovações e cinco entregas provam bug do ciclo | **Confirmado nos números, inferência errada — e já resolvido na tese.** 333 são avaliações contadas uma vez por ciclo de 60 s; 5 são mensagens entregues (orçamento diário); ambos de 2026-08-15, `funil_por_porta.md`, Fig. `fig:sis_funil` (ch4:366–405). O defeito real era de **instrumentação** (a verificação de duplicação não estava registada como etapa), está descrito, corrigido e com teste automático em ch4:408–418. Nada a alterar. |
| 17 · A1§4, A2§1 | Interrupção de 19 dias | **Confirmado, com o âmbito que muda a leitura (ch4:723–728):** os dezanove dias são do **ciclo de maturação da base de casos**, não da entrega de alertas. Causa registada: sistemas de ficheiros efémeros em duas máquinas e ficheiros intermédios não publicados. Não dizer «dezanove dias sem alertas». Continua pendente, e exige inspeção do sistema no ar: confirmar que a correção está ativa e que existe monitorização que apanhasse uma repetição. |
| 18 · A1§5 | One-click e integridade dos dados | Decidido como requisito: inventário, diagnóstico e reparação autorizada; teste numa instalação limpa. Não confundir demonstração offline com instalação completa. |
| 19 · A1§5 | .env encriptado | Requisito a desenhar: chave fora do repositório, nenhuma credencial em claro, permissões e recuperação. Não ler/publicar segredos nesta auditoria. |
| 20 · A1§5 | Limpeza radical para archive | Condicionada a dependências: preservar fontes/modelos/dados ativos; temporários não precisam de ser perpetuados no arquivo. Sem remoção automática. |
| 21 · A1§6, A2§2 | Retirar mascote e cérebro; paleta azul | Proposta visual registada: autor decidiu sobriedade e separação da marca na tese. Inspecionar UI e ativos antes de remover elementos do produto; azul não é regra académica universal. |
| 22 · A1§6 e pedido direto | Figuras todas refeitas em inglês | Decidido. Inventário por figura: pergunta, dados, desenho, tamanho de impressão, legenda e reutilização no artigo. |
| 23 · A1§6, A2§3 | Duas páginas de índice e figura em cada subsecção | Orientação de maior apoio visual; não impor quota que aumente ruído/páginas. Avaliar necessidade por conceito e distribuição. |
| 24 · A1§7, A2§1 | 20 votos, 19 úteis, duas pessoas | Confirmado no fragmento atual feedback_auto.tex, não em nova consulta remota. Uma pessoa tem 80%, sem ela restam quatro; não chamar estudo independente. |
| 25 · A1§7, A2§1 | Wilson [76%,99%] valida utilidade significativa | Corrigir anexo: intervalo marginal não resolve dependência por pessoa/alerta, seleção ou ausência de controlo. Não concluir eficácia humana ou significância só do intervalo. |
| 26 · A1§7 | IA usada exclusivamente para gramática; versões Claude indicadas | Contradito por ch3:650–656: assistência substancial em código, testes, avaliação e prosa. Não adotar declaração falsa nem inventar versões/ferramentas. |
| 27 · A1§8, A2§2, A3§5, A4§4 | Cortar fórmulas para evitar perguntas | Reorientar: explicar o necessário, deslocar derivação secundária mantendo rastreabilidade. Critério não é ocultar matemática que o autor não domina. |
| 28 · A1§8 | Capturas, vídeo e apêndice de fallback | Decidido: gravar depois da estabilização, guardar vídeo separado e capturas no apêndice; mostrar o que é real/gravado. |
| 29 · A1§8/9 | Converter tudo em bullets e cortar 20% | Pendente diagnóstico: medir redundância e legibilidade; 20% é proposta, não obrigação. Não transformar tese em teleponto. |
| 30 · A1§8 | Artigo só após aprovação | Não adotado: conflita com importância/prazo relatados pelo autor. Verificar regulamento e chamada antes de calendarizar. |
| 31 · A2§2 | Glossário tem só 12 entradas | Parcial/incompleto: ficheiro contém 27 definições. Verificar quais aparecem no PDF e quais são usadas; definições não provam cobertura da lista impressa. |
| 32 · A2§2 | Embeddings/backtesting/Platt são acrónimos em falta | Corrigir classificação: termos precisam de explicação, mas não são todos acrónimos. Conferir RAG/LLM/NLP e nomenclatura inglesa separadamente. |
| 33 · A2§3 | 40 figuras, 11 no ch4 e 18 no ch5; ch2 denso | Parcial: contagem anterior do plano coincide; recontar fonte/PDF final e mapear conceitos sem visual, sem assumir que número elevado significa boa comunicação. |
| 34 · A3§3, A4§3 | Sem estudo humano; scores confundem leigos | Parcial: ausência de estudo declarada em ch3:635; confusão é hipótese plausível, não resultado medido. Preparar tarefas e avaliação humana real. |
| 35 · A3§4, A4§5 | 36,8% repetição parcial, 11,3% todos mesmo dia | Corrigir A4: confunde repetição parcial com todos os casos no mesmo dia. explainer.py:413–415 distingue denominadores históricos. Reproduzir contagem antes de novas alegações. |
| 36 · A3§4, A4§5 | Mensagem atual finge três provas independentes | Desatualizado face ao código local: explainer.py:417–435 calcula dias distintos e avisa explicitamente quando repetidos. Falta confirmar versão implantada e amostra de mensagens atuais. |
| 37 · A3 literatura, A4 fonte 1 | SUERF/Amundi e nudges | Pendente leitura integral e ficha de evidência: não transferir recomendações financeiras para o âmbito deste sistema. Não atribuir a produtos ausência de fontes só por usarem geração. |
| 38 · A3 literatura, A4 fonte 2 | Wang/Edimburgo e interações | Pendente identificação/autoria/publicação e avaliação. Artigo de previsão não demonstra falha crítica de ferramenta com objetivo distinto. Procurar versão publicada; não inserir arXiv automaticamente. |
| 39 · A4 fonte 3 | Preprint VADER/Loughran–McDonald/SHAP/Marketaux | Pendente verificação integral e versão revista por pares. Não adotar detalhes de método a partir do resumo do anexo. |
| 40 · A3 literatura | Isolation Forest/LOF falham no mercado financeiro | Corrigir generalização: comparação local não exclui toda uma família. Identificar protocolos e resultados, manter conclusão estreita. |
| 41 · A3 literatura | Engle 1982 como referência de GARCH | Pendente conferência bibliográfica: distinguir ARCH/GARCH e fonte original; não copiar atribuição do anexo. |
| 42 · A4 fonte 3 | Não prever protege juridicamente o sistema | Não adotar garantia jurídica. Restrição de desenho não substitui parecer legal. |
| 43 · A3§5, A4§4 | Fórmulas adicionadas por orientadores/IA e risco de reprovação | Sem evidência de motivação ou prognóstico. Não atribuir decisões a pessoas nem prometer aprovação; avaliar necessidade e compreensão de cada conceito. |
| 44 · todos | Exaustividade e urgências do roadmap | Uma lista abrangente não autoriza aplicar tudo: requisitos diretos, evidência e dependências comandam. Manter estados verificáveis e limitações. |

## Verificação externa já iniciada

Consulta em 2026-09-03, apenas fontes primárias para as conclusões abaixo:

- [Suporte oficial Cortex Digests](https://robinhood.com/us/en/support/articles/cortex-digests/):
  associa disponibilidade a membros Gold nos EUA; a tabela que diz simplesmente gratuito é
  insuficiente. Não generalizar esta condição a todos os países ou datas.
- [Anúncio oficial britânico de agosto de 2025](https://robinhood.com/gb/en/learn/articles/cortex-digests-is-here/):
  distingue anúncio anterior de disponibilização; datas de anúncio e lançamento não são sinónimos.
- [Expansão oficial do Google Finance](https://blog.google/products-and-platforms/products/search/google-finance-expansion/):
  anúncio de 8 de abril de 2026 encontrado; não valida por si a data de junho atribuída a Key Moments.

As três publicações científicas/relatórios referenciados nos anexos ainda não foram lidos
integralmente nesta auditoria. Nenhuma referência nova foi inserida na bibliografia.

## Sequência e porta de conclusão

1. Resolver evidência/contradições críticas: dados, semântica de features, precedentes, feedback,
   fontes e prazo do artigo. Inspeção read-only antes de mudanças documentais substantivas.
2. Desenvolver retreino controlado e corrigir falhas confirmadas; avaliar com dados rastreáveis.
3. Estabilizar software, organização e instalação; preservar versões e resultados anteriores.
4. Reescrever com concisão e evidência; refazer TODAS as figuras em inglês, modelo oficial,
   glossário/termos e arquitetura completa no apêndice. Separar estilo académico da marca.
5. Gravação, slides, guia e artigo coerentes; tradução da tese apenas se decidida depois.

**Feito a 2026-09-03:** itens 12–17 aprofundados contra o código e os artefactos; registo de
evidência em [`VERIFICACAO_ITENS_12_17_2026-09-03.md`](VERIFICACAO_ITENS_12_17_2026-09-03.md).
Nenhuma linha da tese foi alterada nessa passagem; as correções propostas ficam por localizar.

Próxima ação: fechar o contrato de dados do retreino; em paralelo de trabalho
normal, não adiar a confirmação do calendário do artigo até ao fim da tese. Sem novos agentes
ou publicações automáticas. A revisão não está concluída enquanto houver itens pendentes sem
decisão fundamentada, e nenhuma garantia de aprovação resulta deste plano.

## Raciocínio final consolidado

O conteúdo intermédio e final dos anexos altera a execução em quatro aspetos. Primeiro, retreinar
antes de confirmar a semântica das features, a disponibilidade temporal e a persistência dos
registos arrisca produzir um candidato tecnicamente novo sobre evidência incompatível. Segundo,
reescrever ou traduzir a tese antes de estabilizar software e resultados obrigaria a repetir
texto, figuras, slides, guia e artigo. Terceiro, adiar automaticamente o artigo pode desperdiçar
uma componente de avaliação relatada pelo autor. Quarto, converter recomendações externas em
factos introduziria novos erros precisamente durante uma revisão destinada a removê-los.

Assim, a ordem definitiva é:

1. verificar as afirmações críticas dos anexos e a realidade do sistema;
2. corrigir os defeitos confirmados e desenvolver o retreino com versões, comparação e reversão;
3. estabilizar produto, dados, repositório e instalação;
4. reescrever a tese em português, mais curta e defensável, com afirmações sustentadas;
5. refazer todas as figuras em inglês, com apresentação académica neutra e reutilização no artigo;
6. fechar demonstração gravada, slides, guia e artigo;
7. só então decidir se compensa traduzir a dissertação completa para inglês.

Não se recomeça de zero: aproveita-se o que já está verificado e substitui-se apenas o que falhar
a auditoria. Também não se usa o retreino para “salvar” um resultado: um candidato pode perder,
e nesse caso o modelo atual permanece ativo e o resultado negativo é reportado. O objetivo é
uma tese menor, coerente com o sistema real e que o autor consiga explicar, não uma aparência de
sofisticação ou de sucesso.
