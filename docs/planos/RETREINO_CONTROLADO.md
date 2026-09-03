# Retreino controlado — implementação autorizada

Estado: inspeção inicial concluída em 2026-09-03; implementação e avaliação por executar.
Entrada principal: `PLANO_FINAL_2026-09-01.md`, atualização de prioridade da secção 0.

## Objetivo e âmbito

Fechar o ciclo de atualização do componente supervisionado de triagem de materialidade,
sem previsão de preços, direção, sinais de trading ou promessa de melhoria diária.
Esta é a primeira unidade de implementação, não uma afirmação de que todos os componentes
do Investigator aprendem. Recuperação semântica e detetor terão avaliação própria se alterados.

## O que já existe, confirmado no código

| Peça | Evidência | Consequência |
|---|---|---|
| Registo de decisões | `investigator/triage/postval.py`, `log_decision` | Guarda instante, notícia, ticker, probabilidade, gate e kept; não guarda vetor de features nem identidade do modelo. |
| Rótulos atrasados | mesmo módulo, `label_decision`; `scripts/post_validate.py` | Há maturação por preços e relatório, reutilizáveis; falta verificar a disponibilidade temporal dos preços e persistência de snapshots. |
| Treino e calibração | `investigator/triage/model.py` | Estimadores, calibração e persistência já existem. Não precisam de ser reinventados. |
| Treino offline | `scripts/train_triage.py` | Escreve sobre caminhos fixos em models/, relatório e figuras; não executar como retreino operacional. |
| Features | `investigator/triage/features.py` | Contrato ordenado de contexto e setores já existe. |
| Inferência | `investigator/triage/infer.py`, `score_latest` | Calcula features da última barra; não presumir equivalência com o dia da notícia usado no treino. |
| Separação temporal | `investigator/triage/dataset.py`, `assign_splits` | Há divisão por dias e embargo; para dados novos conferir maturação real dos rótulos na fronteira. |

## Ordem de implementação e aceitação

1. **Dados e rastreabilidade.** Inventariar ficheiros disponíveis e as chamadas reais de
   registo; verificar cobertura e duplicação. Definir snapshot por decisão com features,
   instante de disponibilidade e versão do modelo. Dados antigos sem essa evidência não são
   automaticamente equivalentes a snapshots contemporâneos. Não reconstruir usando futuro.
2. **Candidato isolado.** Saída nova por execução, sem sobrescrever models/ ou resultados da
   tese. Manifesto com hashes de dados, esquema, parâmetros, versões, datas e seed. Nenhuma
   escrita no modelo ativo nesta etapa.
3. **Protocolo antes de medir.** Fixar cortes cronológicos, purga por maturação dos rótulos,
   calibração separada e bloco de comparação. Fixar mínimos de dias/classes e critérios de
   aceitação após inventário dos dados, antes de observar resultados dos candidatos. Não
   reutilizar o teste congelado para selecionar sucessivos candidatos.
4. **Comparação emparelhada.** Modelo atual, candidato e baseline no mesmo bloco e contrato
   de features; qualidade, calibração, estabilidade, custo e compatibilidade da explicação.
   Dados insuficientes ou métricas inválidas impedem promoção; não significam sucesso.
5. **Registo e reversão.** Versões preservadas, ativação explícita e reversão testada. Falha
   do retreino não interrompe o envio de alertas. Automatizar execução só após validar o ciclo.
6. **Experiência real.** Executar com dados rastreáveis suficientes, guardar resultados mesmo
   negativos e só então atualizar a tese. Testes sintéticos provam comportamento do software,
   nunca eficácia do modelo ou feedback humano.

## Próximo passo concreto

⚠️ **Atualizado a 2026-09-03.** O contrato de *snapshot* e os testes de compatibilidade estão
implementados e ligados de ponta a ponta; a auditoria do registo está em
[`CONTRATO_DADOS_RETREINO_2026-09-03.md`](CONTRATO_DADOS_RETREINO_2026-09-03.md), com quatro
restrições que decidem o protocolo de aceitação — população filtrada pelas portas, `kept` que
deixou de discriminar com o orçamento diário ligado, só as linhas novas serem reproduzíveis, e
duplicação desigual por reavaliação de sessenta em sessenta segundos.

A seguir, por esta ordem: correr `scripts/auditar_registo_decisoes.py` contra a branch de dados;
decidir se as decisões passam a ser registadas antes das portas; fixar mínimos e critérios de
aceitação a partir desses números, antes de ver candidatos. Só depois construir o treino
isolado. Não correr o treinador antigo como atalho.

## Limites desta passagem

Não houve treino, alteração do modelo ativo, deploy ou nova medição científica. Ainda não foi
auditada a cobertura dos dados reais nem confirmada a cadeia completa em produção. O PDF da
tese permanece inalterado nesta passagem. A apresentação académica neutra e a rejeição do
piloto Figma estão decididas; a revisão visual será feita sobre a arquitetura estabilizada.
