# QUESTIONS — Banco de perguntas prováveis do júri + respostas preparadas

> Cresce ao longo do projeto. Cada componente fecha com uma nota "como explico ao júri em 3 frases".
> Aqui ficam as perguntas difíceis e a resposta defensável. (Respostas a desenvolver com o aluno.)

---

### P1. "Onde está a vossa contribuição — isto não é só integrar ferramentas existentes?"
**Resposta (esboço):** É uma tese de **Engenharia de IA**. A contribuição não é inventar algoritmos, mas
**integrar, aplicar e avaliar criticamente** componentes existentes num sistema funcional, explicável e
reproduzível — com uma **metodologia documentada de correlação notícia–impacto** (escolha de embeddings,
métrica de similaridade, janelas de event-study). Usar modelos existentes de forma rigorosa e transparente
**é** o trabalho de engenharia. *(A desenvolver.)*

### P2. "Porque é que o sistema é explicável (XAI)?"
**Resposta (esboço):** Porque toda a lógica é exposta ao utilizador: deteção estatística transparente, os
precedentes históricos recuperados como evidência, e a explicação montada passo a passo. Percorrer o pipeline
end-to-end mostra que não há caixas negras. *(A desenvolver.)*

### P3. "Como evitam lookahead / fuga de informação futura?"
**Resposta (esboço):** As features num instante nunca usam informação do futuro; o impacto histórico é medido
com janelas pós-notícia bem definidas (+1, +3 dias…), documentadas na metodologia. *(A desenvolver — §6.5.)*

### P4. "Porquê estes métodos e não outros mais sofisticados?"
**Resposta (esboço):** Simplicidade defensável: entre abordagens com resultados semelhantes, escolhe-se a mais
simples, padrão e explicável. A transparência é uma vantagem XAI, não uma limitação. *(A desenvolver — §3, §5.5.)*

### P5. "Como garantem que as citações são reais?"
**Resposta (esboço):** Protocolo de integridade de citações (§6.4): cada entrada do `.bib` é verificada contra
DOI/arXiv/registo real antes de ser citada, com registo em `docs/citation_log.md`. *(A desenvolver.)*
