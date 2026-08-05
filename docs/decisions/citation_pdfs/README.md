# PDFs para a auditoria de conteúdo das citações

> **Esta pasta é `.gitignore`d, e isso não é uma conveniência — é obrigatório.** Os PDFs
> abaixo são material com direitos de autor, o repositório é **público**, e versioná-los
> transformaria uma auditoria de integridade numa violação de copyright. Ficam **só nesta
> máquina**. O que vai para o repositório é o **relatório** da auditoria, não as fontes.

## Para que é

O `citation_log.md` prova que cada fonte **existe**. O
[`bibliography_verification.md`](../bibliography_verification.md) prova, por script, que os
**metadados** batem certo com o registo canónico (84/84). Falta a terceira, que é a mais difícil
e a que um arguente testa: **a fonte sustenta a frase a que está agarrada?**

A auditoria de 2026-07-30 respondeu a isso lendo abstracts, conclusões e secções acessíveis
online. Para a maioria das fontes isso chega. Para as que estão atrás de paywall, ler o texto
completo torna a verificação mais forte — e é aí que a tua conta do ISEP entra.

## O que **não** precisas de descarregar

**44 das 59** já são legíveis sem conta nenhuma e eu leio-as directamente:

- **arXiv** — `araci2019finbert`, `devlin2019bert`, `dong2024fnspid`, `doshivelez2017rigorous`,
  `lundberg2017shap`, `mikolov2013word2vec`, `vaswani2017attention`, `wu2023bloomberggpt`,
  `yang2020finbert`, `ribeiro2016lime` (arXiv:1602.04938), `angelopoulos2023conformal`
  (arXiv:2107.07511)
- **ACL Anthology** — `reimers2019sbert`, `pennington2014glove`
- **Acesso aberto** (editora ou repositório) — `adadi2018peeking`, `arrieta2020xai`,
  `bansal2021whole`, `bollerslev1986garch`, `breunig2000lof`, `cardillo2024robo`,
  `da2011attention`, `friedman2001gbm`, `gama2014survey`, `guidotti2018survey`,
  `johnson2021faiss`, `kearney2014textual`, `lee2004trust`, `lipton2018mythos`,
  `loughran2011liability`, `miller2019explanation`, `pang2021deep`,
  `rousseeuw1987silhouettes`, `rudin2019stop`, `salton1975vsm`, `xing2018nlffsurvey`,
  `tetlock2007media` (cópia SSRN)
- **Cópia livre do autor, confirmada** — `liu2008isolation` (cs.nju.edu.cn),
  `robertson2009bm25` (city.ac.uk), `manning2008ir` (nlp.stanford.edu/IR-book)
- **URL público** — `ccaf2026aifs`, `ding2015deep`, `gallup2025stock`, `sculley2015debt`,
  `sifma2025factbook`, `vinh2010ami`, `worldmonitor2026`

## O que precisa da tua conta — **14 ficheiros**

Guarda cada um **com o nome da chave**, em PDF: `barber2008glitters.pdf`, etc. O nome importa,
porque é por ele que o script encontra o ficheiro certo.

| ficheiro a guardar | referência | identificador |
|---|---|---|
| `aamodt1994cbr.pdf` | Aamodt & Plaza (1994), *AI Communications* 7(1):39–59 | `10.3233/AIC-1994-7104` |
| `ahmed2016financial.pdf` | Ahmed et al. (2016), *Future Gen. Comp. Syst.* 55:278–288 | `10.1016/j.future.2015.01.001` |
| `barber2008glitters.pdf` | Barber & Odean (2008), *Rev. Financial Studies* 21(2):785–818 | `10.1093/rfs/hhm079` |
| `barberis2003behavioral.pdf` | Barberis & Thaler (2003), *Handbook Econ. Finance* cap. 18 | `10.1016/S1574-0102(03)01027-6` |
| `brown1985daily.pdf` | Brown & Warner (1985), *J. Financial Economics* 14(1):3–31 | `10.1016/0304-405X(85)90042-X` |
| `chandola2009anomaly.pdf` | Chandola et al. (2009), *ACM Comput. Surv.* 41(3) | `10.1145/1541880.1541882` |
| `dacunto2019robo.pdf` | D'Acunto et al. (2019), *Rev. Financial Studies* 32(5):1983–2020 | `10.1093/rfs/hhz014` |
| `engle1982arch.pdf` | Engle (1982), *Econometrica* 50(4):987–1007 | `10.2307/1912773` |
| `fama1969adjustment.pdf` | Fama et al. (1969), *Int. Economic Review* 10(1):1–21 | `10.2307/2525569` |
| `fama1970efficient.pdf` | Fama (1970), *J. Finance* 25(2):383–417 | `10.2307/2325486` |
| `kahneman1979prospect.pdf` | Kahneman & Tversky (1979), *Econometrica* 47(2):263–291 | `10.2307/1914185` |
| `niculescu2005calibration.pdf` | Niculescu-Mizil & Caruana (2005), *ICML*:625–632 | `10.1145/1102351.1102430` |
| `vovk2005algorithmic.pdf` | Vovk, Gammerman & Shafer (2005), *Algorithmic Learning in a Random World* (livro) | `10.1007/b106715` |
| `welch2022robinhood.pdf` | Welch (2022), *J. Finance* 77(3):1489–1527 | `10.1111/jofi.13128` |

### Como chegar a eles

`https://doi.org/<identificador>` a partir da rede do ISEP, ou pelo proxy da biblioteca do
IPP/ISEP se estiveres em casa. O `vovk2005algorithmic` é um **livro**: chegam os capítulos 1–2
(é lá que está a garantia de validade e a hipótese de permutabilidade que a tese invoca) — não é
preciso o livro inteiro.

## Prioridade, se não quiseres fazer os 14

Se só fizeres alguns, faz **estes cinco primeiro**. São aqueles em que a tese diz algo específico
que só o texto completo confirma ou desmente:

1. **`chandola2009anomaly`** — a tese atribui-lhe a taxonomia ponto/contextual/colectiva *e* as
   famílias de métodos. É a citação mais reutilizada do Cap. 2.
2. **`vovk2005algorithmic`** — a tese invoca uma garantia. Garantias têm hipóteses, e a hipótese
   (permutabilidade) tem de estar declarada, não escondida.
3. **`brown1985daily`** — sustenta o desenho do *event study*, que é o método de medição de que
   dependem todos os números de impacto.
4. **`niculescu2005calibration`** — sustenta a escolha de Platt em vez de isotónica, que é uma
   decisão de produto defendida na tese.
5. **`barber2008glitters`** — sustenta a afirmação sobre atenção do investidor de retalho, que é
   a motivação do trabalho inteiro no Cap. 1.

## Depois de os pores aqui

Diz-me, e eu leio-os e faço a auditoria de conteúdo contra as frases exactas da tese. O resultado
vai para `docs/decisions/citation_content_audit.md`, com o mesmo formato do resto: cada achado
corrigido **por enfraquecimento da afirmação**, nunca inventando uma fonte que diga o que convém.
