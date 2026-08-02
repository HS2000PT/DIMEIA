"""Recursos de marca das empresas (logótipos) para a interface.

Separado do resto do sistema de propósito: nada aqui influencia deteção, recuperação
ou avaliação. É uma camada de APRESENTAÇÃO, e se falhar por inteiro a interface
continua a funcionar com as iniciais do ticker.
"""

from investigator.branding.logos import (
    LogoAsset,
    cached_logo,
    data_uri,
    fetch_logo,
    parse_branding,
)

__all__ = [
    "LogoAsset",
    "cached_logo",
    "data_uri",
    "fetch_logo",
    "parse_branding",
]
