# Revisão de Produto / UX — InvestiGator (Pass 5)

> Avaliação crítica do **produto** (não da escrita), nas vozes de gestor de produto, especialista de UX,
> arquiteto de software e utilizador real. Objetivo: encontrar o que ajudaria/frustaria um investidor de
> retalho **não-especialista**, com **honestidade** — nada de funcionalidades irreais, nada de prometer o
> que não está construído. Severidade: Crítico / Maior / Moderado / Menor.
> Companheiro de
> `page_audit.md` (citações). Data: 2026-06-27.

## Resumo
InvestiGator resolve um problema real (dar **contexto** aos eventos que já captam a atenção do investidor) e tem
uma postura de produto saudável: **informa, não aconselha**; é transparente; é gratuito; entrega por um canal
ubíquo (Telegram). O principal risco de produto não é a falta de funcionalidades — é a **compreensão**: expor
estatísticas em bruto a um não-especialista é *transparente* mas não necessariamente *compreensível*. Abaixo,
os achados; os de produto já refletidos na tese estão marcados.

---

## Achados

### P-1 — Lacuna de compreensão: estatística em bruto ≠ explicação para leigos — **Maior**
**Problema.** O alerta de mercado expunha `z-score +7.61`, `σ 2.73%`; o de notícia expõe `sim 0.68`. Para o
público-alvo (não-especialista), "z-score" e "similaridade do cosseno" são jargão. Transparência (mostrar o
número) não é o mesmo que compreensão (saber o que significa).
**Porque importa.** O valor da ferramenta e a *confiança calibrada* (Lee & See 2004) dependem de o utilizador
**perceber** o alerta; uma explicação não compreendida não calibra a confiança.
**Recomendação.** Traduzir cada número em linguagem simples, mantendo o número (rigor + leigo).
**Implementado (parcial).** O motor de explicação passa a render­izar o z-score em linguagem simples
("cerca de 7,6× a oscilação diária típica desta ação, muito além da volatilidade normal") — ver
`explain_anomaly` e o novo teste; refletido numa cláusula do Cap. 4. **Recomendado (futuro):** fazer o mesmo
para a similaridade (banda qualitativa: "muito semelhante / semelhante / pouco semelhante" em vez de 0,68).

### P-2 — Fadiga de alertas (volume/over-alerting) — **Maior** *(já em trabalho futuro na tese)*
**Problema.** Uma ferramenta que dispara demasiado treina o utilizador a ignorá-la.
**Recomendação.** Ranking por severidade (magnitude do |z|), *rate-limiting* dos menos importantes,
agregação diária. **Estado:** discutido no Cap. 4 (produto responsável) e Cap. 6 (trabalho futuro). Não
construído — honestamente assinalado.

### P-3 — Sobre-confiança / clusters de direção mista — **Maior** *(já tratado nesta revisão)*
**Problema.** A semelhança capta **tema, não direção**: um título positivo pode recuperar precedentes
negativos e a média mascara o desacordo, induzindo sobre-confiança (Bansal 2021).
**Recomendação.** Mostrar sempre os precedentes individuais e o *spread*; **sinalizar discordância de
direção**; de-duplicar precedentes quase iguais. **Estado:** mostrar precedentes+spread está construído; o
*flag* de direção e a de-dup estão como trabalho futuro (Cap. 4/5/6 + paper + slides + caderno).

### P-4 — Acionabilidade vs. âmbito (informar, não aconselhar) — **Moderado (limite de desenho)**
**Problema.** O utilizador pode perguntar "então o que faço?". O alerta termina com "não é previsão".
**Análise.** É um **limite de desenho deliberado** (decisão-suporte, não consultoria; restrição §5.2), não um
defeito. Deve ser **enquadrado**, não "resolvido": o produto reduz o custo de *interpretar*, deixando a
decisão ao utilizador. Já explícito na tese; manter.

### P-5 — Casos-limite operacionais — **Moderado**
**Problema.** Notícia em dia não-útil (tratado: 1.º dia de negociação ≥ data); sem precedentes (tratado:
mensagem dedicada); horizonte além da série (tratado: n/a em vez de inventar); **falha de fornecedor / KB
desatualizada** (não tratado: protótipo sem recuperação automática).
**Recomendação.** Em produção: *fallback* de fonte (já há 2.º fornecedor de preços previsto), *health-check*
da KB, *retry* com *backoff*. **Estado:** limites de protótipo já declarados no Cap. 4 (uso prático).

### P-6 — Escala e manutenção — **Menor** *(coberto)*
Procura exata é O(N) sobre a KB; caminho de escala = índice ANN (FAISS), já citado e como trabalho futuro.
KB reconstruída por script; sem persistência além do ficheiro — declarado.

### P-7 — Acessibilidade e privacidade — **Menor (força)**
Alertas só-texto via Telegram são compatíveis com leitores de ecrã e baratos em dados; sem contas, sem dados
pessoais processados. É um ponto **positivo** do desenho que vale a pena saber nomear na defesa.

---

## Veredito (Pass 5)
O produto é coerente com o seu propósito e honesto sobre os seus limites. A melhoria de produto de maior
alavancagem é a **compreensão para leigos** (P-1), agora parcialmente implementada (gloss do z-score) e
recomendada para a similaridade. As restantes (fadiga, sobre-confiança, casos-limite) já estão refletidas na
tese como considerações de desenho/trabalho futuro, sem sobre-afirmar o que não foi construído. Nenhuma
funcionalidade irreal foi proposta.

---

## Pass 6 (2026-07-08/09) — Redesenho para painel único, uso real ao vivo

**Motivo.** Depois de dias a usar o sistema a sério, o aluno reportou 3 problemas concretos: (1) quase nunca
recebia alertas de mercado; (2) a linha de materialidade era jargão ilegível; (3) o Streamlit tinha "lixo a
mais" (8 páginas) e não refletia o modelo TREINADO por ele — sentia que o produto tinha ido por um caminho
diferente do que a tese/visão pedia. Pergunta direta feita e respondida com evidência: a tese **não** prende
nenhuma estrutura de UI específica (verificado: só menciona "an interactive dashboard" uma vez + um mockup
desenhado do Telegram) — o pivô de produto não invalida nada da ciência avaliada.

### P-8 — Threshold de produção longe de "vivo" — **Crítico, corrigido**
`threshold=3.0` é o valor AVALIADO na tese (frozen) mas estatisticamente raro num board de 10 tickers em
produção (~1-3%/ticker/dia). **Corrigido:** `config/alerts.yaml` → `threshold=2.0`, divulgado como parâmetro
de implantação distinto da avaliação académica (que nunca muda). Validado ao vivo (dry-run disparou um
alerta real).

### P-9 — Jargão na linha de materialidade — **Maior, corrigido**
"Top factors: sector (+)" não é legível por um leigo. **Corrigido:** `materiality_line` reescrita em
linguagem simples ("raised by X and Y; lowered by Z").

### P-10 — Telegram e Streamlit podiam divergir silenciosamente — **Crítico, corrigido**
Cada superfície recalculava os alertas de forma independente — sem histórico partilhado, podiam discordar, e
a app não tinha memória de dias anteriores. **Corrigido:** novo `investigator/alerts_history.py` + branch
`alerts-history` (dados, escrita pelo workflow) + `fetch_remote()` na app — as duas superfícies leem o MESMO
registo; nunca recalculam.

### P-11 — O modelo treinado ficava escondido — **Maior, corrigido**
A triagem (RQ4, o único componente treinado pelo aluno) só aparecia num painel secundário, só para notícias.
**Corrigido:** novo `score_background()` pontua TODOS os dias, sem notícia — "Background risk" é agora um
elemento permanente de cada aba de ticker no painel único.

### P-12 — Demasiadas páginas, navegação confusa — **Maior, corrigido**
8 páginas (Home/Live/News/Market/Evaluation/How/About/Alerts) reescritas para **UMA** página com abas por
ticker (gráfico Plotly anotado + tabela de histórico + risco); "Method & evaluation" fica num único
`st.expander` no fundo, decisão confirmada com o aluno (não removido — só decluttered).

**2 bugs reais apanhados pelos testes ANTES de produção:** IDs de gráfico Plotly colidiam entre abas
(mesma chave auto-gerada); `st.expander` aninhado dentro de outro (Streamlit não permite). Ambos só
apareceram ao correr o AppTest a sério — reforça o valor de testar a UI, não só a lógica.

## Veredito (Pass 6)
O pivô de produto é legítimo e não custa nada à ciência da tese (verificado, nada reescrito no Cap. 1-6 além
de uma frase de cadência já desatualizada). Os 5 achados críticos/maiores reportados pelo aluno foram
corrigidos e validados (testes + AppTest + arranque real do servidor + captura de ecrã genuína). Continua
sem funcionalidade irreal proposta; o histórico partilhado só mostra o que foi realmente enviado.
