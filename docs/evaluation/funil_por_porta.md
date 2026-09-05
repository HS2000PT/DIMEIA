# funil_por_porta.md — onde morre cada avaliação, por dia

> Gerado por `scripts/snapshot_funil.py` a partir do `gate_log.jsonl` da branch de
> dados `alerts-history`, a mesma fonte que a página serve. **Não editar à mão.**

⚠️ **A coluna chama-se _avaliações_ e não _notícias_, e a diferença decide a leitura.**
O sistema reavalia os mesmos títulos de 60 em 60 segundos, portanto um título que
sobreviva às portas e seja travado no fim conta uma vez por minuto. Estes valores
medem
**onde o tempo do sistema é gasto**, não quantas histórias distintas cada porta deitou
fora. Ler a maior como *«é esta a porta que mais corta»* seria repetir, pelo lado
da interpretação, o defeito que a sessão 58 corrigiu no código.

⚠️ **O registo guarda três dias.** É republicado a cada ciclo, logo o custo é de
publicação e não de armazenamento. Correr este comando amanhã dá outros dias.

---

## A leitura que a dissertação cita — 2026-08-15 (NÃO REGENERÁVEL)

Esta é a Tabela~`tab:sis_funil` do Capítulo 4. É parte de um dia, lida no momento em que o registo foi consultado; os 333 de `alerted` são de ANTES de a etapa `already_sent` existir. O dia já saiu do
registo e não volta; fica escrito aqui para que o número impresso tenha origem.

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Sem precedente forte | 2 994 | 59.2% | nenhum caso passado acima do chão de semelhança |
| Abaixo do piso da triagem | 1 194 | 23.6% | o modelo pontuou abaixo do mínimo |
| Piso escalonado | 269 | 5.3% | o segundo alerta do dia exigia pontuação mais alta |
| A mesma história | 249 | 4.9% | já contada por outras palavras |
| Orçamento esgotado | 21 | 0.4% | o dia já tinha gasto os cinco alertas |
| Sobreviveu às portas | 333 | 6.6% | chegou ao fim do funil |
| **Total avaliado** | **5 060** | | |
| **Mensagens entregues** | **5** | | o orçamento do dia |

---

## O que o mesmo comando deu, dia a dia (6 dias acumulados)

Cada dia entra quando o comando corre e **nunca é retirado**; o registo de
produção só guarda três dias de cada vez, pelo que um dia perdido não volta.

### 2026-08-19  *(dia anterior, conservado)*

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Título velho | 1 | 0.0% | publicado há mais de dois dias |
| Sem precedente forte | 16 | 0.2% | nenhum caso passado acima do chão de semelhança |
| A mesma história | 55 | 0.8% | já contada por outras palavras |
| Orçamento esgotado | 6 267 | 89.0% | o dia já tinha gasto os cinco alertas |
| Já avisei hoje | 700 | 9.9% | este título já saiu neste dia |
| Sobreviveu às portas | 5 | 0.1% | chegou ao fim do funil |
| **Total avaliado** | **7 044** | | |

### 2026-08-20  *(dia anterior, conservado)*

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Título velho | 250 | 3.5% | publicado há mais de dois dias |
| Sem precedente forte | 323 | 4.6% | nenhum caso passado acima do chão de semelhança |
| A mesma história | 13 | 0.2% | já contada por outras palavras |
| Orçamento esgotado | 5 507 | 77.7% | o dia já tinha gasto os cinco alertas |
| Já avisei hoje | 994 | 14.0% | este título já saiu neste dia |
| Sobreviveu às portas | 5 | 0.1% | chegou ao fim do funil |
| **Total avaliado** | **7 092** | | |

### 2026-08-21  *(dia anterior, conservado)*

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Sem precedente forte | 5 | 0.1% | nenhum caso passado acima do chão de semelhança |
| A mesma história | 103 | 1.8% | já contada por outras palavras |
| Orçamento esgotado | 4 896 | 84.3% | o dia já tinha gasto os cinco alertas |
| Já avisei hoje | 799 | 13.8% | este título já saiu neste dia |
| Sobreviveu às portas | 5 | 0.1% | chegou ao fim do funil |
| **Total avaliado** | **5 808** | | |

### 2026-09-03

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Sem precedente forte | 12 | 0.7% | nenhum caso passado acima do chão de semelhança |
| Orçamento esgotado | 1 621 | 95.4% | o dia já tinha gasto os cinco alertas |
| Sem notícias | 67 | 3.9% | a fonte não devolveu nada para esta empresa |
| **Total avaliado** | **1 700** | | |

### 2026-09-04

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Orçamento esgotado | 11 174 | 99.8% | o dia já tinha gasto os cinco alertas |
| Já avisei hoje | 17 | 0.2% | este título já saiu neste dia |
| Sobreviveu às portas | 5 | 0.0% | chegou ao fim do funil |
| **Total avaliado** | **11 196** | | |

### 2026-09-05

| Onde morreu | Avaliações | % | O que é |
|---|---:|---:|---|
| Orçamento esgotado | 7 059 | 99.4% | o dia já tinha gasto os cinco alertas |
| Já avisei hoje | 34 | 0.5% | este título já saiu neste dia |
| Sem notícias | 6 | 0.1% | a fonte não devolveu nada para esta empresa |
| Sobreviveu às portas | 5 | 0.1% | chegou ao fim do funil |
| **Total avaliado** | **7 104** | | |

**Leitura honesta do que mudou.** No dia citado pela dissertação o corte estava
repartido pelas portas de evidência; nos dias acima é o **orçamento diário** que
domina, e por uma razão de contagem e não de política: gastos os cinco alertas, cada
ciclo de 60 segundos volta a registar todas as candidatas nessa etapa até ao fim do
dia. É o mesmo artefacto que a ressalva do topo descreve, e é a razão pela qual a
dissertação cita um dia e não uma média.
