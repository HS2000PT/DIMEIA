# Painel v7 — refazer, com o que a v6 ensinou

> Pedido do autor a 2026-09-01, depois de ver a v6.2. Este ficheiro fixa o que muda, o que
> **não pode** mudar, e as respostas honestas a duas perguntas dele.

## O que ele pediu, sem filtro

Título do separador só «InvestiGator». URL sem sufixo. Usar o espaço lateral que está a sobrar
em ecrã grande. Tipos de letra maiores e mais estilizados. Menos palavras, mais interação.
Logótipos maiores. Cartões. Filtros de data no gráfico. Clique num evento abre modal com o
detalhe. Legenda para toda a cor e todo o sinal. Semáforo, KPIs, indicadores. Atualização
contínua sem F5. A mascote — um jacaré detetive — como relator do «hoje». O «hoje» por defeito,
com o histórico algures. E, textualmente: a secção «Why it stayed quiet» continua confusa, e o
«all companies» não faz sentido onde está.

## As duas respostas honestas

**1. O URL não pode ficar `investigator.herokuapp.com`.** A aplicação já se chama
`investigator`; o `-ddc9d8618935` não faz parte do nome. Desde 14 de junho de 2023 a Heroku
acrescenta um identificador aleatório de doze caracteres a todos os subdomínios, para impedir que
um domínio seja tomado depois de a aplicação ser renomeada ou apagada. Renomear **não** o
remove — gera outro. O único caminho para um endereço limpo é um domínio próprio apontado à
aplicação, que na Basic é suportado com certificado automático. Custa um domínio (poucos euros por
ano) e uma alteração de DNS.

**2. «Refazer do zero» tem um limite que convém nomear.** A apresentação refaz-se toda. O que
**não** se deita fora são as regras que a página aprendeu a cumprir, porque cada uma delas custou
um defeito: a promessa aparece uma vez e não duas; a página só chama rotas que a API serve; os
logótipos são servidos por nós e nunca por terceiros; o texto do alerta é mostrado tal como saiu e
nunca reescrito; a probabilidade da triagem não aparece em vista de produto; o silêncio é
inspecionável. Estão fixadas em `tests/test_api.py` e continuam a valer na v7 — se uma delas
falhar, a v7 não entra.

## As decisões de desenho, e a razão de cada uma

**O funil desaparece como secção, e o estado passa a viver na empresa.** É a resposta ao «continuo
sem perceber». A informação estava certa e no sítio errado: uma lista de portas com nomes
técnicos, longe da empresa a que dizia respeito. Na v7 cada empresa tem um sinal — verde para
alerta entregue, âmbar para assinalado mas travado, cinzento para nada de invulgar — e o clique
abre o percurso completo dessa empresa nesse dia, em palavras. O agregado do dia fica num único
cartão de indicadores. A pergunta «porque é que esta empresa está calada» passa a ter resposta
onde ela é feita.

**O «all companies» deixa de ser um filtro solto** e passa a ser o modo do próprio painel: por
defeito o dia de hoje, com um interruptor para o histórico.

**Menos texto no ecrã, todo o texto no detalhe.** A regra: a superfície mostra estado e número; o
clique mostra a explicação inteira, incluindo o texto exato que o Telegram recebeu. Nada é
apagado — muda de camada.

**Atualização contínua.** Sondagem do `/api/health` a cada trinta segundos; quando o `as_of`
mudar, recarrega e anima a entrada do que é novo. Não é WebSocket de propósito: o produtor publica
num ficheiro a cada ciclo de sessenta segundos, e uma ligação permanente custaria mais do que
resolve.

**A mascote é o relator do dia.** Aparece uma vez, no cartão do «hoje», com a frase que resume o
estado. Não é decoração: dá voz ao único texto que a página precisa de ter em destaque. O
logótipo mantém-se — a cauda é a marca, o jacaré é a mascote.

**Desempenho antes de efeito.** Sem framework. Uma folha de estilo, um ficheiro, o
`lightweight-charts` que já é servido por nós. Animações curtas, com `prefers-reduced-motion`
respeitado. O objetivo é que a página abra e responda de imediato, que é o que a torna
demonstrável ao vivo sem susto.

## O que fica por decidir com o autor

- Domínio próprio: comprar ou não.
- A mascote definitiva: a imagem que ele anexou, ou uma versão com monóculo à Sherlock.
