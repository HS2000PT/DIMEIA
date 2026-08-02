"""Logótipos das empresas da watchlist, obtidos uma vez e guardados no repositório.

**Porque é que isto existe.** A interface pede-se a alguém que reconhece a Apple pelo
símbolo antes de ler "AAPL". Um logótipo é reconhecimento em ~50 ms; um ticker de quatro
letras obriga a ler. Numa lista de dez nomes essa diferença é a diferença entre varrer e
soletrar.

**Desenho, e porquê assim.**

1. **Obtidos em tempo de construção, não em tempo de execução.** `scripts/fetch_logos.py`
   corre uma vez, escreve para `app/assets/logos/` e esses ficheiros são versionados. A app
   implantada nunca chama uma API para desenhar um ecrã. Consequências: sem limite de
   ritmo, sem latência de rede no primeiro pintar, e a app corre sem a chave do Polygon.
2. **Embebidos como `data:` URI.** O ficheiro é lido do disco e embebido no HTML. O
   navegador não faz um pedido por logótipo, o que também significa que nada aqui expõe o
   utilizador a um pedido a terceiros — coerente com a posição de privacidade do Cap. 6.
3. **Degrada para as iniciais.** Sem ficheiro, `cached_logo` devolve `None` e a interface
   desenha um quadrado com as duas primeiras letras do ticker. Nunca há um espaço vazio
   nem um ícone partido.

**Proveniência e uso.** A fonte é o campo `branding` da Polygon.io (plano gratuito, chave
já em uso no projeto para preços). São marcas registadas das próprias empresas, usadas aqui
para **identificar** a empresa a que os dados dizem respeito — uso nominativo, num trabalho
académico não comercial. Não há afiliação nem apoio implícito, e é isso que a legenda da
interface diz.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Onde os ficheiros vivem. Versionado: são ~10 KB cada e a app implantada precisa deles.
LOGO_DIR = Path(__file__).resolve().parents[2] / "app" / "assets" / "logos"

# O Polygon devolve dois: `logo_url` (horizontal, com o nome) e `icon_url` (quadrado, só o
# símbolo). Num alinhamento de lista o quadrado é o certo — largura constante, e a coluna
# não fica serrilhada porque um nome é mais comprido do que outro.
_PREFERRED_KIND = "icon_url"

_EXT_BY_MAGIC = (
    (b"<svg", ".svg"),
    (b"<?xml", ".svg"),
    (b"\x89PNG", ".png"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"GIF8", ".gif"),
)

# WebP não se identifica pelos primeiros bytes: são `RIFF`, partilhados com WAV e AVI, e o
# que distingue está no oitavo byte. Falta disto fez a Apple parecer uma empresa sem
# logótipo — o ficheiro chegou inteiro e foi descartado como formato desconhecido.
_WEBP_HEAD, _WEBP_TAG = b"RIFF", b"WEBP"


@dataclass(frozen=True)
class LogoAsset:
    """Um logótipo já em bytes, com a extensão que lhe corresponde."""

    ticker: str
    data: bytes
    suffix: str

    @property
    def path(self) -> Path:
        return LOGO_DIR / f"{self.ticker.upper()}{self.suffix}"


def _suffix_for(raw: bytes) -> str:
    """Extensão deduzida do conteúdo, não do URL.

    Deliberado: o URL do Polygon não tem extensão, e confiar no `Content-Type` de um
    terceiro é confiar num campo que ninguém valida. Os bytes iniciais de um ficheiro de
    imagem são um formato, e um formato não mente.
    """
    if raw[:4] == _WEBP_HEAD and raw[8:12] == _WEBP_TAG:
        return ".webp"
    head = raw[:8].lstrip()
    for magic, ext in _EXT_BY_MAGIC:
        if head.startswith(magic):
            return ext
    return ".bin"


def parse_branding(payload: dict, kind: str = _PREFERRED_KIND) -> str | None:
    """URL do logótipo a partir da resposta de detalhes de um ticker.

    Puro e testável sem rede, como o resto dos parsers do projeto (a separação
    parsing/HTTP é a convenção em `news_fetcher`). Cai para o outro tipo se o preferido
    não existir — algumas empresas têm só um dos dois.
    """
    branding = (payload or {}).get("results", {}).get("branding") or {}
    url = branding.get(kind) or branding.get(
        "logo_url" if kind == "icon_url" else "icon_url"
    )
    return url or None


def _get(url: str, timeout: int, retries: int, pause: float) -> bytes | None:
    """GET com recuo em 429.

    O plano gratuito do Polygon permite **5 pedidos por minuto**, e cada logótipo custa
    dois (detalhes + imagem). Sem espera, dez tickers batem no limite ao terceiro e o
    resto volta vazio — o que, com um caminho que falha em silêncio, lê-se exactamente
    como "estas empresas não têm logótipo". Foi o que aconteceu à primeira corrida.
    """
    for tentativa in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and tentativa < retries:
                time.sleep(pause * (tentativa + 1))
                continue
            return None
        except (urllib.error.URLError, OSError):
            return None
    return None


def fetch_logo(
    ticker: str,
    api_key: str,
    timeout: int = 20,
    retries: int = 3,
    pause: float = 15.0,
) -> LogoAsset | None:
    """Descarrega o logótipo de um ticker. Devolve `None` em vez de levantar.

    Falhar aqui não é um erro do sistema: é um ícone que não aparece. Levantar obrigaria
    todos os chamadores a apanhar, e o único tratamento sensato seria continuar.
    """
    ticker = ticker.upper()
    detail = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={api_key}"
    body = _get(detail, timeout, retries, pause)
    if body is None:
        return None
    try:
        payload = json.loads(body)
    except (ValueError, json.JSONDecodeError):
        return None

    url = parse_branding(payload)
    if not url:
        return None

    # O Polygon serve as imagens atrás da mesma autenticação dos dados.
    sep = "&" if "?" in url else "?"
    raw = _get(f"{url}{sep}apiKey={api_key}", timeout, retries, pause)
    if not raw:
        return None
    return LogoAsset(ticker=ticker, data=raw, suffix=_suffix_for(raw))


def data_uri(raw: bytes, suffix: str) -> str:
    """`data:` URI a partir de bytes, para embeber directamente no HTML."""
    mime = mimetypes.types_map.get(suffix, "application/octet-stream")
    # Nenhum dos dois está garantido na tabela do `mimetypes` em todas as plataformas.
    mime = {".svg": "image/svg+xml", ".webp": "image/webp"}.get(suffix, mime)
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def cached_logo(ticker: str, directory: Path | None = None) -> str | None:
    """`data:` URI do logótipo em cache, ou `None` se não houver ficheiro.

    Este é o único ponto que a interface chama. Nunca toca na rede.
    """
    directory = directory or LOGO_DIR
    ticker = ticker.upper()
    for candidate in sorted(directory.glob(f"{ticker}.*")):
        if candidate.suffix == ".bin":
            continue
        try:
            return data_uri(candidate.read_bytes(), candidate.suffix)
        except OSError:
            return None
    return None
