web: uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 65
worker: python scripts/run_alerts.py --watch --interval 60
