# archive/ — o que já não é lido nem executado

Critério, aplicado sem excepção: **vai para aqui o que não é lido nem
executado pelo trabalho que falta, e que não faz parte da entrega final.**
Não é «o que parece velho» — é o que se verificou não ter quem o chame.

Nada aqui foi apagado. Está tudo com `git mv`, portanto o histórico de cada
ficheiro sobrevive e o `git log --follow` continua a encontrá-lo.

## O que está aqui

| Pasta | O que era | Porque saiu |
|-------|-----------|-------------|
| `streamlit-app/run/` | lançadores `.bat` de duplo-clique | nenhum script, workflow ou teste os invoca |
| `streamlit-app/quiz/` | app de autoteste para telemóvel | idem |
| `streamlit-app/notebooks/` | o *walkthrough* em Jupyter | idem |
| `streamlit-app/study/` | notas soltas do estudo | o material vivo do estudo está em `docs/study/` |
| `deploy/` | unidade systemd e script de arranque da VM Oracle | a produção é o Heroku desde agosto |
| `thesis-versions/thesis-examples/` | dissertações de terceiros, para consulta | 24 MB de exemplos, nunca compilados |
| `reports/` | nove relatórios e auditorias já consumidos | eram ficheiros soltos na raiz |

## O que **não** veio para aqui, e porquê

Isto é a parte que interessa, porque contraria o que o plano inicial assumia.

- **`app/`** parecia a aplicação Streamlit substituída pelo painel. Não é:
  onze ficheiros importam de lá, incluindo `api/main.py`, `api/services.py` e
  oito testes. `app/verdict.py` é o veredicto que a página mostra.
- **`thesis/`** parecia uma versão antiga da dissertação. Nove scripts de
  avaliação escrevem figuras para `thesis/figures/`, e o `ci.yml` filtra por
  esse caminho — e a dissertação viva lê de `tese-v2/figures/`. Ou seja: o
  pipeline de figuras aponta para uma árvore e o documento lê de outra. É um
  defeito, mas é um defeito **a corrigir**, não a arquivar.
- **`thesis-pt/`**, **`slides/`**, **`paper/`**, **`progress/`** — todos com
  quem os chame (`check_all_gates.py`, `make_public_bundle.py`, `ci.yml`).

Mover qualquer um destes obriga a repontar scripts, e isso é trabalho com
risco, não arrumação. Está descrito em `docs/design/reorganizacao.md`.
