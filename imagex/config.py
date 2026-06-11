from pathlib import Path

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp",
    ".tiff", ".tif", ".bmp", ".gif", ".ico",
}

BACKUP_DIR_NAME = ".imagex_backup"
DEFAULT_OUTPUT_DIR_NAME = "output"


def is_image(file: Path) -> bool:
    return file.suffix.lower() in IMAGE_EXTENSIONS
