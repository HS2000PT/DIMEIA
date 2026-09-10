$ErrorActionPreference = 'Continue'
Set-Location C:\Users\ruifa\Desktop\DIMEIA
Remove-Item 'scripts\_diag_qi4.py' -Force -ErrorAction SilentlyContinue
git add investigator/qi4/colapso.py tests/test_qi4_colapso.py scripts/avaliar_qi4.py
git add ESTADO_ATUAL.md
git commit -F data\_msg.txt
git log -1 --stat --oneline
Remove-Item 'data\_msg.txt' -Force -ErrorAction SilentlyContinue
