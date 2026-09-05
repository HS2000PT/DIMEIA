# Revisão de conteúdo, capítulo a capítulo — 2026-09-05

> Pedida pelo autor: *«reveres agora a tese do início ao fim, e focando-te desta vez no
> conteúdo mesmo»*, **antes** da tradução. Os achados são escritos **à medida que aparecem**,
> para a revisão sobreviver a um reinício de sessão e uma sessão nova pegar onde esta parar.

**Ordem de leitura:** Cap. 4 (sistema) → Cap. 5 (resultados) → Cap. 3 (métodos) → Cap. 6
(conclusões) → Cap. 2 → Cap. 1 → frontmatter. Os capítulos que descrevem o que o sistema
**faz hoje** vêm primeiro, porque é aí que uma afirmação desactualizada se esconde.

---

## Estado

| capítulo | lido | achados | corrigidos |
|---|---|---|---|
| 4 | §4.1–§4.7 | 1 | 1 |
| 5 | — | — | — |
| 3 | — | — | — |
| 6 | — | — | — |
| 2 | — | — | — |
| 1 | — | — | — |

---

## Achados

### C4-1 — A figura do ciclo de vida estava metade em cada língua, e uma caixa a meio de uma tradução

`fig:sis_lifecycle`, `tese-pt/ch4/chapter4.tex`. Rótulos **desenhados**:
`labelled dataset`, `training`, `log of every decision` em inglês, ao lado de
`artefacto versionado`, `teste`, `retreino: ausente` em português — e uma caixa
**a meio de uma substituição**: `the `**`mesmo`**` model, in production`.

É a mesma classe do `declará-claradas` da sessão 61: **compila a zero erros**, porque é
texto válido, e só se vê a ler o que está desenhado.

⚠️ **E o `check_figuras_lingua.py` estava CALADO sobre ela**, tendo sido escrito ontem
exactamente para esta classe. A causa é estrutural e vale mais do que o defeito: o
verificador exige encontrar as **duas** línguas, e o lado português é uma **lista fechada**
de vocabulário. Nenhuma das palavras desta figura — `artefacto`, `versionado`, `teste`,
`mesmo`, `retreino`, `ausente` — estava na lista, logo a figura contava como
monolingue inglesa. **Um verificador cego e um corpus limpo são indistinguíveis no ecrã**,
que é a lição que a sessão 63 já tinha pago no `check_tese_numeros`.

**Corrigido nos dois sítios**, e a correcção do verificador foi verificada com a figura
original plantada.

**E a correcção do verificador encontrou logo uma segunda:** `fig:av_rotulos`, no Cap. 5,
tinha `célula usada` desenhada sobre um eixo rotulado `horizon (days)`. Só apareceu por
causa do sinal novo, que **não depende de vocabulário nenhum** — a ortografia portuguesa
(`ç`, `ã`, acentos) num rótulo desenhado. Uma lista fechada nunca a teria apanhado.

**Controlo:** com o rótulo original replantado, o verificador dispara e nomeia a figura.

### C5-1 — E a mesma classe tinha **três** cegueiras no verificador, não uma

Ao corrigir a lista fechada apareceu `fig:av_rotulos`. Ao ler a secção da deriva apareceu
`fig:av_deriva`, que o verificador continuava a não ver **por duas razões independentes**:

1. **`\gls{}` dentro de um rótulo de eixo.** O padrão era `\{([^{}]+)\}`, que para na
   primeira chaveta interior: `xlabel={\gls{PSI} entre o bloco de treino e o de teste}`
   **não casava de todo**, logo um eixo em português ao lado de escalas inglesas passava.
2. **Os rótulos de escala nunca eram olhados.** `xticklabels` e `yticklabels` são texto
   **desenhado** e não constavam do padrão. A figura da deriva tem
   `5-day momentum, Same-day return, Headline length` desenhados à esquerda, e era esse o
   lado inglês da mistura — invisível ao verificador.

**Três figuras corrigidas** (`fig:sis_lifecycle`, `fig:av_rotulos`, `fig:av_deriva`) e
três defeitos do verificador, cada um encontrado só depois de o anterior ser corrigido.
**A lição não é a lista: é que um verificador que só olha para parte do que é desenhado
dá a mesma saída de um corpus limpo.**

### C5-2 — Verificado e **não** é defeito: as três empresas fora do corpus de treino

`ch5:1385` afirma que a AMD, a Netflix e a Meta não figuram no corpus de treino. O registo
do projeto nomeava só duas (sessão 61). Conferido: são coisas diferentes — a sessão 61
tratava do mapa de setores (`SECTORS`), onde a Meta **está** e as outras duas não; o
corpus indexa a Meta como `FB`, pelo que sob o símbolo `META` está mesmo ausente
(`docs/evaluation/kb_fnspid_build.md`). **As duas afirmações são compatíveis.** Fica
registado para ninguém voltar a gastar tempo aqui.

### C4-2 — A prosa prometia **quatro** pontos de decisão e a figura desenha **cinco**

`ch4:220`, imediatamente antes da `fig:sis_caminho`. As caixas a tracejado são cinco —
*nomeia a empresa*, *é recente*, *evidência suficiente*, *triagem acima do piso*, *já
enviada hoje* — e o exemplo trabalhado que se segue atravessa as cinco, uma a uma.

É a classe que já mordeu duas vezes (a legenda das cinco portas na sessão 61, a contagem
das ocasiões na 63), e incide sobre **o núcleo do trabalho**: os pontos de decisão são o
que a dissertação tem de próprio. Corrigido para cinco.

**Verificadas e certas**, na mesma varredura: as cinco componentes do sistema, as nove
etapas, as sete entradas de nível de empresa em nove, as três causas do atraso, as três
leituras da ablação, as duas razões da janela, as duas precisões da predição conforme e
as duas propriedades da decomposição. O varrimento das promessas de contagem devolveu
**70 candidatas e um único defeito.**
