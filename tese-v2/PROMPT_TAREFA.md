# Texto para colar na tarefa agendada "reescrita tese"

Colar tudo o que está abaixo da linha, no campo de instruções/prompt da tarefa.

---

Estás a continuar a reescrita de uma dissertação de mestrado, na pasta DIMEIA deste computador. Esta sessão é nova e não tem memória de conversas anteriores: todo o contexto está em ficheiro.

PASSO 1, obrigatório antes de tudo o resto. Lê por inteiro, por esta ordem:
1. tese-v2/BRIEF_REESCRITA.md
2. tese-v2/ESTADO.md
3. tese-v2/ch1/chapter1.tex — é a referência de registo de escrita
4. tese-v2/ch3/chapter3.tex — o capítulo mais recente

Se não conseguires ler estes ficheiros, termina imediatamente e responde apenas "SEM ACESSO". Não inventes conteúdo nem prossigas.

PASSO 2. Abre o ESTADO.md e vê a secção "Sessão em curso". Se lá estiver uma linha INICIADA com menos de 90 minutos, para já: outra sessão está a trabalhar. Termina a dizer isso.

PASSO 3. Caso contrário, escreve UM capítulo, o próximo da ordem recomendada no ESTADO.md. Antes de escreveres a primeira linha do capítulo, substitui "Nenhuma." no ESTADO.md pela linha "INICIADA <data> <hora> — a escrever <capítulo>". Isso impede que duas sessões escrevam o mesmo capítulo.

Regras que não podes violar:
- Nenhum parágrafo pode ser copiado da tese antiga em DIMEIA/tese/. Essa pasta é fonte de FACTOS, NÚMEROS e FIGURAS. O texto escreve-se de raiz.
- Nenhum número pode ser inventado. Todos existem em DIMEIA/tese/ ou em DIMEIA/docs/evaluation/. Se não conseguires confirmar um valor, não o escrevas.
- Registo impessoal e declarativo, imitando archive/thesis-versions/thesis-examples/dissertação_Rafael Silva.pdf e o ch1. Proibido: comentários ao próprio texto ("convém dizer", "vale a pena notar", "fica registado"), perguntas retóricas, primeira pessoa, registo confessional.
- Não acrescentes a opção oneside ao main.tex. O modelo oficial exige frente e verso.
- Alvo global: cerca de 112 páginas, 36 000 palavras, 34 figuras, 8 tabelas.

PASSO 4. Compila e verifica. Esta máquina não tem biber nem o babel português: copia tese-v2 para o contentor da sessão, instala texlive-lang-portuguese, biber, lmodern, texlive-fonts-extra e texlive-plain-generic, e compila lá com latexmk. Exige 0 erros e 0 referências indefinidas. O ch3 nunca foi compilado; se fores a primeira sessão a compilar, corrige o que a compilação acusar ANTES de escrever o capítulo novo.

PASSO 5. Atualiza o ESTADO.md: troca a linha INICIADA por "TERMINADA <hora>", marca o capítulo como escrito e regista páginas, palavras, figuras e tabelas reais. Termina com duas ou três frases sobre o que fizeste e o que falta.
