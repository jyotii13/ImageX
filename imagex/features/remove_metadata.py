from pathlib import Path
from typing import Any, Optional

from PIL import Image

NAME = "Remove Metadata"
DESCRIPTION = "Strip EXIF/XMP/IPTC data from images"


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    img = Image.open(file)
    fmt = img.format

    if fmt == "JPEG":
        _clean_jpeg(img, output_path)
    elif fmt == "PNG":
        _clean_png(img, output_path)
    elif fmt == "WEBP":
        _clean_webp(img, output_path)
    elif fmt == "TIFF" or fmt == "TIF":
        _clean_tiff(img, output_path)
    else:
        _save_clean(img, output_path, fmt)

    return True


def _clean_jpeg(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="JPEG", exif=b"")


def _clean_png(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="PNG")


def _clean_webp(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="WEBP")


def _clean_tiff(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="TIFF")


def _save_clean(img: Image.Image, output_path: Path, fmt: str):
    params = {}
    if fmt == "GIF":
        params["save_all"] = True
    img.save(str(output_path), format=fmt, **params)
