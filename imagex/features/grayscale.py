from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image

NAME = "Grayscale / B&W"
DESCRIPTION = "Convert images to grayscale or true black & white"

MODES = {
    "Grayscale (luminosity)": "grayscale",
    "True Black & White (threshold)": "bw",
}


def ask_args(files: list[Path]) -> dict[str, Any]:
    mode_label = questionary.select(
        "Mode:",
        choices=list(MODES.keys()),
    ).ask()

    args = {"mode": MODES[mode_label]}

    if MODES[mode_label] == "bw":
        threshold = questionary.text(
            "Threshold (0-255, lower = more black):",
            default="128",
            validate=lambda v: v.isdigit() and 0 <= int(v) <= 255 or "Enter 0-255",
        ).ask()
        args["threshold"] = int(threshold)

    return args


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for grayscale"
        raise ValueError(msg)

    img = Image.open(file)
    kw = {"format": img.format or "JPEG"}
    if exif := img.info.get("exif"):
        kw["exif"] = exif
    if icc := img.info.get("icc_profile"):
        kw["icc_profile"] = icc

    gray = img.convert("L")

    if args["mode"] == "grayscale":
        gray.save(str(output_path), **kw)
    else:
        threshold = args.get("threshold", 128)
        bw = gray.point(lambda p: 255 if p > threshold else 0, mode="1")
        bw = bw.convert("L")
        bw.save(str(output_path), **kw)

    return True
