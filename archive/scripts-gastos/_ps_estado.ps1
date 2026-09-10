$ErrorActionPreference = 'SilentlyContinue'
foreach ($f in @('mag2','dir2')) {
  Write-Output "--- $f ---"
  $p = "C:\Users\ruifa\Desktop\DIMEIA\data\_qi4_$f.log"
  if (Test-Path $p) {
    Get-Content $p | Select-String -Pattern 'Pares:|Modelo em|passo|EXITCODE' |
      Select-Object -ExpandProperty Line
  } else { Write-Output 'ainda nao comecou' }
}
Write-Output "--- processos python ---"
(Get-Process python -ErrorAction SilentlyContinue | Measure-Object).Count
