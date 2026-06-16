from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image

NAME = "Rotate"
DESCRIPTION = "Rotate images 90° Left, 90° Right, or 180°"

OPTIONS = {
    "Right (90° CW)": Image.ROTATE_270,
    "Left (90° CCW)": Image.ROTATE_90,
    "Upside Down (180°)": Image.ROTATE_180,
}


def ask_args(files: list[Path]) -> dict[str, Any]:
    direction = questionary.select(
        "Rotate direction:",
        choices=list(OPTIONS.keys()),
    ).ask()

    return {"method": OPTIONS[direction]}


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for rotate"
        raise ValueError(msg)

    img = Image.open(file)
    rotated = img.transpose(args["method"])
    kw = {"format": img.format or "JPEG"}
    if exif := img.info.get("exif"):
        kw["exif"] = exif
    if icc := img.info.get("icc_profile"):
        kw["icc_profile"] = icc
    rotated.save(str(output_path), **kw)
    return True
