"""Actualiza TAREFAS_MANUAIS_HENRIQUE.md: fecha a tarefa 1 e abre a tarefa dos dois PDFs novos."""
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ALVO = RAIZ / "docs" / "design" / "TAREFAS_MANUAIS_HENRIQUE.md"

ANTIGO_INICIO = "## 1. CRÍTICO — Cinco PDFs da literatura, com o acesso do ISEP"
ANTIGO_FIM = "## 2. CRÍTICO — O corpus do Finnhub existe nalgum lado?"

NOVO = """## 1. FEITO — Cinco PDFs da literatura ✅

Entregaste-os a 2026-09-09. Os quatro que faltavam foram lidos em texto integral nesse dia e
estão integrados no Capítulo 2, nas duas línguas. O que cada um diz e o que mudou por causa
disso está em `docs/design/capitulo2_literatura_2026-09-09.md`.

**Valeu mesmo a pena, e por uma razão concreta:** eu tinha escrito, a partir do resumo, que o
[Waa21] «justifica empiricamente a opção por explicação baseada em casos». Lido por inteiro, diz
o contrário — as explicações por exemplos **não se distinguiram de não dar explicação nenhuma**
(p = 0,796). Isso teria ido para a tese como uma afirmação falsa sobre um artigo com 385 citações.

---

## 1b. IMPORTANTE — Mais dois PDFs, quando puderes

**Porquê:** são os dois estudos com pessoas **no domínio financeiro** que sustentam a secção
mais honesta do Capítulo 2 (a contraevidência à opção por explicação baseada em casos, §2.7).
Hoje cito-os **apenas pelo que consta do resumo do editor**, que verifiquei. Está correto assim,
mas sem os PDFs não posso escrever quantos participantes tiveram nem os valores concretos --- e
são esses números que dão peso ao parágrafo.

**Passo a passo:**

1. Entra em `https://biblioteca.isep.ipp.pt` com as credenciais do ISEP (ou liga a VPN do IPP).
2. Descarrega estes dois e grava-os com **exactamente** estes nomes:

   | Guardar como | Procurar por | DOI |
   |---|---|---|
   | `cau2023_logic_style.pdf` | Supporting High-Uncertainty Decisions through AI and Logic-Style Explanations (IUI 2023) | `10.1145/3581641.3584080` |
   | `bertrand2023_feature_based.pdf` | Questioning the ability of feature-based explanations... (FAccT 2023) | `10.1145/3593013.3594053` |

   *Nota: o da FAccT costuma ser de acesso aberto na biblioteca digital da ACM. Se abrires
   `https://dl.acm.org/doi/10.1145/3593013.3594053` a partir da rede do ISEP, deve descarregar
   directamente. Eu não consigo lá chegar daqui.*

3. Mete-os em `C:\\Users\\ruifa\\Desktop\\DIMEIA\\data\\literature\\`.
4. Diz-me «PDFs prontos». Leio-os e reforço a §2.7 com os números.

**Se não conseguires:** não é bloqueante. A secção fica como está, correta e mais curta.

---

"""


def main() -> int:
    bruto = ALVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    texto = bruto.replace("\r\n", "\n")
    i, j = texto.find(ANTIGO_INICIO), texto.find(ANTIGO_FIM)
    if i < 0 or j < 0 or j <= i:
        print(f"ABORTADO: marcas nao encontradas (i={i}, j={j})")
        return 1
    resultado = texto[:i] + NOVO + texto[j:]
    ALVO.write_bytes((resultado.replace("\n", "\r\n") if crlf else resultado).encode("utf-8"))
    print("TAREFAS_MANUAIS_HENRIQUE.md actualizado; terminacoes:", "CRLF" if crlf else "LF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
