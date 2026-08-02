# trocar_de_maquina.md — do zero ao sistema a correr, noutro computador

> **A pergunta:** *"se eu mudar de computador, como fico exatamente na mesma?"*
>
> **A resposta curta:** já tens tudo. O ambiente está no repositório e as chaves estão no Heroku,
> que as devolve no formato certo. São **quatro comandos**, e nenhum deles precisa de te lembrares
> de nada.

---

## Os quatro comandos

```bash
git clone https://github.com/HS2000PT/DIMEIA.git
cd DIMEIA

heroku login
heroku config -s --app investigator-meia > .env    # ← as chaves, do cofre

bash scripts/setup_env.sh                          # ambiente Python 3.12 fixado
```

**Verificado a 2026-08-02:** o `.env` reconstruído a partir do Heroku tem as **8 chaves com valor
idêntico** ao original. Não é uma sugestão teórica; foi testado nos dois sentidos.

> A única que não volta é a `GNEWS_API_KEY`, porque não é usada pelo sistema em produção (o
> `investigator/config.py` não a lê). Se um dia for precisa, está no `.env.example` com a
> indicação de onde a obter.

---

## Porque é que isto já funciona (e não precisas de mais uma ferramenta)

Sem saberes, as chaves ficaram guardadas em **três sítios independentes** ao longo do projeto:

| Onde | Serve para | Consegues lê-las de volta? |
|---|---|---|
| `.env` local | desenvolvimento na tua máquina | sim, mas só nessa máquina |
| **GitHub Actions Secrets** | o cron de alertas | **não** (o GitHub nunca as devolve) |
| **Heroku config vars** | a app e o vigia 24/7 | **sim**, com `heroku config -s` |

É o terceiro que resolve o teu problema. O Heroku é, na prática, o teu gestor de segredos: está
autenticado à tua conta, sobrevive à perda do computador, e devolve exatamente o formato que o
`.env` precisa.

**O que isto NÃO protege:** se apagares a app do Heroku, apagas o cofre. Por isso, antes de
qualquer operação destrutiva, corre o comando de exportação e guarda o ficheiro fora do
repositório (nunca dentro: o `.env` está no `.gitignore` e deve continuar).

---

## O ambiente (bibliotecas, versões) já está no repositório

Nada disto precisa de cofre, porque não são segredos:

| Ficheiro | O que fixa |
|---|---|
| `.python-version` | Python 3.12 |
| `requirements.txt` | a stack base, com versões fixadas |
| `requirements.lock.txt` | o conjunto completo resolvido |
| `requirements-ml.txt` | a stack pesada (torch/SBERT), só para re-treinar |
| `scripts/setup_env.sh` | cria o ambiente virtual e instala tudo |

O `setup_env.sh` sem argumentos instala a stack leve, que chega para a app, os alertas, os testes
e as figuras. Com `--ml` acrescenta o torch e o Sentence-BERT, que só são precisos para refazer os
embeddings de raiz.

---

## Se quiseres um cofre a sério (opcional)

O Heroku resolve o teu caso, mas se um dia quiseres uma ferramenta dedicada, o **Doppler** tem
plano *Team* gratuito no GitHub Student Pack. Vale a pena se passares a ter mais ambientes
(desenvolvimento, testes, produção) com valores diferentes. Para um `.env` com oito chaves e um
único ambiente, é mais ferramenta do que problema.

**O que NÃO fazer, em nenhuma circunstância:** committar o `.env`, mesmo num repositório privado.
O histórico do git é para sempre e um repositório privado pode tornar-se público por engano.

---

## Rotação: quando (e como) trocar uma chave

Se uma chave for exposta, trocá-la é rápido. Todas as fontes usadas são gratuitas e emitem chaves
novas em minutos.

```bash
# 1. gerar a nova no site do fornecedor
# 2. atualizar nos dois sítios que a leem:
heroku config:set NOME_DA_CHAVE="nova" --app investigator-meia
#    e em GitHub → Settings → Secrets and variables → Actions
# 3. atualizar o .env local
```

Depois confirma que o vigia continua a correr:

```bash
heroku logs --dyno=worker --tail --app investigator-meia
```

O sistema é **fail-open**: sem uma chave opcional, degrada e diz o que lhe falta em vez de parar.
As únicas realmente necessárias para o produto funcionar são o `TELEGRAM_BOT_TOKEN`, o
`TELEGRAM_CHAT_ID` e a `FINNHUB_API_KEY`.
