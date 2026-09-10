@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
echo === equilibrado: agregado === > data\_53_eq.log
.venv\Scripts\python.exe -u scripts\evaluate.py --news data\finnhub_news_equilibrado.csv --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2 --out data\_arquivo\_53_eq_agregado.md --fig data\_arquivo\_53_eq_agregado.pdf >> data\_53_eq.log 2>&1
echo EXIT_AG=%ERRORLEVEL% >> data\_53_eq.log
echo === equilibrado: por setor === >> data\_53_eq.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py --news data\finnhub_news_equilibrado.csv --out data\_arquivo\_53_eq_setor.md --fig data\_arquivo\_53_eq_setor.pdf >> data\_53_eq.log 2>&1
echo EXIT_ST=%ERRORLEVEL% >> data\_53_eq.log
echo FEITO=1 >> data\_53_eq.log
