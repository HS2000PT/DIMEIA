# vm_watch.md — Alertas em quase-tempo-real numa VM gratuita (modo vigia)

> **Porquê:** o cron gratuito do GitHub Actions é *best-effort* — medimos intervalos reais de
> **1,5–2 h** entre corridas (2026-07-10), não os 30 min do cron. Para latência de **minutos**,
> o runner ganhou um modo vigia (`--watch`) que corre em qualquer máquina Linux sempre ligada.
> Decisão do aluno (2026-07-11): usar uma **VM Oracle Cloud Free** (Always Free). O cron do
> GitHub continua ativo como **rede de segurança** — o dedup partilhado (branch `alerts-history`)
> garante que os dois produtores nunca duplicam alertas no canal.

## Como funciona

```
VM (systemd) ── run_alerts.py --watch --interval 300 ──┐
                                                        ├─> canal Telegram (dedup partilhado)
GitHub Actions (cron, rede de segurança) ──────────────┘
                └──── ambos leem/escrevem alerts_history.jsonl (branch alerts-history)
```

- `--watch`: loop contínuo (1 ciclo a cada ~5 min + jitter), paragem limpa com SIGTERM,
  estado persistente no disco da VM, config relida a cada ciclo (ajustes a quente).
- **Deteção intradiária (só neste modo):** em cada ciclo, a cotação em TEMPO REAL do Finnhub
  (`/quote`) avalia o retorno de hoje em curso contra a norma diária (o mesmo z-score) —
  "caiu 4,8% em 12 min" alerta em minutos. Guarda de sessão US (fora de horas não avalia
  cotações estagnadas). `market.intraday.enabled` no alerts.yaml.
- Antes de cada ciclo, o estado é **semeado com o histórico partilhado** — o que o Actions já
  enviou hoje, a VM não repete (e vice-versa).
- Com `INVESTIGATOR_HISTORY_GIT=1`, a VM também **publica** o histórico na branch de dados
  (commit+push com um PAT local à VM; fail-open — uma falha de push nunca trava um alerta).
- A branch de dados carrega também a **KB viva** (`live_pending.jsonl` + `live_kb.jsonl`):
  manchetes relevantes capturadas em cada ciclo e maturadas a +5d — os precedentes recentes
  que a fusão com decaimento prefere.

## Testar JÁ no teu PC (sem VM)

```bash
python scripts/run_alerts.py --watch --interval 300 --dry-run   # vigia sem enviar
python scripts/run_alerts.py --watch --interval 300             # vigia real (envia)
```
Funciona em Windows também (Ctrl+C para parar). A VM é só a versão "sempre ligada" disto.

## Criar a VM Oracle Free (cliques teus, ~20 min, 1×)

1. Conta em <https://www.oracle.com/cloud/free/> (pede cartão para verificação; o tier
   **Always Free** não cobra — confirma sempre que a *shape* diz "Always Free eligible").
2. Compute → Create instance → imagem **Ubuntu 24.04**, shape **VM.Standard.A1.Flex**
   (Always Free: até 4 OCPUs/24 GB — 1 OCPU/6 GB chega de sobra). Gera/descarrega a chave SSH.
3. Entra por SSH: `ssh ubuntu@<ip-da-vm>`.

## Instalar (na VM, ~5 min)

```bash
git clone https://github.com/HS2000PT/DIMEIA.git && cd DIMEIA
bash deploy/setup_vm.sh
```
O script pede-te 2 coisas:
- **PAT do GitHub** (para a VM publicar o histórico partilhado): GitHub → Settings →
  Developer settings → Fine-grained tokens → repo `DIMEIA`, permissão **Contents: Read and
  write**, mais nada. O PAT fica SÓ na VM (no remote do checkout da branch de dados).
- **Preencher o `.env`** (`nano .env`): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
  `FINNHUB_API_KEY` — os mesmos 3 segredos do Actions.

Depois:
```bash
sudo systemctl enable --now investigator-watch
journalctl -u investigator-watch -f        # ver os ciclos ao vivo
```

## Operação e honestidades

- **Ver estado:** `systemctl status investigator-watch` · **parar:** `sudo systemctl stop …`
- **Atualizar o código:** `cd ~/DIMEIA && git pull && sudo systemctl restart investigator-watch`.
- A VM é mais uma peça para manter (patches do Ubuntu, IP pode mudar se a recriares). Se um dia
  a desligares, **nada parte**: o cron do GitHub continua a cobrir (com a latência dele).
- O Oracle Free pode reclamar instâncias Always Free ociosas em regiões cheias (raro em uso
  contínuo como este). Se acontecer, recriar e correr o setup de novo (~10 min).
- Segurança: os segredos vivem no `.env` da VM e no PAT do remote — **nunca** no repositório;
  a VM não expõe portas (só faz chamadas de saída).
