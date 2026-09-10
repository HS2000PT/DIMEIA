# ESTADO ATUAL — retoma a frio

> **Para que serve.** Se a sessão morrer a meio, este ficheiro chega para retomar noutra
> plataforma (Claude Code, Codex, ChatGPT, Cowork) sem perder nada. É escrito **antes** de cada
> bloco de acções, não depois.
>
> **Última escrita:** 2026-09-09, depois de o `magnitude_v2` passar a porta de colapso.
> **Regra:** quem retomar actualiza esta secção antes de agir.

### 🟢 O RESULTADO DO DIA — o colapso está resolvido

`magnitude_v2` (pares estratificados, taxa 5e-6) **passou a porta de colapso**:

| | base sem ajuste | `magnitude` (v1) | `magnitude_v2` |
|---|---|---|---|
| cosseno entre manchetes **diferentes** | 0,2052 | **0,9936** ⚠️ | **0,2709** ✅ |
| norma do vetor médio | 0,4536 | 0,9968 ⚠️ | 0,5210 ✅ |
| desvio por dimensão | 0,0451 | 0,0040 ⚠️ | 0,0433 ✅ |
| moveu-se face à base (cosseno médio) | — | 0,2688 | 0,7820 |
| preservou a geometria (correlação) | — | 0,2341 | 0,6070 |

Leitura: o v2 **mexeu mesmo** no espaço (cosseno base↔ajustado 0,78; a geometria das semelhanças
correlaciona 0,61 com a original) **sem degenerar**. O v1 continua confirmado como colapsado e os
seus números continuam a não valer nada.

**A causa era a amostragem de pares**, não a taxa de aprendizagem sozinha: pares ao acaso davam
uma distribuição triangular do alvo (média 1/3), e o mínimo da perda era «prever a média para
tudo». Com amostragem estratificada o alvo fica com média 0,499 e desvio 0,289.

Reproduzir: `.venv\Scripts\python.exe scripts\_colapso_rapido.py data\qi4_modelos\magnitude_v2`

### Estado do treino, verificado agora

- `magnitude_v2`: **terminado**, EXITCODE=0. 1250 passos, 3351 s (2,68 s/passo).
- `direcao_v2`: **a treinar**, arrancou por volta das 22:20. Estimativa: ~55 min.
- Verificar com: `.venv\Scripts\python.exe scripts\_estado_treino.py data\_qi4_*.log`

### Bloco em curso — plano pré-registado

**Retomar aqui:**

1. Esperar que `direcao_v2` termine (`data\qi4_modelos\direcao_v2` aparece; log diz EXITCODE=0).
2. Correr a porta de colapso nos dois:
   `scripts\_colapso_rapido.py data\qi4_modelos\magnitude_v2 data\qi4_modelos\direcao_v2`
3. Só se **nenhum** colapsar: correr a avaliação completa
   `python -m scripts.avaliar_qi4 --modelo base=all-MiniLM-L6-v2 --modelo magnitude=data\qi4_modelos\magnitude_v2 --modelo direcao=data\qi4_modelos\direcao_v2`
   (a porta de colapso está também lá dentro; imprime o cosseno antes de qualquer métrica).
4. Se o `direcao_v2` colapsar e o `magnitude_v2` não, **isso é em si um resultado** — dizer que a
   direção é mais difícil de aprender não é o mesmo que ter um treino degenerado, e é preciso
   descer a taxa antes de afirmar seja o que for.
5. Registar em `docs/contexto/TASKS.md` e em `docs/design/`.

**Feito neste bloco (Capítulo 2, tarefa A12):** ver
`docs/design/capitulo2_literatura_2026-09-09.md`. Resumo: quatro PDFs lidos por inteiro
([Mun09], [Liu23d], [Oh07], [Du24]); inserções em §2.1, §2.2, §2.4, §2.6, §2.7, §2.9 e §6.4, nas
**duas** línguas; oito entradas novas na bibliografia; `robertson2009bm25` corrigido; verificador
de bibliografia corrigido com testes. **As duas árvores compilam com zero citações e zero
referências por resolver** (`scripts\_compilar.py`).

### Armadilhas novas, descobertas neste bloco

1. **Nunca correr `python -c "..."` através da ponte.** O PowerShell parte a expressão. Escrever
   sempre um `.py`. O mesmo para regex na linha de comandos: `|` é pipe do cmd e `^` é o escape
   do cmd. Usar `scripts\_g.py` (aceita vários padrões como argumentos separados).
2. **`latexmk` não tem opção `-halt-on-error=false`.** Com ela responde «Bad options specified»,
   devolve 10 e **não compila nada** — e como o PDF antigo fica no sítio, um verificador ingénuo
   diz «ok» sobre um ficheiro que ninguém gerou. O `_compilar.py` passou a exigir código 0 e a
   imprimir o número de páginas.
3. **`tese-eng` não tem `latexmkrc`** e a `tese-pt` tem. Assimetria a corrigir um dia.
4. **A ponte cai com a máquina carregada.** Com treino a decorrer, lançar em segundo plano para
   um ficheiro de log e ler o ficheiro depois, em vez de esperar pela saída.
