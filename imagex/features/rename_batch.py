import shutil
from pathlib import Path
from typing import Any

import questionary
from rich.console import Console

NAME = "Rename Batch"
DESCRIPTION = "Rename multiple files with a pattern"
NEEDS_OUTPUT_MODE = False

console = Console()


def ask_args(files: list[Path]) -> dict[str, Any]:
    sorted_files = sorted(files)

    pattern = questionary.text(
        "Pattern (use %n for number, %o for original name):",
        default="img_%n",
    ).ask()

    start_str = questionary.text("Starting number:", default="1").ask()

    digits_str = questionary.text("Digit padding (e.g. 3 = 001):", default="3").ask()

    start = int(start_str)
    digits = int(digits_str)

    rename_map = {}
    for i, f in enumerate(sorted_files):
        new_stem = pattern.replace("%n", str(start + i).zfill(digits))
        new_stem = new_stem.replace("%o", f.stem)
        new_name = new_stem + f.suffix
        rename_map[str(f)] = new_name

    console.print("\n[bold]Preview:[/bold]")
    for f in sorted_files:
        console.print(f"  {f.name}  →  [green]{rename_map[str(f)]}[/green]")

    confirm = questionary.confirm("Proceed with rename?").ask()
    if not confirm:
        msg = "Cancelled by user"
        raise RuntimeError(msg)

    return {
        "rename_map": rename_map,
        "sorted_files": [str(f) for f in sorted_files],
    }


def run(file: Path, output_path: Path, args: dict[str, Any] | None = None) -> bool:
    if args is None:
        msg = "args required for rename (rename_map)"
        raise ValueError(msg)

    new_name = args["rename_map"][str(file)]
    new_path = file.parent / new_name

    if file.name != new_name:
        shutil.move(str(file), str(new_path))
        console.print(f"  [dim]{file.name} → {new_name}[/dim]")

    return True
