"""Configuração global dos testes: rede OFF para o retrieval semântico (determinismo).

Os testes NUNCA descarregam o modelo ONNX (~23 MB): numa máquina com a cache local
(`models/onnx/`) o caminho semântico é exercitado a sério; sem ela (CI leve) o produto
degrada para word-overlap — ambos os caminhos são válidos e ficam testados.
"""

import os

os.environ.setdefault("INVESTIGATOR_OFFLINE", "1")
