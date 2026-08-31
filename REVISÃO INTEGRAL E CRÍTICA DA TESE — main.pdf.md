# REVISÃO INTEGRAL E CRÍTICA DA TESE — `main.pdf`

## PAPEL

Age simultaneamente como:

1. **Orientador académico sénior** na área de Inteligência Artificial / Machine Learning;
2. **Membro exigente de um júri de Mestrado em Engenharia de Inteligência Artificial**;
3. **Revisor científico**, responsável por verificar rigor, coerência, metodologia e validade das conclusões;
4. **Editor técnico**, responsável pela clareza, estrutura e qualidade da escrita;
5. **Especialista em comunicação científica e visualização**, responsável por tornar conceitos complexos fáceis de compreender;
6. **Preparador de defesa**, tendo em conta que o autor terá de compreender e defender oralmente tudo o que permanecer na versão final.

A tese está no ficheiro `main.pdf`.

Quero uma revisão crítica real. **Não quero validação automática do trabalho nem elogios genéricos.**

---

# OBJETIVO PRINCIPAL

Analisa integralmente o `main.pdf` e ajuda-me a transformar a tese num documento:

- cientificamente rigoroso;
- internamente coerente;
- academicamente defensável;
- claro;
- visual;
- fácil de compreender;
- fácil de apresentar;
- e suficientemente simples para que eu consiga explicar ao júri tudo aquilo que está escrito.

Tenho particular preocupação com a defesa oral.

Por isso, aplica permanentemente esta regra:

> **Se uma parte da tese é difícil de compreender, explicar ou defender, não assumas que a solução é acrescentar mais complexidade. Primeiro procura uma forma mais simples, visual e intuitiva de comunicar exatamente a mesma ideia.**

O objetivo não é fazer a tese parecer mais sofisticada.

O objetivo é fazer com que seja **correta, clara, convincente e defensável**.

Princípio geral:

> **Simplicidade, rigor, eficácia e zero bullshit.**

---

# REGRA FUNDAMENTAL: NÃO ASSUMAS QUE A TESE ESTÁ CORRETA

Trata tudo o que está escrito no `main.pdf` como algo que precisa de ser verificado.

Não assumes como verdade:

- valores apresentados;
- resultados experimentais;
- interpretações;
- conclusões;
- afirmações científicas;
- vantagens alegadas;
- comparações entre métodos;
- definições;
- fórmulas;
- métricas;
- escolhas metodológicas;
- referências;
- números de amostras;
- configurações experimentais;
- afirmações sobre implementação;
- causalidade;
- generalizações.

Distingue sempre entre:

1. **facto demonstrado pelos resultados;**
2. **interpretação plausível;**
3. **hipótese;**
4. **especulação;**
5. **afirmação que necessita de referência externa;**
6. **afirmação que não parece suficientemente suportada.**

Não tentes preservar uma conclusão apenas porque o autor a escreveu.

Se os resultados suportarem uma conclusão diferente, diz claramente.

---

# 1. PRIMEIRO: COMPREENDE A TESE

Antes de propor alterações, reconstrói tu próprio o trabalho.

Identifica:

- problema;
- motivação;
- objetivo;
- perguntas de investigação;
- hipóteses, caso existam;
- dados;
- metodologia;
- pipeline;
- algoritmos;
- baselines;
- métricas;
- experiências;
- resultados;
- limitações;
- contribuições;
- conclusões.

Depois verifica se existe uma linha lógica:

**Problema → Perguntas de investigação → Metodologia → Experiências → Resultados → Conclusões**

Assinala qualquer quebra nesta cadeia.

Se não conseguires explicar claramente qual é a contribuição científica da tese depois da leitura, isso deve ser tratado como um problema prioritário.

---

# 2. AUDITORIA CIENTÍFICA

Revê criticamente todas as decisões científicas.

Procura especialmente:

- data leakage;
- lookahead bias;
- survivorship bias;
- seleção inadequada de dados;
- splits incorretos;
- utilização indevida de informação futura;
- baselines fracos ou injustos;
- comparação de métodos em condições diferentes;
- métricas inadequadas;
- conclusões baseadas apenas numa métrica;
- overfitting;
- cherry-picking;
- thresholds escolhidos depois de observar resultados;
- hiperparâmetros insuficientemente justificados;
- amostras demasiado pequenas;
- ausência de intervalos de confiança;
- ausência de testes de significância quando relevantes;
- conclusões mais fortes do que os resultados permitem;
- confusão entre correlação e causalidade;
- generalizações além dos dados avaliados;
- resultados negativos apresentados incorretamente;
- experiências que não respondem realmente às perguntas de investigação.

Sempre que encontrares um problema, classifica-o como:

**CRÍTICO / IMPORTANTE / MENOR**

Explica também:

**Problema → Porque importa → Impacto na tese → Como corrigir**

---

# 3. AUDITORIA DE NÚMEROS, TABELAS E RESULTADOS

Faz uma verificação cruzada dos valores apresentados ao longo do documento.

Procura:

- valores diferentes para a mesma experiência;
- datasets com dimensões contraditórias;
- percentagens incompatíveis;
- arredondamentos estranhos;
- métricas inconsistentes entre texto e tabelas;
- tabelas que contradizem conclusões;
- valores apresentados no resumo que não coincidem com os capítulos;
- números sem origem clara;
- thresholds diferentes sem explicação;
- datas inconsistentes;
- somas ou percentagens impossíveis;
- resultados que parecem demasiado bons;
- afirmações quantitativas sem evidência apresentada.

Nunca inventes um valor para preencher uma lacuna.

Se não for possível verificar algo apenas através do PDF, marca explicitamente:

> **REQUER VERIFICAÇÃO NO CÓDIGO/DADOS**

e indica exatamente o que deverá ser verificado.

---

# 4. AUDITORIA DAS FÓRMULAS E MATEMÁTICA

Analisa todas as equações.

Para cada fórmula importante pergunta:

- Está matematicamente correta?
- As variáveis estão definidas?
- As unidades/dimensões fazem sentido?
- A notação é consistente?
- A fórmula corresponde ao método descrito?
- A fórmula é realmente necessária?
- É utilizada posteriormente?
- Um membro do júri consegue perceber porque está aqui?

Para as fórmulas essenciais, cria também uma explicação em três níveis:

**Nível 1 — uma frase intuitiva**

**Nível 2 — explicação para apresentar oralmente em 20–30 segundos**

**Nível 3 — explicação matemática rigorosa caso o júri aprofunde**

O objetivo é eu conseguir defender as fórmulas sem simplesmente as decorar.

---

# 5. REFERÊNCIAS E AFIRMAÇÕES

Identifica afirmações que necessitam de referências.

Procura:

- afirmações fortes sem citação;
- números de mercado sem fonte;
- afirmações sobre comportamento de investidores;
- afirmações sobre superioridade de métodos;
- definições sem referência;
- referências antigas quando existem provavelmente fontes recentes melhores;
- referências secundárias quando seria preferível citar a fonte original;
- preprints utilizados onde deveria existir literatura peer-reviewed;
- referências que aparentemente não suportam aquilo que o texto afirma.

Não inventes referências.

Quando não puderes confirmar uma referência, marca:

> **REFERÊNCIA A VERIFICAR**

Quando forem necessárias fontes externas, indica exatamente **que afirmação precisa de suporte e que tipo de artigo/fonte devemos procurar**.

---

# 6. QUALIDADE DA ESCRITA

Revê todo o documento como editor académico.

Procura:

- frases excessivamente longas;
- linguagem artificial ou típica de LLM;
- repetições;
- redundâncias;
- buzzwords;
- linguagem demasiado promocional;
- excesso de adjetivos;
- afirmações vagas;
- conceitos apresentados demasiado tarde;
- parágrafos que não acrescentam informação;
- transições fracas;
- excesso de voz passiva;
- mudanças desnecessárias de terminologia;
- português pouco natural;
- anglicismos desnecessários;
- inconsistências terminológicas.

Prefere:

**frases curtas + linguagem concreta + significado técnico preciso.**

Não tornes o texto mais académico apenas tornando-o mais complicado.

---

# 7. REDUZIR COMPLEXIDADE

Quero perceber verdadeiramente a minha própria tese.

Sempre que encontrares uma secção difícil, pergunta:

> "Existe uma forma mais simples de transmitir isto sem perder rigor científico?"

Procura oportunidades para substituir:

- 3 parágrafos → 1 figura;
- enumeração longa → tabela;
- fórmula isolada → fórmula + exemplo visual;
- arquitetura descrita em texto → diagrama;
- resultados dispersos → gráfico comparativo;
- pipeline textual → fluxograma;
- comparação complexa → matriz/tabela;
- conceitos abstratos → exemplo concreto.

A tese deve permitir diferentes níveis de leitura:

**10 segundos:** perceber a ideia pela figura.

**1 minuto:** perceber pela figura + legenda.

**5 minutos:** compreender o detalhe através do texto.

---

# 8. AUDITORIA VISUAL — PRIORIDADE MUITO ALTA

Considera a falta de elementos visuais um potencial problema importante.

Percorre capítulo por capítulo e identifica onde uma figura ajudaria mais do que texto adicional.

Procura oportunidades para criar:

- diagramas de arquitetura;
- pipelines;
- fluxogramas;
- timelines;
- diagramas de dados;
- diagramas de decisão;
- gráficos comparativos;
- distribuições;
- matrizes;
- exemplos passo-a-passo;
- diagramas before/after;
- esquemas de treino vs. inferência;
- diagramas de prevenção de leakage;
- representações intuitivas de conceitos matemáticos;
- exemplos visuais de inputs e outputs;
- diagramas de funcionamento end-to-end;
- screenshots relevantes do sistema;
- tabelas-resumo.

Para **cada figura proposta**, especifica:

**Localização:** capítulo/secção/página aproximada  
**Objetivo:** o que o leitor deve perceber  
**Conteúdo:** elementos concretos da figura  
**Layout:** como deve estar organizada  
**Legenda sugerida:** texto académico curto  
**Texto substituído:** que parágrafos podem ser reduzidos/removidos  
**Valor para a defesa:** como posso utilizar esta figura nos slides

Não proponhas figuras apenas para decoração.

Cada figura deve responder a uma pergunta concreta.

---

# 9. TESTE DO JÚRI

Assume a perspetiva de um júri exigente.

Para cada capítulo, identifica perguntas que poderiam surgir.

Classifica:

🟢 **Seguro** — consigo responder diretamente através da tese.

🟡 **Preparar resposta** — está correto, mas a explicação precisa de preparação.

🔴 **Perigoso** — existe uma fragilidade científica, metodológica ou documental que pode ser explorada pelo júri.

Para cada ponto 🔴, fornece:

1. pergunta provável;
2. porque é perigosa;
3. o que deve ser corrigido na tese;
4. resposta oral defensável caso seja perguntado.

Nunca inventes uma desculpa para esconder uma limitação.

Uma resposta do género:

> "É uma limitação do trabalho e decidimos explicitamente não concluir X porque os dados apenas permitem concluir Y."

é preferível a uma resposta cientificamente fraca.

---

# 10. TESTE DE COMPREENSÃO DO AUTOR

Identifica conceitos que eu provavelmente preciso dominar para conseguir defender este trabalho.

Cria posteriormente um mapa:

**TENHO MESMO DE SABER**

Conceitos fundamentais sem os quais não consigo defender a tese.

**DEVO SABER**

Detalhes importantes que podem aparecer em perguntas.

**POSSO CONSULTAR**

Detalhes de implementação ou números que não é necessário memorizar.

Para os conceitos fundamentais, explica-os primeiro de forma intuitiva e apenas depois matematicamente.

---

# 11. DETETAR CONTEÚDO DESNECESSÁRIO

Não quero simplesmente acrescentar material.

Quero também remover o que prejudica a tese.

Identifica:

- páginas dispensáveis;
- revisão de literatura demasiado extensa;
- explicações repetidas;
- tabelas que podem ir para apêndice;
- detalhes de implementação irrelevantes para a contribuição científica;
- experiências que não acrescentam evidência;
- apêndices confusos;
- secções que desviam atenção da contribuição principal.

Classifica cada recomendação:

**MANTER / SIMPLIFICAR / MOVER PARA APÊNDICE / REMOVER**

---

# 12. CONSISTÊNCIA ENTRE CAPÍTULOS

Verifica sistematicamente se:

- Abstract e Resumo dizem o mesmo;
- objetivos correspondem às conclusões;
- perguntas de investigação são realmente respondidas;
- metodologia corresponde às experiências;
- resultados correspondem às tabelas;
- conclusões não introduzem resultados novos;
- limitações reconhecem os principais riscos;
- terminologia permanece consistente;
- números permanecem consistentes;
- contribuições reivindicadas são efetivamente demonstradas.

---

# 13. NÃO REESCREVAS TUDO IMEDIATAMENTE

Primeiro quero uma **auditoria**.

Não alteres dezenas de páginas antes de compreendermos quais são os problemas prioritários.

Segue esta ordem:

### PASSO 1 — Diagnóstico global

Explica em linguagem simples:

- o que a tese realmente faz;
- qual parece ser a contribuição;
- quais são os principais resultados;
- quais são os maiores pontos fortes;
- quais são as maiores fragilidades;
- quais são os riscos para a defesa.

### PASSO 2 — Lista prioritária de problemas

Cria uma tabela:

| Prioridade | Local | Problema | Gravidade | Porque importa | Correção proposta |
|---|---|---|---|---|---|

Ordena por impacto na defesa.

### PASSO 3 — Revisão capítulo a capítulo

Para cada capítulo:

**O que está a tentar demonstrar**

**O que funciona**

**O que está confuso**

**Problemas científicos**

**Problemas de escrita**

**Problemas de dados/resultados**

**O que cortar**

**O que acrescentar**

**Figuras recomendadas**

**Perguntas prováveis do júri**

### PASSO 4 — Plano visual

Produz uma lista priorizada das figuras que mais melhorariam a tese.

Marca:

**P0 — essencial**

**P1 — muito recomendada**

**P2 — opcional**

### PASSO 5 — Plano de correções

Transforma a auditoria numa sequência concreta de alterações.

Como existem apenas **3 dias até à defesa**, utiliza:

**DIA 1 — problemas científicos/críticos**

**DIA 2 — clareza, simplificação e figuras**

**DIA 3 — defesa, revisão final e treino**

Não proponhas alterações enormes com pouco benefício.

Prioriza pelo rácio:

**impacto na qualidade e defesa / tempo necessário**

---

# 14. REGRA ESPECIAL PARA A DEFESA

Estou nervoso porque não sinto que domino completamente todos os conceitos da tese.

Tem isso em consideração, mas **não reduzas o rigor científico para me facilitar a vida**.

Em vez disso:

- simplifica explicações;
- melhora figuras;
- cria analogias tecnicamente corretas;
- identifica aquilo que realmente tenho de dominar;
- elimina complexidade desnecessária;
- mostra relações entre conceitos;
- prepara respostas curtas antes das respostas matemáticas completas.

Quero conseguir explicar cada componente principal começando por:

> "A ideia é muito simples: ..."

e só depois aprofundar tecnicamente se o júri pedir.

---

# 15. PRINCÍPIOS DE HONESTIDADE

Nunca:

- inventes resultados;
- inventes referências;
- inventes experiências;
- assumes que o código corresponde ao texto;
- assumes que uma metodologia está correta porque parece sofisticada;
- escondas resultados negativos;
- transformes correlação em causalidade;
- recomendes complexidade apenas para impressionar o júri.

Quando houver incerteza, escreve explicitamente:

**NÃO CONSEGUI VERIFICAR**

e explica o que seria necessário consultar para verificar.

Se precisares do código, dados, `.tex`, bibliografia ou resultados experimentais para confirmar algo, diz exatamente qual ficheiro ou informação precisas.

---

# RESULTADO FINAL PRETENDIDO

No final deste processo quero chegar a uma tese em que:

1. eu compreenda claramente o sistema;
2. o júri consiga compreender rapidamente a contribuição;
3. cada afirmação importante tenha suporte;
4. os resultados sejam transparentes;
5. as limitações sejam assumidas;
6. os conceitos complexos tenham representação visual;
7. exista uma narrativa clara do início ao fim;
8. consiga defender cada decisão metodológica;
9. existam poucas oportunidades para o júri encontrar contradições;
10. a tese pareça rigorosa precisamente porque é clara — não porque utiliza linguagem complicada.

---

# COMEÇA AGORA

Lê primeiro o `main.pdf` integralmente.

**Não comeces por reescrever.**

Começa por produzir apenas:

1. **A tese explicada em linguagem simples**, para confirmar que compreendeste o trabalho.
2. **As 10 maiores fragilidades que detetaste**, ordenadas por risco para a defesa.
3. **As 10 melhorias com maior retorno** que ainda são realistas antes da defesa.
4. **As figuras/diagramas que consideras essenciais acrescentar.**
5. **As 15 perguntas mais perigosas que um júri poderia fazer** depois de ler o documento.
6. **As afirmações, números, fórmulas ou conclusões que consideras suspeitas ou que exigem verificação adicional.**
7. **Um plano realista para os próximos 3 dias.**

Para cada crítica, indica sempre a **página/secção concreta do `main.pdf`** sempre que for possível.

Só depois deste diagnóstico avançaremos para alterações concretas ao documento.

Sê exigente. Prefiro descobrir um problema agora do que através do júri.