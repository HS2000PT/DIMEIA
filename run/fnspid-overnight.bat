@echo off
REM M6 do ML_PLAN — deixar a correr UMA NOITE (duplo-clique e ir dormir).
REM Cadeia completa: 1) download FNSPID 2018-2023 (streaming, ~3-4 h)
REM                  2) reconstruir o dataset de triagem (embargo 5)
REM                  3) retreinar os modelos (SBERT — precisa da stack --ml)
REM Tudo fica em data\fnspid_overnight.log. Se o passo 3 falhar por falta da stack ML,
REM corre antes: bash scripts/setup_env.sh --ml  (tarefa "Setup - + ML / SBERT").
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
echo [%date% %time%] M6 overnight: download FNSPID... (log: data\fnspid_overnight.log)
".venv\Scripts\python.exe" "scripts\download_data.py" > "data\fnspid_overnight.log" 2>&1
if errorlevel 1 goto fail
echo [%date% %time%] a limpar a cache de precos (era do corpus-fumo 2026; o FNSPID e 2018-2023)...
if exist "data\prices" rd /s /q "data\prices"
echo [%date% %time%] dataset de triagem (embargo 5)...
".venv\Scripts\python.exe" "scripts\build_dataset.py" --news "data\fnspid_news_subset.csv" >> "data\fnspid_overnight.log" 2>&1
if errorlevel 1 goto fail
echo [%date% %time%] retreino (SBERT)...
".venv\Scripts\python.exe" "scripts\train_triage.py" --note "FNSPID 2018-2023 (M6)" >> "data\fnspid_overnight.log" 2>&1
if errorlevel 1 goto fail
echo.
echo [%date% %time%] M6 COMPLETO. Ver docs\evaluation\evaluation_triage.md e models\.
echo Depois: correr os testes (run\tests.bat) e fazer commit dos modelos/docs novos.
pause
exit /b 0
:fail
echo.
echo FALHOU — ver o fim de data\fnspid_overnight.log (rede? stack --ml em falta?).
pause
exit /b 1
