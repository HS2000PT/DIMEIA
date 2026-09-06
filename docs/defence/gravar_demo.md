# gravar_demo.md — Guião da demonstração (3 minutos) — **SUPERADO**

> 🛑 **Não uses este.** Há dois guiões de gravação no repositório e contradizem-se: este manda
> percorrer ecrãs que o serviço implantado já não serve, e abrir exactamente a página que o guião
> novo manda evitar.
>
> **O guião a usar é o [`tese/GRAVACAO.md`](../../archive/thesis-versions/tese-pt-v1/GRAVACAO.md)**: 2m30, três partes, alinhado
> com os 22 slides e com o que está no ar.
>
> Este fica como registo de como a demonstração era pensada antes, e porque mudou.

> **Porquê gravar.** Numa defesa, uma demo ao vivo depende de rede, de um free tier e de um
> agendador que não controlas. Uma gravação não depende de nada. Levas as duas: abres a app ao
> vivo se estiver bem, e tens o vídeo se não estiver. **Grava mesmo que aches que não precisas.**

---

## Antes de gravar (10 minutos)

1. **Abrir a app.** <https://investigator-ddc9d8618935.herokuapp.com/>
   Desde 2026-08-02 corre no Heroku num dyno *Basic*, **sempre ligado**: já não hiberna, e
   não precisas do truque de a visitar antes para a acordar. Confirma na mesma que carrega.
2. **Confirmar que há o que mostrar.** O ecrã *Today* precisa de pelo menos um nome que se
   destaque. Se o dia estiver morto, grava noutro dia ou usa a captura já guardada
   (`thesis/figures/app_dashboard.png`) como plano C.
3. **Sondar o narrador**, se o fores mostrar: `python scripts/probe_llm.py`. Se der vermelho,
   **não mostres o narrador** — o sistema cai no texto determinístico e a demo continua honesta.
4. **Limpar o ecrã:** fechar separadores, silenciar notificações, esconder a barra de favoritos.
5. **Zoom do browser a 110–125%.** O júri vê num projetor, não no teu portátil.

---

## O guião (3 minutos, cronometrado)

### 0:00–0:25 · A promessa
> *"Isto é o InvestiGator. Responde a três perguntas que qualquer investidor faz quando uma
> ação se mexe: isto é invulgar, é a empresa ou o mercado, e já aconteceu antes. Nunca prevê
> preços — é uma restrição de desenho, não uma limitação."*

Mostra o cabeçalho. A promessa está lá, uma vez.

### 0:25–1:15 · Today, e o momento que interessa
Aponta para a linha de um mover e lê a decomposição em voz alta:

> *"Esta ação caiu. Mas repare: a maior parte veio do mercado, e a contribuição da própria
> empresa foi [X]. Nenhuma ferramenta gratuita lhe diz isto. É a diferença entre 'a tua ação
> afundou' e 'o mercado caiu, a tua empresa não fez nada de invulgar'."*

Se apanhares um caso como o do AMZN (queda total, contribuição própria positiva), **usa-o**:
é o argumento mais forte que o produto tem.

Se a linha tiver **volume**, lê-o também: é a segunda metade da pergunta.
> *"E moveu-se com 3,2 vezes o volume habitual. Um movimento de 3% com volume normal e outro com
> o triplo do volume não são o mesmo acontecimento. Quando o volume é normal, o sistema não diz
> nada — o silêncio também é informação."*

Depois aponta a linha *Quiet*:
> *"Os nomes que não se destacaram colapsam aqui. O silêncio é legível."*

### 1:15–2:00 · Ticker, e a evidência
Clica num ticker. Mostra a decomposição por extenso e, sobretudo, os alertas:

> *"Estes são os alertas exatamente como o canal Telegram os enviou. A app não recalcula nada:
> lê o mesmo registo. Se o canal e a app discordassem, um dos dois estaria a mentir."*

Abre um alerta de notícia com precedentes e diz a frase que desarma a pergunta óbvia:
> *"Isto não é uma previsão. São casos passados semelhantes no TEMA, e o tema não é a direção —
> a tese mede isso: a consistência de direção fica no chão do acaso."*

### 2:00–2:35 · Method, a honestidade
> *"Este ecrã existe para o cético. Estão aqui os números congelados, incluindo o negativo:
> nenhum modelo com texto bateu a linha de base de volatilidade. Está reportado tal como caiu."*

### 2:35–3:00 · A latência, dita por ti antes de ta perguntarem

⚠️ **Este guião foi reescrito a 2026-08-07, e a versão anterior punha-te a dizer uma coisa
falsa.** Ela mandava-te explicar um número alto com *"a mediana ainda inclui o agendador antigo e
vai descer à medida que o histórico se renova"*. Isso foi **medido e é falso**
([`evaluation_latency.md`](../evaluation/evaluation_latency.md)): separando as duas eras, a mediana
a mediana do agendador é de ~196 min e a do processo permanente de ~402 min, ou seja o
ciclo mais curto **não** reduziu a latência observada. ⚠️ Este próprio parágrafo já ensinou
o contrário — dizia que descia para ~143 min — e a medição sobre a série completa
inverteu-o. Se disseres qualquer das frases antigas, um arguente que abra o documento
apanha-te.

**O ecrã mostra agora duas medidas, e é isso que torna a resposta forte:**

> *"A latência está decomposta de propósito, porque um número agregado não distingue duas coisas
> com consequências opostas. Do lado do sistema — da deteção até à entrega — a mediana é de **cinco
> segundos**. Da publicação até à deteção são **353 minutos** de mediana, e isso é a fonte
> gratuita a listar tarde, mais o facto de o título mais recente que passa o filtro de
> relevância ser tipicamente mais velha do que a mais recente do feed."*

Se te perguntarem se o ciclo de 60 segundos valeu a pena, a resposta honesta é a mais
interessante que tens:

> *"A medição não confirma a expectativa que motivou a alteração. Assumi que a mediana alta era
> contaminação do agendador antigo; medida a série completa, o agendador tem 196 minutos e o
> processo permanente 402. Não digo que o ciclo piorou, porque a comparação não isola o ciclo:
> as duas configurações não operaram em paralelo, entre elas mudaram as fontes e o período, e as
> amostras são de 28 contra 250. O que fica estabelecido é que encurtar o ciclo só paga se o
> tempo estiver na cadência com que consulto a fonte, e não está."*

O argumento é o mesmo e é o que interessa: **a latência é uma quantidade medida do facto até à
entrega, não uma promessa**, e foi por ter sido instrumentada antes que a medição pôde contrariar
a minha própria expectativa em vez de a confirmar.

Fecha aqui. Não mostres o Telegram ao vivo a menos que sobre tempo.

---

## Como gravar

- **Windows:** `Win + G` (Xbox Game Bar) grava a janela do browser sem instalar nada. Alternativa
  melhor: OBS Studio (grátis).
- **Resolução:** 1920×1080. **Não** graves o ecrã inteiro se tiveres dois monitores.
- **Áudio:** grava a tua voz. Uma demo muda obriga o júri a ler e a ouvir-te ao mesmo tempo.
- **Sem cortes.** Uma tomada única é mais credível do que uma montagem. Se te enganares, recomeça.
- **Guarda em dois sítios** (portátil + pen ou nuvem). Testa que abre no computador da sala, se
  puderes.

---

## Se algo correr mal na sala

| Falha | O que fazes |
|---|---|
| A app não abre | Passas ao vídeo. Uma frase: *"tenho aqui a gravação"*. Sem pedir desculpa. |
| A app está lenta a abrir | Normal na primeira visita após um deploy. Espera 10 s antes de assumir que falhou. |
| Sem rede | Vídeo, que está no disco. |
| O dia está calmo e não há movers | É um estado válido do produto: *"hoje não se destacou nada, e o sistema di-lo em vez de inventar"*. |
| O narrador não responde | Não se nota: o alerta sai com o texto determinístico. Foi desenhado assim. |
| Perguntam pelo Telegram | Abres o canal no telemóvel. Se falhar, os alertas estão no ecrã *Ticker*, que é o mesmo registo. |

---

## O erro a não cometer

Não uses a demo para provar que o produto é bonito. Usa-a para provar **uma** coisa: que o
raciocínio é verificável de ponta a ponta, do número no ecrã até ao registo que o gerou. É essa a
tese. A app é a prova, não o argumento.
