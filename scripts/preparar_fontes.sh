#!/usr/bin/env bash
# Gera os subconjuntos latinos do IBM Plex que o painel serve em web/assets/fonts/.
#
# Porque e que as letras sao nossas e nao do Google Fonts: a folha do Google e render-blocking
# e vive noutro dominio (DNS + TLS a dois anfitrioes antes do primeiro pixel); nao queremos que
# o pedido do visitante saia para fora; e as figuras da tese sao capturadas num contentor sem
# saida para o fonts.googleapis.com, onde a folha remota daria a letra de recurso — uma figura
# com a letra errada passa despercebida ate estar impressa.
#
# Origem: pacotes oficiais @ibm/plex-sans e @ibm/plex-mono, licenca SIL OFL 1.1.
# Resultado: 6 ficheiros, ~116 KB no total (os completos pesam 372 KB).
set -euo pipefail

DESTINO="$(cd "$(dirname "$0")/.." && pwd)/web/assets/fonts"
TRABALHO="$(mktemp -d)"
trap 'rm -rf "$TRABALHO"' EXIT

# O mesmo intervalo que o Google Fonts serve como subconjunto "latin", mais os sinais que a
# pagina usa e que nao estao em latin-1: menos unicode (U+2212), setas, travessoes e aspas.
UNICODES='U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'

cd "$TRABALHO"
npm pack @ibm/plex-sans@1.1.0 @ibm/plex-mono@2.5.0 >/dev/null
for t in *.tgz; do tar xzf "$t"; mv package "pkg-${t%.tgz}"; done

mkdir -p "$DESTINO"
subconjunto() {  # $1 = ficheiro de origem
  local nome; nome="$(basename "$1")"
  python3 -m fontTools.subset "$1" --output-file="$DESTINO/$nome" --flavor=woff2 \
    --layout-features='kern,liga,calt,tnum' --unicodes="$UNICODES"
  printf '  %-34s %6s bytes\n' "$nome" "$(stat -c%s "$DESTINO/$nome")"
}

echo "A gerar em $DESTINO:"
for n in Regular Medium SemiBold Bold; do
  subconjunto pkg-ibm-plex-sans-1.1.0/fonts/complete/woff2/IBMPlexSans-$n.woff2
done
for n in Text SemiBold; do
  subconjunto pkg-ibm-plex-mono-2.5.0/fonts/complete/woff2/IBMPlexMono-$n.woff2
done
cp pkg-ibm-plex-sans-1.1.0/fonts/complete/woff2/license.txt "$DESTINO/LICENSE-OFL.txt"
echo "Feito. A licenca SIL OFL 1.1 fica em $DESTINO/LICENSE-OFL.txt"
