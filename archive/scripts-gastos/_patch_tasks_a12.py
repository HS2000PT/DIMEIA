"""Actualiza a seccao A12 do docs/contexto/TASKS.md com o que ficou feito a 2026-09-09.

Escrito como script porque o docs/contexto/TASKS.md tem terminacoes CRLF e o edit_block tropeca nelas.
"""
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ALVO = RAIZ / "docs/contexto/TASKS.md"

ANTIGO = """- [ ] A12.1 · Integrar o corpo Muntermann ([Mun04], [Mun04b], [Mun05], [Mun05b], [Mun07], [Mun09])
      em §2.2 e reformular a lacuna face à literatura, não só aos produtos
- [ ] A12.2 · [Oh07] *Financial market monitoring by case-based reasoning* e [But91] em §2.6
- [ ] A12.3 · [Liu23d] *Alert for Alerts*, [Ell20], [Arn19b] em §2.1 — o efeito medido dos alertas
      no investidor de retalho, mesmo que complique a premissa fundadora
- [ ] A12.4 · [Ber23] (contraevidência), [Dav21], [Cau23b], [Waa21], [Kim24], [Kim24b] em §2.7 e §6.4.
      [Waa21] justifica empiricamente a opção por explicação baseada em casos, hoje sem apoio
- [ ] A12.5 · [Nee25] SPA, [Cha22c] DeepTrust, [Fer19] Squawk Bot em §2.2 — sistemas próximos e como diferem
- [ ] A12.6 · [Fen21b] SIGIR em §6.5 — a direção técnica 2 deixa de ser especulativa
- [ ] A12.7 · [Cor21] em §3.6/§5.4 — relevância de notícias sem anotação humana
- [ ] A12.8 · Reconstruir a Tabela 2.3 e reavaliar a afirmação de lacuna da §2.9"""

NOVO = """> **2026-09-09.** Os quatro PDFs que faltavam foram lidos em texto integral. O que cada um diz,
> e o que mudou na tese por causa disso, está em `docs/design/capitulo2_literatura_2026-09-09.md`.
> Oito entradas novas na bibliografia, todas verificadas; uma correção encontrada de caminho
> (`robertson2009bm25`); uma correção no próprio verificador, com testes.

- [x] A12.1 · [Mun09] em §2.2 — a lacuna passa a ser de **postura epistémica** (prever vs. explicar)
      e não de ausência de sistemas. O MoFiN DSS é DSR, é para o mesmo público, e já usava
      **magnitude** e não direção como definição de acontecimento relevante. §2.9 ressalvada.
      *(Os outros cinco Muntermann não foram lidos; [Mun09] é o mais desenvolvido e chega.)*
- [x] A12.2 · [Oh07] em §2.6 — CBR em finanças classifica o **mercado inteiro** e nunca mostra os
      casos. Serve de contraste. *([But91] não foi obtido; não é necessário.)*
- [x] A12.3 · [Liu23d] em §2.1 — três parágrafos no corpo, não em nota: alertas de limiar pioraram
      o desempenho de investidores particulares em ~1 p.p. em seis meses. A resposta da tese é
      limitada e declarada como tal. §2.6 deixou de transpor a fadiga de alertas do domínio
      clínico por analogia. *([Ell20], [Arn19b] não obtidos; [Liu23d] sozinho sustenta o ponto.)*
- [x] A12.4 · [Waa21], [Cau23b], [Ber23] em §2.7 — cinco parágrafos de contraevidência e resposta.
      **⚠️ ERRO MEU CORRIGIDO:** eu tinha escrito que [Waa21] «justifica empiricamente a opção por
      explicação baseada em casos». É o contrário: as explicações por exemplos **não se
      distinguiram de não dar explicação nenhuma** (p = 0,796 e p = 0,283), e o domínio é diabetes,
      não finanças. A resposta da tese usa o diagnóstico dos próprios autores.
- [ ] A12.4b · Descarregar os PDFs de [Cau23b] e [Ber23] (ISEP) — hoje só se cita o que consta dos
      resumos do editor. Sem os PDFs não se citam participantes nem valores. **Tarefa do Henrique.**
- [ ] A12.5 · [Nee25] SPA, [Cha22c] DeepTrust, [Fer19] Squawk Bot em §2.2 — sistemas próximos e como diferem
- [ ] A12.6 · [Fen21b] SIGIR em §6.5 — a direção técnica 2 deixa de ser especulativa
- [ ] A12.7 · [Cor21] em §3.6/§5.4 — relevância de notícias sem anotação humana
- [x] A12.8 · Tabela 2.3 reconstruída (linha «Por que razão acreditar?» passa a declarar que as
      medições com pessoas não confirmam o ganho) e afirmação de lacuna da §2.9 reavaliada
- [x] A12.11 · [Du24] em §2.4 — o vizinho revisto por pares mais próximo. A **ablação dele** mostra
      que aprendizagem contrastiva só sobre texto **degrada** a exatidão. Terceira indicação
      independente de que a direção é o sinal errado
- [ ] A12.12 · **Fechar a ligação à QI4 em §2.2 e §2.4.** Hoje o texto descreve [Du24] e [Mun09]
      sem dizer que esta tese ajusta o codificador e treina sobre magnitude, porque o Capítulo 1
      ainda declara três questões. Meia frase em cada sítio, depois de C7/C8"""


def main() -> int:
    bruto = ALVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    texto = bruto.replace("\r\n", "\n")
    if texto.count(ANTIGO) != 1:
        print(f"ABORTADO: {texto.count(ANTIGO)} ocorrencias, esperava 1")
        return 1
    texto = texto.replace(ANTIGO, NOVO)
    ALVO.write_bytes((texto.replace("\n", "\r\n") if crlf else texto).encode("utf-8"))
    print("docs/contexto/TASKS.md actualizado; terminacoes:", "CRLF" if crlf else "LF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
