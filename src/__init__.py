"""Sistema de alertas financeiros explicáveis (XAI-first) — pacote raiz.

Estrutura por componente (cada subpacote é uma peça do pipeline):
- market_data        : dados de mercado em tempo real (camada live)
- news_fetcher       : notícias financeiras em tempo real (camada live)
- historical_kb      : base de conhecimento histórica (FNSPID)
- anomaly_detector   : deteção de movimentos abruptos
- correlation_engine : correlação notícia–mercado / precedentes históricos
- explanation_engine : motor de explicação (XAI)
- impact_analyzer    : impacto setorial em tickers relacionados (OPCIONAL)
- telegram_bot       : envio de alertas via Telegram Bot API
"""
