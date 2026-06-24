# risk_register.md — Registo de riscos (vivo)

Cada entrada: risco · probabilidade · impacto · mitigação · contingência. Atualizar ao longo do projeto.

| # | Risco | Prob. | Impacto | Mitigação | Contingência |
|---|---|---|---|---|---|
| R1 | Perda de continuidade / perda de dispositivo | Média | Alto | Push em todas as sessões; `CLAUDE.md` sempre atual; repo = única fonte de verdade | Qualquer dispositivo clona o repo e retoma a partir do `CLAUDE.md` |
| R2 | FNSPID grande demais para portátil | Alta | Médio | Subselecionar tickers + janela temporal cedo; documentar em `data_card.md` | Reduzir mais o subconjunto; metodologia inalterada |
| R3 | API gratuita muda / remove o free tier | Média | Médio | Não assumir; verificar na Fase C; manter `yfinance` + RSS como fallback | Trocar por outra fonte gratuita; documentar a troca |
| R4 | Citação fabricada / não verificável | Baixa | Muito alto | Protocolo de integridade de citações (§6.4); verificar cada DOI | Descartar a citação; nunca adivinhar |
| R5 | LaTeX não compila | Média | Médio | CI compila em cada push; corrigir de imediato | Bisetar a última alteração; manter `main` sempre compilável |
| R6 | Scope creep / aperto de prazo | Alta | Alto | Disciplina de âmbito (§5.3); perguntar antes de adicionar complexidade | Cortar componentes opcionais; entregar o sistema fino mas completo |
| R7 | Aluno não consegue defender um componente | Média | Muito alto | Ensinar à medida (§3); nota de defesa em 3 frases por componente | Simplificar ou remover — indefensável ≠ entregável |
| R8 | Segredo commitado | Baixa | Muito alto | Scan de segredos pré-commit (`end_session.sh`); segredos só no `.env` | Parar, rodar o segredo, limpar da história com cuidado |
| R9 | Wheels indisponíveis (Python demasiado recente) | Média | Médio | Fixar Python 3.12 (D-003); dependências ML faseadas (D-005) | Usar versões alternativas com wheel; ajustar pin |
