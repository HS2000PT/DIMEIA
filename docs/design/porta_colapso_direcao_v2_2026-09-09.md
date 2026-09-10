# Porta de colapso — `direcao_v2` passa. Nenhum braço colapsou.

> Escrito a 2026-09-09, ~22:20 UTC, imediatamente depois de o `direcao_v2` terminar.
> **Proveniência: esta medição NÃO foi feita na máquina do autor** — ver a secção «O que isto
> não é», que é a parte que decide como se lê o número.

## O resultado

O `direcao_v2` terminou com `EXITCODE=0` (1250 passos, 2691 s, 2,15 s/passo) e **passa a porta
de colapso**. Os dois braços da segunda tentativa estão saudáveis:

| | base sem ajuste | `magnitude` (v1) | `magnitude_v2` | `direcao_v2` |
|---|---|---|---|---|
| cosseno entre manchetes **diferentes** | 0,2052 | **0,9936** ⚠️ | 0,2709 ✅ | **0,2771** ✅ |
| desvio do cosseno | 0,1215 | 0,0019 ⚠️ | 0,0683 | 0,0678 |
| norma do vetor médio | 0,4536 | 0,9968 ⚠️ | 0,5210 | **0,5269** ✅ |
| desvio por dimensão | 0,0451 | 0,0040 ⚠️ | 0,0433 | **0,0431** ✅ |

Os dois braços v2 são quase indistinguíveis um do outro em todos os eixos de dispersão, e a
diferença face à base tem o mesmo sinal e a mesma ordem de grandeza nos dois. **A amostragem
estratificada resolveu o colapso nos dois braços, e não só no da grandeza.**

A trajetória de treino já o antecipava: os dois logs correm quase sobrepostos
(epoch 0.4: perda 8,625 contra 8,619; epoch 0.8: 7,676 contra 7,702; perda final 8,031 contra
8,045). O `direcao_v2` correu mais depressa (2691 s contra 3350 s) por a máquina estar menos
carregada, não por ter feito menos trabalho — o número de passos é o mesmo.

## O que isto não é, e é a parte importante

A medição foi feita **noutra máquina** — um contentor Linux, `sentence-transformers` 6.0.1 e
`torch` 2.14.0 CPU, contra os 5.6 e 2.12.1 do ambiente do autor. Um número produzido noutro
ambiente e citado ao lado dos originais é exatamente a classe de defeito que este projeto já
documentou (um artefacto regenerável regenerado noutras condições é indistinguível de um
correto).

**Por isso correu-se um controlo antes de aceitar o número.** O `magnitude_v2` foi reembebido
neste ambiente sobre as mesmas 1500 manchetes distintas e reproduziu o log original **às quatro
casas em todos os quatro valores** (0,2709 · 0,0683 · 0,5210 · 0,0433). Sem esse controlo o
0,2771 não valia nada; com ele, o ambiente está estabelecido como equivalente para esta medição.

**Duas colunas do log original ficaram por medir:** «moveu-se face à base» e «preservou a
geometria», porque exigem embeber o `all-MiniLM-L6-v2` sem ajuste e o acesso ao Hugging Face
está bloqueado neste contentor. Para o `magnitude_v2` valiam 0,7820 e 0,6070. **Não se sabe
quanto valem para o `direcao_v2`**, e são precisamente os números que dizem se o braço da
direção *aprendeu alguma coisa* em vez de apenas *não ter degenerado*.

## O que fazer a seguir, na máquina do autor

```
.venv\Scripts\python.exe scripts\_colapso_rapido.py ^
  data\qi4_modelos\magnitude_v2 data\qi4_modelos\direcao_v2
```

Isto reproduz a tabela acima **e** preenche as duas colunas em falta, no ambiente canónico. É
esse o artefacto a citar; este documento é a antecipação, não o substituto.

Se confirmar — e a expectativa, medida, é que confirme —, o passo seguinte é o 3.2 do
`docs/contexto/ESTADO_ATUAL.md`, sem alteração:

```
.venv\Scripts\python.exe -u -m scripts.avaliar_qi4 ^
  --modelo base=all-MiniLM-L6-v2 ^
  --modelo magnitude=data\qi4_modelos\magnitude_v2 ^
  --modelo direcao=data\qi4_modelos\direcao_v2 ^
  --out data\_arquivo\_qi4_tres_v2.md
```

⚠️ A regra pré-registada mantém-se: **a tabela de métricas só se lê depois de a porta passar no
ambiente canónico.** Este documento não abre essa porta; diz que ela provavelmente abre.
