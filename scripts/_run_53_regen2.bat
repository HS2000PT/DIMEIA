@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
echo === agregado (MiniLM + MPNet) === > data\_53_regen2.log
.venv\Scripts\python.exe -u scripts\evaluate.py --news data\finnhub_news.csv --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2 >> data\_53_regen2.log 2>&1
echo EXIT_AGREGADO=%ERRORLEVEL% >> data\_53_regen2.log
echo === por setor === >> data\_53_regen2.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py --news data\finnhub_news.csv >> data\_53_regen2.log 2>&1
echo EXIT_SETOR=%ERRORLEVEL% >> data\_53_regen2.log
echo FEITO=1 >> data\_53_regen2.log
