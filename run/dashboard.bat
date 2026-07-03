@echo off
REM Abre o dashboard InvestiGator no browser. Fecha esta janela (ou Ctrl+C) para parar.
cd /d "%~dp0.."
".venv\Scripts\python.exe" -m streamlit run "app\streamlit_app.py"
pause
