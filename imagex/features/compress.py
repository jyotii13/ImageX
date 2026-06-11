from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image
from rich.console import Console

NAME = "Compress / Optimize"
DESCRIPTION = "Reduce file size (quality slider, optimization)"

console = Console()


def ask_args(files: list[Path]) -> dict[str, Any]:
    quality = questionary.text(
        "Quality (1-100):",
        default="80",
        validate=lambda v: v.isdigit() and 1 <= int(v) <= 100 or "Enter a number 1-100",
    ).ask()

    return {"quality": max(1, min(100, int(quality)))}


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for compress (quality)"
        raise ValueError(msg)

    quality = args.get("quality", 80)
    img = Image.open(file)
    fmt = img.format
    original_size = file.stat().st_size

    if fmt == "JPEG":
        _compress_jpeg(img, output_path, quality)
    elif fmt == "PNG":
        _compress_png(img, output_path, quality)
    elif fmt == "WEBP":
        _compress_webp(img, output_path, quality)
    else:
        _compress_other(img, output_path, fmt, quality)

    new_size = output_path.stat().st_size
    saved = original_size - new_size
    pct = (1 - new_size / original_size) * 100 if original_size else 0
    console.print(
        f"  [dim]{file.name}: {_fmt_size(original_size)} → {_fmt_size(new_size)} "
        f"({'−' if saved >= 0 else '+'}{abs(pct):.0f}%)[/dim]"
    )

    return True


def _compress_jpeg(img: Image.Image, output_path: Path, quality: int):
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.save(str(output_path), format="JPEG", quality=quality, optimize=True)


def _compress_png(img: Image.Image, output_path: Path, quality: int):
    if quality < 50:
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        colors = max(quality * 2, 16)
        img = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        img.save(str(output_path), format="PNG", optimize=True)
    else:
        img.save(str(output_path), format="PNG", optimize=True)


def _compress_webp(img: Image.Image, output_path: Path, quality: int):
    img.save(str(output_path), format="WEBP", quality=quality)


def _compress_other(img: Image.Image, output_path: Path, fmt: str, quality: int):
    params = {"format": fmt}
    if fmt == "GIF":
        params["save_all"] = True
    img.save(str(output_path), **params)


def _fmt_size(size: int) -> str:
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
