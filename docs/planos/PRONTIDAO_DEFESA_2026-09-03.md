# Prontidão do portátil da defesa — inventário e lacunas

Data: 2026-09-03. Máquina: **hsantos**, `C:\Users\ruifa\Desktop\DIMEIA`. É este o portátil que
vai ser usado no dia.

**O que esta passagem é.** Inventário de ficheiros, leitura de configuração e do ambiente
Python, mais um verificador novo que corre localmente e sem rede. **O que não é.** Não corri
nada neste portátil — esta sessão não tem acesso a uma consola aqui, só a leitura e escrita de
ficheiros. Tudo o que precisa de execução está na lista de comandos do fim, e essa lista é
curta de propósito.

Nenhum valor de credencial foi lido, copiado ou escrito em parte alguma. O `.env` **não** foi
aberto por esta sessão; a verificação de chaves acontece na tua máquina, e olha apenas para os
nomes.

## 1. O que está bem, e é a maior parte

| Peça | Estado |
|---|---|
| **Ambiente Python** | `.venv` completo, com o pacote `investigator` instalado em modo editável. |
| **Versões fixadas** | `numpy 2.1.3` e `pandas 2.2.3` — exatamente os *pins* do projeto. Isto importa: noutra máquina o `numpy` tinha derivado para 2.5 e os artefactos `joblib` emitiam avisos de depreciação ao carregar. Aqui não. |
| **Stack de modelos** | `scikit-learn 1.9.0` (a versão que gravou o artefacto), `joblib 1.5.3`, `onnxruntime 1.27.0`, `tokenizers 0.22.2`. |
| **Stack pesada** | `torch 2.12.1+cpu`, `sentence-transformers 5.6.0`, `transformers 5.12.1` — presentes, embora não sejam precisas no dia. |
| **Produto** | `fastapi`, `uvicorn`, `streamlit`, `plotly`, `yfinance`, `playwright`. |
| **Qualidade** | `pytest 8.3.4`, `ruff 0.8.6`. |
| **Modelo de triagem** | `models/triage_context_lr.joblib` (+ sidecar JSON com o período, as linhas por bloco e as métricas de teste). |
| **Codificador semântico** | `models/onnx/model_quint8_avx2.onnx` (23,0 MB) e `tokenizer.json` (0,5 MB), ambos presentes. **Verifiquei o SHA256 dos dois contra os valores pinados no código e correm: embebi uma frase e saiu um vetor de 384 dimensões, sem rede.** A recuperação semântica funciona numa sala sem wi-fi. |
| **Bases de casos** | `kb_sample.jsonl`, `kb_fnspid_light.jsonl` (7,7 MB), `backfill_kb_meta.jsonl` + `backfill_kb_vec.npy` (58,7 MB), `dashboard_snapshot.json`. |
| **Configuração** | `config/alerts.yaml` com as doze empresas, orçamento diário de 5 e o piso escalonado. |
| **`.env`** | Existe. Quais das chaves estão preenchidas: verifica-se com o comando 3 abaixo. |
| **Tese** | `tese-v2/main.pdf`, 1,99 MB, compilado hoje. |
| **Materiais** | Guia de estudo (PDF), doze documentos de defesa em `docs/defence/`, logótipos das doze empresas e das tecnologias. |

## 2. Lacunas encontradas, por ordem de risco

### 🔴 A demonstração de defesa não corre sem internet — e é a única coisa mesmo crítica

`scripts/demo_defesa.py` lê três registos (`gate_log.jsonl`, `predictions_log.jsonl`,
`alerts_history.jsonl`) e guarda-os em **`data/_demo_cache/`**. **Essa pasta não existe neste
portátil.** Com `--offline` numa sala sem rede, o guião termina com
*«Sem gate_log.jsonl em cache e sem rede. Corre uma vez com internet.»*

Resolve-se com uma execução, hoje, com internet — é o comando 1 do fim.

⚠️ E há uma dependência que convém saber: a cache vem de
`raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/`, **sem autenticação**. Se o
repositório passar a privado antes da defesa, essa descarga deixa de funcionar — e falha em
silêncio, devolvendo lista vazia, que é o defeito já descrito em `docs/design/v3_backlog.md`.
Com a cache criada, o dia está protegido de qualquer forma.

### 🟠 Os *slides* de defesa ainda são os da tese anterior

`slides/main.pdf` e `slides/main-pt.pdf` são de 2026-08-29 e pertencem à árvore `thesis/`, não à
`tese-v2/`. Não é um problema deste portátil — é trabalho por fazer, e já está no plano final
como frente 8. Fica registado aqui para não ser descoberto na véspera.

### 🟠 Os dados integrais das avaliações não estão nesta máquina

Faltam `triage_dataset.csv`, `triage_dataset_ext.csv`, `finnhub_news.csv`,
`fnspid_news_subset.csv` e `kb_fnspid_sbert.jsonl`. **Isto não afeta o dia da defesa**: nada do
que se mostra depende deles, e os números da tese vêm dos artefactos de avaliação em
`docs/evaluation/`, que estão cá.

Afeta duas coisas, e ambas são de antes do dia: re-correr uma avaliação da tese, e o retreino.
Se quiseres poder responder a *«consegue mostrar-nos isso a correr?»*, isso tem de ser tratado
antes, não no dia.

### 🟡 `predictions_log.jsonl` e `gate_log.jsonl` só existem na branch de dados

Estão em `origin/alerts-history`, não em `data/`. É o desenho correto (o registo vive na nuvem),
mas implica um `git fetch` antes de correr a auditoria do retreino ou o
`evaluate_gate_selectivity.py`. Não é preciso no dia.

### 🟡 Cadeia de LaTeX por confirmar

Não consigo ver daqui se o MiKTeX está instalado. O PDF final já existe, portanto só interessa
se quiseres recompilar. O verificador diz-te se o `latexmk` está no PATH.

## 3. O verificador novo

`scripts/check_prontidao_defesa.py` — corre em segundos, **sem rede**, e responde a uma
pergunta só: *se a sala não tiver internet e nada puder ser instalado, o que é que ainda
funciona?*

Verifica o interpretador e dezoito pacotes, o carregamento do modelo de triagem, a
correspondência entre o contrato de *features* do artefacto e o código atual (a guarda que
apanha um *bundle* desatualizado antes de ele falhar à frente do júri), o SHA256 dos dois
ficheiros ONNX **e um arranque real do codificador**, os ficheiros de dados que a demonstração
lê, a configuração, a presença de cada chave do `.env` — nunca o valor — e os documentos.

Sai com código 0 se nenhuma verificação crítica falhar. Corre-o na véspera e na manhã do dia.

Foi verificado numa cópia parcial da árvore, incluindo o caminho de sucesso do codificador ONNX
(vetor de 384 dimensões, sem rede) e o caminho de falha de tudo o resto; `ruff` limpo. **Nunca
correu neste portátil** — é o comando 2.

## 4. O que correr, por esta ordem, hoje

```powershell
# 1. Criar a cache da demonstração — PRECISA de internet, e é a lacuna crítica.
.\.venv\Scripts\python.exe scripts\demo_defesa.py --listar

# 2. Verificar a prontidão. Deve sair a zero.
.\.venv\Scripts\python.exe scripts\check_prontidao_defesa.py

# 3. Confirmar que a demonstração corre MESMO sem rede (desliga o wi-fi antes).
.\.venv\Scripts\python.exe scripts\demo_defesa.py --offline

# 4. E que a demo offline dos dois gatilhos também corre.
.\.venv\Scripts\python.exe scripts\demo.py

# 5. A suite, uma vez, para saber em que estado está a árvore.
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Se o passo 3 falhar depois do passo 1 ter corrido com internet, o problema é a cache e não a
rede — verifica que `data\_demo_cache\` tem os três ficheiros.

## 5. Antes do dia, e não no dia

- **Gravar a demonstração em vídeo.** O guião está em `docs/defence/gravar_demo.md`. É o plano B
  para o caso de a sala não ter rede *e* alguma coisa correr mal com o portátil. Ter o ficheiro
  localmente, não numa nuvem.
- **Levar o PDF da tese também numa pen**, e não só no portátil.
- **Decidir se o repositório fica público.** Se passar a privado, a cache da demonstração e o
  painel deixam de ler a branch de dados — com a cache criada, a demonstração aguenta; o painel
  ao vivo não.
- **Rodar as credenciais expostas** continua na lista de pendências humanas há várias sessões
  (PAT do GitHub primeiro, tem `admin`). Não é do dia da defesa, mas é do antes.
- **Sincronizar os *slides* com a `tese-v2/`.**
