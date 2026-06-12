# Contributing to ImageX

## Quick Start

```bash
git clone https://github.com/kushal1o1/ImageX
cd ImageX
pip install -e ".[dev]"
```

## How Features Work

Every `.py` file inside `imagex/features/` is **auto-discovered** at runtime.

Each feature module exports these variables/functions:

| Attribute | Required | Purpose |
|---|---|---|
| `NAME` (str) | Yes | Display name in the menu |
| `DESCRIPTION` (str) | Yes | Shown next to the name |
| `run(file, output_path, args)` | Yes | The actual image processing logic |
| `ask_args(files)` | No | Prompt user for parameters |
| `NEEDS_OUTPUT_MODE` (bool) | No | Defaults to `True`; set to `False` for in-place features like rename |

## Adding a New Feature

Create a new file in `imagex/features/`, e.g. `blur.py`:

```python
from pathlib import Path
from typing import Any, Optional

import questionary
from PIL import Image, ImageFilter

NAME = "Blur"
DESCRIPTION = "Apply Gaussian blur to images"


def ask_args(files: list[Path]) -> dict[str, Any]:
    radius = questionary.text(
        "Blur radius (px):",
        default="5",
        validate=lambda v: v.isdigit() and int(v) > 0 or "Enter a positive number",
    ).ask()
    return {"radius": int(radius)}


def run(file: Path, output_path: Path, args: Optional[dict[str, Any]] = None) -> bool:
    if args is None:
        msg = "args required for blur"
        raise ValueError(msg)

    img = Image.open(file)
    img = img.filter(ImageFilter.GaussianBlur(radius=args["radius"]))
    img.save(str(output_path))
    return True
```

That's it. Restart `imagex` and your feature appears in the menu.

### Guidelines

- Keep features **pure** — let `run()` read from and write to the given paths.
- Use `questionary` for CLI prompts (text, select, checkbox, confirm).
- Use Pillow (`PIL`) for image ops. No heavy frameworks like OpenCV.
- Return `True` on success, raise on failure (error is caught by the CLI).
- If a feature doesn't need output mode (rename, etc.), add `NEEDS_OUTPUT_MODE = False`.

## Testing

```bash
pytest tests/ -v
```

Add tests in `tests/test_<your_feature>.py` following the existing patterns.

## Code Style

```bash
ruff check .
```

The project uses ruff with default rules (E, F, W, I). Keep it clean.

## Operations Docs

If your feature is user-facing, add a section to `OPERATIONS.md` describing how it works.
