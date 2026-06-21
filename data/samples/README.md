# data/samples — amostras versionadas

Só amostras **pequenas** são versionadas (§5.4). Os dados grandes (subconjunto FNSPID
completo, KB completa) ficam em `data/` e são gitignored, recriados pelos scripts.

| Ficheiro | Origem | Notas |
|---|---|---|
| `news_sample.csv` | **Sintético / ilustrativo** (escrito à mão) | Títulos inventados para demonstrar o pipeline sem descarregar o FNSPID. **Não são notícias reais.** Tickers reais para casar com preços do yfinance. |
| `fnspid_news_sample.csv` | Gerado por `scripts/download_data.py` (FNSPID real) | Cabeça do subconjunto real (CC BY-SA 4.0). Só títulos — não republicar texto integral. |
| `kb_sample.jsonl` | Gerado por `scripts/build_kb.py` | Amostra da base de conhecimento (notícia + impacto + embedding). |

## Demonstração rápida (sem descarregar o FNSPID)

```bash
# Constrói uma KB a partir da amostra sintética + preços reais (yfinance):
python scripts/build_kb.py --news data/samples/news_sample.csv \
    --out data/kb_demo.jsonl --sample data/samples/kb_sample.jsonl
```

## Atribuição (FNSPID)

Dong, Z., Fan, X., & Peng, Z. (2024). *FNSPID: A Comprehensive Financial News Dataset in
Time Series.* arXiv:2402.06698. Licença CC BY-SA 4.0.
