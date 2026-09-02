# deployment.md — Publicar o dashboard InvestiGator (Streamlit Community Cloud)

> Guia para pôr o **dashboard interativo** (`app/dashboard_v4.py`) online, de graça, com um URL
> público que se pode citar na tese. É a forma mais simples de um examinador **clicar** e ver o
> sistema a funcionar sem instalar nada.

## O que é o dashboard
**Duas vistas, e só duas** (visão final do aluno, 2026-07-12). **📊 Live:** uma aba por
empresa; em cada aba UM gráfico grande estilo Google Finance (intervalos 1D/5D/1M/6M,
intraday via yfinance ~15 min de atraso) com os EVENTOS detetados (anomalias 🔺 + notícias ●,
exatamente os que o canal Telegram recebeu — branch `alerts-history`, nunca recalculados)
marcados no gráfico com hover, a mesma lista numa tabela por baixo, e o "background risk" do
modelo treinado pelo autor (RQ4) numa linha compacta. Read-only. **ℹ️ About:** o que é, como
funciona, avaliação, como receber alertas, citação, e a única "ação" da app (a demo de
retrieval por manchete) num expander. Não treina nada em produção, não prevê preços, não envia nada.
O retrieval de precedentes é **semântico**: o MESMO MiniLM da tese exportado em **ONNX**
(~23 MB, `onnxruntime` CPU, sem torch), descarregado uma vez no arranque com SHA256 pinado
(paridade numérica com o SBERT verificada em `docs/evaluation/onnx_minilm_validation.md`).
Se o modelo não estiver disponível, degrada para o baseline word-overlap — a app nunca cai.

## Correr localmente (para testar antes de publicar)
```bash
pip install -r requirements.txt -r requirements-app.txt
streamlit run app/dashboard_v4.py
# abre http://localhost:8501
```

## Publicar no Streamlit Community Cloud (grátis)

> ⚠️ **OBRIGATÓRIO: Python 3.12 em "Advanced settings" ao criar a app.** Com o defeito
> (3.14), os pins `pandas==2.2.3`/`numpy==2.1.3` NÃO têm wheels → o uv tenta compilar do
> código-fonte durante ~45 min, FALHA em silêncio, e a plataforma arranca a app com o ambiente
> base dela (pandas 3.x, **sem plotly**) → `ModuleNotFoundError` e comportamentos diferentes
> dos testados. Diagnóstico confirmado 2026-07-11 (logs reais de dois deploys). A versão de
> Python de uma app existente NÃO se muda — é preciso apagar e recriar.

1. Garantir que o repositório está no GitHub e **público** (o tier gratuito exige repo acessível).
2. Ir a <https://share.streamlit.io> e autenticar com o GitHub.
3. **New app** → escolher o repositório `HS2000PT/DIMEIA`, o branch `main` e o ficheiro principal
   **`app/dashboard_v4.py`** → **Advanced settings → Python 3.12**.

   ⚠️ **Se a app do Cloud já existe, isto tem de ser MUDADO à mão** (Manage app → Settings →
   Main file path). O Streamlit Cloud guarda o ficheiro principal escolhido no primeiro
   *deploy* e **não** o relê do repositório; promover a v3 no `Procfile` do Heroku não lhe
   toca. Sem esta mudança, a reserva serve a **v1** enquanto o primário serve a **v3** — ou
   seja, dois produtos diferentes no mesmo projecto, e o que a tese descreve é o primário.
4. *Deploy*. A plataforma:
   - já traz o `streamlit` pré-instalado;
   - instala automaticamente o **`requirements.txt`** (stack leve) para o resto das dependências
     (pandas, numpy, yfinance, ...). **Não** é preciso a stack pesada de ML.
5. Ao fim de ~1–2 min fica online num URL do tipo `https://<algo>.streamlit.app`.

## Notas e limites (honestos)
- **Segredos:** o dashboard não precisa de nenhum (não envia Telegram, não usa Finnhub). Se um dia
  precisar, usar *Streamlit secrets* (nunca commitar chaves).
- **Rede:** a página *Market trigger* usa o yfinance ao vivo — funciona na nuvem (tem internet).
- **Adormecer / "sempre online" (honesto):** as apps gratuitas do Community Cloud hibernam
  quando ficam sem visitas e acordam ao primeiro acesso (~30-60s) — não há SLA. Mitigações:
  (1) o workflow Alerts faz um **ping keep-alive** à app em cada corrida (semana + fim de
  semana), o que na prática a mantém acordada; (2) para um site 24/7 A SÉRIO, a mesma VM
  Oracle Free do vigia pode servir o dashboard (`archive/deploy/investigator-app.service` + abrir a
  porta 8501 — ver `vm_watch.md`), sem hibernação nenhuma.
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
- Para o botão "Open the Telegram channel" (vista **ℹ️ About → Get the alerts**): preenche
  `public.channel_url` no `config/alerts.yaml` (não é segredo — o canal é público). O
  histórico partilhado usa `public.history_url` (tem um valor por defeito sensato).
