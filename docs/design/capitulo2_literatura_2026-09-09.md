# Capítulo 2 — integração da literatura em falta (tarefa A12)

**Data:** 2026-09-09
**Estado:** escrito em `tese-pt/ch2/chapter2.tex` e `tese-eng/ch2/chapter2.tex`; bibliografia
verificada; compilação por confirmar no fecho do bloco.

Este documento regista **o que os artigos dizem**, verificado contra o texto integral, e **o que
mudou na tese** por causa disso. Serve para que ninguém tenha de voltar a ler os PDFs para
perceber por que razão uma frase está escrita como está.

---

## 0. O que motivou este bloco

A pesquisa profunda da Fase A concluiu que a §2.2 estabelecia a lacuna **inspecionando produtos
comerciais** e nunca a literatura académica da mesma classe de sistema, que existe desde 2004. Uma
afirmação de lacuna assente em páginas de fornecedores é frágil e é exatamente o tipo de coisa que
um arguente desmonta em trinta segundos.

Cinco PDFs foram obtidos por Henrique com credenciais do ISEP e colocados em `data/literature/`.
Quatro estavam por ler em texto integral. Foram lidos neste bloco.

Extração: `python scripts/_extrair_pdf.py` (usa pypdf; escreve `.txt` ao lado de cada `.pdf`).

---

## 1. [Mun09] Muntermann (2009), *Decision Support Systems* 47(2):82–92

**A descoberta mais consequente deste bloco.** É o vizinho mais próximo da tese inteira, e tinha
ficado de fora.

| | MoFiN DSS | InvestiGator |
|---|---|---|
| Público | investidor particular | investidor particular |
| Paradigma | investigação por desenho (Hevner, March & Smith, Simon) | o mesmo |
| Entrada | comunicados de empresas alemãs (ad-hoc) | notícias gratuitas |
| Medida de relevância | retorno anormal **em valor absoluto**, ajustado pelo índice CDAX e corrigido pelo MAAR da própria ação | z-score móvel sobre o retorno, relativo à norma da própria empresa |
| Uso dessa medida | **prever** o efeito que se vai seguir | **medir** o efeito que já se produziu |
| Explicação entregue | nenhuma | decomposição + precedentes |
| Avaliação | simulação *ex ante* de excedente do consumidor | qualidade do que entrega, sobre dados reais |
| Estudo com utilizadores | **remetido para trabalho futuro** | **remetido para trabalho futuro** |

Factos verificados no texto integral:
- 425 comunicados, 2003-08-01 a 2005-07-31; preços intradiários ao minuto (Xetra + CDAX).
- `MAAR_i` = média, sobre a janela de estimação, de |ln(P_i,t/P_i,t-1) − ln(P_cdax,t/P_cdax,t-1)|.
  Janela de 10 dias, excluindo o dia anterior ao acontecimento (antecipação/uso de informação
  privilegiada). Até 11 880 fixações de preço por cálculo.
- `CAAR_i,t` = |retorno ajustado pelo mercado| − `MAAR_i`. **É magnitude, não direção.**
- Modelo 1 (relevância): OLS, `F(ΣCAAR_3..10) = 0,013 + 0,531·CAAR_1 + 1,366·CAAR_2`.
  R² = 0,365; F = 53,835; p < 0,001. Notifica se o efeito estimado exceder o médio (~2,47 %).
- Modelo 2 (duração): `F(Δt_3,10) = 36,70 + 0,082·Δt_1,2 − 0,018·TVol_1,2 − 0,681·#Analistas`.
  F = 30,054; p < 0,001.
- Divisão 200 (construir) / 225 (avaliar).
- Limitações declaradas pelo autor: modelos de previsão limitados a um tipo de acontecimento;
  **«behavioral science oriented research that incorporate user feedback and usage patterns and
  its context also remains a topic of future research»**; só custos de transação explícitos.

**O que mudou na tese:**
- §2.2 ganhou três parágrafos: o que o MoFiN DSS faz, e as três consequências (a lacuna passa a
  ser de postura epistémica e não de ausência; a magnitude como definição operacional de
  acontecimento relevante tem precedente publicado em 2009; a ausência de estudo com utilizadores
  é uma dificuldade da área).
- §2.9 ganhou um parágrafo de ressalva à frase «nunca como um sistema em funcionamento contínuo
  contra fontes reais», que sozinha era forte de mais.

**Por confirmar:** o artigo dá `R² = 0,365` para o modelo de relevância — não foi escrito na tese
porque a tese não precisa do número, só do desenho. Se algum dia for citado, está aqui.

---

## 2. [Liu23d] Liu, Chen & Wen (2023), SSRN 4466498

**Contraevidência direta à premissa da tese.** Um sistema de alertas para investidores
particulares foi medido em campo e **piorou o desempenho deles**.

Factos verificados:
- Plataforma de fundos em Taiwan, >3 000 fundos. 20 904 investidores, 1 303 340 observações
  investidor-semana, janeiro de 2017 a junho de 2020. 932 (~4,5 %) ativaram alertas.
- Alerta = limiar superior/inferior **definido pelo investidor** sobre o preço do fundo; a
  mensagem dá o preço atual. Sem informação de causa. Sem negociação automática.
- Desenho: DID escalonado; pré 8 semanas, pós 24 semanas. Verificação de tendências paralelas
  (modelo de tempo relativo); PSM 1:1; controlo sintético generalizado; 10 000 aleatorizações.
- Desempenho medido pela medida de Dietz modificada.
- **Resultado principal:** `Track × Post` = −0,111 (modelo principal), −0,111 (DID empilhado),
  −0,086 (PSM+empilhado); todos p < 0,01. Os autores resumem-no como **«about 1 % in 6 months»**.
- Mecanismos: transações +6,9 % (e^0,067−1); rotação da carteira +11,9 %; os fundos ajustados no
  período pós têm desempenho pior (−1,293, p < 0,01).
- Interpretação dos autores: atenção dirigida à volatilidade de curto prazo; **negociação por
  realimentação de preço**, por oposição ao uso de informação sobre o valor da empresa.
- Conclusão: melhorar o **acesso** não basta; é preciso atender à **capacidade de processar**.

> ⚠️ **Inconsistência interna do artigo, assinalada e não resolvida.** O coeficiente é descrito no
> corpo como «a loss of 0.11 % in investment returns» e o resumo fala de «about 1 % in 6 months».
> Sendo a variável dependente semanal, −0,111 % × 24 semanas daria ≈ −2,7 %. Não se percebe, pelo
> texto, de onde vem o 1 %. **Por isso a tese cita apenas a formulação dos autores («da ordem de
> um ponto percentual em seis meses») e não reproduz o coeficiente.** Se for preciso citar o
> número exato, é preciso escrever aos autores ou reler as tabelas com mais cuidado.

**O que mudou na tese:**
- §2.1 ganhou três parágrafos. Não escondidos numa nota: o resultado é incómodo e está no corpo.
- A resposta dada é honesta e limitada: o alerta estudado é de limiar e sem causa; a tese entrega
  a evidência e limita o orçamento por decisão; **se isso basta, é matéria por demonstrar**.
- §2.6 deixou de transpor por analogia a fadiga de alertas do domínio clínico
  (`ancker2017alertfatigue`) e passa a ter evidência do próprio domínio ao lado.

---

## 3. [Oh07] Oh & Kim (2007), *Expert Systems with Applications* 32(3):789–800

Raciocínio baseado em casos aplicado a finanças, e **não é o que a tese faz**.

Factos verificados:
- Indicador diário da condição do mercado financeiro coreano (DFCI). Classifica cada dia em
  período estável (SP), instável (UP) ou de crise (CP), a partir de volatilidade.
- Três sub-indicadores (KOSPI 200, câmbio won/dólar, taxa do tesouro a 3 anos) combinados por
  algoritmo genético. Base de casos construída sobre a crise de 1997.
- CBR é comparado com rede neuronal; a vantagem reivindicada é a **facilidade de atualização com
  pouca informação**, não a explicação.
- **O artigo nunca fala de explicação a um utilizador.** Os casos recuperados produzem a etiqueta.

**O que mudou na tese:** §2.6 ganhou um parágrafo que regista o que o CBR tem feito neste domínio
(mercado inteiro, risco sistémico, etiqueta automática) e sublinha por contraste que mostrar os
casos é o que ali fica por fazer. Serve para que a originalidade reivindicada não pareça maior do
que é.

---

## 4. [Kol91] Kolodner (1991), *AI Magazine* 12(2):52

**A alteração de melhor relação valor/custo do Capítulo 2.**

Do resumo do próprio artigo, na página do editor:

> «I present **case-based decision aiding** as a methodology for building systems in which people
> and machines work together to solve problems. The case-based decision-aiding system **augments
> the person's memory by providing cases (analogs) for a person to use** in solving a problem.
> **The person does the actual decision making** using these cases as guidelines.»

Isto é, literalmente, o que o InvestiGator faz — descrito em 1991 por quem definiu a área.

**O que mudou na tese:** a §2.6 dizia que o sistema faz uma «implementação parcial» do ciclo de
quatro processos. Passa a dizer que executa **por inteiro uma metodologia distinta**, que tem
nome. A diferença retórica é grande e não custa nada: uma implementação parcial explica o que lhe
falta; uma metodologia declara o que entrega. A legenda da Figura 2.2 foi atualizada em
conformidade, nas duas línguas.

**Nota bibliográfica:** a AAAI não depositou os números de 1991 no Crossref. O DOI
`10.1609/aimag.v12i2.895` **resolve** (200, redireciona para ojs.aaai.org) mas não tem registo na
API do Crossref. Isto obrigou a corrigir o verificador — ver secção 6.

---

## 5. [Du24] Du, Mao, Xing & Cambria (2024), CIKM '24, pp. 529–537

O vizinho revisto por pares mais próximo da QI4. **Não colide, e ainda ajuda.**

Factos verificados:
- Rede de tripletos sobre tweets + séries de preço. Âncora = série de *l* dias (l = 7).
- Positivo: **mesmo rótulo de direção**, maior correlação de Pearson dos retornos passados, **maior**
  distância no espaço de características. Negativo: **rótulo oposto**, alta correlação, **menor**
  distância.
- Rótulo: movimento ≤ −0,5 % → 0; > 0,55 % → 1. **A magnitude só define a faixa morta.**
- SBERT (384 dimensões) é usado como **camada de embedding congelada**; o que é treinado é uma
  CNN 2D + LSTM atentiva de duas fases. **O codificador de frases nunca é ajustado.**
- Tarefa: previsão binária de movimento. Métricas: exatidão e MCC.
- Conjuntos: ACL18 (87 ações), CIKM18 (38), BIGDATA22 (50).
- Exatidão: 0,5670 / 0,5790 / 0,5728. **O SLOT bate-os no ACL18** (0,5872). Ganham 2 de 3.
- **Ablação (o achado que interessa):** contrastivo só sobre texto (CL+TIE) = 0,5177 / 0,5426 /
  0,5184, **abaixo** de TIE+QIE sem contrastivo nenhum (0,5423 / 0,5551 / 0,5609). Os autores
  concluem que a informação textual tem papel «suplementar».
- Explicabilidade: **três estudos de caso** com mapas de atenção e correlações de Pearson entre
  pesos de atenção. Sem avaliação com pessoas, sem métrica de recuperação.

**Por que razão isto ajuda a QI4:**
1. Direção como sinal de treino sobre texto é fraca — e agora há **três** indicações
   independentes: a ablação de [Du24], o ROC-AUC ≈ 0,505 de [Jeong26], e a §5.3.5 desta tese.
2. Nem [Du24] nem [Jeong26] **ajustam o codificador de frases**. A QI4 ajusta. É um diferenciador
   verificável, não retórico.

**O que mudou na tese:** §2.4 ganhou três parágrafos. **Não** se escreveu ligação à QI4, porque a
QI4 ainda não existe no texto (o Capítulo 1 declara três questões). Ver tarefa aberta em baixo.

---

## 6. [Waa21] van der Waa, Nieuwburg, Cremers & Neerincx (2021), *Artificial Intelligence* 291:103404

**Correção de um erro meu.** O documento de projeto `claude/fase-A-novidade.md` afirmava que este
artigo «justifica empiricamente a opção por explicação baseada em casos». **Está errado, e o
sentido é o oposto.**

Factos verificados no texto integral:
- Domínio: **autogestão de diabetes tipo 1** (dose de insulina). **Não é finanças.**
- Duas experiências, **45 participantes cada** (diferentes). Recrutados na população neerlandesa.
- Explicações por regras melhoram significativamente a identificação do fator decisivo (p < 0,001
  contra as outras duas condições).
- **Explicações por exemplos não se distinguem de não dar explicação nenhuma:** p = 0,796
  (identificação do fator) e p = 0,283 (compreensão auto-reportada).
- Diagnóstico dos autores, no resumo: *«both explanation styles only provide details relevant for
  a single decision, not the underlying rational or causality»*.

**Os 88 % / 71 % / 68 % que constavam das minhas notas anteriores vinham da Figura 6 e não do
texto. Não foram usados na tese.**

---

## 7. [Cau23b] e [Ber23] — verificados ao nível do resumo do editor

Não há PDF destes dois em `data/literature/`. Os resumos foram obtidos e conferidos hoje
(Semantic Scholar, a partir do DOI). As afirmações escritas na tese usam **apenas** o que consta
dos resumos.

**[Cau23b]** Cau, Hauptmann, Spano & Tintarev, IUI '23, pp. 251–263:
- Domínio: **negociação de ações**, não-especialistas, alta incerteza.
- Três estilos de explicação (indutivo, abdutivo, dedutivo) + papel da confiança da IA.
- Do resumo: *«specific explanation styles (abductive and deductive) improve the user's task
  performance in the case of high AI confidence **compared to inductive explanations**»*.
- O **indutivo é o baseado em exemplos** — o mais próximo do que o InvestiGator entrega.

**[Ber23]** Bertrand, Eagan & Maxwell, FAccT '23, pp. 943–958:
- Domínio: **seguros de vida** com consultor automático, em França. Explicações **por atributos**.
- Do resumo: *«providing feature-based explanations does not improve appropriate reliance or
  understanding compared to not providing any explanation»*; *«dialogic explanations increase
  users' trust in the recommendations of the robo-advisor, sometimes to the users' detriment»*.

> **TAREFA MANUAL PARA O HENRIQUE.** Descarregar estes dois PDFs com as credenciais do ISEP
> (`10.1145/3581641.3584080` e `10.1145/3593013.3594053`) e colocá-los em `data/literature/`. Sem
> eles não se pode citar o número de participantes (184 e 256, nas minhas notas de uma sessão
> anterior, **por confirmar**) nem os valores concretos. A tese hoje **não os cita**, e está
> correta assim; com os PDFs fica mais forte.

**O que mudou na tese:** §2.7 ganhou cinco parágrafos, com a contraevidência em destaque e a
resposta dada em três consequências. A terceira é a que interessa ao Capítulo 6: estes resultados
tornam o estudo com utilizadores **mais** necessário, não menos.

A resposta substantiva, e é honesta: [Waa21] culpa a **ausência do cálculo subjacente**. O
InvestiGator não entrega só casos — entrega casos **e a decomposição aditiva cuja soma reproduz o
movimento**. É exatamente a peça cuja falta os autores responsabilizam. Se isso basta é pergunta
empírica em aberto, e a tese diz isso por palavras suas.

---

## 8. Bibliografia — oito entradas novas e uma correção

Todas em `tese-pt/references.bib`, sincronizadas para `tese-eng/` por
`python scripts/_sincronizar_bib.py --escrever`.

| chave | verificação |
|---|---|
| `muntermann2009ubiquitous` | Crossref ✅ |
| `liu2023alerts` | Crossref ✅ (ordem dos autores: usa-se a da assinatura do PDF, não a alfabética do registo) |
| `kolodner1991aiding` | **não está no Crossref**; DOI resolve em doi.org; campos conferidos na página do editor |
| `oh2007cbrmonitoring` | Crossref ✅ (nota: registo declara 2006/2007) |
| `du2024contrastive` | Crossref ✅ |
| `waa2021xai` | Crossref ✅ (nota: registo declara 2020/2021) |
| `cau2023logicstyle` | Crossref ✅ |
| `bertrand2023featurebased` | Crossref ✅ |

**Correção encontrada de caminho:** `robertson2009bm25` (o BM25, adicionado na sessão anterior)
tinha `3(4), 333–389`. O depósito do próprio editor no Crossref diz **volume 4, número 1–2,
páginas 1–174**. A citação errada é a que o Google Scholar propaga. Corrigido, com comentário na
entrada a explicar a divergência — senão alguém «corrige» de volta.

**Correção no verificador (`scripts/verify_bibliography.py`), com testes primeiro:**
o script resolvia DOIs só pela API do Crossref e, não encontrando registo, escrevia
«DOI **não resolve**». Para o Kolodner isso é **falso**: o DOI resolve. Um relatório que existe
para não ter afirmações falsas não pode ter esta. Foi acrescentada `doi_resolve()`, que só é
chamada quando o Crossref falha, e o caso passa a **nota** em vez de achado.
Testes em `tests/test_verify_bibliography.py` (7, todos a passar).

Estado após a correção: **98/99 sem achados**; o único achado era o BM25, agora corrigido.

---

## 9. O que fica em aberto

1. **Ligar a QI4 ao Capítulo 2.** §2.4 diz hoje que [Du24] treina sobre direção e usa o
   codificador congelado, mas não diz que esta tese faz o contrário — porque a QI4 ainda não
   existe no Capítulo 1. Quando a QI4 entrar (tarefas C7/C8), voltar a §2.4 e a §2.2 e fechar a
   ligação. **Não deixar isto por fazer: é meia frase que transforma dois parágrafos descritivos
   em posicionamento.**
2. **PDFs de [Cau23b] e [Ber23]** — ver tarefa manual acima.
3. **§6.4** — a limitação nº 1 (ausência de estudo com utilizadores) tem agora duas razões novas
   para ser reformulada: [Mun09] deixou-a igualmente por fazer, e [Cau23b]/[Ber23]/[Waa21] tornam-na
   mais urgente. Tarefa A12.10.
4. **Verificar a compilação nas duas línguas** e a paridade das referências cruzadas novas
   (`sec:sis_politica`, `sec:con_limitacoes`, `sec:sis_inteligencia`, `sec:met_metodologia`).
