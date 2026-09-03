# Pós-plano — o pedido de auditoria integral

> **Não é para agora.** O `docs/planos/PLANO_FINAL_2026-09-01.md` manda até à defesa. Este ficheiro guarda o
> pedido que o Henrique fez a 2026-09-01, para ser executado quando o plano fechar.

## O que é pedido

### Reconfirmação e complemento recebidos a 2026-09-03

O autor reenviou o pedido e reiterou: concluir primeiro as pendências atuais, depois executar
esta auditoria, sem alterar automaticamente tese ou código na sua primeira fase. O reenvio não
aprova por si o piloto Figma nem manda recomeçar a dissertação. Esta passagem foi uma triagem
documental, não a auditoria integral e não uma nova validação do sistema em produção.

Evidência diretamente relida nesta passagem:

- `tese-v2/ch1/chapter1.tex:45`: generalização sobre aplicações gratuitas que não respondem a
  nenhuma das três perguntas; o parágrafo não inclui fonte ou delimitação de produtos. Prioridade
  alta na frente de escrita: confrontar com a comparação documentada e substituir a generalização
  por uma afirmação sustentada. Não foi determinada nesta passagem a veracidade para cada produto.
- `tese-v2/ch4/chapter4.tex:848`: retreino expressamente ausente; a arquitetura subsequente é
  proposta, não executada. Acumulação de dados, pós-validação e melhoria medida do modelo são três
  estados distintos. Qualquer experiência nova deve ter protocolo, validação temporal e comparação
  antes de reivindicar aprendizagem contínua.
- `tese-v2/ch4/chapter4.tex:656`: latência documentada; não converter rapidez de organização ou
  potencial poupança de tempo em vantagem financeira demonstrada.

Complementos a preservar na fila, com dependências explícitas:

| Pedido | Encaminhamento e critério |
|---|---|
| Texto curto e defensável; fórmulas compreensíveis | Frentes 06/07: cortar redundância, preservar evidência e explicar cada fórmula mantida com finalidade, entradas e leitura. Não eliminar limites para facilitar a defesa. |
| Figuras variadas; arquitetura completa | Frente 05: cada visual responde a uma pergunta; versão simples no corpo e detalhe horizontal no apêndice quando necessário. Não impor uma figura por subsecção nem uma extensão artificial ao índice. |
| Acrónimos, termos ingleses, agradecimentos, negrito | Frente 07: verificar cobertura e consistência, manter empréstimos técnicos quando mais claros, agradecimento sóbrio e ênfase seletiva. |
| Histórico, concentração por empresa, limites e dados em falta | Auditoria técnica: distinguir universo observado, portas, orçamento e falhas de recolha antes de aumentar limites ou dados. Não escolher amostras para aparentar melhores resultados. |
| Painel intuitivo e mascote | Reavaliar com tarefas concretas de um leigo, incluindo clique em eventos, sem confundir preferência estética com falha funcional. |
| Repositório limpo e instalação num clique | Frente 09 e extensão de portabilidade: mapear dependências antes de mover; inventário de requisitos, modelos e dados, verificação em máquina limpa e reparações autorizadas. |
| Credenciais transportáveis | Estudar armazenamento cifrado com chave separada e acesso autorizado; nunca incluir segredos em claro ou a chave de desencriptação no repositório. Downloads sujeitos a licença e acesso. |
| Continuidade entre ferramentas e computadores | Plano final como entrada única, estado com evidência e próximo passo; evitar planos concorrentes. |
| Vídeo de Telegram e painel | Frente 08, depois de estabilizar produto: guião, gravação ensaiada e cópia local para defesa, identificando o que é demonstração gravada. |
| Artigo científico | Entrega dependente dos resultados fechados. Prazo, formato e regra dos dois valores foram relatados pelo autor, não verificados nesta passagem; confirmar antes de calendarizar a submissão. |
| Inglês ou edição bilingue | Decisão final do autor, após ficar confortável com a versão portuguesa; não duplicar agora as árvores da tese. |
| Modelos e conectores de apoio | Avaliar quando a tarefa correspondente começar; verificar disponibilidade e capacidades atuais, não inferir qualidade pelo nome ou instalar ferramentas em bloco. |

Feedback: preparar estrutura e análise para pessoas reais. Simulações, se usadas para testar o
software, devem ficar identificadas e excluídas da evidência humana. Não fabricar participantes,
ocultar a origem de avaliações ou manipular metadados para dissimular autoria. A revisão da escrita
visa clareza e correção, mantendo a declaração transparente de uso de IA.

Próximo passo da fila atual: decisão sobre o piloto revisto da Figura 4.10; a tese permanece
intacta nesta triagem. A auditoria integral continua pendente e terá as treze secções abaixo.

Uma auditoria baseada em evidência — nunca genérica, sempre com o sítio onde a coisa está — que
compare a tese e o InvestiGator **já existentes** contra a visão do autor, e produza um plano de
melhorias priorizado. Nada de tese nova nem de sistema novo: o ponto de partida é o que existe.

**Restrição fundamental, e é absoluta:** previsão de preços, sinais de compra ou venda,
*price targets*, recomendação e execução de estratégias estão **fora de âmbito**. É permitido
mostrar retrospetivamente o que aconteceu depois de acontecimentos semelhantes, como contexto
histórico e evidência, nunca como previsão. Nenhuma melhoria proposta pode violar isto.

**Oito perguntas:** o que a tese já cumpre; o que o sistema já implementa; o que está
parcialmente feito ou mal explicado; o que não existe; o que acrescentaria valor científico,
técnico e empresarial; o que se pode aproveitar do sistema para melhorar a tese; o que existe no
sistema e não está documentado, justificado, avaliado ou demonstrado na tese; e o que é
realista no tempo e âmbito de um mestrado.

**Treze secções na saída,** de resumo executivo a priorização, e **cada melhoria** com
descrição, justificação, evidência, ficheiro ou capítulo afetado, alteração concreta, benefício,
esforço, prioridade, dependências e risco de inchar o âmbito. Classificada em crítica, alta,
média, baixa ou trabalho futuro, e distinguindo melhorias documentais, de investigação, de
experiências, de alteração ao sistema, e as que se fazem aproveitando o que já existe.

**O texto integral do pedido está no histórico da conversa de 2026-09-01** e deve ser relido na
íntegra antes de executar, porque traz a lista completa das famílias de técnicas a considerar
(de econometria descritiva a *knowledge graphs*, sistemas multiagente e calibração), as treze
perguntas a fazer a cada família, e as colunas da tabela comparativa.

## O que já está respondido, e não precisa de ser reaberto

| Ponto do pedido | Estado |
|---|---|
| Declaração de uso de IA, com ferramentas, tarefas, revisão e responsabilidade | **Feito.** Secção 3.8.4, no sítio que o modelo oficial manda. |
| Apêndices para diagramas grandes, hiperparâmetros, exemplos e evidências | **Existem dois**, e os anexos não contam para o limite de 120 páginas. |
| Distinção entre deteção, explicação, correlação, causalidade, contexto histórico e recomendação | **Feito** e defendido em várias secções; é a espinha ética do trabalho. |
| Validação posterior de cada alerta | **No ar desde a release v53** — o desfecho observado a +1, +3 e +5 sessões, anexado à mensagem original. |
| Utilidade percebida pelo utilizador | **Instrumentado desde a v51**, com a análise pré-registada e a secção da tese gerada a partir dos votos. |

## Uma nota sobre o enquadramento do valor

O pedido enuncia o valor como **redução da latência informacional e do tempo de análise**, que
aumenta a capacidade de reação — dizendo explicitamente que isso não significa lucro nem
recomendação. É um enquadramento diferente do de mais cedo no mesmo dia («quem vende primeiro
perde menos»), e é o correto: sobrevive à medição dos 353 minutos, sobrevive à resposta negativa
da QI3, e não colide com a recusa de aconselhar. A Correção 1 do
`docs/planos/POS_PLANO_TESE_IDEAL.md` fica assim resolvida pelo próprio autor.

Mantém-se a Correção 2 desse ficheiro: a seleção experimental tem de acontecer sobre validação e
não sobre teste. O pedido já a acomoda ao dizer que não é obrigatório testar todas as
combinações e que a tese deve justificar como escolheu um conjunto representativo.

## Como executar, quando chegar a altura

1. Reler o pedido integral no histórico da conversa.
2. Inventariar por evidência: `tese-v2/`, `investigator/`, `api/`, `web/`, `scripts/`,
   `docs/evaluation/`, `docs/design/`, `tests/`. Cada afirmação da auditoria com o ficheiro e a
   linha.
3. Só depois escrever. **Não alterar tese nem código nesta primeira fase** — é auditoria, e o
   autor pediu-o assim.
