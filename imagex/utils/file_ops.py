import shutil
from datetime import datetime
from pathlib import Path

from imagex.config import BACKUP_DIR_NAME, is_image


def find_images(directory: Path) -> list[Path]:
    files = []
    for f in sorted(directory.iterdir()):
        if f.is_file() and is_image(f):
            files.append(f)
    return files


def backup_file(file: Path) -> Path | None:
    backup_root = file.parent / BACKUP_DIR_NAME
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = backup_root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / file.name
    shutil.copy2(file, dest)
    return dest


def get_output_path(
    file: Path,
    mode: str,
    output_dir: Path | None = None,
) -> Path:
    if mode == "overwrite":
        return file
    elif mode == "output":
        return (file.parent / "output" / file.name).resolve()
    elif mode == "custom":
        if output_dir is None:
            msg = "output_dir required for custom mode"
            raise ValueError(msg)
        return output_dir / file.name
    msg = f"Unknown output mode: {mode}"
    raise ValueError(msg)
