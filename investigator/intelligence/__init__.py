"""Camada de inteligência — a síntese generativa ancorada em evidência medida.

## Onde é que esta camada se encaixa

O sistema tinha quatro camadas e a quarta estava desligada e invisível:

    1. DADOS        preços, manchetes, carimbos temporais           (medido)
    2. ESTATÍSTICA  z-score, excedência empírica, decomposição      (determinístico)
    3. APRENDIZAGEM SBERT, recuperação semântica, triagem calibrada (modelos treinados)
    4. GERAÇÃO      síntese em linguagem natural                    (LLM, ancorado)

O `investigator/narrator/` já implementava a camada 4 para **um** caso — o parágrafo de um
alerta — com uma guarda de vocabulário fechado. Ficou `enabled: false` e, sobretudo, ficou
**invisível no produto**: o utilizador nunca via inteligência nenhuma, via aritmética.

Este pacote generaliza a camada 4 para os âmbitos que o produto precisa (mercado, activo,
período, acontecimento) e — o ponto que interessa academicamente — mantém **cada frase gerada
ligada aos factos que a produziram**.

## A afirmação que este pacote torna verdadeira

> Nenhum número que apareça num texto gerado deixa de existir no pacote de evidência que
> alimentou o gerador, e cada secção gerada declara de que factos saiu.

Não é a mesma garantia do narrador de alertas, e **essa diferença está declarada e medida**
(ver `guard.py`, secção "Dois níveis de garantia"). Fingir que é a mesma seria o tipo de
afirmação que este projecto passou uma auditoria inteira a remover.

## O que o LLM NÃO faz aqui

Não sabe o que aconteceu. Não consulta o mercado. Não tem memória do activo. Recebe um bloco
de factos que os motores calcularam — incluindo a recuperação sobre casos passados com
desfecho **medido** — e o seu trabalho é exclusivamente **redigir a síntese**. É essa a
divisão que torna a coisa defensável: o LLM escreve a língua; os motores escrevem os factos.
"""

from investigator.intelligence.context import (
    Bundle,
    Fact,
    build_asset_bundle,
    build_market_bundle,
)
from investigator.intelligence.guard import GroundingReport, check_grounding
from investigator.intelligence.report import Report, ReportSection, generate_report

__all__ = [
    "Bundle",
    "Fact",
    "GroundingReport",
    "Report",
    "ReportSection",
    "build_asset_bundle",
    "build_market_bundle",
    "check_grounding",
    "generate_report",
]
