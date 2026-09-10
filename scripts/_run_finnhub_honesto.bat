@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
.venv\Scripts\python.exe -u scripts\fetch_finnhub_news.py --days 27 --fim 2026-06-25 --fatiar 1 --max-per-ticker 100000 --pausa 1.1 --out data\_arquivo\_finnhub_news_fatiado.csv --sample data\_arquivo\_finnhub_sample_fatiado.csv > data\_finnhub_fatiado.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> data\_finnhub_fatiado.log
