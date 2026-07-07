# Migrar para um repositório NOVO sem história de commits

> Pedido do aluno (2026-07-07): mover tudo para um repositório novo, **sem a história**,
> para manter as coisas privadas. É seguro e simples — mas há trade-offs REAIS que
> convém decidir de olhos abertos. Nada aqui foi executado: são os teus cliques.

## 0. Decidir primeiro: privado ou só sem história?

Duas motivações diferentes, duas soluções:

| Queres… | Solução | Custo |
|---|---|---|
| **Esconder a história** (commits, mensagens, evolução) | Repo novo com 1 commit único — pode continuar **público** | Quase nenhum (ver §2) |
| **Esconder o código todo** (repo privado) | Repo novo privado | **Perde-se o produto ao vivo como está** (ver ⚠️ abaixo) |

⚠️ **O que quebra se o repo ficar PRIVADO:**
1. **GitHub Actions deixa de ser ilimitado.** Em repos privados o plano gratuito tem
   ~2.000 min/mês. A varredura intradiária (≈18 corridas/dia útil × 2–3 min ≈
   900–1.300 min/mês) fica *perto ou acima* do limite com o CI incluído — o canal
   Telegram pode parar a meio do mês. Mitigação: reduzir o cron (ex.: 1×/dia ao fecho)
   ou manter o repo público.
2. **Streamlit Community Cloud**: apps de repos privados contam para o limite de 1 app
   privada e o deploy tem de ser re-autorizado; a app pública atual morre com o repo antigo.
3. **Badges e links** no README/tese apontam para o repo antigo (novo repo = **sem
   redireção**; só o *rename* redireciona, criar um novo não).

O canal Telegram em si **não é afetado** (os segredos vivem no runner, basta recriá-los).

## 1. O que a migração NÃO muda (honestidade)

Apagar a história git **não apaga a declaração de uso de IA da tese** — essa fica, por
ser verdadeira (regra do projeto: nunca encobrir). A história desaparece do repo novo,
mas o repo antigo continua a existir até o apagares; **não o apagues** até o novo estar
100% funcional (e considera arquivá-lo privado em vez de apagar).

## 2. Procedimento (≈15 minutos)

```bash
# 1) No GitHub: criar o repo novo (ex.: InvestiGator), público ou privado, VAZIO
#    (sem README/licença auto-gerados).

# 2) Exportar a árvore ATUAL commitada, sem .git (respeita o .gitignore por construção —
#    dados grandes, .env e modelos ONNX ficam de fora, como devem):
cd /c/Users/henri/Desktop/DIMEIA
mkdir ../InvestiGator-novo
git archive HEAD | tar -x -C ../InvestiGator-novo

# 3) Repo novo com UM commit:
cd ../InvestiGator-novo
git init -b main
git add -A
git commit -m "InvestiGator — estado final consolidado (sistema + tese + produto)"
git remote add origin https://github.com/<o-teu-user>/InvestiGator.git
git push -u origin main
```

## 3. Pós-migração (checklist de religação)

- [ ] **Segredos** no repo novo (Settings → Secrets → Actions): `TELEGRAM_BOT_TOKEN`,
      `TELEGRAM_CHAT_ID`, `FINNHUB_API_KEY`.
- [ ] Correr o workflow **Alerts** 1× à mão (Actions → Run workflow) e ver o canal receber.
- [ ] **Streamlit**: share.streamlit.io → New app → repo novo → `app/streamlit_app.py`
      → Advanced: Python **3.12** → depois ⋮ Settings → Sharing → **público**.
      (O URL muda, salvo se apagares a app antiga primeiro e reclamares o mesmo subdomínio.)
- [ ] **README**: atualizar os 3 badges e links (URLs do repo novo) + URL da app se mudou.
- [ ] **CITATION.cff**: atualizar o URL do repositório.
- [ ] **Tese**: nada a fazer — verificado (2026-07-07) que os `.tex` NÃO referenciam o URL
      do repositório nem o da app; a migração não toca na tese.
- [ ] Desativar o cron no repo ANTIGO (`.github/workflows/alerts.yml`) ou arquivar o repo,
      para não haver duas varreduras a publicar no mesmo canal.
- [ ] Só depois de tudo verde: arquivar (não apagar) o repo antigo.

## 4. Alternativa: renomear em vez de migrar

Se o objetivo for só o nome (`DIMEIA` → `InvestiGator`) **mantendo a história**:
Settings → Rename no repo atual. O GitHub redireciona os URLs antigos, o Streamlit e os
badges sobrevivem (atualizar na mesma), e não se perde nada. É a opção sem riscos.
