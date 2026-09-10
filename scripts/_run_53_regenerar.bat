@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
echo === 1/4 agregado (MiniLM + MPNet) === > data\_53_regen.log
.venv\Scripts\python.exe -u scripts\evaluate.py --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2 >> data\_53_regen.log 2>&1
echo EXIT_AGREGADO=%ERRORLEVEL% >> data\_53_regen.log
echo === 2/4 por setor === >> data\_53_regen.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py >> data\_53_regen.log 2>&1
echo EXIT_SETOR=%ERRORLEVEL% >> data\_53_regen.log
echo === 3/4 corpus e filtro === >> data\_53_regen.log
.venv\Scripts\python.exe -u scripts\evaluate_corpus_and_filter.py >> data\_53_regen.log 2>&1
echo EXIT_CORPUS=%ERRORLEVEL% >> data\_53_regen.log
echo === 4/4 codificadores === >> data\_53_regen.log
.venv\Scripts\python.exe -u scripts\evaluate_retrieval_embedders.py >> data\_53_regen.log 2>&1
echo EXIT_EMBEDDERS=%ERRORLEVEL% >> data\_53_regen.log
echo TUDO_FEITO=1 >> data\_53_regen.log
