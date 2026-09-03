# Revisão visual — primeira vaga da frente 05

## Âmbito

O inventário do candidato confirmou 40 figuras, 13 tabelas e quatro equações numeradas.
Esta passagem trata seis gráficos do capítulo 5 e dois diagramas do capítulo 4, sem recalcular
resultados. O documento mantém 126 páginas físicas, das quais 94 anteriores aos apêndices.

| Figura | Alteração |
|---|---|
| 4.10 | Rótulo do retreino separado do conector; fase de observação fora das caixas |
| 4.11 | Caminho de rejeição deslocado para baixo, sem colidir com a maturação |
| 5.3 | Precisão e cobertura em dispersão, com F1 junto de cada método |
| 5.4 | Pares ligados por medida, incluindo a cobertura idêntica |
| 5.6 | MiniLM preenchido, MPNet em contorno; corrigida a contagem para seis alternativas |
| 5.8 | Par de pontos numa escala completa 0–1, sem barras truncadas |
| 5.9 | Intervalos marginais de 95% dos cinco modelos; referência de prevalência |
| 5.10 | Três painéis por limiar, horizontes ordenados e definição canónica assinalada |

## O que a renderização apanhou

A primeira compilação aprovada automaticamente ainda tinha um retângulo a ocultar texto na
Figura 4.10, uma legenda cortada na Figura 5.3 e valores cortados na Figura 5.4. Foram corrigidos
nas fontes e novamente renderizados. A aprovação automática não substitui esta inspeção.

## Validação e limites

### Quinta passagem: figura setorial

Figura 5.7 regenerada dos mesmos artefactos com método verde e referência branca com trama.
Títulos encurtados e anotações numéricas com vírgula. Corrigido o destino por defeito do gerador
para tese-v2; dois testes verificam entradas, margens e destino. Figura isolada e página física
81 inspecionadas; sem cortes. A fonte continua a ser a do Matplotlib: esta passagem harmoniza
cor e distinção em impressão, não equivale a uma conversão nativa para LaTeX.

### Quarta passagem: semântica cromática e ablação

Na Figura 5.5, o marcador e a guia da janela implantada passam a verde. Na Figura 5.10,
a linha da volatilidade passa a neutra: ser a melhor alternativa não a torna implantada.
A faixa verde continua a identificar apenas a definição de rótulo usada. A legenda da Figura
5.12 deixa de afirmar que as variantes são remoções cumulativas: a tabela de consulta e a
volatilidade são referências alternativas, não degraus sucessivos. Nenhum valor foi alterado.

### Terceira passagem: orçamento e comparação final

A Figura 5.11 fica dedicada ao contraste entre desempate alfabético (0,163) e escolha aleatória
(0,379). As barras repetidas do modelo (0,632) e da volatilidade (0,662) saem dessa figura e
mantêm-se na Figura 5.18, para onde há uma remissão explícita. A segunda conserva as cinco
políticas e aplica o preenchimento verde exclusivamente ao modelo implantado.
Os valores aleatórios dos dois artefactos não foram substituídos: `evaluation_budget_baselines.md`
reporta 0,379 e `evaluation_endtoend_baselines.md` reporta 0,375. Não se recalcularam resultados.

### Segunda passagem: contabilidade do funil

A Figura 4.4 passa a mostrar as seis categorias que somam 5 060 avaliações:
2 994 + 1 194 + 269 + 249 + 21 + 333. As cinco mensagens entregues são apresentadas
separadamente, não como mais uma categoria. A versão anterior omitia as 333 passagens e
substituía-as visualmente por cinco entregas, misturando unidades. Não se inventou uma etapa
histórica de 328 duplicados: a instrumentação dessa etapa não existia naquele instantâneo.
Mantém-se a advertência de que o piso de triagem pertencia à configuração anterior.

- 176 testes dirigidos a marca, feedback, persistência, webhook e aplicação passaram.
- Ruff e verificação de espaços do Git passaram.
- A porta canónica passou com a opção explícita de permitir nomes do júri ainda por preencher.
- A suite integral de testes continua por concluir; não foi substituída pelos testes dirigidos.
- A frente 05 inteira NÃO está fechada: falta harmonizar os restantes visuais, rever o funil,
  resolver redundâncias e executar/comparar o piloto conceptual externo previsto no plano.
- Nenhum resultado científico foi recalculado e nenhuma alteração desta passagem foi implantada.
