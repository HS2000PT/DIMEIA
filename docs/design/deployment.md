# deployment.md — Publicar o dashboard InvestiGator (Streamlit Community Cloud)

> Guia para pôr o **dashboard interativo** (`app/streamlit_app.py`) online, de graça, com um URL
> público que se pode citar na tese. É a forma mais simples de um examinador **clicar** e ver o
> sistema a funcionar sem instalar nada.

## O que é o dashboard
Uma interface fina e **sem estado** por cima das funções já validadas do InvestiGator (gatilho de
notícia, gatilho de mercado, avaliação). Não treina nada, não prevê preços, não envia nada.
Corre com o **embedder baseline** (offline, determinístico) — o SBERT/torch não é usado na nuvem
(stack pesada); a vantagem medida do SBERT está na página *Evaluation* (números da tese).

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
- **SBERT:** deliberadamente fora da nuvem (torch é pesado para o tier gratuito). A app di-lo e
  aponta para a página *Evaluation* com os números reais do SBERT.

## Depois de publicado
- Colocar o URL no `README.md` (secção "Try it") e na tese (como artefacto + captura de ecrã).
- Alternativa equivalente: **Hugging Face Spaces** (também gratuito; ver `docs/design/…` futuro).
