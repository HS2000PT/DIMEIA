# Backlog do aluno — pedidos por trabalhar

> **Estatuto: por analisar.** Registado a **2026-08-05**, tal como o aluno o ditou, para não se
> perder na mudança de sessão ou de máquina. **Nada aqui foi pensado, estimado ou decidido** — é
> a lista em bruto, e é de propósito que está em bruto: analisá-la agora seria decidir sozinho
> coisas que ele quer decidir depois.
>
> Ordem = a ordem em que foi ditada, não prioridade.

---

## 1. Refazer o painel por completo

Tecnologias novas, estudo de mercado, usabilidade talhada para o utilizador. Interface
**premium**: responsividade, desempenho, moderno, *drill-downs*, estados de *hover*, cliques,
detalhe. **Interactivo.**

*Já existe material para arrancar, e é só isto que registo:*
[`docs/design/PROMPT_dashboard_v4.md`](../docs/design/PROMPT_dashboard_v4.md) (briefing para uma
sessão nova) e o estudo de mercado que **completou** na sessão 49 — 4 agentes, resultado em bruto
no `journal.jsonl` da corrida `wf_c5217b07-1db`. A conclusão que ficou registada no `CLAUDE.md`:
o custo não é CSS nem afinação do Streamlit, é **carga a frio**, e a recomendação era
**pré-computar para um *snapshot* estático** no worker de 60 s.

## 2. Rever a revisão de literatura por completo

Com **o PDF real de cada referência numa pasta do repositório**, e um documento que diga
**exactamente o que foi extraído e de onde**.

⚠️ **Uma restrição que ele vai precisar de saber quando pensar nisto, e por isso fica escrita
aqui em vez de ser descoberta depois:** o repositório é **público** e os PDFs são material com
direitos de autor. Versioná-los transformaria uma auditoria de integridade numa violação de
copyright. A infra-estrutura já está montada com esse cuidado:
[`docs/decisions/citation_pdfs/`](../docs/decisions/citation_pdfs/) existe, tem README com a
lista exacta do que descarregar, e os `*.pdf` estão **gitignored**. Ou seja: os PDFs podem viver
na máquina e ser lidos; o que vai para o repositório é o **relatório** da extracção.
Se ele quiser mesmo os ficheiros versionados, a saída é **tornar o repositório privado** — e isso
tem consequências já medidas (parte a app em silêncio, limita minutos do Actions), registadas em
[`v3_backlog.md`](../docs/design/v3_backlog.md). **É decisão dele, não minha.**

*Estado actual, para ele saber de onde parte:* metadados **84/84** verificados por script;
conteúdo **129/129 instâncias, 59/59 chaves**; paridade EN↔PT **0 assimetrias**. O que falta é o
que ele está a pedir: o **texto integral** de cada fonte lido e a extracção registada.
Das 59, **44 são legíveis sem conta nenhuma**; **14 precisam da conta ISEP** (lista no README
acima, com prioridade indicada).

## 3. Melhorar a latência dos alertas (quase tempo real)

**Sintoma dado por ele:** ontem foi notificado **depois** de o acontecimento já ter ocorrido no
mundo real.

*Sem análise, só o que já está registado e é relevante:* o worker corre a **60 s** desde a sessão
44; antes era o cron do GitHub, medido em **1,5–2 h**. A mediana de latência mostrada
(**208 min, n=44**) ainda **inclui o histórico do cron antigo**, portanto o número no ecrã e a
latência actual não são a mesma coisa.

## 4. Melhorar o guia de estudo

(86 slides hoje.) Sem mais detalhe dado.

## 5. Rever a escrita

**Humana, jovem, natural** — e que **não seja apanhada por detectores de IA**.

⚠️ **Nota de integridade que fica registada porque a regra do projecto obriga:** a declaração
honesta de uso de IA no *front matter* **mantém-se**. O pedido é sobre **voz e naturalidade do
texto**; não é, e não pode virar, encobrir o uso de IA. Já houve uma passagem destas na sessão 41
com exactamente esta fronteira: limparam-se os *tells* de meta-comentário defensivo e a
declaração ficou intacta.

## 6. Quaisquer pendências que restem nos TODOs do repositório

Varrer [`CHECKLIST.md`](../CHECKLIST.md), os `TODO` no código e nos `.tex`, e o que sobrar do
[`v3_backlog.md`](../docs/design/v3_backlog.md).

---

## O que já estava em fila antes disto (não apagar)

Da sessão 49/50, por ordem:

1. **Arrumação do repo** — feita em parte a 2026-08-05: `progress/_historico/` criado com os três
   planos superados, `progress/README.md` novo, `dashboard_v2_design.md` marcado como superado,
   0 links relativos partidos. **Falta** varrer o resto de `docs/design/` (27 ficheiros).
2. **Demo e notificações** — [`docs/defence/gravar_demo.md`](../docs/defence/gravar_demo.md) já
   tem o guião de 3 min. Falta gravar, e falta a captura das **notificações push no telemóvel**,
   que ele pediu explicitamente e ainda não tem procedimento escrito.
3. **Humano, e nenhum destes sou eu que faço:** enviar a tese ao orientador; rodar as 3
   credenciais expostas (PAT do GitHub primeiro, tem `admin: true`); mudar o *Main file path* no
   Streamlit Cloud para `app/dashboard.py`; estudo de utilidade (6–10 pessoas); agradecimentos;
   licença e redacção da declaração de IA com o orientador.
