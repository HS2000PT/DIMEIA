# run/ — atalhos de duplo-clique (Windows)

Não gostas da consola? **Faz duplo-clique** num destes ficheiros no explorador de ficheiros.
Abre uma janela, corre, e fica aberta no fim (`pause`) para leres o resultado.

| Ficheiro | O que faz |
|----------|-----------|
| `dashboard.bat` | Abre o **dashboard** InvestiGator no browser (os dois gatilhos + avaliação). |
| `demo.bat` | Corre a **demo** de consola (notícia offline + mercado ao vivo). Não envia nada. |
| `tests.bat` | Corre os **testes + lint** (47 testes + ruff). |
| `thesis-pdf.bat` | Compila a **tese** → `thesis/main.pdf` (precisa de LaTeX/MiKTeX). |

> **Pré-requisito (uma vez):** ter o ambiente criado (`bash scripts/setup_env.sh`). Para o dashboard,
> instalar também o Streamlit: `pip install -r requirements-app.txt`.
> Preferes clicar dentro do VS Code? Ver [`docs/design/run_in_vscode.md`](../docs/design/run_in_vscode.md).
