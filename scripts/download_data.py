"""Descarrega e prepara o FNSPID (stub).

Dataset: FNSPID — Financial News and Stock Price Integration Dataset.
- Hugging Face: Zihan1004/FNSPID
- GitHub: Zdong104/FNSPID_Financial_News_Dataset
- Licença: CC BY-SA 4.0 — ATRIBUIÇÃO OBRIGATÓRIA no README e na tese.

Nesta fase (Sessão 0) é apenas um stub. A lógica real (descarregar, subselecionar
tickers + janela temporal, limpar, guardar amostras em data/samples/) é implementada
numa fase posterior. Decisões de subconjunto/pré-processamento ficam em docs/data_card.md.

Governança (§5.4): dados grandes são gitignored e recriados por este script; só amostras
pequenas vão para data/samples/. Não republicar texto integral de notícias de terceiros.
"""

from __future__ import annotations


def main() -> None:
    """Ponto de entrada do download/preparação do FNSPID. Ainda não implementado."""
    raise NotImplementedError(
        "Download do FNSPID ainda não implementado — ver docs/data_card.md e "
        "progress/PLANO_SESSOES.md."
    )


if __name__ == "__main__":
    main()
