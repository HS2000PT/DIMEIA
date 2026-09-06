# Antes de estudares por qualquer documento desta pasta

> Escrito a 2026-08-20 e atualizado a 2026-09-06, depois de medir. **Lê isto primeiro,
> uma vez.** São dois minutos e evitam que decores números que já não existem no documento
> que vais defender.

## Por onde estudar (se só leres uma linha, é esta)

👉 **[`simulacro_tese_curta.md`](simulacro_tese_curta.md)** — escrito a 2026-08-23 **para a tese
curta**, com a numeração QI e as armadilhas. Dez perguntas, do "onde está a contribuição?" ao
"onde está a IA?". É o documento desta pasta que precisa de menos tradução mental.

⚠️ **E não precisava de nenhuma até 2026-09-06, altura em que quatro números seus tinham sido
substituídos pela tese** (estão na tabela da secção 2, corrigidos nesse dia). Um documento que se
declara alinhado é o mais perigoso de todos, porque é aquele por onde se estuda sem desconfiar.

Os outros continuam bons para estudar o raciocínio, com os avisos abaixo.

## O que se passa

Estes documentos foram escritos para a **tese longa em inglês** (arquivada em
`archive/thesis-versions/`, 130 páginas), ao longo de várias sessões. O que vais entregar e
defender é a **tese em português** (`tese-pt/`, 132 páginas), que é um documento diferente: tem
menos resultados, outra numeração e alguns números corrigidos.

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
| "a triagem funciona em produção" | "em produção não mostra benefício" | Intervalo [0,403, 0,571], que contém o acaso |
| "84% das decisões" | **48% dos títulos distintos** | O sistema repontua o mesmo título de minuto a minuto, logo contar decisões inflaciona a fração — e **na direção que convinha à conclusão** |
| "0,064 dentro / 0,385 entre / 6,1×" | **0,072 / 0,392 / 5,4×** | Janela nova, 36 925 decisões contra 4 366 |
| "944 → 42, uma razão de 22:1" | **743 → 15, cerca de 1 para 50** | A janela antiga contava avaliações num lado e casos cumulativos no outro |
| "~2,5 h até detetar, 1 s até entregar" | **353 minutos e 5 segundos** | O `1 s` era a era do agendador, com n=28 |

## 3. O que estes documentos ensinam e a tese curta não tem

Se citares isto, o júri procura no teu documento e não encontra: agrupamento por tipo de
evento (AMI, pureza, silhueta), predição conforme, lift por setor, exportação ONNX, o narrador
de linguagem natural, a guarda de ancoragem, e a camada generativa inteira.

Nada disso está na tese curta. Foi trabalho real, está na tese longa, e **não é o que vais
defender**.

## O que usar

Para a defesa, os materiais alinhados com a tese entregue são:

- `tese-pt/slides/main.tex` — 22 slides, os que vais projetar
- `tese-pt/guia/main.tex` — 25 slides de estudo
- `tese-pt/quiz/index.html` — o quizz, para o telemóvel
- `docs/defence/gravar_demo.md` — o guião da gravação da demonstração

Esses quatro são verificados por `scripts/check_materiais.py`, que falha se algum deles disser
um número que a tese não diz.
