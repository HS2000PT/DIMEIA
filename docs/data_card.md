# data_card.md — Cartão de dados (reproduzível)

> Fonte, licença, atribuição, subconjunto exato de tickers e janela temporal escolhidos, e cada decisão de
> pré-processamento/limpeza (para o dataset ser reproduzível).

## FNSPID (camada histórica)
- **Fonte:** Hugging Face `Zihan1004/FNSPID`; repo `Zdong104/FNSPID_Financial_News_Dataset`.
- **Licença:** **CC BY-SA 4.0** — atribuição obrigatória no README e na tese.
- **Subconjunto (tickers / janela):** a definir na Fase C.
- **Pré-processamento:** a documentar.

## Camada live
- Fontes e tratamento a documentar na Fase C (ver `free_apis.md`).

> Nota de governança: dados grandes gitignored e recriados por `scripts/download_data.py`; só amostras pequenas
> em `data/samples/`. Não republicar texto integral de notícias de terceiros — citar minimamente.
