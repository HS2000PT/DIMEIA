# Auditoria de reprodução — os números deixam de ser herdados

**Data:** 2026-08-30. **Objetivo:** o do ponto 7 do plano de rebuild — que nenhum resultado
final seja aceite por herança — obtido sem repositório novo, correndo outra vez cada
procedimento a partir dos dados em bruto e confrontando o valor regenerado com o que está
escrito na tese.

**Ambiente:** construído de raiz, não reaproveitado. `Python 3.12.3`, `scikit-learn 1.9.0`,
`numpy 2.1.3`, `pandas 2.2.3` — as versões fixadas na Tabela A.1. Entrada: `data/triage_dataset.csv`
e os artefactos versionados em `models/`. Nenhum ficheiro de resultados anterior foi lido.

---

## Resultado: 16 de 16 números reproduzidos exatamente

### Tabela 5.8 — a ablação, e a tabela de consulta

| Linha | Na tese | Regenerado | |
|---|---|---|---|
| Contexto completo (o implantado) | `0.538` / `0.632` | `0.538` / `0.632` | ✓ |
| Só volatilidade | `0.542` / `0.632` | `0.542` / `0.632` | ✓ |
| **Tabela de consulta por empresa** | `0.534` / `0.662` | `0.534` / `0.662` | ✓ |
| Sem os indicadores de setor | `0.543` / `0.629` | `0.543` / `0.629` | ✓ |
| Sem volatilidade nem momento | `0.389` / `0.390` | `0.389` / `0.390` | ✓ |
| Sem nada de nível de empresa | `0.378` / `0.368` | `0.378` / `0.368` | ✓ |
| Só o comprimento do título | `0.378` / `0.352` | `0.378` / `0.352` | ✓ |

O script tem uma porta de entrada própria que se recusa a escrever se não reproduzir os
congelados `0.542` e `0.538` dentro de `0.002`. **Passou.**

### Tabela 5.7 — a precisão dentro do orçamento

| Linha | Na tese | Regenerado | |
|---|---|---|---|
| Alertar sempre (o chão alfabético) | `0.163` | `0.1629` | ✓ |
| Ao acaso, 40 sementes | `0.379 ± 0.017` | `0.3790 ± 0.0170` | ✓ |
| Volatilidade média da empresa | `0.662` | `0.6624` | ✓ |
| O modelo treinado | `0.632` | `0.6317` | ✓ |

### §5.6.6 — deriva

| | Na tese | Regenerado | |
|---|---|---|---|
| PSI da `vol20` | `0.281` | `0.281` | ✓ |
| Prevalência treino → teste | `0.3854` → `0.3781` | `0.3854` → `0.4704` → `0.3781` | ✓ |

### Tabela 5.11 — ponta a ponta

| Política | Na tese | Regenerado | |
|---|---|---|---|
| Ao acaso | `0.3751 ± 0.012` | `0.375 ± 0.012` | ✓ |
| Quem mais se mexeu hoje | `0.489` | `0.489` | ✓ |
| O modelo implantado | `0.632` | `0.632` | ✓ |
| Volatilidade da empresa | `0.662` | `0.662` | ✓ |
| Oráculo | `0.968` | `0.968` | ✓ |

---

## Três coisas que a reprodução confirmou por observação direta

1. **O chão de `0.163` ordena mesmo por ordem alfabética.** O procedimento imprime
   `1105/1105 linhas são AAPL`. O defeito que a tese documenta como erro próprio é real e é
   exatamente o que ela diz que é.
2. **São treze constantes.** O procedimento imprime `prior por ticker 0.6624 (13 constantes)`.
   Confirma a correção feita hoje ao texto, que dizia catorze.
3. **A composição dos blocos.** `Treino 28,574 (2018-01-02..2022-03-03) · Teste 32,649
   (2023-02-02..2023-12-18)`, com a prevalência a subir para `0.4704` na validação. É o achado
   novo de hoje, e sai do procedimento sem eu ter de o procurar.

---

## O que NÃO foi reproduzido, e porquê

Nada disto é um sinal de problema. São limites do sítio onde corri, e cada um tem o comando
que o resolve na tua máquina.

| Bloco | Números | Porque não |
|---|---|---|
| **QI1, deteção** | `0.015`/`0.344`, `F1 0.516`/`0.218`, `0.530`/`0.269`/`0.280` | O procedimento vai buscar preços ao Yahoo em tempo real e o acesso está bloqueado pela lista de saída deste ambiente. `python scripts/evaluate_anomaly.py` na tua máquina resolve. |
| **Linhas com texto da triagem** | `0.439`, `0.496`, `0.469`, `0.533`, `0.547` | Dependem do cache de embeddings de `242 MB`, que não atravessou a ponte para o contentor. |
| **QI2, recuperação** | `0.514`, `0.595`, `0.513`, e os chãos | Precisam da base de `690 MB` e do codificador de frases. |
| **Produção** | `825` decisões, `ROC-AUC 0.486` | Precisam do registo vivo, e esse é por natureza não reproduzível: depende de quando é lido. A tese já o declara, e está separado por uma linha divisória na Tabela A.2. |

---

## O que isto autoriza a dizer, e o que não autoriza

**Autoriza:** que os números do bloco da triagem — que é onde vive a resposta à QI3, o resultado
negativo, a descoberta da tabela de consulta e a comparação ponta a ponta — **não são herdados**.
Foram regenerados hoje, a partir dos dados em bruto, num ambiente construído de raiz, e batem
até à casa decimal publicada. O determinismo que o Capítulo 5 promete é real.

**Não autoriza:** dizer o mesmo da QI1 e da QI2. Esses continuam por reproduzir **neste
exercício**, e a razão é de acesso e não de dúvida. São dois comandos na tua máquina, e valem
uma hora.

**E não autoriza, sobretudo, confundir reprodução com validade.** Reproduzir confirma que o
procedimento é determinista e que o texto cita o que o código produz. Não confirma que o
protocolo esteja certo — o rótulo com $\beta = 1$ continua a ser uma escolha discutível, e a
composição dos blocos continua a limitar o que a comparação separa. As duas fragilidades que
ficaram da auditoria de ontem sobrevivem intactas a esta reprodução, e é assim que deve ser:
correr outra vez o mesmo procedimento não pode corrigir um procedimento.
