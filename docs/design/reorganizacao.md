# Frente 09 — Organização da pasta e do repositório

Pedido dele, a 2026-09-01: o repositório é público, e está uma confusão.
Quer três coisas: nada de ficheiros soltos na raiz, `code/` e `archive/`
certos, e uma `Dissertation/` com `Thesis/`, `Slides/` e `Guide/`.

Este ficheiro é o plano. Ainda não foi executado.

---

## 1. O que está mal, em números

Contado hoje, não estimado:

| Sintoma | Número |
|---------|--------|
| Ficheiros `.md` soltos na raiz | 17 |
| Pastas na raiz | 23 |
| Pastas que são versões antigas da tese | 5 (`tese`, `thesis`, `thesis-pt`, `thesis-examples`, `paper`) |
| Ficheiros de `tmp/` **versionados** | 406 |
| Peso de `tmp/` | 66 MB |
| Ficheiros versionados em `tmp/pdfs/tese_main_2026-08-29` | 176 |
| Peso de `docs/` | 94 MB |

Os 176 ficheiros de `tmp/pdfs/tese_main_2026-08-29` são páginas renderizadas
de uma compilação de 29 de agosto. Estão num repositório público. Quem clona
o repositório descarrega-os.

---

## 2. Uma restrição que não se contorna

O *buildpack* de Python do Heroku deteta a aplicação **na raiz do
repositório**. Se `requirements.txt` e o `Procfile` deixarem de estar na
raiz, o deploy deixa de arrancar — não com um aviso, com uma falha de
deteção.

Há maneiras de contornar isto (*buildpacks* de terceiros que empurram um
subdiretório para a raiz). Não vou usar nenhuma a duas ou três semanas da
defesa: acrescenta uma dependência externa não oficial ao caminho crítico do
único artefacto que tem de estar de pé no dia da defesa.

Portanto: **cinco ficheiros ficam na raiz por obrigação técnica**, e não por
desleixo. Ficará escrito no `README.md` porque é que lá estão.

| Ficheiro | Porque tem de ficar |
|----------|---------------------|
| `Procfile` | o Heroku lê-o na raiz |
| `requirements.txt` | é o que faz o *buildpack* de Python detetar a aplicação |
| `.python-version` | fixa a versão do runtime |
| `pyproject.toml` | empacotamento e configuração do `pytest` e do `ruff` |
| `README.md` | é a porta de entrada de um repositório público |

Mais dois, por convenção das ferramentas que usamos: `AGENTS.md` e
`CLAUDE.md` são lidos na raiz. Ficam.

O código em si **pode** mudar de sítio. O `Procfile` passa a apontar para lá:

```
web:    PYTHONPATH=code uvicorn api.main:app --host 0.0.0.0 --port $PORT ...
worker: PYTHONPATH=code python code/scripts/run_alerts.py --watch --interval 60
```

---

## 3. A árvore proposta

Minúsculas em tudo. Motivo concreto: ele trabalha em Windows, que trata
`Thesis` e `thesis` como o mesmo nome, e o Heroku corre Linux, que não. Um
ficheiro renomeado só na caixa passa despercebido na máquina dele e parte no
deploy. Minúsculas em todo o lado elimina essa classe inteira de bug.

```
DIMEIA/
├── README.md
├── AGENTS.md  CLAUDE.md          (convenção das ferramentas)
├── Procfile  requirements.txt
├── .python-version  pyproject.toml
├── CITATION.cff  app.json
│
├── code/
│   ├── investigator/             o pacote
│   ├── api/                      FastAPI
│   ├── scripts/                  ~109 scripts
│   ├── web/                      o painel
│   ├── tests/
│   ├── config/
│   ├── archive/deploy/
│   ├── models/
│   └── requirements/             requirements-app/ml/notebook/lock
│
├── dissertation/
│   ├── thesis/                   ← tese-v2
│   ├── slides/
│   ├── guide/                    ← guia de defesa e de estudo
│   └── figures/                  figuras finais, partilhadas
│
├── docs/                         documentação viva do projeto
│   ├── REGISTO_PEDIDOS.md
│   ├── decisions/
│   ├── design/
│   └── evaluation/
│
├── data/                         só as amostras versionadas
│
└── archive/
    ├── thesis-versions/          tese, thesis, thesis-pt, thesis-examples, paper
    ├── streamlit-app/            app, run, quiz, notebooks
    ├── reports/                  os 14 .md soltos que já não são consultados
    └── README.md                 uma linha por pasta a dizer o que era
```

---

## 4. O que vai para `archive/`, e porquê

Critério, dito uma vez e aplicado sem excepção: **vai para o arquivo tudo o
que não é lido nem executado pelo trabalho que falta, e que não faz parte da
entrega final.** Não é «tudo o que parece velho».

| Vai | Motivo |
|-----|--------|
| `tese/`, `thesis/`, `thesis-pt/` | versões anteriores da dissertação; a viva é `tese-v2` |
| `archive/thesis-versions/thesis-examples/` | 24 MB de exemplos de terceiros |
| `paper/` | tentativa de artigo, abandonada |
| `app/`, `archive/streamlit-app/run/`, `archive/streamlit-app/quiz/`, `archive/streamlit-app/notebooks/` | a aplicação Streamlit, substituída pelo painel |
| `progress/` | diários de progresso |
| 14 dos 17 `.md` da raiz | relatórios e auditorias já consumidos |

Ficam na raiz, dos `.md`: `README.md`, `AGENTS.md`, `CLAUDE.md`.
`docs/planos/PLANO_FINAL_2026-09-01.md` e os dois `POS_PLANO_*` passam para `docs/`,
porque ainda estão a ser executados.

---

## 5. `tmp/` — mover não chega

Mover `tmp/` para `archive/` deixa 66 MB versionados num repositório
público. O que é preciso é `git rm --cached -r tmp/` e uma regra no
`.gitignore`.

Aviso honesto, para não haver ilusões: isto tira-os do HEAD, portanto quem
clonar deixa de os ver na árvore de trabalho. **Não os tira do histórico** —
o repositório continua a pesar o mesmo, e os ficheiros continuam
alcançáveis por SHA. Limpar o histórico a sério obriga a reescrevê-lo
(`git filter-repo`) e a forçar o *push*, o que quebra qualquer clone
existente. Não recomendo fazer isso antes da defesa; recomendo fazê-lo
depois, se ele quiser, e a decisão é dele.

---

## 5.5. O que se descobriu ao executar, e que muda o plano

Escrito a 2026-09-02, depois do primeiro passo. **A secção 4 assumia coisas
que não se verificaram**, e fica aqui o que se mediu em vez do que se supôs.

**`app/` não é a aplicação morta.** Onze ficheiros importam de lá —
`api/main.py`, `api/services.py` e oito testes. O `app/verdict.py` é o
veredicto que a página mostra em palavras antes de qualquer número. Arquivá-lo
partia a API.

**`thesis/` não é uma versão antiga esquecida.** Nove scripts de avaliação
escrevem as figuras para `thesis/figures/`, e o `ci.yml` filtra por esse
caminho. Só que a dissertação viva, a `tese-v2`, lê de `tese-v2/figures/`.

Isso é um defeito por si só, e não de arrumação: **o pipeline que gera as
figuras aponta para uma árvore, e o documento que as usa lê de outra.** Quer
dizer que correr um `evaluate_*.py` hoje não actualiza nenhuma figura da
dissertação — as que lá estão foram copiadas à mão em algum momento. É um
alvo óbvio de pergunta na defesa («como é que as figuras são geradas?»), e é
trabalho da frente 05, não desta.

**`thesis-pt/`, `slides/`, `paper/` e `progress/`** têm todos quem os chame:
`check_all_gates.py` lê o *frontmatter* do `thesis-pt`, o
`make_public_bundle.py` lista `progress/` e `slides/` como exclusões, e o
`ci.yml` filtra por `slides/**` e `paper/**`.

### Consequência para o plano

Passa a haver duas metades, e só a primeira é arrumação:

| Metade | O que é | Risco | Quando |
|--------|---------|-------|--------|
| **A — arrumar** | tirar `tmp/` do índice, criar `archive/`, mover o que não tem quem o chame, tirar os ficheiros soltos da raiz | nenhum: nada referencia o que se move, e o que referenciava foi reescrito e verificado | ✅ feito a 2026-09-02 |
| **B — repontar** | `code/`, e reduzir as cinco árvores de tese a uma | real: obriga a mudar ~10 scripts, o `ci.yml` e os caminhos de compilação | **depois das frentes 05 e 07**, que são as que ainda escrevem nesses caminhos |

A razão de adiar a metade B é a mesma que antes fazia adiantá-la, aplicada a
factos novos: mover ficheiros que ninguém chama é seguro em qualquer altura;
mudar dez scripts que alimentam as figuras da dissertação, enquanto as frentes
05 e 07 ainda estão a mexer nessas mesmas figuras, é criar conflitos com as
minhas próprias mãos. A metade B faz-se quando o conteúdo parar de se mexer.

**O que a metade A já deu**, em números: 406 ficheiros e 66 MB fora do índice,
17 ficheiros `.md` na raiz reduzidos a 3, e 23 pastas na raiz reduzidas a 17.

## 6. Ordem de execução

O trabalho é feito por passos, e cada passo só fecha se a verificação
passar. Nenhum passo avança com o anterior partido.

| Passo | O quê | Verificação |
|-------|-------|-------------|
| 1 | `git rm --cached -r tmp/`, `.gitignore` | `git ls-files tmp \| wc -l` → 0 |
| 2 | Criar `archive/`, mover com `git mv` | `git status` mostra renomeações, não pares apagado/novo |
| 3 | Mover o código para `code/` | `pytest` verde (toda a suite) |
| 4 | `Procfile`, `pyproject.toml`, `.github/workflows/*` | *deploy* para o Heroku e o painel responde |
| 5 | `tese-v2` → `dissertation/thesis` | a tese compila: 0 erros, 0 referências por resolver |
| 6 | Reescrever o `README.md` para a árvore nova | leitura |

`git mv` em vez de mover e voltar a adicionar: o Git deteta a renomeação e o
histórico de cada ficheiro sobrevive. Se a mudança for feita à mão, o
`git log --follow` deixa de encontrar o passado dos ficheiros — e num
repositório que é para ser visto, isso é perder o rasto do trabalho.

---

## 7. Quando

**A seguir à frente 03 (o painel v7), antes da frente 04.**

O pedido chegou a meio da frente 03 e a regra dele é que a sequência se
respeita, portanto a v7 fecha primeiro. Mas a seguir vem esta, e não no fim
da fila, por um motivo que não é de arrumação:

as frentes 05, 07 e 08 escrevem dentro de `tese-v2/`, das figuras e do guia
de defesa. Se a mudança de sítio ficar para o fim, o último dia útil antes
da entrega inclui mexer nos caminhos de compilação da tese. Feita agora, há
duas ou três semanas para dar por partido o que se partir, e uma suite de
testes e uma compilação para o dizer no próprio dia.

Fazer arrumação com pressa, em cima de uma entrega, é como se perdem
entregas.
