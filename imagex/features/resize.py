from pathlib import Path
from typing import Any

import questionary
from PIL import Image

NAME = "Resize"
DESCRIPTION = "Scale images (dimensions, percentage, or fit within bounds)"

METHODS = {
    "Percentage": "percentage",
    "Exact dimensions": "exact",
    "Fit within (maintain ratio)": "fit",
}


def ask_args(files: list[Path]) -> dict[str, Any]:
    method_label = questionary.select(
        "Resize method:",
        choices=list(METHODS.keys()),
    ).ask()

    method = METHODS[method_label]

    if method == "percentage":
        pct = questionary.text(
            "Percentage of original (e.g. 50 for half size):",
            default="50",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
        ).ask()
        return {"method": "percentage", "value": int(pct)}

    if method == "exact":
        w = questionary.text(
            "Width (px):",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
        ).ask()
        h = questionary.text(
            "Height (px):",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
        ).ask()
        return {"method": "exact", "width": int(w), "height": int(h)}

    if method == "fit":
        mw = questionary.text(
            "Max width (px):",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
        ).ask()
        mh = questionary.text(
            "Max height (px):",
            validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
        ).ask()
        return {"method": "fit", "max_width": int(mw), "max_height": int(mh)}

    msg = f"Unknown method: {method}"
    raise ValueError(msg)


def run(file: Path, output_path: Path, args: dict[str, Any] | None = None) -> bool:
    if args is None:
        msg = "args required for resize"
        raise ValueError(msg)

    img = Image.open(file)
    method = args["method"]

    if method == "percentage":
        pct = args["value"] / 100
        new_w = max(1, int(img.width * pct))
        new_h = max(1, int(img.height * pct))
    elif method == "exact":
        new_w = args["width"]
        new_h = args["height"]
    elif method == "fit":
        new_w, new_h = _fit_within(img.width, img.height, args["max_width"], args["max_height"])
    else:
        msg = f"Unknown method: {method}"
        raise ValueError(msg)

    resized = img.resize((new_w, new_h), Image.LANCZOS)
    resized.save(str(output_path), format=img.format or "JPEG")

    return True


def _fit_within(orig_w: int, orig_h: int, max_w: int, max_h: int) -> tuple[int, int]:
    ratio = min(max_w / orig_w, max_h / orig_h)
    if ratio >= 1:
        return orig_w, orig_h
    return max(1, int(orig_w * ratio)), max(1, int(orig_h * ratio))
