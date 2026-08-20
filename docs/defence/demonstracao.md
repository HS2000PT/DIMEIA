# demonstracao.md — o que mostrar ao júri, por que ordem, e o que dizer

> ⚠️ **Este documento foi escrito para a tese longa em inglês.** A que vais defender é a
> tese curta em português (`tese/`), que tem **três QI** e não quatro RQ, e onde alguns
> números foram corrigidos. Lê o [`LEIA-ME-PRIMEIRO.md`](LEIA-ME-PRIMEIRO.md) antes de
> estudares por aqui.

> **Regra da sala:** nada aqui depende de o mercado colaborar, de haver wi-fi, ou de um alerta
> chegar no momento certo. Se alguma dessas coisas correr bem, é bónus.

---

## Porque é que a demonstração é um *replay*, e porque isso é a favor

É a primeira pergunta que te podem fazer, e a resposta é o resultado central do trabalho:

> «Escolhi reproduzir um dia real em vez de correr ao vivo, e a razão é que **nove em cada dez
> varreduras não enviam nada**. O silêncio é o comportamento correcto do sistema, não uma
> avaria. Uma demonstração ao vivo mostrava, com toda a probabilidade, um ecrã parado — e a
> alternativa, forçar um alerta, seria fabricar exactamente aquilo que esta tese recusa
> fabricar. O que mostro saiu dos ficheiros que o sistema escreveu enquanto decidia.»

Se a pergunta vier com desconfiança («então não me mostra o sistema a funcionar?»), a resposta
é: **mostro-o a decidir**, que é a parte difícil. Enviar uma mensagem é trivial; decidir não
enviar 649 vezes é o que o trabalho faz.

---

## Antes de entrares na sala

```bash
python scripts/demo_defesa.py --dia 2026-08-09
```

Corre isto **uma vez com internet**, em casa. Fica em cache local, e a partir daí funciona sem
rede. Na sala, corre com `--offline` e não dependes de nada.

Confirma também que os PDFs estão no portátil, e que são os certos: **`tese/main.pdf`** (a
dissertação que entregaste), `tese/slides/main.pdf` (os 20 slides) e `tese/guia/main.pdf`.
As teses longas em `thesis/` e `thesis-pt/` foram superadas e não são o que vais defender.

---

## A ordem, em ~5 minutos

### 1 · O funil do dia *(≈60 s)*

O que aparece: quantas decisões, quantos alertas, e a barra de cada portão.

O que dizes:

> «24 decisões, 13 alertas. Isto é a resposta à fadiga de alertas, e é medida e não afirmada.
> A maior parte do trabalho do sistema é decidir calar-se.»

### 2 · O silêncio, com a margem *(≈90 s — é aqui que ganhas)*

O que aparece: cada empresa que ficou de fora, o portão que a parou, e **por quanto**.

O que dizes:

> «Repare que cada linha traz a margem que faltou, não só o veredicto. A Apple ficou a três
> centésimas do limiar. Nenhum produto comercial mostra o que descartou — e para este sistema
> isso é obrigatório, porque o silêncio é uma decisão dele e uma decisão que não se pode
> inspeccionar é indistinguível de um sistema avariado.»

Se quiseres a versão viva da mesma ideia, o painel implantado tem a página **«Why quiet?»**.

### 3 · Um alerta até ao fim *(≈2 min)*

O que aparece: o título, os cinco portões que passou, a mensagem verbatim, e a latência
decomposta.

O que dizes, sobre a latência (e é o número que te salva a pergunta sobre tempo real):

> «180 minutos entre a publicação e a detecção, 2 segundos entre a detecção e a entrega. O
> tempo está todo na descoberta, e não no meu lado. Reporto as duas componentes separadas
> porque um número agregado não distingue “somos lentos” de “a fonte é lenta”, e as duas
> afirmações pedem coisas opostas — a primeira pede engenharia, a segunda pede honestidade
> sobre a limitação.»

⚠️ **Se a mensagem terminar em «not a forecast»**, o script avisa-te. Diz tu primeiro:

> «Esta mensagem é de antes de 9 de Agosto e termina em “not a forecast”. Essa frase era falsa
> — uma probabilidade sobre os próximos dias é uma afirmação sobre o futuro — e está corrigida.
> O registo fica como está porque é histórico: o que mudou foi o sistema, não o passado.»

---

## Se houver wi-fi e quiseres arriscar 30 segundos

<https://investigator-ddc9d8618935.herokuapp.com/>

Quatro superfícies, e a que interessa mostrar é a terceira:

| onde | o que dizer |
|---|---|
| **grelha** | «As três perguntas do Capítulo 1 são três secções em cada cartão, sempre pela mesma ordem — inclusive quando a resposta é que não aconteceu nada.» |
| **Why quiet?** | «Cada nome que a varredura olhou, o portão que o parou, e a margem.» |
| **Method** | «Os números congelados da avaliação, cada um ao lado do ficheiro de onde vem. Incluindo o negativo.» |
| detalhe | «O gráfico tem o detector reproduzido sobre o último ano — são as marcas da mesma regra que corre ao vivo, não anotações à mão.» |

**Não abras isto primeiro.** Se a rede falhar no início, perdes o ritmo; se falhar no fim, não
perdeste nada.

---

## Plano B, por ordem de degradação

1. Sem rede → `--offline` (é o modo normal na sala).
2. Sem portátil teu → os PDFs bastam: o Apêndice A tem a **Matriz de Evidência** e a §4.5 tem a
   viagem de uma notícia em dez etapas.
3. Sem nada → conta o funil de cabeça: **944 títulos relevantes capturadas em cinco dias,
   42 alertas, 22:1**. E o que travou a maioria: precedente fraco e triagem.

---

## As três perguntas que a demonstração convida

**«Isto está mesmo a correr agora?»**
Sim — dois processos num alojamento pago, ciclo de 60 segundos, e o registo partilhado tem 332
alertas com carimbos. O que mostrei foi um dia desse registo.

**«Porque é que o gate travou uma notícia com P=0,47 e deixou passar uma com 0,55?»**
Porque o limiar está em 0,50, e esse valor é derivado e não escolhido: vem do varrimento de
custo a R=1, onde uma falha e um falso alarme custam o mesmo. **E depois acrescenta o que é
teu:** medi esse gate em produção e ele não separa — ROC-AUC 0,494. Fica como controlo de
volume, e a afirmação de que selecciona materialidade está retirada da tese.

**«Consegue mostrar-me o modelo a treinar?»**
Não em cinco minutos, e não é preciso: o treino aconteceu uma vez e está congelado num ficheiro
de 1,8 KB. O que posso mostrar é melhor — **um teste que carrega esse ficheiro, recalcula as
quatro métricas que a tese cita e exige igualdade exacta.** Se alguém re-treinar com outra
semente, a suite parte.
