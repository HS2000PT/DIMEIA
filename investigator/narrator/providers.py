"""Clientes de LLM com cadeia de fornecedores — a canalização do narrador.

**O que este módulo é e o que NÃO é.** Aqui só há transporte: enviar um prompt, receber
texto, falhar com graça. **Nenhuma lógica de prompt, nenhum juízo sobre conteúdo** — isso
vive no narrador propriamente dito, que é onde está a contribuição científica (geração
ancorada + avaliação de fidelidade).

**Ordem dos fornecedores, decidida por MEDIÇÃO** (sondagem de 2026-07-29, reproduzível com
`scripts/probe_llm.py`; ver `docs/design/keys.md`). A suposição inicial era Gemini primeiro,
por reputação de free tier generoso. A medição desmentiu-a numa chave acabada de criar:

- `gemini-2.5-flash` / `2.5-flash-lite` → **404**, "no longer available to new users";
- `gemini-2.0-flash*` → **429 à primeira chamada**, quota esgotada;
- `gemini-flash-latest`, `gemini-3-flash-preview` → **200 sem texto** (modelos de raciocínio:
  gastam todo o orçamento de tokens a "pensar" e não chegam a escrever);
- Groq `llama-3.3-70b-versatile` → **0,57 s**, saída fiel ao input.

Daí: **Groq → Gemini → None**. Evita-se de propósito os modelos `-preview` no fallback: um
nome de preview pode desaparecer antes da defesa.

**Fail-open é o contrato.** `complete()` NUNCA levanta e NUNCA bloqueia um ciclo de alertas.
Devolver `None` é um resultado válido e esperado — quem chama volta ao texto determinístico.
O canal e a app têm de funcionar com zero chaves, sem rede, e com os dois fornecedores em
baixo.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from investigator import config

# Fixados pela sondagem. Alterar só com nova medição (`scripts/probe_llm.py`).
GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-flash-lite-latest"  # nome estável, ao contrário dos "-preview"

# Um alerta não pode esperar por um LLM. O Groq responde em ~0,6 s e o Gemini em ~7 s no free
# tier, por isso 12 s cobre o caso lento sem deixar um ciclo pendurado.
TIMEOUT_S = 12.0


@dataclass(frozen=True)
class LLMResponse:
    """Resposta de um fornecedor, com proveniência — o mesmo princípio da cadeia de preços:
    saber QUEM serviu é o que permite medir fiabilidade em vez de a afirmar."""

    text: str
    provider: str
    model: str
    latency_s: float


# Orçamento de saída por defeito: chega para o parágrafo de um alerta, que foi o caso de uso
# para que este módulo nasceu. Um relatório com cinco secções não cabe aqui — e quando não
# cabe, o texto é cortado a meio de uma frase, o que parece uma avaria e não um limite. Quem
# chama passa o seu próprio valor.
MAX_TOKENS = 300


def _post_groq(prompt: str, timeout: float, max_tokens: int = MAX_TOKENS) -> str:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,  # determinismo: a mesma evidência deve dar o mesmo texto
            "max_tokens": max_tokens,
        },
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _post_gemini(prompt: str, timeout: float, max_tokens: int = MAX_TOKENS) -> str:
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
        params={"key": config.GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": max(400, max_tokens)},
        },
        timeout=timeout,
    )
    r.raise_for_status()
    # Modelos de raciocínio devolvem 200 sem `parts`. Tratar como falha para a cadeia seguir
    # em frente, em vez de devolver uma string vazia que passaria por resposta válida.
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


# (nome, nome-da-função, atributo-da-chave, modelo) — a ordem É a preferência.
#
# Guardam-se NOMES, não os objetos-função nem os valores das chaves: a resolução acontece na
# chamada. Guardar as funções congelava a cadeia no momento do import — impossível de
# substituir em teste e impossível de estender em execução; e guardar o valor da chave
# ignoraria um `.env` carregado depois deste módulo.
_CHAIN: tuple[tuple[str, str, str, str], ...] = (
    ("groq", "_post_groq", "GROQ_API_KEY", GROQ_MODEL),
    ("gemini", "_post_gemini", "GEMINI_API_KEY", GEMINI_MODEL),
)


def _has_key(attr: str) -> bool:
    return bool(getattr(config, attr, None))


def available() -> list[str]:
    """Fornecedores com chave, por ordem de preferência ([] = só texto determinístico)."""
    return [name for name, _fn, key_attr, _m in _CHAIN if _has_key(key_attr)]


def complete(prompt: str, timeout: float = TIMEOUT_S, verbose: bool = False,
             max_tokens: int = MAX_TOKENS) -> LLMResponse | None:
    """Percorre a cadeia e devolve a primeira resposta com texto. `None` se todos falharem.

    Nunca levanta. Um fornecedor sem chave é saltado em silêncio (não é erro — é configuração).
    """
    for name, fn_name, key_attr, model in _CHAIN:
        if not _has_key(key_attr):
            continue
        fn = globals()[fn_name]  # resolvido AGORA: permite substituir/estender a cadeia
        t0 = time.time()
        try:
            text = fn(prompt, timeout, max_tokens)
            if not text:
                raise ValueError("resposta vazia")
            return LLMResponse(text=text, provider=name, model=model,
                               latency_s=time.time() - t0)
        except Exception as exc:  # noqa: BLE001  (um fornecedor em baixo não pára a cadeia)
            if verbose:
                print(f"[narrador] {name} falhou em {time.time() - t0:.1f}s "
                      f"({type(exc).__name__}: {str(exc)[:90]}) — a tentar o seguinte")
    if verbose:
        print("[narrador] nenhum fornecedor respondeu — usa-se o texto determinístico")
    return None
