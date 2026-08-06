# Prompt para uma sessão nova: repensar o painel do zero

> **Como usar.** Abrir um Claude Code novo na raiz deste repositório e colar **tudo** o que
> está abaixo da linha. Foi escrito por quem construiu a v3 e já não consegue vê-la com
> olhos limpos — o enviesamento é real e está declarado no próprio prompt.

---

Estás a pegar num projecto que já existe e a **repensar uma camada dele do zero**. Lê este
briefing por inteiro antes de escrever uma linha de código.

## 1. O que é o projecto

Dissertação de Mestrado em Engenharia Informática — Inteligência Artificial (ISEP), a
entregar a **13 de Setembro de 2026**. Chama-se **InvestiGator**: alertas financeiros
explicáveis para investidores de retalho, sobre 12 empresas dos EUA.

O sistema responde a três perguntas, por esta ordem:

1. *Isto é invulgar, ou é normal para esta acção?*
2. *É esta empresa, ou é o mercado inteiro?*
3. *Já aconteceu algo parecido antes, e o que se seguiu?*

**A restrição fundadora: o sistema nunca prevê preços.** Descreve o passado e mede
desfechos observados. Isto não é uma limitação técnica, é a posição do trabalho, e está
argumentada na tese.

## 2. O que NÃO se toca

O motor está feito, avaliado e congelado. **Não é isso que está em causa.**

- `investigator/` — detecção de anomalias, recuperação semântica, decomposição de
  movimento, triagem, narrador. Funciona e está medido.
- `models/`, `docs/evaluation/evaluation_{triage,results,anomaly}.md` — **artefactos
  congelados, byte-a-byte**. Se um `git diff` os tocar, algo correu mal.
- `scripts/run_alerts.py` e o canal Telegram — o produtor de alertas.
- A tese, os slides e o guia de estudo — só se sincronizam **depois** de uma decisão de
  promoção, nunca durante a exploração.

**O que está em causa é só a camada de apresentação:** hoje `app/dashboard.py`, em
Streamlit.

## 3. Porque é que estás a ser chamado

O aluno rejeitou **sete** versões da interface. A mais recente (v3) está em produção e a
avaliação dele é:

> *"too laggy. too zoomed out. not responsive enough. not cool UX/UI design. very
> old-school and static. there are many more and better more modern architectures and
> technologies and methodologies for websites (panels, dashboards) nowadays, that guarantee
> less latency, better usability and faster movement."*

E, textualmente, sobre quem escreveu isto:

> *"since you are kinda biased already, I suggest you write me an ultimate prompt that I can
> run on a new chat from scratch."*

**Ele tem razão nas duas coisas.** Quem escreveu este prompt desenhou a v3 e defende-a por
construção. Trata a v3 como **uma hipótese que falhou**, não como a linha de base a
melhorar.

## 4. A ordem de trabalhos, e ela não começa em código

### 4.1 Primeiro: estudo de mercado a sério

**Não abras um editor antes disto.** Procura na web (estás em 2026 — usa fontes de 2025-26,
não de memória) e responde com evidência:

- Que padrões usam hoje os painéis financeiros que as pessoas realmente escolhem?
  Olha para produtos concretos e diz o que fazem: TradingView, Bloomberg Terminal Web,
  Koyfin, Finviz, Yahoo Finance, Robinhood, Perplexity Finance, worldmonitor.app.
- O que é que **um utilizador não profissional** consegue extrair em 10 segundos em cada um?
- Quais são os padrões de *dashboard* de 2026 que reduzem latência percebida —
  *streaming* de dados, actualização optimista, *skeleton states*, *virtual scrolling*,
  transições que dão continuidade em vez de repintar o ecrã?
- Que arquitecturas se usam hoje para isto e que compromissos trazem?

**Entrega desta fase:** `docs/design/market_study_v4.md`, com fontes ligadas e uma tabela
que separe *o que é transferível para 12 tickers e um utilizador leigo* do *que é escala que
este projecto não tem*. Sê explícito sobre o que **não** copiar.

### 4.2 Segundo: questiona a tecnologia, com números

O Streamlit repinta o servidor inteiro a cada interacção. Boa parte das queixas
(«lento», «estático») é disso, não de CSS. **Estás autorizado a propor sair do Streamlit.**

Avalia honestamente, com prós e contras, e mede se conseguires:

- ficar em Streamlit e optimizar (fragments, caching, componentes próprios);
- **FastAPI + front-end moderno** (React/Svelte/SolidJS), com o `investigator/` como
  biblioteca — a separação mais limpa, e a que dá controlo real de UX;
- geração estática com actualização incremental (Observable Framework, Evidence.dev);
- híbrido: API leve + uma página com *islands*.

**Critérios de decisão, não gosto:** tempo até ao primeiro pintar, custo de uma interacção,
se corre num dyno Heroku de 512 MB, e quanto trabalho é migrar. Se recomendares mudar de
stack, mostra um protótipo pequeno a provar o ganho **antes** de reescrever tudo.

Restrições reais: só APIs gratuitas; um dyno Basic de 512 MB; a app tem de arrancar sem
chaves de API; e um utilizador tem de conseguir abrir um URL e perceber, sem instalar nada.

### 4.3 Terceiro: critérios de aceitação ANTES do código

Isto é inegociável e é a única coisa que travou o ciclo de redesenhos. Lê
`docs/design/dashboard_acceptance.md` (§6 tem os critérios da v3) e escreve os teus, novos,
em `docs/design/dashboard_v4_acceptance.md`, **antes** de programar. Cada critério tem de ser
verificável por um teste ou por uma medição — nunca por opinião. Sem condição de paragem
escrita, esta será a oitava versão rejeitada.

## 5. As regras de honestidade — herdadas e não negociáveis

Vêm da tese e a violação de qualquer uma invalida o trabalho:

| # | Regra |
|---|---|
| **H1** | A promessa do produto aparece **uma** vez, não repetida em cada painel |
| **H2** | **Zero números previstos.** Sem alvos de preço, sem recomendações, sem "movimento esperado". Isto inclui a probabilidade da triagem, que é um número sobre o futuro |
| **H3** | Precedentes sempre com a moldura *tema ≠ direcção* — parecido no assunto não é parecido na direcção |
| **H4** | **Nenhum score que a medição não sustente.** Proíbe hoje o score de convergência fundido (ganha em 1 de 3 orçamentos) e os crachás de tipo de evento (silhueta 0,084) |

Mais três, do projecto:

- **Nunca fabricar.** Nenhum dado, número, citação ou resultado inventado. Se não foi medido,
  não se escreve. Um resultado negativo reporta-se tal como caiu.
- **Interface só em inglês.** O código e os comentários são PT-PT; o que o utilizador lê é EN.
- **Falhar aberto, mas em voz alta.** Uma fonte em baixo tira uma linha do ecrã, nunca o ecrã
  inteiro — e o ecrã diz que falta, em vez de mostrar um vazio que parece normal.

## 6. Sete lições que este projecto pagou caro

Não as redescubras:

1. **Verifica a renderizar, não nos logs.** Um `200` já apareceu numa página que era
   inteiramente um erro. Todas as afirmações visuais confirmam-se por captura (Playwright
   está instalado), a 1920×1080 **e** a 1366×768.
2. **Testa o comando que o utilizador escreve.** A app foi "verificada" com
   `python -m streamlit`, que acrescenta o directório actual ao `sys.path`; o comando normal
   rebentou com `ModuleNotFoundError`.
3. **Um commit não é uma implantação.** `git push origin` vai para o GitHub, que não implanta
   nada. Confirma com `heroku ps`. Ver `docs/design/heroku_setup.md`.
4. **A "magia" do Streamlit desenha qualquer expressão solta do script principal, mesmo
   dentro de funções.** Um `a.append(x), b.append(y)` pintou 253 caixas `(None,None,None)`
   por cima de um gráfico.
5. **O tema do Streamlit (`.streamlit/config.toml`) governa os componentes dele.** Enquanto
   discordava do CSS da app, havia texto escuro sobre fundo escuro que voltava sempre que se
   acrescentava um componente.
6. **Uma lista de palavras proibidas perde nos dois sentidos.** Acusou "price target" numa
   frase que dizia *"No price targets"*.
7. **Um painel vazio é um painel válido para os testes.** O ecrã de detalhe já abriu sem
   nada do que existe para mostrar, com todos os testes verdes. Só a captura deu por isso.

## 7. Repensa também a lógica, não só o aspecto

O aluno pediu isto explicitamente: *"the logic of functionalities should be reviewed, and the
steps, and the way data is presented"*. Ou seja — **não assumas que a informação de hoje é a
informação certa**. Pergunta o que resolve mesmo o problema de quem olha, o que dá mais
informação em menos tempo, e o que só está lá por inércia.

Material que existe e que podes usar (ou decidir não usar, com razão escrita):
z-score contra os 20 dias anteriores; contagem empírica de excedências no último ano;
repartição mercado/sector/empresa com encolhimento de Vasicek; volume invulgar; precedentes
por semelhança semântica com o impacto medido a +1/+3/+5 dias; ~38 mil notícias com impacto
medido; 240+ alertas reais enviados; o funil de gates; deriva; predição conformal.

## 8. Como saber que acabaste

- Os critérios que **tu** escreveste em §4.3, todos verificados.
- `pytest` verde (~626 testes hoje) e `ruff check .` limpo.
- `git status --porcelain models/ docs/evaluation/evaluation_{triage,results,anomaly}.md`
  **vazio**.
- Capturas nas duas resoluções, comparadas lado a lado com a v3.
- Uma medição de latência **antes e depois**, porque «mais rápido» sem número é opinião.
- A app actual continua a servir até a nova passar tudo. Constrói **ao lado**.

## 9. Uma última coisa

O aluno está a semanas da entrega e já foi desapontado sete vezes por esta camada. **Não
prometas.** Mostra pequeno, cedo, e mede. Se o estudo de mercado concluir que a v3 já está
próxima do que é razoável com estas restrições, **diz isso** — é uma conclusão legítima, e
mais útil do que uma oitava reconstrução para ser rejeitada.
