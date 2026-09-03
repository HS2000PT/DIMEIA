# O canal de Telegram — identidade, textos e imagens

> **Porque é que este ficheiro existe.** O nome, a descrição, a mensagem fixada e o avatar do
> canal viviam em três sítios: parte no [`going_live.md`](going_live.md), parte só na cabeça de
> quem criou o canal, e o avatar em lado nenhum — havia um `icon.svg` desenhado de propósito
> para ser avatar do Telegram, mas nunca tinha sido convertido para um ficheiro que se pudesse
> carregar. Se o canal tivesse de ser recriado (perda de conta, mudança de nome, um segundo
> canal para a defesa), a identidade teria de ser reinventada de memória. Está aqui.

## O canal

| | |
|---|---|
| Nome | **InvestiGator** |
| Handle | `@investigator_alerts` |
| Avatar | [`app/assets/telegram_avatar.png`](../../app/assets/telegram_avatar.png) — 512×512 |
| Painel ligado | <https://investigator-ddc9d8618935.herokuapp.com> |

## Avatar

Carregar `app/assets/telegram_avatar.png` em **Manage channel → Channel Photo**.

É gerado a partir de [`app/assets/icon.svg`](../../app/assets/icon.svg), que foi desenhado
exactamente para isto: é a **única** peça da marca que traz contentor próprio, porque a
plataforma desenha sempre um quadrado e sem fundo a marca ficaria à mercê da cor de sistema de
quem olha. O glifo está ampliado e recentrado face ao `logo.svg` — um ícone lido a 16 px precisa
de margens menores do que uma marca lida a 88 px, e foi precisamente esse teste que a marca
anterior ("The Stare") falhou.

Para regenerar depois de mexer no SVG:

```powershell
.\.venv\Scripts\python.exe scripts\build_brand_assets.py
```

## Descrição do canal

**Manage channel → Description.** O Telegram corta aos 255 caracteres, por isso esta versão
cabe inteira (238):

```
Explainable US-market alerts, automated: abnormal moves and material news, each with the
reasoning attached. Evidence from the past, never a forecast. Not financial advice.
Dashboard: investigator-ddc9d8618935.herokuapp.com
```

A ordem das frases não é acidental. O que o canal **faz** vem primeiro, o que ele **recusa**
fazer vem logo a seguir e antes do link — porque quem chega a um canal de alertas financeiros
assume previsão por defeito, e desfazer essa suposição depois do primeiro alerta é tarde.

## Mensagem fixada

Fica no topo para quem entra a meio. É o único sítio onde a promessa aparece por extenso — a
regra **H1** do projecto diz que a promessa aparece **uma** vez e não repetida em cada alerta,
e é este o sítio dela.

```
InvestiGator — alertas explicáveis do mercado dos EUA

O que recebes:
• Movimentos invulgares — medidos contra a norma recente da PRÓPRIA acção, não contra
  uma percentagem fixa. 3% é muito numa acção calma e banal numa volátil.
• Notícias materiais — com precedentes semelhantes do passado e o que se seguiu a esses,
  medido a +1, +3 e +5 dias.
• Uma nota de abertura e um resumo de fecho em todos os dias úteis, mesmo quando não há
  nada a assinalar — para o silêncio ser legível em vez de ambíguo.

O que NUNCA vais receber:
• Alvos de preço, recomendações de compra ou venda, ou "movimento esperado".
  O sistema descreve o que já aconteceu. Não prevê, por desenho.

Painel ao vivo: https://investigator-ddc9d8618935.herokuapp.com

Trabalho académico (dissertação de Mestrado, ISEP). Não é aconselhamento financeiro.

Feedback voluntário:
• Os botões “Useful” e “Didn't help” guardam a escolha, a hora, a mensagem e um resumo
  criptográfico estável do identificador de utilizador. Não são guardados nome, username ou
  identificador pessoal em claro. O registo pseudonimizado é versionado na branch pública de
  dados do projeto e serve apenas a avaliação agregada da dissertação.
• Uma pessoa conta no máximo uma vez por alerta; a escolha mais recente substitui a anterior.
• /deletefeedback (ou /apagar) retira da análise todos os votos anteriores dessa pessoa.
  Por o registo ser versionado e de auditoria, as linhas pseudonimizadas anteriores permanecem
  no histórico Git, mas deixam de contar. Um voto posterior inicia nova participação.
• Votar é opcional e não altera os alertas recebidos.
```

## Nota de tom

Os alertas do canal são em **inglês** — mesma regra da interface: o código e os comentários são
PT-PT, o que o utilizador lê é EN. A descrição e a mensagem fixada seguem a mesma regra, com a
exceção da identificação académica. A nota de feedback permanece bilingue nos comandos para que
`/apagar`, exigido no plano de consentimento, continue fácil de encontrar.

## Antes de convidar participantes

São duas ações manuais do proprietário do canal, porque nenhum script deve alterar a apresentação
ou notificar pessoas sem confirmação:

1. substituir a mensagem fixada pela versão acima e voltar a fixá-la;
2. carregar o `telegram_avatar.png` regenerado se a imagem do canal ainda usar uma versão antiga.

## Ver também

- [`going_live.md`](going_live.md) — como criar o canal, definir os segredos e correr o workflow
- [`cadence_contract.md`](cadence_contract.md) — o que é enviado, o que nunca é, e os cinco gates
- [`brand.md`](brand.md) — o teste de aceitação da marca às escalas reais
