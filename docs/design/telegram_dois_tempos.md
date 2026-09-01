# Alerta em dois tempos e desfecho observado — frente 02

> Escrito a 2026-09-01, depois de construir as peças e antes de as ligar ao caminho de envio.
> Contém uma mudança de âmbito face ao `PLANO_FINAL_2026-09-01.md`, com a medição que a motiva.

## A mudança de âmbito, e a razão

A frente 02 tinha duas metades. Uma delas não se justifica, e é melhor dizê-lo do que
construí-la porque estava na lista.

**Metade que NÃO se faz: enviar o esboço primeiro e editá-lo com a análise.**

O plano já dizia que o ganho de latência era de segundos e não de minutos. Ao ir ligar isto ao
`scripts/run_alerts.py` ficou claro que o custo é maior do que o plano supunha, e que o ganho é
ainda menor:

| | |
|---|---|
| Publicação → deteção pela fonte gratuita | **353 min** (mediana) |
| Deteção → chegada da mensagem | **5 s** (mediana), 16 s (p90) |
| O que o esboço pouparia | os tais 5 s, no melhor caso |

E o argumento secundário — «tira a recuperação semântica do caminho crítico, que custa 7,5 s a
frio» — não se aplica ao sistema como ele corre. Os 7,5 s são de **carregamento a frio** do
codificador de frases, e é por isso que a recuperação está fora do painel, que arranca a frio a
cada pedido. O `worker` é um processo permanente com ciclo de 60 s: o modelo está quente, e a
medição de 5 s de mediana ponta a ponta é a prova disso.

Restaria a divulgação progressiva — ver o sistema a trabalhar. Reestruturar o percurso de
varredura de um sistema em produção, a três semanas da defesa, por cinco segundos e por um
efeito estético, é uma troca má. **Não se faz, e a razão fica escrita para não voltar a ser
discutida.**

As peças ficam construídas e testadas, porque são baratas e porque a decisão pode mudar se a
medição mudar: `esboco_news_impact` no `explainer.py`, com o cabeçalho extraído para
`_cabecalho_noticia` e a garantia — testada — de que o esboço e o alerta completo partilham
esse cabeçalho byte a byte. Se algum dia o p90 subir, ligar isto é uma tarde.

**Metade que SE faz, e que era a boa desde o início: o desfecho observado.**

## O que o desfecho observado faz

Ao fim de uma, três e cinco sessões, a **mensagem original** é editada com o que a ação veio a
fazer. Não uma mensagem nova: a mesma, no sítio onde a afirmação foi feita, para as mesmas
pessoas que a leram.

```
📰 News alert for TSLA (Tesla) (2026-09-01)
"Tesla recalls 12k vehicles"
Reuters
Right now: +5.36% today · 12 of the last 249 trading days moved this much or more

3 similar past headlines. Their 3-day move ranged −2.10% to +4.30% ...
▸ ...

📌 What happened next          ← acrescentado dias depois
▸ +1d · +2.10%
▸ +3d · −0.40%
This is what the stock did after the alert, measured from the close of the alert day.
It is not a claim that the alert caused it, and none of it was knowable when the alert
was sent.
```

Nenhum dos produtos comparados no Capítulo 2 volta atrás para dizer como correu. É a diferença
entre um sistema que explica e um sistema que se deixa verificar, e é reivindicável na defesa.

## As seis regras que impedem isto de virar uma previsão disfarçada

1. **Acrescenta, nunca reescreve.** O texto original fica intacto por baixo. Reescrever a
   afirmação depois de saber o resultado é a forma mais eficaz de um sistema parecer sempre
   certo. Há um teste que verifica que o texto anotado **começa** pelo texto original.
2. **Diz que é o desfecho da empresa, não o efeito do alerta.** O sistema não sabe o que causou
   o movimento, e o alerta não é uma intervenção.
3. **Diz que não era conhecível.** De cada vez, e não uma vez: sem essa frase, dez anotações
   positivas seguidas ensinam o leitor a ler o sistema como preditivo.
4. **Só edita quando há informação nova.** Cada edição é uma notificação; uma edição vazia é a
   única forma de isto incomodar quem recebe.
5. **Nada de espaços reservados.** A primeira versão escrevia «+5d not yet available», e isso
   partia a deteção de novidade — no dia em que o valor chegasse, o sistema concluía que a
   linha já existia e não editava. Um espaço reservado que impede a informação de chegar é
   pior do que a sua ausência. Há um teste com o nome desta regressão.
6. **Mede em sessões, não em dias de calendário.** Um alerta de sexta mede o +1d contra a
   segunda. E a referência é a última barra **anterior ou igual** ao dia do alerta, nunca a
   seguinte: medir contra uma barra futura seria olhar para o futuro a partir do momento do
   alerta, exatamente o defeito que a avaliação passou o trabalho todo a evitar.

## O que falta ligar (precisa da máquina do aluno)

O `scripts/run_alerts.py` não estava acessível quando isto foi escrito. Faltam três pontos, e
são pequenos:

1. **Guardar o `message_id`.** No ciclo de envio, `send_message` já devolve a resposta; falta
   passar por `sender.message_id_de(...)` e entregar o valor ao `_record_history_safe`.
2. **Gravar `message_id` e `chat_id` na entrada do histórico.** Os campos já existem no
   `HistoryEntry` (acrescentados nesta sessão, opcionais e retrocompatíveis).
3. **Agendar `scripts/anotar_desfechos.py`** uma vez por dia, depois do fecho americano
   (22:30 UTC serve). Correr primeiro com `--dry-run`.

⚠️ **Sem o ponto 1, o ponto 3 não tem nada em que trabalhar.** Os 522 alertas já entregues não
têm `message_id` guardado e são inalcançáveis — o Telegram não oferece maneira de reencontrar
uma mensagem pelo conteúdo. A anotação começa nos alertas enviados a partir do momento em que
o ponto 1 estiver no ar, e é por isso que ele deve entrar já.

## Ficheiros

| Ficheiro | Papel | Testes |
|---|---|---|
| `investigator/explanation_engine/desfecho.py` | Puro: constrói e atualiza o bloco do desfecho | `tests/test_desfecho.py` (13) |
| `investigator/explanation_engine/explainer.py` | `_cabecalho_noticia` extraído; `esboco_news_impact` novo | `tests/test_esboco.py` (10) |
| `investigator/alerts_history.py` | `message_id`, `chat_id`, `estado` opcionais | `tests/test_alerts_history.py` (16) |
| `scripts/anotar_desfechos.py` | O trabalho diário: lê o histórico, mede, edita, republica | coberto pelos de seleção |
