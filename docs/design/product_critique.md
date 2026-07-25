# Crítica honesta do produto — o que não chega, porquê, e o que fazer

> Documento interno (PT-PT). Pedido do aluno: "sê crítico". Escrito sem suavizar. Regra dura:
> melhorar o PRODUTO e a NARRATIVA, **nunca fabricar números**. A ciência congelada é o que é.
> Última revisão: 2026-07-25 (sessão 41).

## 1. O diagnóstico honesto (o que falha)

1. **"Notícia positiva → precedentes de queda" parecia uma contradição.** É o achado
   tema ≠ direção (Cap. 5, CS3): o retrieval encontra casos do mesmo TEMA, não da mesma
   direção. Um exemplo REAL do próprio corpus mostra-o: a manchete "Crude Awakening… Energy
   Sector Takes A 20% Spill" (AAPL, 2020-03-09) tem impactos +7,2% / −6,7% / −9,0% — o tema é
   um, a direção é mista. Mostrar só a MÉDIA era enganador. **→ corrigido nesta corrida**
   (mostra-se o split de direção e "not a prediction for this news").

2. **Os alertas são poucos e tardios, por isso "parece morto".** O cron do GitHub corre de
   facto de 1–2 h em 1–2 h; o critério de mercado era duro; a "história real" chega depois do
   movimento. Um canal calado lê-se como "não funciona". **→ mitigado**: estado do mercado ao
   vivo, badge de prova de vida ao topo, e **critérios agora ajustáveis** (painel de admin) —
   o investidor afina a sensibilidade sem tocar no código nem na avaliação congelada.

3. **A ciência é honesta mas modesta, e isso frustra.** A RQ4 pré-comprometeu-se e reportou
   que **nenhum modelo com TEXTO bate a volatilidade** na PR-AUC. O valor não está em prever —
   está na TRIAGEM (precisão@5/dia 0,632 vs 0,163; ao vivo 0,667 vs base 0,455) e na
   EXPLICABILIDADE. Se o produto se vende como "prevê", perde; se se vende como "evidência
   explicada, nunca previsão", ganha. **→ enquadramento reforçado** no texto dos alertas e na
   app.

4. **Os ícones confundiam.** As setas eram vermelhas nos dois sentidos. **→ corrigido**:
   📈 verde a subir, 📉 vermelho a descer.

## 2. O que já mudou nesta corrida (produto, não número)
- Clareza dos precedentes (split de direção + enquadramento honesto).
- Estado do mercado US ao vivo (aberto/fechado + contagem, DST correto).
- Badge "está vivo e a funcionar" (alertas entregues + precisão vs base rate, fora da amostra).
- Painel guest/admin: thresholds/critérios ajustáveis que **chegam aos alertas do Telegram**
  (fail-open; a avaliação da tese fica congelada e separada).
- Setas verdes/vermelhas; robustez (10 defeitos latentes corrigidos).

## 3. O que ainda falha e como atacar (roteiro, produto)
1. **Latência.** O cron é best-effort. → VM Oracle Free (guia pronto, `docs/design/vm_watch.md`)
   corta para minutos; ou reduzir o intervalo do fragmento da app. Custo: minutos do Actions /
   1 clique de setup humano.
2. **"A história chega tarde."** → o caminho intradiário já existe; dar-lhe mais peso na app
   (visão intradiária por defeito no gráfico) e um alerta de "movimento EM CURSO" mais cedo.
3. **Sensibilidade.** O default 1.5 de |z| pode ainda ser duro para dias calmos. → agora é
   ajustável no painel; medir a taxa de disparo real antes de mexer no default (não às cegas).
4. **Distribuição de precedentes, não média.** → mostrar um mini-histograma das direções dos
   precedentes (a app já tem o split textual; falta o visual).
5. **Confiança do utilizador.** → cartão "o que é / o que NÃO é" logo à entrada; glossário
   visual de 6 ícones; painel de saúde já ajuda.

## 4. O que NÃO vamos fingir (limites duros)
- **Não prevemos preços** (restrição fundadora §5.2). Qualquer "score de confiança preditivo"
  contradiz a tese E o próprio resultado da RQ4. Fora.
- **Não fabricamos resultados.** Os números da avaliação estão congelados e reproduzíveis. Se
  são modestos, dizemo-lo — é isso que dá credibilidade na defesa.
- **Não inflamos o canal.** Mais sensível ≠ spam; os limites do painel são conservadores e há
  tetos anti-fadiga.

## 5. Onde está o valor real para o investidor (a resposta franca)
O InvestiGator não é um oráculo; é um **investigador**: quando algo mexe ou sai uma notícia,
diz *o que* aconteceu, *o que* já aconteceu em casos parecidos (com a direção honesta), e
*porque* foi assinalado — em segundos, de graça, explicável, sem pedir confiança cega. Esse é
o produto defensável. A melhoria de "valor" faz-se tornando essa história **mais clara, mais
cedo e mais viva** — não inventando uma previsão que a tese, com integridade, recusa.
