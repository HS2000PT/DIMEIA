# hosting.md — onde correr o vigia, decidido com os números de hoje

> **Estado:** análise fechada a **2026-08-01**, com as ofertas verificadas na própria página do
> GitHub Student Developer Pack e nos preços do fornecedor nesse dia. **Falta só o clique do
> aluno.** Nada nesta página altera um único número da tese: é produto, não ciência.

---

## 1. O problema que isto resolve (e o que NÃO resolve)

O aluno disse que *"os alertas chegam demasiado tarde"*. A causa está medida e não é o código: o
`cron` do GitHub Actions é **best-effort** e, na prática, corre de **1,5 a 2 horas**, não de 30 em
30 minutos. Um facto de mercado das 14:35 pode ser entregue às 16:10.

O caminho já desenhado e testado para isso é o **modo vigia** (`run_alerts.py --watch`), com
polling de 60 s, descrito em [`vm_watch.md`](vm_watch.md). Precisa de uma máquina que esteja
sempre ligada. É essa máquina que esta página escolhe.

**O que não resolve:** a latência do *facto* até à *fonte*. Se o Finnhub publicar a manchete com
oito minutos de atraso, nenhum alojamento recupera esses oito minutos. O que se ganha é o troço
que está sob o nosso controlo, e o `latency_seconds()` já mede os dois separadamente.

---

## 2. Estado real das opções, a 2026-08-01

| Opção | Oferta | Estado hoje | Serve? |
|---|---|---|---|
| **Oracle Cloud Free** | VM ARM gratuita para sempre | ⚠️ **bloqueado** — a criação de conta falhou, ticket aberto no suporte | Talvez, sem data |
| **DigitalOcean** | $200 em crédito **"through 7/31/26"** | ❌ **a janela fechou ontem** | Não |
| **Heroku** | **$13/mês durante 24 meses** ($312) | ✅ ativo | **Sim** |
| **Microsoft Azure** | $100 + 25 serviços gratuitos | ✅ ativo | Possível, mas o crédito é único e esgota |
| **GitHub Actions** (atual) | grátis | ✅ a correr | Só como rede de segurança |

O ponto decisivo contra o Azure não é o preço, é a **forma** do crédito: $100 de uma vez esgotam-se
e deixam o sistema a cair sem aviso, enquanto $13/mês durante 24 meses cobrem a entrega
(13 de setembro de 2026), a defesa, e mais um ano depois disso.

---

## 3. A recomendação (e o que ela custa mesmo)

> ⚠️ **Secção reescrita a 2026-08-02, DEPOIS de implantar.** O plano original dizia Basic ($7)
> para a app + Eco ($5) para o vigia = $12/mês. **Esse plano não existe:** o Heroku recusa
> misturar tipos de dyno na mesma app (*"You can't mix dyno types: Basic and Eco"*). Abaixo
> ficam os números reais, verificados na conta.

| Processo | Dyno | Preço | Porquê este |
|---|---|---|---|
| App Streamlit | **Basic** | $7/mês | Sempre ligado; não hiberna como o Streamlit Community Cloud |
| Vigia de alertas | **Basic** | $7/mês | Obrigatório: não se pode misturar com Eco |
| | **Total** | **$14/mês** | |

**E mesmo assim compensa, porque o crédito não é o que a oferta anuncia.** A página do Student
Pack diz "$13 por mês durante 24 meses", mas na conta o crédito aparece como um **saldo único de
$312** a expirar em **2028-07-31**. A $14/mês isso dá **≈22 meses** de autonomia, contra uma
entrega a seis semanas de distância. A aritmética mensal era a preocupação errada.

**Um passo que a oferta não menciona:** o Heroku exige **verificação da conta com cartão** antes
de criar qualquer app, mesmo com $312 de crédito por gastar. Os créditos são consumidos primeiro;
o cartão só é cobrado se a despesa os exceder.

**O que isto compra, em concreto:** o ciclo de alertas passa de *best-effort 1,5–2 h* para
**polling de 60 s**, e a app deixa de precisar do keep-alive que existia só para a manter
acordada.

**Se o orçamento apertar**, a saída barata é manter só o worker no Heroku ($7/mês, ≈44 meses) e
deixar a app no Streamlit Community Cloud, que é grátis e hiberna. A latência dos alertas é o
problema que importa; a app a acordar em dez segundos não é.
---

## 4. Porque não simplesmente esperar pela Oracle

Continua a ser a opção **gratuita para sempre**, e se o ticket for resolvido vale a pena. Mas:

1. **Não tem data.** O ticket está aberto sem prazo, e faltam seis semanas para a entrega.
2. **A capacidade ARM da camada gratuita é notoriamente escassa** — mesmo com conta criada, a
   criação da instância falha com frequência por falta de capacidade na região.
3. **O crédito Heroku não se gasta se não for usado**, mas os 24 meses começam a contar quando se
   ativa. Ativar agora e migrar para a Oracle depois é perfeitamente possível; o inverso, esperar e
   descobrir a duas semanas da entrega que a Oracle não vai acontecer, não é.

**Recomendação prática:** ativar o Heroku agora, e manter o ticket da Oracle aberto. Se a Oracle
aparecer, migra-se sem pressa.

---

## 5. Passos (são cliques, não engenharia)

1. Confirmar o Student Pack ativo em <https://education.github.com/pack>.
2. Reclamar a oferta Heroku (crédito aplicado à conta).
3. Criar a app; ligar ao repositório.
4. `Procfile` com dois processos: `web` (Streamlit) e `worker` (`run_alerts.py --watch`).
5. Definir os segredos como *config vars* — os **mesmos nomes** do `.env`, listados em
   [`keys.md`](keys.md). Nunca no repositório.
6. Escalar: `web` a Basic, `worker` a Eco.
7. Manter o workflow do Actions **ligado** como rede de segurança. A deduplicação por histórico
   partilhado já impede alertas em duplicado, por isso os dois podem correr ao mesmo tempo sem
   estragar nada.

---

## 6. O que isto significa para a tese

**Nada muda nos números.** A latência é reportada como **medida**, e continuará a sê-lo: se o
vigia entrar em produção, a mediana medida desce e o Capítulo 4 passa a poder dizer *quanto* desceu
com o mesmo instrumento que já a mede hoje. Se não entrar, a limitação fica como está, medida e
declarada.

É exatamente por isso que a instrumentação foi feita **antes** desta decisão: qualquer que ela
seja, o efeito é observável em vez de alegado.
