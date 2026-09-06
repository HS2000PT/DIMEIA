# Política linguística do projeto

> ## ⚠️ A DECISÃO DA §2 FOI TOMADA AO CONTRÁRIO — atualizado a 2026-09-06
>
> A recomendação abaixo era **manter inglês no interior das figuras**, e media o custo da
> conversão: o português é mais largo, a conversão inversa encontrara quatro armadilhas, e
> perdia-se a reutilização no artigo.
>
> **O autor decidiu ao contrário a 05/09, e a decisão resolve o custo em vez de o ignorar:**
> existem agora **duas árvores**, pelo que a reutilização no artigo fica garantida pela
> `tese-eng` e o português só tem de caber na `tese-pt`. Foram convertidos **172 rótulos**, e
> as quatro armadilhas que este documento previa apareceram todas — o *bilião* que vale mil
> vezes mais em português, o trocadilho da figura dos *embeddings*, os exemplos com palavras
> portuguesas num corpus inglês, e os decimais.
>
> **O que continua a valer aqui:** as regras da §1 por artefacto, o mecanismo de fonte única, e
> a razão pela qual os títulos de notícia citados e as capturas ficam em inglês nas duas
> árvores. **O que não vale é a recomendação da §2.**


Escrita a 2026-09-04, a pedido da §5 da directiva de revisão final. Fixa as regras que já
estavam a ser seguidas sem estarem escritas, e mede o custo da única mudança que continua
em aberto, que é uma decisão do autor e não minha.

---

## 1. As regras, por artefacto

| Artefacto | Prosa | Interior das figuras | Legendas |
|---|---|---|---|
| Dissertação (`tese-v2/`) | **PT-PT** | inglês | **PT-PT** |
| Artigo (`paper/`) | inglês | inglês | inglês |
| Slides e guias (`slides/`) | **PT-PT** | inglês | **PT-PT** |
| Produto (mensagens, interface) | inglês | — | — |
| Documentos internos, registos, planos | **PT-PT** | — | — |

**Três regras transversais, que valem em todos eles:**

1. **Texto citado nunca se traduz.** Um título de notícia, o nome de um ponto de controlo
   público, o nome de uma publicação. Traduzi-los quebra a verificabilidade, que é a
   propriedade central deste trabalho. É por isso que `AI` aparece uma vez em prosa
   portuguesa: está dentro de um título citado.
2. **Terminologia estabelecida fica na forma corrente da área.** Não se traduz
   *z-score*, *bootstrap*, *Brier* ou *Platt* quando a tradução é artificial ou inventada.
   Traduz-se o que tem forma corrente em português: *entradas* e não *features*,
   *precisão* e não *precision*, *título* e não *manchete* — e este último é verificado
   pela porta `check_escrita`, que exige um termo por conceito.
3. **Nenhuma figura mistura as duas línguas dentro de si.** É a regra que produz o único
   defeito que esta passagem encontrou, descrito abaixo.

---

## 2. Por que razão o interior das figuras está em inglês

A prosa é portuguesa e o interior das figuras é inglês. A razão é a mesma que o Cap. 4
invoca para as mensagens do sistema, e desde 2026-09-04 está escrita no fim do Cap. 1:
os títulos de notícia, os identificadores de empresa e os nomes das métricas provêm de
fontes em inglês e são citados sem tradução, porque traduzi-los quebraria a
correspondência com o material que o leitor pode consultar. Manter o interior das figuras
nessa língua evita que uma mesma quantidade apareça com dois nomes no mesmo documento.

A consequência prática é a reutilização: uma figura da dissertação entra no artigo sem
tradução, e as duas versões não podem divergir porque **são a mesma**.

---

## 3. O que esta passagem mediu

- **43 figuras** no corpo e no apêndice.
- **35** têm texto inglês no interior, com cerca de **761 palavras**.
- **Uma** misturava as duas línguas dentro de si, e foi corrigida:
  `fig:sis_caminho`, o percurso de um acontecimento, tinha sete nós em inglês e dois em
  português (`recuperar precedentes` e `entregar e registar`). A conversão de uma sessão
  anterior falhou-os. Passaram a `retrieve precedents` e `deliver and log`.
- **Três** figuras estão inteiramente em português, e todas foram criadas **depois** da
  conversão: `fig:con_futuro`, `fig:con_fronteira` e `fig:ap_infra`. São internamente
  consistentes; o que não são é consistentes com as outras quarenta.

---

## 4. A decisão que fica em aberto, com o custo dos dois lados

As três figuras portuguesas obrigam a escolher uma direcção, e a escolha é do autor
porque as duas são defensáveis.

### Direcção A — tudo em inglês no interior (mudança pequena)

Converter as três figuras portuguesas. **Custo: baixo**, cerca de 40 palavras e três
renderizações a verificar. O documento fica consistente, a explicação já está escrita no
Cap. 1, e as figuras continuam reutilizáveis no artigo sem tradução.

### Direcção B — tudo em português no interior (mudança grande)

Converter as 35 figuras inglesas. **Custo: alto e com risco de composição real.**

- ~761 palavras em 35 figuras, cada uma a exigir renderização e verificação visual.
- **O português é mais largo.** A sessão 57 registou uma tabela a rebentar a caixa em
  54 pt exactamente por isso. Trinta e cinco figuras TikZ com larguras fixas mudam de
  forma.
- A conversão inversa, feita numa sessão anterior, **encontrou quatro armadilhas** que
  uma passagem cega teria criado: «biliões» contra *billions*, que difere por mil vezes;
  um trocadilho que a legenda citava e que deixou de existir; exemplos em português para
  ilustrar um sistema cujo corpus é inglês; e cinquenta decimais com vírgula. A direcção
  contrária tem a mesma classe de armadilhas.
- E **perde a reutilização no artigo**, a menos que se construa o mecanismo da secção 5.

### Recomendação

**A direcção A, e a razão não é o custo.** É que a direcção B só compensa se as figuras
deixarem de ser partilhadas com o artigo, e o artigo já as usa. A **17 dias** do
congelamento do documento, trocar trinta e cinco figuras verificadas por trinta e cinco
por verificar gasta risco sem comprar nenhuma afirmação.

---

## 5. Fonte única, se a direcção B for escolhida

A directiva pede que as duas versões não sejam ficheiros mantidos à mão. Se o autor
escolher a direcção B, o mecanismo é este e não exige ferramenta nova:

```latex
% no preâmbulo
\newif\ifpt \pttrue                  % a tese liga; o artigo desliga
\newcommand{\bl}[2]{\ifpt #1\else #2\fi}   % bilingue: \bl{português}{english}
```

e cada rótulo passa a `\bl{recuperar precedentes}{retrieve precedents}`. A figura fica
**uma só**, no mesmo ficheiro, e a língua é escolhida por quem compila. Uma actualização
não pode deixar as duas versões diferentes, porque não há duas versões.

O custo continua a ser o das 761 palavras: o mecanismo resolve a **divergência**, não a
**conversão**.

---

## 6. O que esta política não cobre, e porquê

- **Os gráficos gerados por script** (`eval_*.pdf`, dois deles usados pelo artigo) têm os
  rótulos no Python que os produz. Aplicar-lhes a direcção B exige mexer nos geradores, o
  que é mais seguro do que mexer em TikZ, mas obriga a re-correr o gerador e a conferir que
  os números não mudaram.
- **As capturas da aplicação** estão em inglês porque a aplicação está em inglês, e a
  aplicação está em inglês pela razão da secção 1, regra 1.
