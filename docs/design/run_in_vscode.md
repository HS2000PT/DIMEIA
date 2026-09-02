# run_in_vscode.md — Correr tudo **por cliques** (sem consola)

> Para quem prefere clicar a escrever comandos. Há três formas, da mais simples à mais poderosa.
> Pré-requisito (uma vez): ambiente criado — ver [setup.md](setup.md) (`bash scripts/setup_env.sh`);
> para o dashboard, `pip install -r requirements-app.txt`.

## 1. Duplo-clique no explorador de ficheiros (o mais simples)
Na pasta [`archive/streamlit-app/run/`](../../run/), faz **duplo-clique**:
- `dashboard.bat` → abre o dashboard no browser.
- `demo.bat` → corre a demo (notícia + mercado).
- `tests.bat` → corre testes + lint.
- `thesis-pdf.bat` → compila a tese.

A janela fica aberta no fim para leres o resultado. (Detalhes em [`archive/streamlit-app/run/README.md`](../../run/README.md).)

## 2. VS Code — botão ▶ "Run and Debug" (corre e permite pausar/depurar)
1. Abre o painel **Run and Debug** (ícone ▶ com um inseto na barra lateral, ou `Ctrl+Shift+D`).
2. No topo há uma caixa com uma lista. Escolhe uma configuração:
   - **▶ Dashboard (Streamlit)** — abre o dashboard.
   - **▶ Demo (both triggers)** — corre a demo.
   - **▶ Current Python file** — corre o ficheiro `.py` que tens aberto.
3. Carrega no **▶ verde** (ou `F5`). O resultado aparece no terminal integrado.

> Na primeira vez, o VS Code sugere instalar as extensões recomendadas (Python e LaTeX Workshop).
> Aceita — são precisas para os botões ▶ e para compilar LaTeX. (Ficam listadas em `.vscode/extensions.json`.)

## 3. VS Code — menu "Run Task" (para builds e testes)
1. Menu **Terminal → Run Task…** (ou `Ctrl+Shift+P` → *Tasks: Run Task*).
2. Escolhe:
   - **Demo — both triggers** / **Dashboard — Streamlit**
   - **Tests + lint (verify)** — os 47 testes + ruff (é a *test task* por defeito: `Ctrl+Shift+P` →
     *Run Test Task*).
   - **Thesis — compile PDF** — compila a tese (é a *build task* por defeito: `Ctrl+Shift+B`).
   - **Slides / Study guide / Paper — compile PDF**.
   - **Setup — light venv** / **Setup — + ML** — recriar o ambiente (estas precisam do Git Bash).

## Notas
- As tarefas de Python usam diretamente o interpretador do `.venv` — não precisam de bash.
- As tarefas de **Setup** correm `scripts/setup_env.sh` e por isso precisam do **Git Bash** no PATH; se
  falharem, abre um terminal Git Bash e corre `bash scripts/setup_env.sh` (ou `--ml`).
- Compilar LaTeX precisa do **MiKTeX/TeX Live** (com `latexmk`) instalado. A extensão *LaTeX Workshop*
  também dá um ▶ dentro dos ficheiros `.tex`.
- Nada disto envia mensagens nem usa chaves — é tudo local e seguro.
