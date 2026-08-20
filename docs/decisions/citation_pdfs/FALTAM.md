# PDFs das fontes: o que existe, e o que falta

> Reescrito a 2026-08-20 **contando os ficheiros**, não de memória: a versão anterior dizia
> *"tenho 14 de 60"* e estava desactualizada em dezenas de entradas.
>
> Os `*.pdf` desta pasta estão no `.gitignore`, e isso é obrigatório e não conveniência: o
> repositório é público e o material tem direitos de autor. A pasta existe para se poder
> conferir uma afirmação **contra o original**, que é diferente de confirmar que o registo
> bibliográfico existe.

## Estado medido

**57 de 65 entradas do `references.bib` têm o PDF.** Faltam oito, e nenhuma delas por acaso:

| Chave | Porque falta | O que fazer |
|---|---|---|
| `sifma2025factbook` | é uma **página web**, não um artigo | abrir o endereço e ver se ainda diz o que a tese afirma |
| `gallup2025stock` | idem | idem |
| `ccaf2026aifs` | idem | idem |
| `robinhood2025cortex` | idem (página do próprio fornecedor) | idem |
| `google2026finance` | idem | idem |
| `worldmonitor2026` | idem (é um produto, creditado como tal) | idem |
| `huang2023finbert` | **Wiley responde 403** com desafio anti-robô | descarregar com a conta do ISEP |
| `rousseeuw1987silhouettes` | **Elsevier responde 403** com desafio anti-robô | descarregar com a conta do ISEP |

Sobre as seis primeiras: para uma página web o "original" **é** a página, e a tese regista a data
de consulta. Guardar um PDF impresso dela não acrescenta verificabilidade — o que acrescenta é
abrir o endereço e confirmar que continua a dizer o mesmo.

Sobre as duas últimas: os editores servem um desafio de robô, e **não se contorna** um desafio
desses. Descarregam-se de dentro da rede do ISEP, ou ficam por conferir — e nesse caso a tese
continua honesta, porque a Matriz de Evidência regista o que foi verificado e como.

## O que foi corrigido a 2026-08-20

- ⚠️ **`bollerslev1986garch.pdf` era o ficheiro errado.** Estava lá um projecto de mestrado de
  2003 da Simon Fraser University (Michael S. Lo), *"Generalized Autoregressive Conditional
  Heteroscedastic Time Series Models"* — título parecido, trabalho diferente. Substituído pelo
  artigo verdadeiro, da página do próprio autor em Duke: *Journal of Econometrics* **31** (1986)
  **307–327**, Tim Bollerslev. Confere com a entrada do `.bib` em revista, volume, páginas e ano.
- **`mikolov2013word2vec.pdf`** era a pré-publicação arXiv `1301.3781`, e a entrada passou, na
  sessão 60, a citar as **actas do NIPS 2013**. Substituído pelo PDF das actas.
- **`liu2020finbert.pdf`** e **`vinh2010ami.pdf`** descarregados das actas do IJCAI-20 e do JMLR,
  ambos de acesso livre.

## Como se confere que o ficheiro é mesmo o artigo

Não basta o `curl` devolver `200`: um servidor pode responder com uma página de erro, com um
desafio de robô, ou com outro documento. O que se faz é ler a **primeira página** e comparar com
a entrada do `.bib` — título, apelidos dos autores, e uma marca dura como o intervalo de páginas.

Foi assim que se apanhou o Bollerslev, e a marca que o denunciou foi o intervalo `307–327`. No
`liu2020finbert` a primeira página nem escreve o ano por extenso, mas as páginas **4513–4519**
batem certo, e isso é evidência mais forte do que a cadeia "2020".
