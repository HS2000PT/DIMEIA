# Antes de estudares por qualquer documento desta pasta

> Escrito a 2026-08-20, depois de medir. **Lê isto primeiro, uma vez.** São dois minutos e
> evitam que decores números que já não existem no documento que vais defender.

## O que se passa

Estes documentos foram escritos para a **tese longa em inglês** (`thesis/`, 130 páginas), ao
longo de várias sessões. O que vais entregar e defender é a **tese curta em português**
(`tese/`, 114 páginas), que é um documento diferente: tem menos resultados, outra numeração e
alguns números corrigidos.

Não os apaguei porque o conteúdo continua a ser bom para estudar o raciocínio. Mas há três
coisas que tens de saber antes de te fiares neles.

## 1. A numeração das perguntas mudou, e não é uma tradução

A tese longa tem **quatro RQ**. A tese curta tem **três QI**, e a correspondência não é
um-para-um:

| Tese longa | Tese curta | Assunto |
|---|---|---|
| RQ1 | **QI1** | detetar o que é invulgar |
| RQ2 | **QI2** | encontrar casos passados parecidos |
| RQ3 | *(não existe)* | as explicações são úteis a uma pessoa |
| RQ4 | **QI3** | um modelo treinado decide o que merece alerta |

**A RQ3 desapareceu.** Na tese curta a utilidade das explicações não é uma pergunta de
investigação: está declarada como não medida, porque não houve estudo com pessoas. Se disseres
"a minha terceira pergunta é sobre as explicações", estás a descrever o documento errado.

E cuidado com o oposto: quando estes ficheiros dizem **"RQ4"**, na tua tese isso é a **QI3**, e
a resposta é um **"Não"** firme — nenhum modelo com texto bate a volatilidade.

## 2. Números que foram retirados

| Não digas | Diz | Porquê |
|---|---|---|
| "quase 4×" | **1,67×** (de 0,379 para 0,632) | O chão de `0,163` ordenava por ordem alfabética das empresas. Ao acaso a sério dá 0,379 |
| "0,667 vs 0,455 ao vivo" | **0,589 vs 0,617** | Eram 12 decisões. Com 825, o sinal **inverte-se** |
| "a triagem funciona em produção" | "em produção não mostra benefício" | Intervalo [0,391, 0,601], que contém o acaso |

## 3. O que estes documentos ensinam e a tese curta não tem

Se citares isto, o júri procura no teu documento e não encontra: agrupamento por tipo de
evento (AMI, pureza, silhueta), predição conforme, lift por setor, exportação ONNX, o narrador
de linguagem natural, a guarda de ancoragem, e a camada generativa inteira.

Nada disso está na tese curta. Foi trabalho real, está na tese longa, e **não é o que vais
defender**.

## O que usar

Para a defesa, os materiais alinhados com a tese entregue são:

- `tese/slides/main.tex` — 21 slides, os que vais projetar
- `tese/guia/main.tex` — 24 slides de estudo
- `tese/quiz/index.html` — o quizz, para o telemóvel
- `tese/GRAVACAO.md` — o guião da gravação da demonstração

Esses quatro são verificados por `scripts/check_materiais.py`, que falha se algum deles disser
um número que a tese não diz.
