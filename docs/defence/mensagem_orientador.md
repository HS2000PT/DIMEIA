# Primeira mensagem ao orientador (PT-PT, pronta a copiar)

> **Contexto:** esta é a **primeira vez** que o Prof. Luís Gomes vê o trabalho feito. Não é um
> pedido de revisão de uma versão que ele já acompanhou; é a apresentação do que existe. Por isso
> a mensagem orienta a partir do zero e diz por onde começar, em vez de assumir contexto.
>
> **Como usar:** copiar o bloco entre as linhas. Confirmar os três links ⚠️ antes de enviar.

---

**Assunto:** Dissertação MEIA (nº 1180934) — primeira versão completa para leitura

Caro Professor Luís Gomes,

Envio pela primeira vez o trabalho completo da dissertação. Está tudo a compilar, o sistema está
a correr em produção, e os números são todos reproduzíveis. O que precisa da sua leitura é o
conteúdo e o rumo, não o estado.

**O que é, em três linhas.** Quando uma ação se mexe, um investidor não profissional faz sempre as
mesmas três perguntas: *isto é invulgar para esta ação?*, *é a empresa ou é o mercado?*, e *já
aconteceu antes, e o que se seguiu?*. As ferramentas gratuitas não respondem a nenhuma; um terminal
profissional responde às três por cerca de 2.000 dólares por mês. O sistema responde às três, de
graça, e mostra as contas. **Nunca prevê preços**, e isso é uma restrição de desenho assumida, não
uma limitação por resolver.

**Por onde começar, se tiver pouco tempo**

O **Capítulo 1** (o problema e as três perguntas) e o **Capítulo 6** (os veredictos, incluindo os
resultados negativos). São cerca de 20 páginas e dão o essencial.

**O que existe**

| | |
|---|---|
| Tese (EN), 107 pp | `thesis/main.pdf` |
| Tese (PT), 111 pp | `thesis-pt/main.pdf` — tradução fiel, mantida em sincronia |
| Slides de defesa, 23 | `slides/main.pdf` |
| Sistema a correr | ⚠️ <https://investigator-meia-fa8287a1e568.herokuapp.com/> |
| Canal de alertas | ⚠️ <https://t.me/InvestiGatorMEIA> |
| Código | ⚠️ <https://github.com/HS2000PT/DIMEIA> |

A tese tem **oito estudos de caso** e **59 referências**, todas verificadas contra a fonte
primária. O sistema corre 24 horas por dia e o código tem 469 testes automáticos.

**O que eu gostaria que olhasse com atenção crítica**

- **Os resultados negativos (Cap. 6).** Nenhum modelo que lê o texto da manchete bateu a linha de
  base de volatilidade (PR-AUC 0,542 contra 0,496). Está reportado tal como caiu, com testes de
  robustez a confirmar que não é sub-ajuste. Preferi isto a procurar um número mais simpático, mas
  gostava da sua opinião sobre se está bem enquadrado.
- **Os quatro estudos que terminam em "não" (Casos 5 a 8).** Construí quatro capacidades e não
  liguei nenhuma à produção, porque a medição não as sustentou. Acho que é a parte mais forte do
  trabalho em termos de engenharia, mas é também a que mais depende de estar bem escrita.
- **A secção "Posições Assumidas por Exclusão" (Cap. 6).** O que o sistema deliberadamente não faz
  e porquê: sem preços-alvo de analistas, sem carteira do utilizador, e sem lhe chamar sistema
  multi-agente, porque não é.

**Duas coisas que preciso de si**

1. A **redação exata da declaração de uso de IA** exigida pela MEIA. Escrevi uma versão honesta no
   início da tese, mas quero confirmar a forma antes de submeter.
2. A **licença** a aplicar ao código.

**O que ainda falta, e é meu**

O estudo de utilidade com 6 a 10 pessoas (protocolo e materiais prontos; fecha a única linha em
aberto do Cap. 6), os agradecimentos, e a gravação da demonstração.

Fico a aguardar os seus comentários e agradeço desde já a disponibilidade.

Com os melhores cumprimentos,
**Henrique José da Silva Santos** · nº 1180934 · MEIA

---

## Notas para ti (NÃO enviar)

- **Confirmar antes de enviar:** (1) a app abre numa janela anónima sem pedir login; (2) o canal do
  Telegram está público; (3) o repositório está acessível à conta dele.
- **A app já não hiberna.** Está no Heroku num dyno *Basic*, sempre ligado. O URL do Streamlit
  Community Cloud, se ainda o tiveres em algum lado, está desatualizado.
- **Se ele perguntar pelo Rafael Silva:** o `worldmonitor.app` foi recomendação dele, está citado
  na bibliografia e creditado no Caso de Estudo 8. Vale a pena dizê-lo, porque é verdade e é
  elegante.
- **Não prometas data para o estudo de utilidade.** Depende de recrutar pessoas, e isso não
  controlas.
- **Se ele perguntar "porquê tantos resultados negativos?":** a resposta honesta é que são quatro
  comparações pré-comprometidas em que a opção transparente ganhou, e que um trabalho que só
  reporta o que correu bem é um trabalho em que não se pode confiar. Não peças desculpa por eles.
