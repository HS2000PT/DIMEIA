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
