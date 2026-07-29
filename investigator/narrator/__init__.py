"""Narrador — a camada de LINGUAGEM do sistema.

Princípio de desenho, e a razão de ser defensável: **o LLM escreve a língua, nunca os factos.**
Todos os números vêm dos motores determinísticos (deteção de anomalia, decomposição,
retrieval de precedentes, triagem); o modelo só os põe em prosa legível, e uma guarda de
fidelidade em execução (`check_faithfulness`) rejeita qualquer resposta que invente um
número, use linguagem preditiva/de conselho, ou omita o facto central — caindo então no
template determinístico. O texto entregue é seguro POR CONSTRUÇÃO, não por confiança.

- `providers` — transporte (cadeia Groq → Gemini → None), sem juízo de conteúdo;
- `evidence` — o contrato de dados; enumera mecanicamente os números permitidos;
- `core` — prompt citável, template-chão, verificador puro e `narrate()` com guarda.
"""

from investigator.narrator.core import (
    FaithfulnessReport,
    NarrationResult,
    build_prompt,
    check_faithfulness,
    narrate,
    template_text,
)
from investigator.narrator.evidence import AlertEvidence, Precedent, fmt_num, fmt_pct
from investigator.narrator.providers import LLMResponse, available, complete

__all__ = [
    "AlertEvidence",
    "FaithfulnessReport",
    "LLMResponse",
    "NarrationResult",
    "Precedent",
    "available",
    "build_prompt",
    "check_faithfulness",
    "complete",
    "fmt_num",
    "fmt_pct",
    "narrate",
    "template_text",
]
