# brand.md — "The Tail"

> Sistema de marca do InvestiGator. Adotado a 2026-07-29, substitui "The Stare".

## A marca

**Um traço contínuo que se lê ao mesmo tempo como a cauda serrilhada de um jacaré e como uma
linha de mercado a subir.** A base espessa em baixo-à-esquerda afina até à ponta em
cima-à-direita; os dentes do bordo superior são simultaneamente escamas e volatilidade.

Uma ideia, uma forma. É essa leitura dupla que faz a marca dizer o nome (*Invest* na linha,
*Gator* na cauda) sem desenhar um animal.

## Porque a anterior saiu

"The Stare" (olho de crocodilo com íris dourada sobre uma linha de mercado) tinha três
problemas, e o primeiro é objetivo:

1. **Falhava a 16 px.** A 16 px o sobrolho fundia-se com o olho e a linha de mercado
   desaparecia, deixando uma mancha indistinta. 16 px é o favicon, o separador do browser e o
   avatar do canal Telegram, ou seja, o tamanho em que a marca mais vezes aparece.
2. **Três metáforas a competir** num só ícone (sobrolho, olho, linha). As marcas que aguentam
   redução carregam uma ideia.
3. **Contra-mensagem.** Um olho de pupila em fenda lê-se como predador. Todo o produto se
   define por mostrar evidência e nunca prever; a marca dizia o contrário.

A escolha foi feita com as três variantes lado a lado às escalas reais, incluindo a marca
antiga como controlo — a comparação está em `docs/design/brand_candidates.md`.

## Ficheiros

| Ficheiro | Uso | Cor |
|---|---|---|
| `app/assets/logo.svg` | fundos CLAROS (a app, o README) | esmeralda `#0A8F52` |
| `app/assets/logo-dark.svg` | fundos ESCUROS (slides, capas) | esmeralda viva `#00E37A` |
| `app/assets/logo-mono.svg` | uma só cor; herda via `currentColor` | — |
| `app/assets/icon.svg` | favicon, avatar, ícone de app | glifo `#00E37A` sobre tinta `#0A0E12` |

**Duas cores, não uma.** Um verde intermédio que "servisse" ambos os fundos ficaria apagado no
escuro e com pouco contraste no claro. Ter dois ficheiros é o que as marcas reais fazem.

**O glifo é NU; o contentor só existe no ícone.** Um quadrado escuro à volta da marca obriga um
bloco escuro a toda a superfície clara onde ela aterre. O ícone de aplicação é a exceção porque
a plataforma desenha sempre um quadrado, e sem fundo próprio a marca ficaria à mercê da cor de
sistema do utilizador. No `icon.svg` o glifo é ainda ampliado 14%: um ícone lido a 16 px precisa
de margens menores do que uma marca lida a 88 px.

## Paleta

| Papel | Hex | Nota |
|---|---|---|
| Esmeralda (claro) | `#0A8F52` | marca e cor primária da app |
| Esmeralda (escuro) | `#00E37A` | a mesma marca sobre tinta |
| Tinta | `#14171A` | quase-preto, ligeiramente frio |
| Fundo do ícone | `#0A0E12` | mais escuro do que a tinta, para o glifo saltar |
| Neutro de painel | `#F1F5F2` | viés muito ligeiro para o verde: escolhido, não herdado |

O verde-pântano `#0E2A20` e o dourado `#E7B24C` de "The Stare" foram **retirados**. Liam-se mais
casino do que fintech, e o dourado competia com o próprio sinal da marca.

## Slogan

> **Every move investigated, never predicted.**

Mantém-se. Diz o que o sistema faz e o que recusa fazer, na mesma linha, e é literalmente
verificável contra a saída do produto.

## Onde a marca aparece

- **App** (`app/streamlit_app.py`): `st.logo` + tema em `.streamlit/config.toml`.
- **Tese**: Figura 4.5 é uma captura real da app, por isso apanha a marca sozinha ao ser
  recapturada por `scripts/screenshot_app.py`.
- **Slides**: leem o mesmo ficheiro de asset.
- **Canal Telegram**: avatar, definido à mão pelo aluno (é um clique, não engenharia).

## Teste de aceitação da marca

Uma marca nova só entra se passar isto, que é exatamente o que a anterior falhava:

- [x] Legível a **16 px** com a silhueta reconhecível.
- [x] Funciona a preto e branco (`logo-mono.svg`).
- [x] Funciona sobre fundo claro **e** escuro.
- [x] Uma só ideia, não três.
- [x] Não contradiz a postura do produto.
