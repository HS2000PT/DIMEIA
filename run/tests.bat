@echo off
REM Corre os testes e o lint (o mesmo que scripts/verify.sh, sem precisar de bash).
cd /d "%~dp0.."
".venv\Scripts\python.exe" -m pytest
".venv\Scripts\python.exe" -m ruff check .
pause
