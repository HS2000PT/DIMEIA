# Bundle público — isolar a app + a tese num repositório de 1 commit

> Objetivo (pedido do aluno): ter um repositório **público** e limpo com o que importa mostrar
> — a **app**, a **tese** e o **código** que as sustenta — separado do repositório de trabalho
> (que tem 200+ commits, planeamento interno e material de estudo privado). Um único commit,
> história limpa.
>
> Publica só um SUBCONJUNTO curado (app + tese + código), deixando o material
> interno de fora. Enacted por `scripts/make_public_bundle.py` (parte de `git ls-files`, por isso
> nunca inclui `.env`, segredos ou os corpora grandes — estão gitignored). **Nada é publicado
> pelo script; o push é o teu clique.**

## Como correr

```bash
python scripts/make_public_bundle.py --out ../InvestiGator-public          # monta + scan de segredos
python scripts/make_public_bundle.py --out ../InvestiGator-public --git    # + git init & 1 commit
```

O script: (1) lista os ficheiros versionados, (2) remove os caminhos só-internos (tabela abaixo),
(3) copia para `--out` (uma pasta IRMÃ, fora do repo), (4) faz um **scan de segredos** (aborta se
encontrar algo), (5) com `--git`, inicia um repo com **1 commit** (sem remote, sem push).

## O que ENTRA (público)

| Caminho | Porquê |
|---|---|
| `investigator/` | o sistema (um pacote por componente) — corre a app e reproduz os números |
| `app/` | o dashboard Streamlit |
| `thesis/` | a dissertação (fonte LaTeX + `main.pdf`) — o trabalho do aluno |
| `paper/` | o artigo IEEE destilado da tese |
| `scripts/`, `tests/` | reprodutibilidade + credibilidade (199 testes) |
| `archive/streamlit-app/notebooks/` | o walkthrough executado |
| `models/`, `config/`, `data/samples/` | modelos congelados pequenos, config sem segredos, amostras |
| `docs/design/`, `docs/evaluation/`, `docs/decisions/` | desenho, provas de avaliação, glossário/learning/citações |
| `archive/deploy/`, `archive/streamlit-app/run/`, `.github/`, `.streamlit/`, `.vscode/`, `.devcontainer/` | deploy + CI (segredos ficam nos Actions, não em ficheiros) |
| `README.md`, `CITATION.cff`, `pyproject.toml`, `requirements*.txt`, `.env.example`, `.gitignore`, `.gitattributes`, `.python-version` | porta de entrada + como correr |

## O que FICA DE FORA (só-interno)

| Caminho | Porquê fica de fora |
|---|---|
| `progress/` | planeamento multi-sessão (PLANO_V2/TRACKER/SESSIONS/DECISIONS + `_historico/`) |
| `CLAUDE.md` | memória de continuidade (processo interno) |
| `.claude/` | settings + planos internos |
| `docs/defence/` | caderno de defesa + guia rápido (estudo **privado**) |
| `slides/` | slides de defesa + guia de estudo (preparação **privada**) |
| `docs/planos/CHECKLIST.md`, `archive/reports/RELATORIO_FINAL.md` | listas/relatório internos para o orientador |
| `.env`, corpora grandes | nunca versionados (gitignored) — o bundle parte de `git ls-files` |

## Decisões de julgamento (defaults, muda se quiseres)

- **`slides/` e `docs/defence/` ficam de fora por defeito** (material de estudo pessoal). Se
  quiseres o *deck* de defesa público, tira `slides/` do `EXCLUDE_PREFIXES` no script.
- **`archive/reports/RELATORIO_FINAL.md` fica de fora** (é um resumo interno para o orientador). Sem problema em
  incluir se preferires.
- **`paper/` entra** (é um artefacto publicável).

## Antes de publicar (2 coisas que NÃO são automáticas)

1. **LICENÇA.** O repo ainda não tem `LICENSE` (decisão do código a tomar com o Prof. Luís Gomes —
   ver o CHECKLIST). O script avisa se faltar. **Adiciona uma licença antes do push.**
2. **A declaração de uso de IA da tese FICA** (é verdadeira; regra do projeto: nunca encobrir).
   Apagar a história não a apaga — nem deve.

## Próximos passos (os teus cliques)

1. Adicionar `LICENSE` ao bundle.
2. Criar o repo público VAZIO no GitHub (sem README/licença auto-gerados).
3. `cd ../InvestiGator-public && git remote add origin <URL> && git push -u origin main`.
4. (Opcional) re-ligar Streamlit Cloud ao repo novo e atualizar badges.
