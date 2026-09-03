# Piloto conceptual: ciclo de vida do modelo

Estado: piloto editável criado e inspecionado no Figma em 2026-09-03.
Ficheiro: https://www.figma.com/design/sNfbRq1WUSM8gRK95FjtWy
Frame: `1:2`. As nove etapas, a passagem do mesmo modelo e a ausência de retreino estão desenhadas.
Não substituir a Figura 4.10 antes de comparar as duas versões e obter a decisão do autor.

## Fonte e afirmação a preservar

Fonte: `tese-v2/ch4/chapter4.tex`, Figura 4.10 (`fig:sis_lifecycle`).
O modelo implantado é o mesmo modelo avaliado. O sistema observa decisões e deriva,
mas não fecha automaticamente o ciclo com retreino. Não confundir este diagrama do sistema
existente com a arquitetura de retreino proposta e não executada da Figura 4.11.

## Composição proposta

Dois percursos horizontais, ambos da esquerda para a direita, numa peça vetorial de fundo
branco. Título da faixa fora das caixas; ligações sem atravessar texto.

**Faixa 1 — Construção e avaliação**

Conjunto de dados rotulado → Treino → Validação e calibração → Teste, utilização única →
Artefacto versionado.

**Passagem entre faixas**

Do artefacto versionado para o primeiro bloco da faixa seguinte. Ligação explícita com
o rótulo «o mesmo modelo», sem criar uma nova etapa de treino.

**Faixa 2 — Observação em produção**

Modelo em produção → Registo de cada decisão → Espera pela resposta do preço →
Pós-validação e deriva.

**Limite visível**

Uma ligação tracejada interrompida, fora das caixas, assinala «Retreino automático ausente».
Não desenhar uma seta contínua a regressar ao treino: isso afirmaria uma capacidade inexistente.

## Gramática

- Verde `#0B7A53` apenas no artefacto versionado e no mesmo modelo em produção.
- Tinta `#1D2824`; referências e conectores `#66736F`; fundo branco.
- Caixas neutras para as outras etapas; sem sombras ou decoração.
- Exportação PDF vetorial e cópia editável; confirmar fontes/contornos na exportação.
- Largura final de comparação igual à largura da figura atual, não à largura do monitor.

## Critérios de aceitação antes da substituição

1. Todas as nove etapas atuais estão presentes, sem capacidades novas.
2. Teste de utilização única e identidade avaliado/implantado leem-se sem recorrer à legenda.
3. A ausência de retreino não pode ser confundida com um ciclo implementado.
4. Nenhuma seta atravessa texto; nenhuma caixa corta ou reduz excessivamente as letras.
5. A versão reduzida à largura da tese continua legível em cor e em escala de cinzentos.
6. Comparar lado a lado com a Figura 4.10 atual e conservar a atual se não houver ganho claro.

## Retoma

### Revisão de escala concluída

No mesmo frame, rótulos e fases passaram a 22 px: 8,03 pt à largura de 390 pt.
Caixas com 128 px de altura e ligações reposicionadas. Prova e exportação atualizadas,
inspecionadas em cor/cinzentos. A perda de leitura foi resolvida; a figura fica mais alta.
Proposta pronta para decisão do autor. Não foi incorporada na tese.
Os valores menores descritos abaixo pertencem à primeira versão.

### Comparação concluída em 2026-09-03

Exportação recuperada pela ferramenta de descarga de recursos: `output/pdf/piloto-ciclo-modelo.pdf`.
Prova à largura igual: `output/pdf/comparacao-ciclo-modelo.pdf`, gerada por
`scripts/figures/compare_lifecycle_pilot.py`, com recorte vetorial da página física 70.
Ambas ocupam 390 pt (137,6 mm). Piloto: rótulos 6,57 pt e fases 5,84 pt, contra cerca de
8 pt na figura atual. Cor e cinzentos renderizados e inspecionados; sem cortes nem colisões.
O contraste sobrevive, mas a tipografia fica menor. **Recomendação: não substituir nesta versão.**
O PDF exportado usa fonte Type 3 incorporada; não afirmar conversão integral em contornos.
O bloqueio de exportação abaixo é histórico e está resolvido. A tese permanece intacta.

A autenticação foi restabelecida e o ficheiro acima foi criado no único espaço disponível.
A inspeção visual a escala 1 não mostrou cortes nem sobreposições. Texto e caixas são editáveis.
A exportação PDF devolveu 250 712 bytes, mas a ferramenta não disponibilizou um ficheiro
descarregável: não se considera entregue nem verificado. Falta obter o PDF local e comparar
à largura da tese, em cor e cinzentos, antes da decisão do autor. A tese não foi alterada.
