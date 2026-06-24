from pathlib import Path
from typing import Any, Optional

from PIL import Image, ImageOps

NAME = "Invert Colors"
DESCRIPTION = "Invert image colors (negative effect)"


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    img = Image.open(file)
    kw = {"format": img.format or "JPEG"}
    if exif := img.info.get("exif"):
        kw["exif"] = exif
    if icc := img.info.get("icc_profile"):
        kw["icc_profile"] = icc

    if img.mode == "RGBA":
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        inverted = ImageOps.invert(rgb)
        r2, g2, b2 = inverted.split()
        img = Image.merge("RGBA", (r2, g2, b2, a))
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = ImageOps.invert(img)

    img.save(str(output_path), **kw)
    return True
