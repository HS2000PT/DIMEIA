@echo off
REM Bot interativo (Fase B): /start, /watch TSLA, /unwatch, /list, /stop.
REM Requer TELEGRAM_BOT_TOKEN no .env. Fecha a janela (ou Ctrl+C) para parar.
cd /d "%~dp0.."
".venv\Scripts\python.exe" scripts\run_bot.py
pause
