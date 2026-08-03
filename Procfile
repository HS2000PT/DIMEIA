web: streamlit run app/dashboard.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
worker: python scripts/run_alerts.py --watch --interval 60
