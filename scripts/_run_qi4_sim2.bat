@echo off
cd /d C:\Users\ruifa\Desktop\DIMEIA
set HF_HUB_OFFLINE=1
set PYTHONPATH=C:\Users\ruifa\Desktop\DIMEIA
set TOKENIZERS_PARALLELISM=false
.venv\Scripts\python.exe -u -m scripts.avaliar_qi4 --modelo base=all-MiniLM-L6-v2 --modelo magnitude=data\qi4_modelos\magnitude_v2 --modelo direcao=data\qi4_modelos\direcao_v2 --out data\_arquivo\_qi4_tres_v2_local2.md > data\_qi4_sim2.log 2>&1
echo EXITCODE=%ERRORLEVEL% >> data\_qi4_sim2.log
