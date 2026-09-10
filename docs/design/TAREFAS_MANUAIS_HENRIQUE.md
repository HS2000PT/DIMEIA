# Tarefas que só o Henrique pode fazer

> Lista viva. Actualizada a 2026-09-09. O que está aqui está aqui porque **precisa de
> credenciais, de uma conta, ou de uma decisão tua** — não porque seja difícil.
>
> Ordem: as de cima desbloqueiam mais trabalho do que as de baixo.

---

## 1. FEITO — Cinco PDFs da literatura ✅

Entregaste-os a 2026-09-09. Os quatro que faltavam foram lidos em texto integral nesse dia e
estão integrados no Capítulo 2, nas duas línguas. O que cada um diz e o que mudou por causa
disso está em `docs/design/capitulo2_literatura_2026-09-09.md`.

**Valeu mesmo a pena, e por uma razão concreta:** eu tinha escrito, a partir do resumo, que o
[Waa21] «justifica empiricamente a opção por explicação baseada em casos». Lido por inteiro, diz
o contrário — as explicações por exemplos **não se distinguiram de não dar explicação nenhuma**
(p = 0,796). Isso teria ido para a tese como uma afirmação falsa sobre um artigo com 385 citações.

---

## 1b. IMPORTANTE — Mais dois PDFs, quando puderes

**Porquê:** são os dois estudos com pessoas **no domínio financeiro** que sustentam a secção
mais honesta do Capítulo 2 (a contraevidência à opção por explicação baseada em casos, §2.7).
Hoje cito-os **apenas pelo que consta do resumo do editor**, que verifiquei. Está correto assim,
mas sem os PDFs não posso escrever quantos participantes tiveram nem os valores concretos --- e
são esses números que dão peso ao parágrafo.

**Passo a passo:**

1. Entra em `https://biblioteca.isep.ipp.pt` com as credenciais do ISEP (ou liga a VPN do IPP).
2. Descarrega estes dois e grava-os com **exactamente** estes nomes:

   | Guardar como | Procurar por | DOI |
   |---|---|---|
   | `cau2023_logic_style.pdf` | Supporting High-Uncertainty Decisions through AI and Logic-Style Explanations (IUI 2023) | `10.1145/3581641.3584080` |
   | `bertrand2023_feature_based.pdf` | Questioning the ability of feature-based explanations... (FAccT 2023) | `10.1145/3593013.3594053` |

   *Nota: o da FAccT costuma ser de acesso aberto na biblioteca digital da ACM. Se abrires
   `https://dl.acm.org/doi/10.1145/3593013.3594053` a partir da rede do ISEP, deve descarregar
   directamente. Eu não consigo lá chegar daqui.*

3. Mete-os em `C:\Users\ruifa\Desktop\DIMEIA\data\literature\`.
4. Diz-me «PDFs prontos». Leio-os e reforço a §2.7 com os números.

**Se não conseguires:** não é bloqueante. A secção fica como está, correta e mais curta.

---

## 2. CRÍTICO — O corpus do Finnhub existe nalgum lado?

**Porquê:** o `data/finnhub_news.csv`, com as 3 714 manchetes, é a base da §5.3.2 — a Figura
5.6, o resultado de recuperação que a tese apresenta **em primeiro lugar**. Não está nesta
máquina (procurei o perfil `ruifa` inteiro, incluindo ficheiros ocultos), não está no histórico
do git, não está no `archive/`. Só sobrevivem 30 linhas de amostra.

Pela regra que deste hoje — o que não se reproduz aqui, desconsidera-se — este resultado **sai
da tese** se o ficheiro não aparecer.

**Passo a passo:**

1. O `models/triage_lr.json` antigo aponta para `C:\Users\henri\Desktop\DIMEIA\…`. **Essa
   máquina não é esta.** Tens outro portátil, um PC antigo, ou uma máquina do ISEP onde
   trabalhaste em julho?
2. Se sim: procura lá por `finnhub_news.csv` (procura no disco todo por `finnhub_news`).
3. Vê também: OneDrive, Google Drive, Dropbox, uma pen, uma cópia de segurança do Windows.
4. Diz-me **«encontrei»** e o caminho, ou **«não existe»**.

**O que acontece em cada caso:**

- **Encontrado:** copio-o para o repositório, fixo-o por `sha256` como fiz ao FNSPID, versiono
  uma amostra, e a §5.3.2 fica reproduzível e mantém-se.
- **Não existe:** refaço a §5.3.1–§5.3.3 sobre o corpus FNSPID, que **é** reproduzível.
  Perdem-se os números concretos; ganha-se um resultado assente num corpus de seis anos fixado
  por soma de controlo, em vez de 27 dias irrepetíveis. **A tese sai a ganhar.** Não é uma
  perda disfarçada de vitória: é mesmo melhor.

---

## 3. IMPORTANTE — Chave da API do Finnhub (só se a nº 2 der «não existe»)

**Porquê:** se decidirmos recolher um corpus recente novo — não para reproduzir o antigo, que
é impossível, mas para ter um braço «corpus recente» reproduzível daqui para a frente.

**Passo a passo:**

1. Vai a `https://finnhub.io/dashboard` e entra na tua conta (ou cria uma gratuita).
2. Copia a chave da API.
3. Abre `C:\Users\ruifa\Desktop\DIMEIA\.env` e confirma que existe a linha
   `FINNHUB_API_KEY=...` com a chave actual. Se não existir, acrescenta-a.
4. Diz-me «chave pronta».

**Só faz sentido depois de responderes à nº 2.** Não avanço sem isso.

---

## 4. IMPORTANTE — Decisão sobre o narrador

**Porquê:** o `docs/evaluation/evaluation_narrator.md` foi gerado por um arnês que chama um
modelo de linguagem. Para o voltar a correr é preciso saber qual e com que credenciais.

**Passo a passo:**

1. Diz-me que fornecedor usaste (OpenAI? Anthropic? um modelo local via Ollama?).
2. Se for um serviço pago, confirma que a chave está no `.env` e ainda é válida.
3. Se preferires não gastar créditos, diz «não repetir» — nesse caso trato os números do
   narrador como **observacionais** (um registo do que aconteceu, não uma medição repetível) e
   digo-o no texto.

---

## 5. QUANDO PUDERES — Rever a decisão do Capítulo 1

**Porquê:** decidi hoje, com o teu «avança», que a QI4 **refina** a restrição fundadora em vez
de a obedecer sem mais: a grandeza do movimento é parcialmente aprendível do texto, a direção
não é, e é isso que os dois braços medem. Isto muda o enquadramento do Capítulo 1.

**Não é para fazeres nada agora.** É para saberes que está decidido e porquê, e para me
travares se discordares. Reescrevo o Capítulo 1 só quando os resultados dos três braços
estiverem em cima da mesa.

---

## Já não é preciso

- ~~Apagar pastas inúteis do repositório~~ — não havia nenhuma; o `.gitignore` é exemplar.
- ~~Voltar a descarregar o FNSPID~~ — feito, fixado por revisão e `sha256`, com teste a guardá-lo.
