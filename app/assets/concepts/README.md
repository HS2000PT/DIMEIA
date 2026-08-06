# Três direcções novas de marca — e o que a medição disse

> Geradas a 2026-08-06 a pedido do aluno: *"algo que dê nas vistas, com olhos, ou o jacaré, ou
> uma mascote — tipo uma marca registada"*, e, no mesmo dia, *"a Stare era má, quero coisa
> **nova**"*. Não são revivalismos: são três ideias novas, uma ideia cada.
>
> Regenerar a folha de comparação: `python scripts/render_brand_concepts.py`

## O teste, que é o mesmo de sempre

[`docs/design/brand.md`](../../../docs/design/brand.md): legível a **16 px** com a silhueta
reconhecível · funciona a preto e branco · funciona em fundo claro **e** escuro · **uma ideia
só** · não contradiz a postura do produto.

**16 px é onde vive um favicon**, e é o teste que a marca de 2026-07 falhou. Por isso a folha
[`comparacao.png`](comparacao.png) mostra 16/24/32/48/88/160 px, nos dois fundos, **com a marca
actual como controlo** — sem controlo não se sabe se o novo é melhor ou apenas diferente.

## Veredicto, a olhar para o render

| | ideia | 16 px | grande | veredicto |
|---|---|---|---|---|
| **A — Waterline** | o jacaré submerso: só os olhos acima da linha de água, que é também a linha do mercado | ❌ colapsa numa mancha horizontal; os olhos desaparecem | ✅ **a melhor das três** — lê-se imediatamente | **não serve como logótipo; serve como imagem grande** |
| **B — Pupil Tick** | o mercado dentro do olho: a pupila é uma barra de preço | ✅ **a única que sobrevive** — lê-se olho com marca dentro | ✅ limpa e distinta | **a única candidata a logótipo** |
| **C — Gator Mark** | a cabeça do jacaré vista de cima, como marca | ❌ borrão | ❌ **falhou**: não se lê como jacaré, lê-se como um vulto com dois olhos | **descartar ou redesenhar de raiz** |

**O C falhou e fica registado como falhou.** A geometria do focinho não sobrevive à simplificação;
o que sai é uma forma arredondada sem espécie. Não é um problema de tamanho, é de desenho.

## A conclusão que interessa, e que não é a esperada

**Nenhuma das três bate claramente a marca actual aos 16 px.** A "Tail" a 16 px continua a ser um
traço limpo; a A e a C são piores lá, e a B é comparável e não obviamente melhor.

Isto empurra para a separação que já estava escrita no backlog e que o render confirma:

- **Logótipo** (16 px, favicon, cabeçalho): ou fica a **Tail**, ou passa a **B**. São as duas
  únicas que passam o teste.
- **Mascote / imagem grande** (avatar do canal, capa dos slides, guia, ecrã inicial): é aqui que
  vive o "dar nas vistas" com olhos. A **A** é forte neste papel e não paga o custo dos 16 px.

Ou seja: provavelmente não é preciso escolher entre marca e mascote — é preciso parar de lhes
exigir a mesma coisa.

## Próximo passo, se o aluno quiser continuar

1. Dizer qual das duas leituras prefere para o logótipo (manter a Tail, ou passar à B).
2. Se quiser a A como mascote, ela precisa de tratamento a sério em tamanho grande: mais
   detalhe, ondulação melhor, talvez cor secundária. Aos 160 px já aguenta; aos 512 px de um
   avatar de canal precisa de mais.
3. O C só volta se for redesenhado de raiz, e não vale a pena sem uma ideia melhor para o focinho.
