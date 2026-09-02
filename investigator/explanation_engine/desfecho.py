"""O desfecho observado, acrescentado à mensagem original dias depois.

## Porque é isto que dá valor ao alerta em dois tempos

Enviar o esboço primeiro e editá-lo com a análise poupa segundos — a medição do Capítulo 4 é
clara: a mediana entre a deteção e a entrega é de 5 segundos, e os 353 minutos que separam a
publicação da deteção são da fonte e não do sistema. O ganho real está aqui: uma vez que a
mensagem é editável, ela pode ser **anotada com o que veio a acontecer**, no sítio onde a
afirmação foi feita e para quem a leu.

É a diferença entre um sistema que explica e um sistema que se deixa verificar. Nenhum dos
produtos comparados no Capítulo 2 volta atrás para dizer como correu.

## As três regras que impedem isto de virar uma previsão disfarçada

1. **Acrescenta, nunca substitui.** O texto original fica intacto por baixo. Reescrever a
   afirmação depois de saber o resultado é a forma mais eficaz de parecer sempre certo.
2. **Diz que é o desfecho da empresa, e não o efeito do alerta.** O sistema não sabe o que
   causou o movimento, e o alerta não é uma intervenção. Uma anotação que sugerisse causa
   estaria a afirmar exatamente aquilo que a dissertação recusa afirmar.
3. **Diz que não era conhecível.** Sem essa frase, um leitor que veja dez anotações positivas
   conclui que o sistema prevê. A anotação é medição retrospetiva, e tem de o dizer de cada
   vez, não uma vez.

Puro: só constrói texto. Quem obtém os preços e edita as mensagens é
`scripts/anotar_desfechos.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

HORIZONTES = (1, 3, 5)

TITULO = "📌 <b>What happened next</b>"
AVISO = ("<i>This is what the stock did after the alert, measured from the close of the alert "
         "day. It is not a claim that the alert caused it, and none of it was knowable when "
         "the alert was sent.</i>")


@dataclass(frozen=True)
class Desfecho:
    """Retorno observado a `dias` sessões do alerta. `retorno` a `None` = ainda não há barra."""

    dias: int
    retorno: float | None


def _pct(v: float) -> str:
    # O menos tipográfico (U+2212) e não o hífen: num telemóvel, "-0.40%" com hífen lê-se mal
    # a par de "+0.40%", porque o hífen é mais estreito e as duas linhas deixam de alinhar.
    texto = f"{v * 100:+.2f}%"
    return texto.replace("-", "−", 1) if texto.startswith("-") else texto


def anotacao(desfechos: list[Desfecho]) -> str:
    """As linhas a acrescentar à mensagem. Cadeia vazia se ainda não houver nada medido.

    **Só entram horizontes já medidos.** A primeira versão imprimia «+5d · not yet available»
    como espaço reservado, e isso partia a deteção de novidade: a linha do quinto dia passava a
    existir no texto antes de haver valor, e no dia em que o valor chegasse o sistema concluía
    que já lá estava e não editava. Um espaço reservado que impede a informação de chegar é
    pior do que a sua ausência.

    Devolver cadeia vazia — e não um bloco a dizer «sem dados» — é igualmente deliberado: uma
    edição que não acrescenta informação faz a mensagem aparecer como «editada» a quem já a
    leu, sem lhe dar nada em troca.

    **Não há carimbo de quando foi acrescentado**, e a razão é a mesma. Um «adicionado há 3
    dias» muda todos os dias, obrigaria a uma edição diária de cada mensagem, e cada edição é
    uma notificação. Os horizontes «+1d», «+3d» e «+5d» já dizem que a medição é posterior, e
    o aviso final di-lo por extenso.
    """
    medidos = [d for d in sorted(desfechos, key=lambda x: x.dias) if d.retorno is not None]
    if not medidos:
        return ""
    linhas = [TITULO]
    linhas += [f"▸ +{d.dias}d · {_pct(d.retorno)}" for d in medidos]
    linhas.append(AVISO)
    return "\n".join(linhas)


def anotar(texto_original: str, desfechos: list[Desfecho]) -> str:
    """O texto da mensagem com o desfecho anexado. Devolve o original se nada houver a anexar.

    ⚠️ Idempotente e progressivo: chamar duas vezes não duplica o bloco, e chamar de novo com
    um horizonte a mais substitui o bloco antigo pelo novo. O trabalho agendado corre todos os
    dias sobre as mesmas mensagens à medida que os horizontes ficam disponíveis.
    """
    novo = anotacao(desfechos)
    if not novo:
        return texto_original
    base = texto_original.split(TITULO)[0].rstrip()
    return f"{base}\n\n{novo}"


def esta_anotado(texto: str) -> bool:
    return TITULO in texto


def precisa_de_edicao(texto: str, desfechos: list[Desfecho]) -> bool:
    """True se anotar acrescentaria alguma coisa ao que a mensagem já mostra.

    É esta a guarda que impede a única forma de esta funcionalidade incomodar quem a recebe:
    uma notificação de edição que não traz nada de novo. Poupa também uma chamada à API do
    Telegram por mensagem e por dia.
    """
    return anotar(texto, desfechos) != texto
