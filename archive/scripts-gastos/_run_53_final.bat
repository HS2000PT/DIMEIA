@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
set EQ=data\finnhub_news_equilibrado.csv
set FULL=data\finnhub_news.csv
echo === PRIMARIO: equilibrado -^> artefactos congelados === > data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate.py --news %EQ% --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2 --out docs\evaluation\evaluation_results.md --fig tese-pt\figures\eval_retrieval_precision.pdf >> data\_53_final.log 2>&1
echo EXIT_A=%ERRORLEVEL% >> data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py --news %EQ% --out docs\evaluation\evaluation_per_sector.md --fig tese-pt\figures\eval_retrieval_per_sector.pdf >> data\_53_final.log 2>&1
echo EXIT_B=%ERRORLEVEL% >> data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate_retrieval_embedders.py --news %EQ% --out docs\evaluation\evaluation_retrieval_embedders.md >> data\_53_final.log 2>&1
echo EXIT_C=%ERRORLEVEL% >> data\_53_final.log
echo === SENSIBILIDADE: corpus completo === >> data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate.py --news %FULL% --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2 --out docs\evaluation\evaluation_results_composicao.md --fig data\_arquivo\_composicao_agregado.pdf >> data\_53_final.log 2>&1
echo EXIT_D=%ERRORLEVEL% >> data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate_per_sector.py --news %FULL% --out docs\evaluation\evaluation_per_sector_composicao.md --fig data\_arquivo\_composicao_setor.pdf >> data\_53_final.log 2>&1
echo EXIT_E=%ERRORLEVEL% >> data\_53_final.log
.venv\Scripts\python.exe -u scripts\evaluate_retrieval_embedders.py --news %FULL% --out docs\evaluation\evaluation_retrieval_embedders_composicao.md >> data\_53_final.log 2>&1
echo EXIT_F=%ERRORLEVEL% >> data\_53_final.log
copy /Y tese-pt\figures\eval_retrieval_precision.pdf tese-eng\figures\eval_retrieval_precision.pdf >nul
copy /Y tese-pt\figures\eval_retrieval_per_sector.pdf tese-eng\figures\eval_retrieval_per_sector.pdf >nul
echo FEITO=1 >> data\_53_final.log
