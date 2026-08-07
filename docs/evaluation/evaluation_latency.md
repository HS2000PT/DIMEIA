# Latência facto → notificação, decomposta

> Gerado por `python scripts/evaluate_latency.py --escrever`. Não editar à mão.

Histórico partilhado: **308 entradas**, das quais **101** têm hora de publicação e de envio (só alertas de notícia as têm). Janela de envio: 2026-07-29 a 2026-08-07.

## O resultado, e ele contradiz a explicação que estava registada

| componente | mediana |
|---|---|
| **total** (publicação → entrega) | 158 min (p90 430 min, máx 776 min, n=101) |
| descoberta (publicação → detecção) | 158 min (p90 430 min, máx 776 min, n=101) |
| pipeline (detecção → entrega) | 1 s (p90 2 s, máx 30 s, n=101) |

**A descoberta é 100% da mediana total. O nosso lado do sistema custa 1 s.**

A hipótese que estava escrita no projecto era que a mediana mostrada estava contaminada pelo histórico do cron do GitHub Actions e que a latência actual seria muito melhor. Separando as duas eras:

| era do produtor | total | descoberta | pipeline |
|---|---|---|---|
| cron (Actions, best-effort) | 196 min (p90 576 min, máx 776 min, n=28) | 196 min (p90 576 min, máx 776 min, n=28) | 1 s (p90 2 s, máx 6 s, n=28) |
| worker 60 s (≥2026-08-02) | 143 min (p90 360 min, máx 690 min, n=73) | 143 min (p90 360 min, máx 690 min, n=73) | 1 s (p90 2 s, máx 30 s, n=73) |

Passar de um cron best-effort de 1,5–2 h para um ciclo de 60 s **não** trouxe a latência para a ordem dos minutos. Encurtar o ciclo só paga se o tempo estiver na descoberta **por causa da cadência do produtor** — e não está.

## Então onde está o tempo

Com o worker a 60 s, uma manchete que esteja no feed é vista em menos de um minuto. O que a medição mostra é que, quando o alerta sai, a manchete **já é velha**, e há três causas possíveis, por ordem do que este número consegue distinguir:

1. **A fonte lista tarde.** O Finnhub *company news* não é um canal em tempo real; uma história pode aparecer no feed horas depois da hora de publicação que ela própria declara. Isto é fora do nosso controlo e é a limitação já reportada em [`evaluation_news_coverage.md`](evaluation_news_coverage.md).
2. **A manchete mais recente do feed não é a mais recente RELEVANTE.** O filtro de relevância exige menção da empresa e rejeita boilerplate de mercado. Numa amostra ao vivo (2026-08-07, 14 h UTC) o feed da NVDA trazia 250 manchetes com a mais recente às 11:39, mas das 30 relevantes a mais recente era de **08:14** — mais de cinco horas antes. O alerta sai correctamente sobre a manchete certa; ela é que é velha.
3. **O tecto diário já foi gasto** — ver a secção seguinte. Este é um defeito separado, e é o único dos três que **apaga** histórias em vez de as atrasar, portanto não aparece nesta medição: um alerta que nunca sai não tem `sent_at`.

As três são diagnósticos diferentes e a primeira é a única que este histórico não consegue isolar sozinho: exigiria registar quando é que cada item apareceu no feed, não só quando foi publicado. Fica dito como o que é — **não medido** — em vez de atribuído por eliminação.

## O tecto diário: um segundo defeito, encontrado a medir isto

A investigação da latência destapou um defeito que não é de latência. A 2026-08-05 escreveu-se que o tecto diário passara a ser servido por **materialidade** em vez de por ordem de chegada. **Não passou.** A ordenação acrescentada vale dentro de um ciclo, e o scan de notícias emite **uma manchete por ticker por ciclo** — duas candidatas ao mesmo tecto (que é por ticker) nunca coexistem no lote, logo a ordenação nunca as pode reordenar. O teste que a validava comparava três manchetes do mesmo ticker numa só chamada, um cenário que a produção não sabe produzir.

A correcção (2026-08-07) é um **piso escalonado**: o k-ésimo alerta de um ticker no dia exige um P(movimento anormal) maior. Os pisos são derivados do varrimento de política — τ*(R=1)=0,49 para o primeiro, τ*(R=0,5)=0,64 para o segundo, onde o custo dominante passa a ser a fadiga. Não há piso de "última hora" acima disso porque o score máximo observado está entre 0,65 e 0,66: seria código morto com aparência de rigor.

**O que continua sem solução, e nenhum algoritmo online a tem:** o primeiro slot é gasto na primeira manchete que passe o gate, porque nesse momento a notícia da tarde ainda não existe. Não se reserva quota para uma história que ainda não se viu, nem se retira um alerta já entregue. O que se pode é tornar cada slot extra mais caro.

## Limite inferior, não estimativa

`event_at` é a hora que a **fonte declara**, não o instante do acontecimento no mundo. Um comunicado publicado 40 minutos depois do facto conta aqui como 0 minutos de atraso. Portanto todos os números acima são um **limite inferior** da latência que o utilizador sente.

## Consequência para o produto

O ganho de ciclo (1,5–2 h → 60 s) está medido e é real, mas é pequeno face ao total: a latência sentida é dominada por uma componente que não se compra com infra-estrutura. A afirmação defensável é **"o sistema entrega em segundos o que a fonte lhe dá"** (pipeline 1 s (p90 2 s, máx 30 s, n=101)), e não "o sistema alerta em tempo quase real".

