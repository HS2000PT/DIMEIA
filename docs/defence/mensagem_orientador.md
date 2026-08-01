# Mensagem para o orientador (PT-PT, pronta a copiar)

> **Como usar:** copiar o bloco abaixo para email ou Teams. Confirmar os três links marcados
> com ⚠️ antes de enviar (a app pode estar hibernada; o canal tem de estar público).
> Escrita para ser lida em dois minutos e dar direção a quem vai abrir 106 páginas.

---

**Assunto:** Dissertação InvestiGator — versão para revisão (tese, slides, sistema a correr)

Caro Professor Luís Gomes,

Envio a versão atual da dissertação para revisão. Está tudo a compilar e o sistema está a
funcionar em produção, por isso o que precisa mesmo da sua leitura é o conteúdo, não o estado.

**O que abrir, por ordem de importância**

1. **Tese (EN), 106 páginas** — `thesis/main.pdf`
   Se tiver pouco tempo: o **Capítulo 1** (o problema e as três perguntas que o sistema
   responde) e o **Capítulo 6** (os veredictos, incluindo os resultados negativos).
2. **Tese (PT), 110 páginas** — `thesis-pt/main.pdf`
   Mesmo conteúdo, tradução fiel. Mantidas em sincronia: 52 secções e 63 figuras/tabelas em
   ambas, idênticas por capítulo.
3. **Slides de defesa, 23 frames** — `slides/main.pdf`
4. **Sistema a correr** — ⚠️ app: <https://investigator.streamlit.app> ·
   ⚠️ canal Telegram: <https://t.me/InvestiGatorMEIA>
5. **Código** — ⚠️ <https://github.com/HS2000PT/DIMEIA> (465 testes, tudo reproduzível por
   script)

**O que o sistema faz, em três linhas**

Quando uma ação se mexe, o investidor de retalho faz sempre as mesmas três perguntas: *isto é
invulgar para esta ação?*, *é a empresa ou é o mercado?*, e *já aconteceu antes, e o que se
seguiu?*. As ferramentas gratuitas não respondem a nenhuma; um terminal profissional responde às
três por cerca de 2.000 dólares por mês. O sistema responde às três, de graça, e mostra as
contas. **Nunca prevê preços** — é uma restrição de desenho, não uma limitação.

**O que eu gostaria que olhasse com atenção crítica**

- **Os resultados negativos, no Capítulo 6.** Nenhum modelo com texto bateu a linha de base de
  volatilidade (PR-AUC 0,542 vs 0,496). Está reportado tal como caiu, com testes de robustez a
  confirmar que não é sub-ajuste. Preferi isto a procurar um número mais simpático.
- **A secção "Posições Assumidas por Exclusão"** (Cap. 6). Coisas que o sistema
  deliberadamente **não** faz e porquê: sem price targets de analistas (importar a previsão de
  outra pessoa contradiria a tese), sem carteira do utilizador (dados pessoais + fronteira do
  aconselhamento), e sem lhe chamar sistema multi-agente, porque não é.
- **A honestidade da avaliação do narrador** (Cap. 6, RQ3). Reporto duas métricas e admito que
  uma delas é parcialmente circular, explicando o que uso como contrapeso.

**O que ainda falta, e é meu**

- Correr o estudo de utilidade com 6–10 pessoas (protocolo e materiais já prontos; fecha a
  única linha "em aberto" do Cap. 6).
- Fechar consigo a **redação exata da declaração de uso de IA** exigida pela MEIA, e a
  **licença** do código.
- A gravação da demonstração para a defesa.

Fico a aguardar os seus comentários, e agradeço desde já a disponibilidade.

Com os melhores cumprimentos,
**Henrique José da Silva Santos** · nº 1180934 · MEIA

---

## Notas para ti (não enviar)

- **Confirmar antes de enviar:** (1) a app abre sem pedir login numa janela anónima; (2) o canal
  Telegram é público; (3) o repositório está acessível a quem o Professor for.
- **Se a app estiver hibernada** (o Streamlit Community Cloud adormece sem visitas), basta abri-la
  uma vez antes de enviar o email.
- **Se ele perguntar pelo Rafael Silva:** o worldmonitor.app foi recomendação dele e está citado
  na tese; vale a pena dizê-lo, porque é verdade e é elegante.
- **Não prometas** o estudo de utilidade para uma data que não controlas — depende de recrutar
  pessoas.
