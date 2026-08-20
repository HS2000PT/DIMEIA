# Protocolo de estudo de utilidade (RQ3) — fechar a lacuna "útil = em aberto"

> **Porque existe:** a RQ3 tem duas metades. A **fidelidade** das explicações está resolvida (por
> construção + teste automático). A **utilidade para um humano** está reportada como *em aberto* —
> é a maior lacuna honesta da tese. Este documento é o desenho executável que a fecha de forma
> barata e defensável. **Não fabrica nada.** Enquanto não for corrido, é já um forte artefacto de
> defesa ("desenhei exatamente como medir isto"). Depois de corrido (mesmo com N pequeno), vira um
> resultado real para o Cap. 5/6.

---

## 1. Pergunta e hipóteses

**Pergunta:** um investidor de retalho **não-especialista** compreende um alerta do InvestiGator e
sabe o que ele diz — e o que **não** diz — melhor do que com um alerta de referência sem explicação?

- **H1 (compreensão):** com a explicação, os participantes identificam corretamente *o que foi
  detetado* e *porquê* mais vezes do que com o alerta-base.
- **H2 (calibração de confiança):** com a explicação, os participantes reconhecem corretamente que o
  alerta **não é uma previsão** (evita a sobre-confiança — o risco de produto central).
- **H3 (utilidade percebida):** os participantes classificam a explicação como mais clara, completa
  e acionável (rubrica §4).

> Nota honesta: com N pequeno (piloto), o objetivo NÃO é significância estatística forte — é
> **evidência dirigida** e deteção de problemas de usabilidade. Reportar como estudo-piloto.

---

## 2. Desenho

- **Tipo:** within-subject (cada participante vê ambas as condições, ordem contrabalançada) para
  poupar participantes. Alternativa between-subject se houver ≥20 pessoas.
- **Condições:**
  - **A — Base:** só o facto ("TSLA subiu 19,8% a 24 Out 2024"), sem explicação/precedentes.
  - **B — InvestiGator:** o alerta completo (facto + severidade em palavras + "porquê sinalizado" +
    precedentes + nota anti-previsão).
- **Contrabalanço:** metade vê A→B, metade B→A; alertas diferentes em cada condição (para não
  memorizar), retirados de um conjunto fixo de **6 alertas reais** (3 de mercado, 3 de notícia),
  cobrindo um caso "tema ≠ direção" (o precedente de queda com notícia positiva — o ponto duro).

> ⚠️ **Congelar o pacote antes do primeiro participante, e não voltar a gerá-lo.** O gerador é
> determinístico *para a mesma história*, mas o canal continua vivo: a selecção é feita sobre os
> alertas existentes no momento, portanto **regenerar a meio do estudo troca os estímulos** e os
> participantes deixam de ver a mesma coisa. Verificado ao correr duas vezes com a mesma semente e
> obter estímulos diferentes, porque entretanto o histórico crescera. Depois de gerado: commit ao
> pacote, e só se volta a correr para um estudo novo.

---

## 3. Participantes

- **Alvo:** 6–10 adultos sem formação em finanças/IA (colegas, família — o perfil do utilizador
  real). Critério de inclusão: nunca fez trading algorítmico; não trabalha em mercados.
- **Consentimento:** informado, anónimo, sem dados pessoais sensíveis, sem recolha de identificáveis.
  Podem desistir a qualquer momento. (Sem IRB para um piloto de aula, mas seguir boa prática.)
- **Duração:** ~15 min por pessoa.

---

## 4. Rubrica (o instrumento de medição)

Para cada alerta apresentado, o participante responde:

**Parte 1 — Compreensão objetiva (0/1 cada, corrigível sem ambiguidade):**
1. O que é que o sistema detetou? (movimento de preço / notícia) — *certo/errado*
2. Porque é que isto foi sinalizado? (aponta a razão estatística/relevância) — *certo/errado*
3. Isto é uma **previsão** do que vai acontecer a seguir? (resposta correta: **NÃO**) — *certo/errado*

**Parte 2 — Perceção (Likert 1–5; 1=discordo totalmente, 5=concordo totalmente):**
| # | Item | Dimensão |
|---|------|----------|
| Q1 | "Percebi claramente o que este alerta me diz." | Clareza |
| Q2 | "O alerta deu-me a informação de que preciso para o avaliar." | Completude |
| Q3 | "Sei o que poderia fazer a seguir com esta informação." | Acionabilidade |
| Q4 | "Confio neste alerta na medida certa — sei que não é uma garantia." | Calibração de confiança |
| Q5 | "Preferia receber este alerta a só um número de preço." | Preferência global |

**Parte 3 — Aberta (qualitativo, opcional):** "O que faltou ou confundiu?" (1 linha).

---

## 5. Procedimento (guião do facilitador)

1. Consentimento + 1 frase de contexto ("vais ver alertas financeiros; não precisas de saber de
   bolsa").
2. Condição 1 (A ou B conforme o contrabalanço): mostra o alerta → responde Parte 1 → Parte 2.
3. Condição 2: idem, com alertas diferentes.
4. Parte 3 aberta.
5. **Não ajudar nem explicar durante** — o objetivo é o alerta explicar-se sozinho.

---

## 6. Análise

- **H1:** % de respostas corretas nas Q1–Q2 da Parte 1, B vs A. Reportar a diferença.
- **H2:** % de acerto na Q3 ("não é previsão"), B vs A — a métrica de **anti-sobre-confiança**.
- **H3:** média/mediana das Likert Q1–Q5, B vs A. Se N≥8, teste de Wilcoxon pareado (não-paramétrico,
  apropriado a Likert e N pequeno); caso contrário, reportar só descritivo + citações da Parte 3.
- **Qualitativo:** agrupar os comentários da Parte 3 em temas (o que confunde) → lista de melhorias.

> **O que este estudo PODE concluir:** que a explicação ajuda (ou não) na compreensão e na
> calibração, neste grupo pequeno, e QUE problemas de usabilidade existem. **O que NÃO pode:**
> generalizar a toda a população de retalho nem medir decisões de investimento reais. Dizer isto.

---

## 7. Ameaças à validade

- **Construct:** "utilidade" operacionalizada como compreensão+perceção, não como retorno financeiro
  (por desenho — a tese recusa previsão).
- **Internal:** efeito de ordem → mitigado por contrabalanço; facilitador enviesar → guião fixo, sem
  ajuda.
- **External:** N pequeno, conveniência → reportado como piloto; participantes lusófonos a ler
  alertas EN → registar se a língua atrapalhou.
- **Conclusion:** N pequeno → usar não-paramétrico ou só descritivo; não sobre-interpretar p-values.

---

## 8. Como entra na tese (se corrido)

- **Cap. 3:** 1 parágrafo de metodologia (este desenho, resumido).
- **Cap. 5:** um **Case Study 5** curto com a tabela de resultados (compreensão B vs A; Likert;
  2–3 citações da Parte 3).
- **Cap. 6:** a RQ3 passa de "fidelidade sim; utilidade em aberto" para "utilidade com evidência
  preliminar de um piloto de N=…". **Sem inflar** — piloto é piloto.

Se **não** for corrido antes da defesa: fica como trabalho futuro **desenhado em detalhe** — o que
já é uma resposta muito mais forte do júri do que "não medimos".

---

## 9. Bloco C — o texto gerado (acrescentado a 2026-08-13)

> # ⛔ NÃO CORRER. Fora de âmbito desde 2026-08-20, e a razão não é falta de tempo.
>
> **O que este bloco testa deixou de estar no produto.** A 3.ª parte da sessão 61 retirou sete
> rotas da API, entre elas o `POST /api/report` e o `GET /api/evidence`, que são exactamente as
> duas de que o Bloco C depende. Verificado por execução a 2026-08-20:
> `python scripts/capture_report_stimuli.py --base <produção>` devolve `HTTPError` em todos os
> tickers e **não escreve nada** — o script falha fechado, como deve.
>
> **E a retirada foi deliberada, não um acidente a corrigir.** O texto gerado era servido por
> dois `POST` públicos sem limite de ritmo contra a quota de um fornecedor de LLM, e **a tese
> curta não reivindica camada generativa nenhuma**: o §2.7 posiciona-se precisamente *contra* o
> resumo gerado. Correr o Bloco C mediria a utilidade de uma funcionalidade que o sistema
> entregue não tem e que o documento não afirma ter.
>
> **O que fica em vez disso, e é a resposta honesta a dar se perguntarem:** a garantia de
> ancoragem continua verificada por máquina (23/23 ataques bloqueados, 8/8 controlos de texto
> fiel) e **nunca por um humano**. A H5 — *dada uma frase com âncora, uma pessoa consegue abrir
> o facto e julgar se ele a sustenta?* — permanece **por medir**, e é isso que se diz. O código
> da camada continua no repositório e testado, porque as teses longas descrevem-no; o que saiu
> foi a exposição.
>
> Este bloco fica escrito por inteiro, e não apagado, por duas razões: é o desenho que se usaria
> se a camada voltasse a ser exposta, e apagá-lo esconderia que a pergunta existe.

> **Porque é que este bloco existe, e porque é que NÃO estava aqui.** Este protocolo foi escrito na
> sessão 42, antes de existir a camada generativa. Desde a sessão 56 a 5.ª contribuição da tese é
> **geração ancorada**, e o `CLAUDE.md` passou a afirmar que o estudo humano "cobre também o texto
> gerado". **Não cobria.** Cobria o alerta. Este bloco fecha a diferença entre o que estava escrito
> e o que estava desenhado.

### 9.1 A pergunta

A garantia de ancoragem é hoje verificada por **máquina** (a guarda rejeita texto cujos números não
pertençam ao facto que a frase cita) e **por construção** (o gerador nunca produz factos). Nunca foi
verificada por um **humano**. E a afirmação do produto não é "a guarda passa": é *"cada `[f3]` abre o
facto que o sustenta"* — uma **travessia que um leitor faz**. Se ninguém a consegue fazer, a
contribuição é verdadeira e inútil.

- **H4 (utilidade incremental):** com o relatório ancorado ao lado dos painéis, um não-especialista
  responde melhor às perguntas de compreensão do que com os painéis sozinhos.
- **H5 (a travessia é praticável):** dada uma frase com âncora, o participante consegue abrir o facto
  citado e dizer se ele sustenta a frase — **sem ajuda** do facilitador.

H5 é a mais importante das duas e é a que **não precisa de N grande**: se 6 de 8 pessoas não
conseguirem fazer a travessia, isso é um resultado de usabilidade e não uma questão estatística.

### 9.2 Condições

- **C1 — painéis apenas:** veredicto, movimento, raridade, decomposição e precedentes, como a página
  os mostra, **sem** o relatório.
- **C2 — painéis + relatório ancorado:** o mesmo, mais o texto gerado com as âncoras clicáveis.

### 9.3 ⚠️ Os estímulos TÊM de ser congelados, e isto é uma exigência de método

O relatório é gerado por um LLM e **não é determinístico**: gerar ao vivo daria a cada participante
um texto diferente, e a comparação deixaria de medir a condição para passar a medir a variação entre
chamadas. Os estímulos são **capturados de produção uma vez** e ficam fixos para todos
(`scripts/capture_report_stimuli.py`). Captura-se **também o pacote de evidência** que os sustenta,
para a travessia de H5 poder ser feita em papel se não houver ecrã.

Regista-se, para cada estímulo capturado, se veio **gerado** ou da **composição determinística** (o
campo `source` da resposta). Um estímulo que caiu no chão determinístico **não** testa a camada
generativa e tem de ser identificado como tal na análise — misturá-los mediria outra coisa.

### 9.4 Medição

Além da rubrica do §4 aplicada a C1/C2:

- **H5, por frase ancorada** (3 por participante, escolhidas antes): *"esta frase cita [fN]; abra-o.
  O facto sustenta o que a frase diz?"* → **conseguiu abrir** (sim/não) · **julgou correctamente**
  (sim/não/não sei). Sem ajuda; regista-se o tempo até desistir, se desistir.
- **Uma pergunta aberta que vale por si:** *"acredita mais no texto por ele trazer as âncoras, ou
  ignorou-as?"* — se a resposta modal for "ignorei", a contribuição precisa de outra forma de
  apresentação, e isso é accionável.

### 9.5 Custo, e a decisão honesta de âmbito

Somar C1/C2 ao A/B leva a sessão de ~15 para ~25 minutos e **divide ao meio** a evidência de cada
comparação. Com N=6–10 nenhuma das duas comparações teria potência de qualquer maneira, portanto a
escolha não é entre rigor e conveniência.

**Recomendação:** correr o **bloco A/B como principal** (é o que fecha a metade em aberto declarada
da RQ3 e o objectivo 4) e o **bloco C como exploratório**, reportado como tal, com **H5 em primeiro
plano** — é qualitativo, é barato, e é a única evidência humana que existiria sobre a 5.ª
contribuição. Se houver ≥16 participantes, promover C a confirmatório com o mesmo limiar do §6.

**Pré-registo:** este limiar fica fixado **antes** de haver dados, como o do §6. Baixá-lo depois é
p-hacking e fica visível no diff deste ficheiro.

---

## Anexo — folha de recolha (uma por participante)

```
Participante: P__   Ordem: [A→B | B→A]   Data: ____
── Condição 1 (___) · Alerta: ____
  P1.1 detetou o quê? [c/e]   P1.2 porquê? [c/e]   P1.3 é previsão? [c/e]
  Q1_ Q2_ Q3_ Q4_ Q5_   (1–5)
── Condição 2 (___) · Alerta: ____
  P1.1 [c/e]  P1.2 [c/e]  P1.3 [c/e]
  Q1_ Q2_ Q3_ Q4_ Q5_
── Aberta: "O que faltou ou confundiu?" ____________________
```

---

## Anexo B — kit de execução turn-key (para correres numa tarde)

> Sem fabricar nada: os estímulos são **alertas reais** (do teu canal Telegram + os dois exemplos
> documentados abaixo). Regra: cada alerta tem uma versão **A (só o facto)** e **B (o alerta completo)**.
> A versão A constrói-se tirando ao alerta real tudo menos a 1.ª linha (o facto).

**Guião do facilitador (30 s):** *"Vais ver alertas financeiros. Não precisas de saber de bolsa.
Para cada um, responde ao que percebeste — não te ajudo durante. Não há respostas 'erradas' sobre ti."*

**Selecionar os 6 alertas:** 3 de mercado + 3 de notícia, tirados do canal real; **inclui pelo menos um
caso tema≠direção** (notícia com sentido positivo mas precedentes que caíram — é o teste mais duro e o
mais revelador). Contrabalança a ordem (metade A→B, metade B→A), alertas diferentes em cada condição.

**Exemplo trabalhado 1 — mercado (TSLA, real, 24 Out 2024):**
- **A (só o facto):** *"A TSLA subiu 19,8% no dia 24 de outubro de 2024."*
- **B (completo):** *"📈 TSLA · +19,82% hoje. Movimento extremo — cerca de 7,6× a oscilação diária
  típica. Porquê: z-score +7,61 vs limiar ±3 (norma de 20 dias: μ −0,92%, σ 2,73%). Movimento
  observado, não previsão."*

**Exemplo trabalhado 2 — notícia com tema≠direção (NVDA, real, CS3 da tese):**
- **A (só o facto):** *"Notícia sobre a NVDA: 'Qualcomm apresenta linha de chips de IA para data
  centers.'"*
- **B (completo):** *"📰 NVDA — 'Qualcomm apresenta linha de chips de IA para data centers.' Impacto
  potencial (5 eventos passados semelhantes): movimento médio a 1 dia −1,97%. Precedentes: MSFT
  (sim 0,68) −3,46%; NVDA (sim 0,68) −1,64%; META (sim 0,68) −2,65%; GOOGL (sim 0,64) −0,46%; NVDA
  (sim 0,58) −1,64%. Nota: precedentes recuperados por similaridade; impacto = resultado passado
  observado, não previsão."*
  → **este é o caso-chave:** a Q1.3 ("isto é uma previsão?") deve dar **NÃO**, e a Q4 (calibração de
  confiança) mede se o participante percebe que um cluster de quedas **não** prevê esta notícia.

**Analisar (10 min, à mão):** conta os acertos da Parte 1 (B vs A) e a média das Likert (B vs A). Com
N pequeno, reporta descritivo + 2–3 citações da Parte 3. Isto dá-te o **Case Study 5** (ou a nota da
RQ3 "com evidência de um piloto de N=…") — reportado como piloto, sem inflar.
