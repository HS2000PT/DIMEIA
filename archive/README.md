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
| `progress-historico/` | planeamento multi-sessão (`PLANO_V2`, `TRACKER`, `SESSIONS`, `DECISIONS`, `_historico/`) | o plano-mestre vivo é `docs/contexto/TASKS.md`; verificado que nenhum script, teste ou *workflow* os lê |
| `scripts-gastos/` | 17 *one-shots* já corridos (`_patch_*`, `_run_53_*`, `_ps_*`) | zero referências vivas, e eram os sete últimos avisos do `ruff` |
| `estado-obsoleto/` | `_estado_novo.md`, cópia de arranque a frio | superado por `docs/contexto/ESTADO_ATUAL.md`; dois ficheiros a dizer «o estado é este» é um a dizer o estado errado |
| `_rascunho-auditoria-web/` | 39 ficheiros da auditoria ao painel (capturas, JSON, sondas) | 47 MB de rascunho; **fica fora do git**, porque não é evidência de nada que a tese afirme |

## O que **não** veio para aqui, e porquê

Isto é a parte que interessa, porque contraria o que o plano inicial assumia.

- **`app/`** parecia a aplicação Streamlit substituída pelo painel. Não é:
  onze ficheiros importam de lá, incluindo `api/main.py`, `api/services.py` e
  oito testes. `app/verdict.py` é o veredicto que a página mostra.
- **`paper/`** — o artigo IEEE, com verificador próprio (`check_artigo_numeros.py`).

⚠️ **Duas afirmações que esta secção fazia e deixaram de ser verdade** — corrigidas a
2026-09-10, porque um aviso obsoleto num ficheiro de arrumação manda a sessão seguinte
proteger o que já não existe:

- Dizia que **`thesis/`** e **`thesis-pt/`** tinham de ficar. As duas estão hoje em
  `thesis-versions/`, e o defeito que a nota descrevia — o pipeline de figuras a escrever
  numa árvore e o documento a ler de outra — está resolvido: as figuras vivem em
  `tese-pt/figures/` e `tese-eng/figures/`.
- Dizia que **`progress/`** tinha quem o chamasse (`check_all_gates.py`,
  `make_public_bundle.py`, `ci.yml`). Medido a 2026-09-10: **nenhum dos três**. O único
  acerto de `grep progress` nos *workflows* é `cancel-in-progress`, que não é a pasta —
  exactamente a classe de falso positivo que este projecto já pagou cinco vezes.

Mover qualquer um destes obriga a repontar scripts, e isso é trabalho com
risco, não arrumação. Está descrito em `docs/design/reorganizacao.md`.
