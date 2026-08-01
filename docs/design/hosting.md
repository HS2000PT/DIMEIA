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

## 3. A recomendação

**Heroku**, com a repartição que cabe exatamente no crédito:

| Processo | Dyno | Preço | Porquê este |
|---|---|---|---|
| App Streamlit | **Basic** | $7/mês | **Sempre ligado.** Não adormece, que é a falha do Streamlit Community Cloud (hiberna sem visitas). |
| Vigia de alertas | **Eco** | $5/mês | O worker não recebe pedidos HTTP, por isso a regra de adormecer do Eco não se lhe aplica da mesma forma; e é o processo mais barato que corre um ciclo contínuo. |
| | **Total** | **$12/mês** | dentro dos **$13** de crédito, com folga de $1 |

**O que isto compra, em concreto:** o ciclo de alertas passa de *best-effort 1,5–2 h* para
**polling de 60 s**, e a app deixa de precisar do keep-alive que hoje existe só para a manter
acordada. É a diferença entre "o sistema notifica quando calhar" e "o sistema notifica".

**Nota honesta sobre o Eco:** o Heroku documenta que o Eco *adormece após 30 minutos de
inatividade*. Para um processo web isso é fatal; para um worker que está permanentemente a
executar o seu próprio ciclo, não há inatividade que o faça adormecer. Se na prática se revelar
que adormece, a correção é trivial e cabe no crédito: passar o worker a Basic ($7 + $7 = $14, um
dólar acima do crédito) ou manter o vigia no Actions como rede de segurança, que é o que já
acontece hoje.

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
