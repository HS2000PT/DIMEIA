@echo off
REM P3 do PLANO_FINAL: KB de retrieval multi-ano (FNSPID 2018-2023) com SBERT real.
REM Lancado DESTACADO (sobrevive ao fecho do VS Code); estado no log data\kb_build.log.
REM NAO toca em data\samples\kb_sample.jsonl (a amostra da demo/tese fica intacta):
REM a amostra nova vai para data\samples\kb_fnspid_sample.jsonl.
cd /d "%~dp0.."
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
echo [%date% %time%] KB FNSPID: inicio >> data\kb_build.log
".venv\Scripts\python.exe" -u scripts\build_kb.py --news data\fnspid_news_subset.csv --sbert --out data\kb_fnspid_sbert.jsonl --sample data\samples\kb_fnspid_sample.jsonl >> data\kb_build.log 2>&1
if %errorlevel%==0 (
  echo [%date% %time%] KB COMPLETA >> data\kb_build.log
) else (
  echo [%date% %time%] KB FALHOU exit=%errorlevel% >> data\kb_build.log
)
