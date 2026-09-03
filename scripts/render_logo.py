"""Compatibilidade: regenera todo o sistema de marca e os PNG do LaTeX.

O gerador deixou de conhecer apenas três imagens. A fonte de verdade é agora
``scripts/build_brand_assets.py``, que produz as cinco peças, as três variantes,
os PNG de 512 px e os três nomes legados usados pelos materiais antigos.
"""

from build_brand_assets import main

if __name__ == "__main__":
    raise SystemExit(main())
