@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
.venv\Scripts\python.exe -u scripts\evaluate.py --news data\_arquivo\_finnhub_news_fatiado.csv --out data\_arquivo\_53_agregado_honesto.md --fig data\_arquivo\_53_agregado_honesto.pdf > data\_53_agregado.log 2>&1
echo EXITCODE_AGREGADO=%ERRORLEVEL% >> data\_53_agregado.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py --news data\_arquivo\_finnhub_news_fatiado.csv --out data\_arquivo\_53_setor_honesto.md --fig data\_arquivo\_53_setor_honesto.pdf > data\_53_setor.log 2>&1
echo EXITCODE_SETOR=%ERRORLEVEL% >> data\_53_setor.log
