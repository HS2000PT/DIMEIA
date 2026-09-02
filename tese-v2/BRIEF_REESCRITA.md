# BRIEF — reescrita da dissertação em `tese-v2/`

> **Este ficheiro é auto-suficiente.** Uma sessão nova, sem memória de conversas anteriores,
> deve conseguir ler só isto e continuar o trabalho corretamente. Ler por inteiro antes de tocar
> em qualquer ficheiro.

## 0. Regra de ouro

O trabalho consiste em **reescrever a dissertação do zero em `tese-v2/`**, imitando ao máximo a
dissertação de referência (`archive/thesis-versions/thesis-examples/dissertação_Rafael Silva.pdf`), adaptada ao tema.
A tese antiga vive em `tese/` e serve **apenas como fonte de factos, números e figuras**.
**Nenhum parágrafo de `tese/` pode ser copiado para `tese-v2/`.** O texto é escrito de novo.

## 1. Regras oficiais (modelo MEIA/ISEP) — não negociáveis

| Regra | Valor | Estado |
|---|---|---|
| Páginas totais | mínimo 60, **máximo 120** | a tese antiga tinha 134: tem de descer |
| Resumo (PT) | **≤ 200 palavras** | ✅ está a 199 |
| Abstract (EN) | **≤ 200 palavras** | ✅ está a 175 |
| Palavras-chave | máximo 6 | ✅ tem 5 |
| Impressão | **frente e verso** (`twoside`); capítulo novo sempre em página ímpar | ✅ não acrescentar `oneside` |
| Margens | inner 3,5 cm · outer 2,6 · topo 3,5 · fundo 2,5 | ✅ já no `.cls` |
| Estrutura | Introdução + 5 capítulos: estado da arte, métodos/opções, implementação, experimentação, conclusões | ✅ já criada |
| Legendas | tabela **acima**, figura **abaixo** | manter |
| Referências | autor-data (`authoryear-comp`) | manter |

## 2. Alvo quantitativo (perfil medido da dissertação do Rafael Silva)

| Capítulo | Páginas | Figuras | Tabelas |
|---|---|---|---|
| 1 Introdução | 8 | 0–2 | 0 |
| 2 Estado da arte | 18 | 2–3 | 1 |
| 3 Métodos e materiais | 10–12 | 4–5 | 2–3 |
| 4 Implementação | 16 | 8 | 1–2 |
| 5 Casos de estudo | 20 | **18–22** | 2 |
| 6 Conclusões | 12 | 0–2 | 0 |
| **Corpo** | **~86** | **~34** | **~8** |

Mais *front matter* (~18 pp), bibliografia (~4 pp) e apêndices (~8 pp) → **~112 páginas**.
Total de palavras alvo: **~36 000** (o Rafael tem 32 402; a tese antiga tinha 51 447).

**A transformação mais importante:** o Rafael tem 6 tabelas e 34 figuras, e 22 dessas figuras
estão no capítulo de casos de estudo. **Os resultados apresentam-se como gráficos, não como
tabelas.** Ao escrever o Capítulo 5, converter as tabelas de resultados da tese antiga em
gráficos (pgfplots ou matplotlib com saída PDF para `figures/`).

## 3. Registo de escrita — o que imitar e o que é proibido

O `ch1/chapter1.tex` **já está escrito no registo correto e serve de referência**. Ler antes de
escrever qualquer outro capítulo.

**Imitar (registo do Rafael):**
- Impessoal e declarativo. Nunca "eu", "o meu", "convém", "vale a pena", "repare-se".
- Cada capítulo abre com um parágrafo do tipo *"Este capítulo apresenta…"*.
- Cada secção abre com uma frase que diz o que a secção faz.
- Facto → citação → implicação. Frases completas, parágrafos densos.
- Terminologia constante: um termo por conceito, do princípio ao fim.

**Proibido, por ordem de gravidade (o autor rejeitou explicitamente):**
1. **Comentários ao próprio texto** — "convém dizer", "fica registado", "é preciso dizer",
   "vale a pena notar", "e isto é uma nota contra mim".
2. **Perguntas retóricas**, sobretudo a abrir secções.
3. **Frases em primeira pessoa** e qualquer registo confessional ou de diário
   ("o erro que mais me custa", "não tinha visto até o pôr aqui").
4. Adjetivos que não acrescentam informação; ênfase a negrito para dramatizar.

Uma limitação continua a ser declarada — mas em registo descritivo, não confessional.
Comparar: ❌ "Escolhi um modelo que não podia fazer o que eu lhe pedia" →
✅ "O modelo implantado não podia executar a função que lhe foi atribuída."

## 4. Estado do trabalho

Ficheiro de estado: **`ESTADO.md`** na mesma pasta. Atualizar sempre no fim de cada sessão.
Cada secção por escrever está marcada com `% POR ESCREVER` no `.tex` respetivo.

## 5. Procedimento de cada sessão

1. Ler este ficheiro e `ESTADO.md`.
2. Se `ESTADO.md` indicar uma sessão iniciada há menos de 90 minutos e ainda não terminada,
   **não fazer nada** e terminar: outra sessão está a trabalhar.
3. Marcar em `ESTADO.md` o capítulo que se vai escrever e a hora de início.
4. Escrever **um capítulo por sessão**, no máximo. Ir buscar os factos, números e figuras à tese
   antiga em `tese/`, reescrevendo o texto de raiz.
5. **Nenhum número pode ser inventado.** Todos os valores existem em `tese/` ou em
   `docs/evaluation/`. Em caso de dúvida sobre um número, não o escrever.
6. Compilar e verificar (secção 6).
7. Atualizar `ESTADO.md` com o resultado, as contagens e o que falta.

## 6. Verificação obrigatória antes de terminar

```bash
cd tese-v2 && latexmk -pdf -interaction=nonstopmode main.tex
```
Exigir: **0 erros**, 0 referências e citações indefinidas.
Depois, a partir da raiz do repositório:
```bash
python3 scripts/check_escrita.py     # PT-PT, um termo por conceito
python3 scripts/check_floats.py      # todo o flutuante referenciado e com legenda
python3 scripts/check_tex_escapes.py
```
E registar em `ESTADO.md`: páginas, palavras, figuras, tabelas.

## 7. Se a compilação falhar

A máquina local não compila LaTeX (falta `biber` e o babel português). Compilar no contentor da
sessão depois de instalar:
`texlive-lang-portuguese biber lmodern texlive-fonts-extra texlive-plain-generic`.
Copiar `tese-v2/` para o contentor, compilar lá, e trazer só o resultado.

## 8. Fontes de facto

- `tese/` — a dissertação antiga: todos os números, figuras TikZ e resultados.
- `docs/evaluation/*.md` — os relatórios gerados pelos procedimentos de avaliação.
- `archive/reports/AUDITORIA_CRITICA_PRE_DEFESA.md` — as fragilidades conhecidas e como estão declaradas.
- `archive/reports/AUDITORIA_REPRODUCAO.md` — que números foram reproduzidos de raiz e batem certo.
- `archive/thesis-versions/thesis-examples/` — as quatro dissertações aprovadas; a do Rafael Silva é a referência.
