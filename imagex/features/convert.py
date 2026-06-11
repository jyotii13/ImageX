from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image

NAME = "Convert Format"
DESCRIPTION = "Convert images between formats"

OUTPUT_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "TIFF": ".tiff",
    "BMP": ".bmp",
    "GIF": ".gif",
}

HEIF_AVAILABLE = False
try:
    import pillow_heif  # noqa: F401

    pillow_heif.register_heif_opener()
    HEIF_AVAILABLE = True
    OUTPUT_FORMATS["HEIC"] = ".heic"
except ImportError:
    pass


def ask_args(files: list[Path]) -> dict[str, Any]:
    choices = list(OUTPUT_FORMATS.keys())
    target = questionary.select(
        "Convert to which format?",
        choices=choices,
    ).ask()

    return {
        "target_format": target,
        "target_ext": OUTPUT_FORMATS[target],
    }


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for convert (target_format)"
        raise ValueError(msg)

    target_fmt = args["target_format"]

    img = Image.open(file)
    actual_output = output_path.with_suffix(args["target_ext"])

    if target_fmt == "JPEG":
        _save_as_jpeg(img, actual_output)
    elif target_fmt == "PNG":
        _save_as_png(img, actual_output)
    elif target_fmt == "WEBP":
        _save_as_webp(img, actual_output)
    elif target_fmt == "TIFF":
        img.save(str(actual_output), format="TIFF")
    elif target_fmt == "BMP":
        img.save(str(actual_output), format="BMP")
    elif target_fmt == "GIF":
        img.save(str(actual_output), format="GIF")
    elif target_fmt == "HEIC":
        _save_as_heic(img, actual_output)

    return True


def _save_as_jpeg(img: Image.Image, output_path: Path):
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.save(str(output_path), format="JPEG")


def _save_as_png(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="PNG")


def _save_as_webp(img: Image.Image, output_path: Path):
    img.save(str(output_path), format="WEBP")


def _save_as_heic(img: Image.Image, output_path: Path):
    if not HEIF_AVAILABLE:
        msg = (
            "HEIC support requires pillow-heif.\n"
            "Install with: pip install pillow-heif"
        )
        raise ImportError(msg)
    img.save(str(output_path), format="HEIF")
