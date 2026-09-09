@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
.venv\Scripts\python.exe -u -m scripts.treinar_qi4 --arma magnitude --base ProsusAI/finbert --n-pares 40000 --taxa 5e-6 --saida data\qi4_modelos\controlo_finbert > data\_qi4_c4.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> data\_qi4_c4.log
