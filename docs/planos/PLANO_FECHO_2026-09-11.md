# Plano de fecho — 2026-09-11

> **Este plano manda sobre o `PLANO_REESCRITA_EXECUCAO.md`**, que a sessão 68 mediu item a item e
> deu como **não executável a partir da lista**: foi escrito contra um documento que as sessões 63
> a 68 já corrigiram. O que resta da reescrita está rederivado aqui, do documento actual.

## 0. O que o autor pediu, em 2026-09-11

Ditado numa passagem só. Fica em bruto, para nada se perder na tradução:

1. **Rever a tese do início ao fim** e garantir que tudo o que está escrito é **verdade e
   verificado contra o sistema actualmente em curso**. A aplicação web já foi actualizada e a
   imagem da tese **não corresponde** — logo é provável que haja mais texto por rever.
2. **O número de páginas continua enorme.** É muito para memorizar e muita superfície para os
   professores assinalarem erros. Analisar cortes que **não impliquem perda de qualidade**.
   Método sugerido pelo próprio autor: **comparar a nossa estrutura e dimensão com as quatro
   dissertações aprovadas** e perceber o que temos de diferente.
3. **Optimizar a aplicação ANTES de tirar capturas novas.** Onze pontos concretos, na §2.
4. **Estudar melhorias gerais** de funcionalidade e usabilidade.
5. **Revisão final criteriosa e rigorosa** — «como se a minha vida dependesse disso».
6. **Slides finalizados**, para irem em anexo.
7. **Mensagem ao orientador e ao coorientador**, com o conteúdo da §4.

---

## 1. A tese

### 1.1 Verificação contra o sistema vivo — a prioridade
O risco não é o texto estar mal escrito: é **afirmar sobre o produto o que o produto já não faz**.
É a classe de defeito que este projecto pagou mais vezes (sessões 33, 48, 63, 65, 67).

- [ ] **V1** Inventariar cada afirmação da tese sobre a **interface** e confrontá-la com a v8 no ar.
- [ ] **V2** Regenerar **todas** as capturas a partir da v8. A tese mistura hoje
      `app_v7_painel.png` com `app_v8_empresa.png`, ou seja **duas gerações do produto na mesma
      dissertação**.
- [ ] **V3** Reler as legendas das capturas: a sessão 65 mediu que trocar só a imagem **muda o
      defeito de sítio**, porque o texto ao lado descreve o ecrã antigo número a número.
- [ ] **V4** Confrontar o Cap. 4 inteiro com o comportamento vivo (portas, orçamento, políticas).
- [ ] **V5** Correr `check_prontidao_defesa` e a auditoria de números depois de tudo.

### 1.2 Páginas: a comparação que o autor pediu
Estado medido a 2026-09-11: **EN 142 físicas / 124 árabes · PT 143 / 125**. Limite oficial: **120
árabes**.

⚠️ **E o que já está medido, para não se voltar a tentar:** o documento **não encolhe
incrementalmente**. Três medições independentes: cortar uma tabela de meia página deu **zero**
páginas; cortar 84 palavras deu **zero**; e a varredura de densidade encontrou **3 páginas em
branco e nenhuma página magra no corpo**. Chegar a 120 exige remover **quatro páginas de material
contíguo** — uma secção, ou dois a três flutuantes — e não aparar.

- [ ] **P1** Medir as quatro aprovadas: páginas por capítulo, nº de figuras, nº de tabelas,
      palavras. Pôr a nossa ao lado. **É isto que decide o que é gordura e o que é norma.**
- [ ] **P2** Do resultado do P1, nomear os cortes contíguos com o custo escrito.
- [ ] **P3** Decidir com o autor, com os números à frente.

### 1.3 Revisão final
- [ ] **R1** Leitura seguida, capítulo a capítulo, a reportar o que não segue.
- [ ] **R2** Todas as portas verdes no fim, e a lista escrita no registo.

---

## 2. A aplicação — os onze pontos, verbatim do autor

Ordem de execução proposta: primeiro o que se vê nas capturas (1, 7), depois o que muda a
compreensão (2, 8), depois a interacção (3, 4, 5, 6), depois o resto.

| # | Pedido | Nota |
|---|---|---|
| A1 | **Logótipo com fundo branco** num tema escuro — não encaixa | visível em toda a captura |
| A2 | **«How reliable is this split?»** não explica o suficiente. Quer perceber **o que é o R²**, **a fórmula**, **a fórmula com os valores substituídos**, e o **resultado**. Passo a passo, com transparência: «o utilizador não precisa de ser um génio» | é o pedido mais substantivo |
| A3 | Seleccionar uma empresa deve **filtrar também a lista de alertas** | hoje só governa o gráfico |
| A4 | Clicar num ponto do gráfico deve **saltar e dar foco** ao alerta na lista | |
| A5 | Os **filtros de dias** do gráfico devem filtrar a lista em sincronia | |
| A6 | **«All companies» passa para junto dos logótipos** e a *combobox* desaparece — a selecção passa a ser o clique no logótipo | |
| A7 | O texto **«unusual»** precisa de mais destaque, ou de um ícone | |
| A8 | As percentagens do **«contributed»**: não se percebe de onde vêm, **sobretudo a da empresa**. Percebe-se que o real é a soma das três, mas não o cálculo | par do A2 |
| A9 | Em *history*, o **«messages per day»** precisa de eixos: **x = intervalo de datas, y = nº de alertas** | |
| A10 | O filtro de mensagens precisa de opção para **market open** e **market close** | |
| A11 | **Melhorias gerais** de funcionalidade e usabilidade, com sugestões | |

⚠️ **O A2 e o A8 são o mesmo pedido por dois lados, e são o pedido mais importante da lista:** o
produto mostra números que o utilizador não consegue reconstruir. É exactamente a tese do
trabalho — explicar sem prever — aplicada ao próprio ecrã. Tratar os dois juntos.

⚠️ **E o A6 tem uma consequência a verificar antes de executar:** a *combobox* é hoje a via de
teclado para escolher empresa. Substituí-la por cliques em logótipos **sem** alternativa acessível
degrada a acessibilidade, que este projecto já mediu duas vezes (contraste WCAG, sessões 61 e 67).
Os logótipos têm de ser botões focáveis.

---

## 3. Slides
- [ ] **S1** Sincronizar com a tese actual (v8, números actuais, QI4).
- [ ] **S2** Compilar a zero erros e confirmar a contagem.

---

## 4. A mensagem ao orientador e ao coorientador

**Restrições que o autor fixou:**
- Prática e honesta, **sem spam e sem um texto gigante** — «isso também é chato».
- «Jogar na defensiva.»

**Conteúdo pedido:**
- [ ] Anexar o **documento da tese** para apreciação, e os **slides**.
- [ ] Explicação **muito breve** do que é o sistema e **que técnicas de IA usa e para quê cada uma**.
- [ ] Ligações do **Heroku** e do **Telegram**.
- [ ] Perguntar se pode **responder ao inquérito da Professora Goreti** para ir a defesa.
- [ ] Perguntar se **concordam com o título**.
- [ ] Dizer, **brevemente e sem soar a desculpa**, que só agora apresenta porque só agora tem uma
      versão semi-finalizada e o sistema a funcionar ao vivo, e não queria fazê-los perder tempo a
      rever algo em mudança; e que daqui para a frente as alterações serão menores e sobretudo de
      documento.
- [ ] Pedir feedback **sobretudo** sobre: estrutura do documento, escrita, se está demasiado
      extensa, o que cortar, o que acrescentar, o que rever.

---

## 5. Ordem de execução

1. **P1** — a comparação com as quatro aprovadas. É o que desbloqueia a decisão das páginas.
2. **V1/V2/V3** — a verificação contra o sistema vivo, que é o risco de integridade.
3. **A1–A10** — a aplicação, porque as capturas dependem dela.
4. **V2** outra vez — capturas novas, agora que a aplicação está estável.
5. **R1** — a leitura seguida.
6. **S1/S2** — os slides.
7. **§4** — a mensagem, em último, quando os anexos existirem.

⚠️ **A mensagem é o último passo por uma razão e não por arrumação:** ela anexa o documento e os
slides, e enviá-la antes de as capturas corresponderem ao produto seria pedir a revisão de uma
versão que já sabemos estar desactualizada.
