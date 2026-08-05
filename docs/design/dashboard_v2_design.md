# dashboard_v2_design.md — o que copiar do worldmonitor, e o que não

> ⚠️ **ESTATUTO: SUPERADO (2026-08-04). Registo histórico — não dirige trabalho nenhum.**
> Esta é a v2, que o aluno **rejeitou por inteiro** ("usability is messy and confusing and
> dirty… re-do everything"). O que está implantado é a **v3** (`app/dashboard.py`, promovida na
> sessão 48), desenhada contra os critérios **V1–V8** de
> [`dashboard_acceptance.md`](dashboard_acceptance.md) §6 — que são outros.
>
> **Fica como registo por uma razão concreta:** a leitura do worldmonitor.app que está aqui foi
> o que produziu as duas ideias que a medição depois **derrubou** — o score de convergência
> (ganha em 1 de 3 orçamentos) e os crachás de tipo de evento (silhueta 0,084). Foi daí que
> saiu o critério **H4** ("nenhum score que a medição não sustente"), que continua a valer. O
> caminho até um "não" é defensável na defesa; apagá-lo deixaria só o "não".
>
> A reconstrução seguinte tem briefing próprio em
> [`PROMPT_dashboard_v4.md`](PROMPT_dashboard_v4.md).
>
> **Método:** em vez de redesenhar por gosto (o que já falhou cinco vezes por não ter condição de
> paragem), este desenho parte de uma leitura do worldmonitor.app e da pergunta *o que é que
> daquilo se aplica a dez tickers e a um utilizador que não é profissional?*

---

## 1. O que o worldmonitor faz, e o que disso é transferível

| Padrão do worldmonitor | Transferível? | Porquê |
|---|---|---|
| **Uma superfície densa**, tudo na mesma vista | ✅ **sim, é o principal** | A app atual tem três ecrãs com botões de rádio. Navegar entre ecrãs perde o contexto; o worldmonitor nunca te tira de onde estás. |
| **Dossiê ao clicar** (clicas num país, abre painel com tudo) | ✅ sim | Clicar num sinal do gráfico deve abrir o alerta completo ali, sem mudar de ecrã. |
| **Paleta de comandos** (⌘K, 154 comandos) | ✅ sim, reduzida | Saltar para um ticker ou intervalo sem aprender a interface. Com 10 tickers são ~20 comandos, não 154. |
| **Divulgação progressiva** ("viste talvez um décimo") | ✅ sim | Denso à primeira vista, detalhe só quando pedido. |
| **Proveniência inline** (cada painel com data e fonte) | ✅ **já fazemos** | É a tese: cada número rastreável. Aqui só é preciso mostrá-lo melhor. |
| **Indicadores ▲▼─** de direção | ✅ sim | Texto simples, sempre legível. Resolve de vez o problema dos emoji que não renderizam igual em todo o lado. |
| **Alertas com limitação de ritmo** | ✅ **já fazemos** | Gates, tetos diários, dedup. |
| **Score de convergência** ("três sistemas movem-se juntos") | ❌ **NÃO** | Medimos e ganha em 1 de 3 orçamentos. O critério **H4** proíbe mostrar um score que a medição não sustenta. Copiar isto seria copiar a estética e ignorar a evidência. |
| Mapa-múndi, 56 camadas, 65 fornecedores | ❌ não | Não há geografia em dez tickers, e o âmbito é só APIs gratuitas. |
| Motor de cenários ("game disruptions") | ❌ **nunca** | É previsão. Contradiz a restrição fundadora. |

**A lição de fundo:** o worldmonitor é impressionante pela **densidade com disciplina**, não pelo
mapa. Um utilizador vê muito de uma vez, e cada coisa que vê está datada e tem fonte. Isso é
exatamente o que esta tese defende, e é por isso que o padrão se aplica mesmo com dez tickers em
vez de um planeta.

---

## 2. O que muda, em concreto

### 2.1 Uma superfície, não três ecrãs

A app atual: `Today` / `Ticker` / `Method`, com rádio na barra lateral. Mudar de ecrã perde o fio.

O novo: **uma página**. Em cima, a watchlist densa (o que hoje é o `Today`). Ao clicar numa linha,
o painel do ticker **expande por baixo**, sem sair da página. O método fica num painel recolhido no
fim, onde não estorva mas está sempre a um clique.

### 2.2 O gráfico é o herói, e os sinais estão nele

Foi o pedido literal do aluno, e é o que falta. O gráfico grande, e sobre ele:

- **▲ verde / ▼ vermelho** nos dias de movimento sinalizado
- **● azul** nos dias de notícia
- **hover** = a primeira linha do alerta que o canal enviou
- **clique** = o alerta completo, com a decomposição e os precedentes

O que estava em duas listas separadas passa a estar num sítio só, no eixo do tempo. É a diferença
entre "aqui está o gráfico, e aqui está uma lista de coisas que aconteceram" e "aqui está o que
aconteceu, quando aconteceu".

### 2.3 Direção por texto, não por emoji

Os emoji 📈📉 renderizam a cores num sítio e como quadrados cinzentos noutro, e já produziram um
bug visível (seta verde para cima num movimento de −7,64%). Passa a **▲ ▼ ─** com cor aplicada por
nós, que é legível em qualquer lado e não depende da fonte do sistema.

### 2.4 Paleta de comandos

`Ctrl-K` abre uma caixa: escreve `nvda` e salta para a NVIDIA; escreve `6m` e muda o intervalo. Com
dez tickers é um luxo pequeno, mas é o que faz a interface parecer rápida em vez de burocrática.

---

## 3. O que NÃO se copia, e porquê dizê-lo em voz alta

Vale a pena escrever isto porque é a diferença entre inspirar-se e imitar:

1. **Score de convergência.** Existe no worldmonitor e é bonito. Medimos o nosso e ganha em 1 de 3
   orçamentos. **Não entra.** Um score que a medição não sustenta é exatamente o que esta tese
   critica nas ferramentas comerciais.
2. **Badges de tipo de evento.** Idem: silhueta 0,084 e rubrica a cobrir 15,1%.
3. **Motor de cenários.** É previsão, e a recusa de prever é a posição fundadora.

Ou seja: copia-se a **forma** (densidade, progressividade, proveniência) e recusa-se o **conteúdo**
que a nossa própria avaliação não sustenta. É essa a diferença entre um clone e um sistema com
critério.

---

## 4. Como se sabe que está pronto

Os critérios estão em [`dashboard_acceptance.md`](dashboard_acceptance.md) e não se mexem. Em
resumo: densidade sem scroll, cada número rastreável a um motor num clique, carrega em menos de 5 s
a frio, e as quatro regras de honestidade (H1–H4).

**Se não passar, a app atual fica.** É por isso que se constrói ao lado.
