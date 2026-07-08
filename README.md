# alerts-history — dados, não código

Esta branch existe SÓ para guardar `alerts_history.jsonl`: o registo dos alertas que o
InvestiGator realmente enviou ao canal do Telegram (produzido por
`scripts/run_alerts.py`/`investigator/alerts_history.py` a cada corrida do workflow
"Alerts (scheduled scan)").

O painel público (Streamlit) lê este ficheiro ao vivo via `raw.githubusercontent.com` — nunca
recalcula os alertas, só mostra o que já foi enviado. Por isso vive numa branch separada da
`main`: mantém a história de commits do código/tese limpa, sem um commit automático a cada
30 minutos.

Não editar à mão. Não abrir PR desta branch para a `main`. Ver `docs/design/going_live.md`.
