"""Lista os processos python, com tempo de CPU, para ver se o treino esta mesmo a trabalhar.

Um processo vivo mas com o tempo de CPU parado esta bloqueado, nao a treinar. Chamar duas vezes
com alguns segundos de intervalo e comparar.
"""
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

CONSULTA = (
    "Get-Process python -ErrorAction SilentlyContinue | "
    "Select-Object Id,CPU,WorkingSet64,StartTime | Format-Table -AutoSize | Out-String -Width 200"
)


def instantanea():
    r = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", CONSULTA],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.stdout.strip() or "(nenhum processo python)"


def main():
    espera = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print("--- agora ---")
    print(instantanea())
    if espera:
        time.sleep(espera)
        print(f"\n--- {espera} s depois (o CPU deve ter subido se estiver a treinar) ---")
        print(instantanea())


if __name__ == "__main__":
    main()
