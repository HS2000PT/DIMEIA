@echo off
REM Corre os dois gatilhos (noticia offline + mercado ao vivo). Nao envia nada.
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" "scripts\demo.py"
pause
