# deployment.md — Publicar o dashboard InvestiGator (Streamlit Community Cloud)

> Guia para pôr o **dashboard interativo** (`app/streamlit_app.py`) online, de graça, com um URL
> público que se pode citar na tese. É a forma mais simples de um examinador **clicar** e ver o
> sistema a funcionar sem instalar nada.

## O que é o dashboard
**Painel único ao vivo** (redesenho de produto, 2026-07-08): uma aba por ticker da watchlist,
cada uma com o "background risk" do modelo de triagem TREINADO pelo autor (RQ4; pontua todos os
dias, mesmo sem notícia), um gráfico Plotly do preço anotado com cada evento detetado, e a
tabela de histórico — tudo lido do MESMO registo partilhado que o canal Telegram recebeu
(`investigator/alerts_history.py`, branch `alerts-history`), nunca recalculado de forma
independente. "Method & evaluation" (como funciona, os números da tese, uma sandbox de
manchete/ticker, como receber alertas, citação) fica num único `st.expander` no fundo.
Não treina nada em produção, não prevê preços, não envia nada.
O retrieval de precedentes é **semântico**: o MESMO MiniLM da tese exportado em **ONNX**
(~23 MB, `onnxruntime` CPU, sem torch), descarregado uma vez no arranque com SHA256 pinado
(paridade numérica com o SBERT verificada em `docs/evaluation/onnx_minilm_validation.md`).
Se o modelo não estiver disponível, degrada para o baseline word-overlap — a app nunca cai.

## Correr localmente (para testar antes de publicar)
```bash
pip install -r requirements.txt -r requirements-app.txt
streamlit run app/streamlit_app.py
# abre http://localhost:8501
```

## Publicar no Streamlit Community Cloud (grátis)
1. Garantir que o repositório está no GitHub e **público** (o tier gratuito exige repo acessível).
2. Ir a <https://share.streamlit.io> e autenticar com o GitHub.
3. **New app** → escolher o repositório `HS2000PT/DIMEIA`, o branch `main` e o ficheiro principal
   **`app/streamlit_app.py`**.
4. *Deploy*. A plataforma:
   - já traz o `streamlit` pré-instalado;
   - instala automaticamente o **`requirements.txt`** (stack leve) para o resto das dependências
     (pandas, numpy, yfinance, ...). **Não** é preciso a stack pesada de ML.
5. Ao fim de ~1–2 min fica online num URL do tipo `https://<algo>.streamlit.app`.

## Notas e limites (honestos)
- **Segredos:** o dashboard não precisa de nenhum (não envia Telegram, não usa Finnhub). Se um dia
  precisar, usar *Streamlit secrets* (nunca commitar chaves).
- **Rede:** a página *Market trigger* usa o yfinance ao vivo — funciona na nuvem (tem internet).
- **Adormecer:** as apps gratuitas hibernam quando inativas e acordam ao primeiro acesso (alguns
  segundos). É normal.
- **SBERT/torch:** continua fora da nuvem (pesado para o tier gratuito) — mas desde 2026-07-07
  a app usa o **mesmo modelo MiniLM em ONNX** (leve), pelo que o retrieval na nuvem já é
  semântico; a página *Evaluation* mantém os números da tese (medidos com o SbertEmbedder).

## Depois de publicado
- Colocar o URL no `README.md` (secção "Try it") e na tese (como artefacto + captura de ecrã).
- Alternativa equivalente: **Hugging Face Spaces** (também gratuito; ver `docs/design/…` futuro).


## Notas do deploy real (observadas no log do Streamlit Cloud, 2026-07-06)
- O Streamlit Cloud usou **Python 3.14** (o projeto pinna 3.12). A stack leve + streamlit
  funciona em 3.14 (a app boota; 47 pacotes resolvidos com uv), mas por coerência com o projeto,
  se recriares a app escolhe **3.12** em "Advanced settings". Os testes/CI continuam em 3.12.
- Aviso `More than one requirements file (uv requirements.txt vs poetry pyproject.toml)` é
  **benigno**: o pyproject é para o pacote/ferramentas; o Cloud usa o requirements.txt (correto,
  e a linha `-e .` instala o pacote `investigator`).
- Para o botão "Open the Telegram channel" (agora dentro do expander **Method & evaluation → Get
  alerts**): preenche `public.channel_url` no `config/alerts.yaml` (não é segredo — o canal é
  público). O histórico partilhado usa `public.history_url` (tem um valor por defeito sensato).
