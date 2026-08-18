# PDFs que faltam para validar as citações contra o original

**Estado: tenho 14 de 60.** As 46 abaixo nunca foram conferidas contra o artigo original.

Põe os ficheiros nesta pasta com o **nome exacto da chave** (por exemplo
`reimers2019sbert.pdf`) e eu corro a validação sobre eles. A pasta está no `.gitignore`, portanto
material com direitos de autor não vai para o repositório.

> **Porque é que isto vale a pena.** Das 14 que tinha, saíram **25 achados**, um deles crítico:
> uma fonte que argumentava contra a escolha que era chamada a sustentar. Não há razão para supor
> que as outras 46 estejam todas certas.

---

## Prioridade 1: as oito que mais pesam (faz estas primeiro)

São as mais citadas e as que sustentam afirmações centrais. Quatro são de acesso livre.

| Chave | Vezes | Onde ir buscar | Acesso |
|---|---|---|---|
| `reimers2019sbert` | **7x**, em 5 capítulos | ACL Anthology: `aclanthology.org/D19-1410` | **livre** |
| `liu2008isolation` | 6x | IEEE Xplore, ICDM 2008 | precisa ISEP |
| `dong2024fnspid` | 5x | arXiv `2402.06698` (ou ACM DL, DOI 10.1145/3637528.3671629) | **livre** |
| `rudin2019stop` | 5x | arXiv `1811.10154` | **livre** |
| `breunig2000lof` | 5x | ACM DL, SIGMOD 2000 | precisa ISEP |
| `vasicek1973beta` | 5x | Journal of Finance, Wiley | precisa ISEP |
| `sculley2015debt` | 5x | NeurIPS 2015 proceedings | **livre** |
| `lee2004trust` | 4x | Human Factors, SAGE | precisa ISEP |

**Porquê estas.** O `reimers2019sbert` é a representação que o trabalho inteiro usa. O
`vasicek1973beta` é aquele onde a tese **declara um desvio** face à formulação original, e essa
declaração merece ser conferida. O `sculley2015debt` sustenta o episódio do ciclo parado dezanove
dias, que é um dos achados fortes. E o `lee2004trust` já produziu uma correcção nesta revisão
**sem** eu ter o PDF, o que é exactamente a situação a evitar.

---

## Prioridade 2: citadas três vezes

| Chave | Onde | Acesso |
|---|---|---|
| `manning2008ir` | `nlp.stanford.edu/IR-book/` (livro completo online) | **livre** |
| `robertson2009bm25` | Now Publishers, PDF em `staff.city.ac.uk/~sbrp622/` | **livre** |
| `ding2015deep` | IJCAI 2015 proceedings | **livre** |
| `bansal2021whole` | arXiv `2006.14779` (ou ACM CHI) | **livre** |
| `bollerslev1986garch` | Journal of Econometrics, Elsevier | precisa ISEP |
| `salton1975vsm` | Communications of the ACM | precisa ISEP |
| `gama2014survey` | ACM Computing Surveys | precisa ISEP |

---

## Prioridade 3: livres no arXiv, rápidas de juntar

Estas são todas de acesso aberto. Vale a pena apanhá-las de uma vez, porque é pouco esforço:

| Chave | arXiv |
|---|---|
| `devlin2019bert` | 1810.04805 |
| `mikolov2013word2vec` | 1301.3781 |
| `vaswani2017attention` | 1706.03762 |
| `ribeiro2016lime` | 1602.04938 |
| `lundberg2017shap` | 1705.07874 |
| `doshivelez2017rigorous` | 1702.08608 |
| `arrieta2020xai` | 1910.10045 |
| `guidotti2018survey` | 1802.01933 |
| `miller2019explanation` | 1706.07269 |
| `angelopoulos2023conformal` | 2107.07511 |
| `pang2021deep` | 2007.02500 |
| `johnson2021faiss` | 1702.08734 |
| `araci2019finbert` | 1908.10063 |
| `yang2020finbert` | 2006.08097 |
| `wu2023bloomberggpt` | 2303.17564 |
| `xing2018nlffsurvey` | 1809.03052 |

Mais duas fora do arXiv, também livres:

| Chave | Onde |
|---|---|
| `pennington2014glove` | ACL Anthology, `aclanthology.org/D14-1162` |
| `friedman2001gbm` | Annals of Statistics, Project Euclid |
| `adadi2018peeking` | IEEE Access (acesso aberto) |

---

## Prioridade 4: baixo peso ou já verificáveis de outra forma

**Revistas de finanças, precisam de ISEP**, mas cada uma é citada só uma ou duas vezes:
`da2011attention`, `tetlock2007media`, `loughran2011liability`, `blume1971risk`,
`kearney2014textual`, `cardillo2024robo`.

**Páginas web e relatórios**, onde o "original" é a própria página e a tese já regista a data de
consulta: `sifma2025factbook`, `gallup2025stock`, `ccaf2026aifs`, `robinhood2025cortex`,
`google2026finance`. Estas não precisam de PDF: o que precisa é que a página ainda diga o que a
tese afirma, e isso confere-se abrindo o endereço.

---

## Se só tiveres tempo para um lote

Faz os **livres da Prioridade 1** (`reimers2019sbert`, `dong2024fnspid`, `rudin2019stop`,
`sculley2015debt`) mais os **quatro livres da Prioridade 2**. São oito ficheiros, todos de
descarga directa e sem login, e cobrem as afirmações de maior peso que continuam por conferir.

Os que precisam de ISEP podem ficar para uma sessão na biblioteca, ou ficar por fazer: nesse caso
a tese continua honesta, porque a Matriz de Evidência regista o que foi verificado e como.
