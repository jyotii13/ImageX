from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from imagex.config import is_image

NAME = "Watermark"
DESCRIPTION = "Add or remove watermarks from images"

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\Arial.ttf",
]

POSITIONS = [
    "Top-Left",
    "Top-Right",
    "Bottom-Left",
    "Bottom-Right",
    "Center",
]

REMOVE_SIZES = ["Small (10%)", "Medium (20%)", "Large (30%)"]


def ask_args(files: list[Path]) -> dict[str, Any]:
    action = questionary.select(
        "Watermark action:",
        choices=["Add watermark", "Remove watermark"],
    ).ask()

    if action == "Add watermark":
        return _ask_add(files)

    return _ask_remove(files)


def _ask_add(files: list[Path]) -> dict[str, Any]:
    wm_type = questionary.select(
        "Watermark type:",
        choices=["Text", "Image (logo)"],
    ).ask()

    position = questionary.select(
        "Position:",
        choices=POSITIONS,
    ).ask()

    opacity_str = questionary.text(
        "Opacity (1-100):",
        default="50",
        validate=lambda v: v.isdigit() and 1 <= int(v) <= 100 or "Enter 1-100",
    ).ask()

    args = {
        "action": "add",
        "type": "text" if wm_type == "Text" else "image",
        "position": position,
        "opacity": max(0, min(255, int(int(opacity_str) * 2.55))),
    }

    if args["type"] == "text":
        text = questionary.text("Text content:", default="©").ask()
        size_str = questionary.text(
            "Font size (px):",
            default="36",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a number",
        ).ask()
        color = questionary.text("Color (name or hex):", default="white").ask()

        args["text"] = text
        args["font_size"] = int(size_str)
        args["color"] = color
    else:
        logo_input = questionary.text("Logo file path:").ask()
        logo_path = Path(logo_input.strip())

        if not logo_path.exists():
            msg = f"Logo file not found: {logo_path}"
            raise FileNotFoundError(msg)
        if not is_image(logo_path):
            msg = f"Not an image file: {logo_path}"
            raise ValueError(msg)

        scale_str = questionary.text(
            "Logo scale (% of image width):",
            default="10",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a number",
        ).ask()

        args["logo_path"] = str(logo_path)
        args["scale"] = int(scale_str)

    return args


def _ask_remove(files: list[Path]) -> dict[str, Any]:
    position = questionary.select(
        "Watermark position:",
        choices=POSITIONS,
    ).ask()

    size_choice = questionary.select(
        "Watermark size:",
        choices=REMOVE_SIZES,
    ).ask()

    size_map = {"Small (10%)": 0.1, "Medium (20%)": 0.2, "Large (30%)": 0.3}

    return {
        "action": "remove",
        "position": position,
        "size_ratio": size_map[size_choice],
    }


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for watermark"
        raise ValueError(msg)

    src = Image.open(file)
    meta = {}
    if exif := src.info.get("exif"):
        meta["exif"] = exif
    if icc := src.info.get("icc_profile"):
        meta["icc_profile"] = icc
    img = src.convert("RGBA")
    action = args["action"]

    if action == "add":
        _run_add(img, args)
    elif action == "remove":
        _run_remove(img, args)
    else:
        msg = f"Unknown action: {action}"
        raise ValueError(msg)

    out = img.convert("RGB") if img.mode == "RGBA" else img
    out.save(str(output_path), **meta)
    return True


def _run_add(img: Image.Image, args: dict[str, Any]):
    wm_type = args["type"]
    position = args["position"]
    opacity = args["opacity"]
    w, h = img.size
    margin = max(20, int(min(w, h) * 0.03))

    if wm_type == "text":
        overlay = _make_text_overlay(w, h, args)
    else:
        overlay = _make_image_overlay(w, h, args)

    if opacity < 255:
        overlay.putalpha(overlay.split()[3].point(lambda a: int(a * opacity / 255)))

    paste_x, paste_y = _calc_position(w, h, overlay.width, overlay.height, position, margin)
    img.paste(overlay, (paste_x, paste_y), overlay)


def _run_remove(img: Image.Image, args: dict[str, Any]):
    position = args["position"]
    ratio = args["size_ratio"]
    w, h = img.size

    rw = max(10, int(w * ratio))
    rh = max(10, int(h * ratio))
    margin = max(5, int(min(w, h) * 0.01))

    rx, ry = _calc_position(w, h, rw, rh, position, margin)

    _fill_region(img, rx, ry, rw, rh)


def _calc_position(
    img_w: int, obj_w: int, img_h: int, obj_h: int, position: str, margin: int
) -> tuple[int, int]:
    positions = {
        "Top-Left": (margin, margin),
        "Top-Right": (img_w - obj_w - margin, margin),
        "Bottom-Left": (margin, img_h - obj_h - margin),
        "Bottom-Right": (img_w - obj_w - margin, img_h - obj_h - margin),
        "Center": ((img_w - obj_w) // 2, (img_h - obj_h) // 2),
    }
    return positions.get(position, (margin, margin))


def _make_text_overlay(img_w: int, img_h: int, args: dict[str, Any]) -> Image.Image:
    text = args["text"]
    font_size = args["font_size"]
    color = args["color"]

    font = None
    for fp in FONT_PATHS:
        try:
            font = ImageFont.truetype(fp, font_size)
            break
        except (OSError, IOError):
            continue

    overlay = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    text_overlay = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_overlay)
    tdraw.text((10 - bbox[0], 10 - bbox[1]), text, fill=color, font=font)

    return text_overlay


def _make_image_overlay(img_w: int, img_h: int, args: dict[str, Any]) -> Image.Image:
    logo = Image.open(args["logo_path"]).convert("RGBA")
    scale = args["scale"] / 100
    new_w = max(10, int(img_w * scale))
    new_h = int(logo.height * (new_w / logo.width))
    return logo.resize((new_w, new_h), Image.LANCZOS)


def _fill_region(img: Image.Image, rx: int, ry: int, rw: int, rh: int):
    samples = []
    border = max(2, int(min(rw, rh) * 0.05))
    left = max(0, rx - border)
    right = min(img.width, rx + rw + border)
    top = max(0, ry - border)
    bottom = min(img.height, ry + rh + border)

    for x in range(left, right):
        for y in (top, bottom - 1):
            if 0 <= y < img.height:
                samples.append(img.getpixel((x, y)))
    for y in range(top, bottom):
        for x in (left, right - 1):
            if 0 <= x < img.width:
                samples.append(img.getpixel((x, y)))

    avg_color = tuple(
        int(sum(c[i] for c in samples) / len(samples)) for i in range(4)
    ) if samples else (128, 128, 128, 255)

    fill = Image.new("RGBA", (rw, rh), avg_color)
    img.paste(fill, (rx, ry))

    region = img.crop((rx, ry, rx + rw, ry + rh))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=max(2, min(rw, rh) // 10)))
    img.paste(blurred, (rx, ry))
