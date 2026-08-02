# arquitetura_dados.md — "tens uma base de dados?"

> A pergunta do teu irmão é boa, e é quase certo que aparece na defesa noutra forma: *"onde é que
> os dados vivem, e porquê assim?"*. Esta página é a resposta, com o que existe mesmo e a
> justificação honesta de cada escolha, incluindo o que **não** é ideal.

---

## Resposta curta

**Sim, há três camadas de persistência, e uma delas é mesmo uma base de dados.** O que não há é
um servidor de base de dados, e isso foi uma decisão, não um esquecimento.

| Camada | O que guarda | Tecnologia | Onde |
|---|---|---|---|
| Subscrições do bot | quem segue que tickers | **SQLite** | ficheiro local do bot |
| Histórico partilhado | alertas enviados, decisões, casos maturados | **JSONL** versionado | branch `alerts-history` |
| Artefactos de modelo | modelos treinados $+$ metadados | joblib $+$ JSON | sob controlo de versões |

---

## Porque não um Postgres

A restrição fundadora do projeto é **só recursos gratuitos**. Mas a razão real é melhor do que
"é grátis", e é esta: **o histórico partilhado é evidência da tese, não só estado da aplicação.**

Guardá-lo como ficheiros de texto versionados dá quatro coisas que um Postgres não dá de borla:

1. **Rasto de auditoria.** Cada alterção tem autor, data e diferença. Um arguente pode ver quando
   um alerta apareceu e que não foi editado depois.
2. **Legível por qualquer pessoa**, sem credenciais e sem cliente. A app pública lê o mesmo URL
   que o júri pode abrir no browser.
3. **A app nunca recalcula.** Lê exatamente o que o canal enviou. Se a app e o Telegram
   divergissem, um dos dois estaria a mentir; partilhando o ficheiro, não podem divergir.
4. **Zero manutenção.** Não há servidor para cair, migrar, ou pagar.

Um Postgres daria consultas, transações e escrita concorrente a sério. **Nada disso é preciso
aqui:** o padrão de acesso é "lê tudo, acrescenta ao fim", o volume total é ~24 MB, e há dois
escritores, não duzentos.

---

## A limitação real (di-la antes que ta apontem)

**Escrita concorrente.** Dois produtores a escrever o mesmo ficheiro podem colidir. Isto não é
teórico: o vigia do Heroku corre de 60 em 60 segundos e o agendador do GitHub corre em paralelo.

Está tratado, e vale a pena saber como:

- O publicador **lê o `sha` do ficheiro antes de escrever** e envia-o de volta. Se alguém
  escreveu entretanto, o GitHub responde **409** e nós desistimos dessa ronda em vez de sobrepor.
- A junção é **por chave de entrada**, a mesma que serve a deduplicação entre produtores, por
  isso juntar duas vezes não duplica nada.

É controlo de concorrência otimista, que é o que uma base de dados faria por baixo. A diferença
é que aqui está à vista.

**Onde é que isto deixaria de servir:** com escritores a sério em paralelo, com mais de algumas
centenas de MB, ou quando fosse preciso consultar (por ticker, por intervalo, por tipo) em vez de
ler tudo. Nenhuma dessas condições se verifica, e dizer *"a escolha certa para esta escala, e sei
qual é o ponto de rutura"* é uma resposta mais forte do que ter posto um Postgres por reflexo.

---

## A redundância: dois produtores, dois consumidores

Isto é deliberado e é o que mantém o sistema vivo se o Heroku cair.

```
PRODUTORES  →   branch alerts-history   →   CONSUMIDORES
Heroku worker (60 s)  ─┐               ┌─ app no Heroku
GitHub Actions (~2 h) ─┴──── JSONL ────┴─ app no Streamlit Cloud
```

- **Ambos escrevem** no mesmo ficheiro, e a deduplicação por chave impede alertas repetidos: o
  arranque do runner semeia o estado a partir do histórico partilhado, por isso nenhum reenvia o
  que o outro já enviou.
- **Ambos leem** o mesmo URL. Se o Heroku estiver em baixo, o agendador continua a enviar para o
  Telegram e a app do Streamlit Cloud continua a mostrar o histórico. Mais lento, mas vivo.

**Não é preciso mudar nada para manter esta rede de segurança:** já está assim. Só é preciso não
desligar o workflow do GitHub Actions.

---

## Como dizes isto em três frases, se perguntarem

> *"Há três camadas: SQLite para as subscrições do bot, ficheiros JSONL versionados para o
> histórico partilhado, e os modelos treinados guardados com os seus metadados. Não há servidor de
> base de dados porque o padrão de acesso é acrescentar-e-ler-tudo sobre 24 MB, e versionar o
> histórico dá-me rasto de auditoria e leitura pública, que servem a tese da transparência melhor
> do que uma tabela daria. A limitação é a escrita concorrente, e está tratada com controlo
> otimista: leio a versão, escrevo com ela, e se houver conflito tento na ronda seguinte."*
