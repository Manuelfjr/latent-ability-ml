"""Gera o QR code do site do tutorial (site/assets/ita/qr-ita.svg).

Precisa do pacote qrcode (pip install qrcode). Rode a partir da raiz do repositório:

    python notebooks/ita/make_qr.py
"""

from pathlib import Path

import qrcode
import qrcode.image.svg

URL = "https://manuelfjr.github.io/latent-ability-ml/ita/"
OUT = Path(__file__).resolve().parents[2] / "site" / "assets" / "ita" / "qr-ita.svg"

# Módulos em Chumbo, sem fundo e sem margem: o cartão do site dá o fundo claro e a zona de silêncio.
image = qrcode.make(URL, image_factory=qrcode.image.svg.SvgPathImage, border=0,
                    error_correction=qrcode.constants.ERROR_CORRECT_M)
svg = image.to_string(encoding="unicode").replace('fill="#000000"', 'fill="#1C2127"')
OUT.write_text(svg, encoding="utf-8")
print(OUT, len(svg), "bytes")
