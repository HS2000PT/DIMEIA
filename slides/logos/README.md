# Logos das tecnologias — como pôr os logos reais nos slides

O slide **"Built with"** (e o frame **"Feito com"** do guia) já funciona: mostra badges com o
NOME de cada tecnologia. Se quiseres os **logos reais** (o professor adora visuais), basta
**largar aqui os PNG** com os nomes exatos abaixo — o LaTeX passa a mostrar o logo **antes** do
badge, automaticamente. Não é preciso mexer no `.tex`. Se o ficheiro não existir, fica só o badge
(degrada com graça).

## Como fazer (5 min)
1. Descarrega cada logo (links oficiais abaixo), de preferência **PNG com fundo transparente**.
2. Guarda-o **nesta pasta** com o nome exato da coluna "ficheiro" (ex.: `python.png`).
3. Recompila os slides. O logo aparece a 13pt de altura, alinhado com o texto.

> Dica: para ficar consistente, ou pões **todos** os de uma linha, ou nenhum. Alturas diferentes
> misturam-se mal. Usa PNG (não SVG) — o Beamer com pdflatex não lê SVG.

## Ficheiros esperados e onde obter o logo oficial

| Tecnologia | ficheiro | fonte oficial do logo |
|---|---|---|
| FNSPID / Hugging Face | `huggingface.png` | huggingface.co/brand |
| yfinance / Yahoo Finance | `yfinance.png` | github.com/ranaroussi/yfinance (ou logo Yahoo Finance) |
| Finnhub | `finnhub.png` | finnhub.io (rodapé / press kit) |
| RSS | `rss.png` | ícone RSS padrão (feedicons / Wikimedia) |
| Sentence-BERT / MiniLM | `sbert.png` | sbert.net (ou o logo Hugging Face) |
| scikit-learn | `scikit-learn.png` | scikit-learn.org/stable/ (brand) |
| PyTorch | `pytorch.png` | pytorch.org/assets (brand guidelines) |
| ONNX Runtime | `onnx.png` | onnx.ai / github.com/microsoft/onnxruntime |
| Telegram | `telegram.png` | telegram.org/tour (logo) |
| Streamlit | `streamlit.png` | streamlit.io/brand |
| Plotly | `plotly.png` | plotly.com/brand-guidelines |
| Python | `python.png` | python.org/community/logos |
| GitHub Actions | `githubactions.png` | github.com/logos (ou brand.github.com) |
| pytest | `pytest.png` | docs.pytest.org (logo) |

Sem logo (ficam sempre badge, e está bem assim): SPY, calibração Platt, joblib.

## Nota académica
No **corpo da tese** os logos de marca são incomuns; por isso a tese usa a figura da *jornada dos
dados* e badges de nome. Os logos reais fazem mais sentido nos **slides** e no **guia** — que é
exatamente onde este mecanismo está ligado.
