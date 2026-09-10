@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
.venv\Scripts\python.exe -u -m scripts.treinar_qi4 --arma magnitude --n-pares 40000 --taxa 5e-6 --saida data\qi4_modelos\magnitude_v2 > data\_qi4_mag2.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> data\_qi4_mag2.log
.venv\Scripts\python.exe -u -m scripts.treinar_qi4 --arma direcao --n-pares 40000 --taxa 5e-6 --saida data\qi4_modelos\direcao_v2 > data\_qi4_dir2.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> data\_qi4_dir2.log
