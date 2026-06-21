# glossary.md — Glossário de termos técnicos (PT-PT)

> Termo · definição curta em PT-PT · (sigla, se aplicável). Cresce ao longo do projeto.
> Explicações desenvolvidas em `docs/learning.md`.

| Termo | Definição curta | Sigla |
|---|---|---|
| Retorno | Variação percentual do preço entre dois instantes | — |
| Log-return | ln(preço_t / preço_t-1); retorno logarítmico, mais estável | — |
| Volatilidade | Desvio-padrão dos retornos; mede a oscilação típica do preço | — |
| Janela móvel (rolling) | Cálculo sobre uma janela deslizante (ex.: últimos 20 dias) | — |
| Z-score | (valor − média) / desvio-padrão; nº de desvios face à norma | — |
| Anomalia | Observação que se desvia fortemente do padrão esperado | — |
| Embedding | Representação de texto como vetor numérico semântico | — |
| Similaridade do cosseno | Medida de alinhamento entre dois vetores (1=igual, 0=sem relação) | — |
| Event study | Medir o efeito de um evento via retornos numa janela pós-evento | — |
| Janela de impacto | Período após a notícia onde se mede o retorno (+1d, +3d, …) | — |
| Explicabilidade | IA com lógica compreensível e rastreável pelo utilizador | XAI |
| Lookahead / fuga de informação | Usar (erradamente) informação do futuro no presente | — |
| FinBERT | Modelo de linguagem para sentimento em texto financeiro | — |
| FNSPID | Dataset de notícias financeiras alinhadas a preços (histórico) | — |
| Base de conhecimento (KB) | Coleção de notícias históricas com impacto medido + embedding | KB |
| Precedente | Notícia histórica semelhante usada como evidência na explicação | — |
| Embedder | Componente que converte texto em vetor (interface intermutável) | — |
| Hashing embedder | Embedding lexical determinístico por hash de palavras (baseline) | — |
| SBERT | Sentence-BERT; modelo que gera embeddings de frases | SBERT |
| Baseline | Método simples de referência para comparar (ablação) na avaliação | — |
| Ablação | Remover/trocar um componente para medir o seu contributo | — |
| JSONL | Ficheiro com um objeto JSON por linha (formato da KB) | — |
| Streaming (de dados) | Ler/processar um ficheiro grande em blocos, sem o carregar todo | — |
| Top-k | Os k itens mais bem classificados (aqui, mais semelhantes) | — |
| Gatilho 2 | Alerta despoletado por uma notícia nova (vs. Gatilho 1 = movimento) | — |
| RSS | Formato de feed para distribuir notícias/atualizações de um site | — |
| Finnhub | API financeira gratuita (preços, notícias de empresa) | — |
| Capitalização de mercado | Valor total das ações de uma empresa/mercado (preço × nº de ações) | market cap |
| Investidor de retalho | Investidor individual não-profissional (por oposição a institucional) | retail |
| Liquidez | Facilidade de comprar/vender um ativo sem mover muito o preço | — |
| OHLCV | Open/High/Low/Close/Volume — dados de preço por período | — |
| Telegram Bot API | API gratuita para enviar mensagens via bot do Telegram | — |
