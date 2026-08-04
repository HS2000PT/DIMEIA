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

```bash
python - <<'PY'
import pathlib
from playwright.sync_api import sync_playwright
svg = pathlib.Path('app/assets/icon.svg').read_text(encoding='utf-8')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.set_viewport_size({"width": 512, "height": 512})
    pg.set_content(f'<style>html,body{{margin:0}}svg{{width:512px;height:512px;display:block}}</style>{svg}')
    pathlib.Path('app/assets/telegram_avatar.png').write_bytes(
        pg.query_selector('svg').screenshot(omit_background=True))
    b.close()
PY
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
```

## Nota de tom

Os alertas do canal são em **inglês** — mesma regra da interface: o código e os comentários são
PT-PT, o que o utilizador lê é EN. A descrição e a mensagem fixada seguem a mesma regra, com a
excepção da linha final da mensagem fixada, que identifica o trabalho académico.

## Ver também

- [`going_live.md`](going_live.md) — como criar o canal, definir os segredos e correr o workflow
- [`cadence_contract.md`](cadence_contract.md) — o que é enviado, o que nunca é, e os cinco gates
- [`brand.md`](brand.md) — o teste de aceitação da marca às escalas reais
