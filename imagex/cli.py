import sys
from pathlib import Path

import questionary
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from imagex import __version__
from imagex.features import get_features
from imagex.utils.file_ops import find_images
from imagex.utils.progress import process_files

console = Console()


def show_banner():
    text = (
        f"[bold cyan]ImageX[/bold cyan] [white]v{__version__}[/white]\n"
        "[dim]Image processing, right in ur CLI[/dim]"
    )
    console.print(Panel(text, width=50))


def select_features() -> list[str] | None:
    features = get_features()

    if not features:
        console.print("[red]No features found! Add a .py file to imagex/features/.[/red]")
        return None

    choices = []
    for name, info in features.items():
        label = f"{info['name']:<30} {info['description']}"
        choices.append(questionary.Choice(title=label, value=name))

    choices.append(questionary.Choice(title="[Done] Quit", value="__quit__"))

    selected = questionary.checkbox(
        "What do you want to do? (↑↓ to move, Space to toggle, Enter to confirm)",
        choices=choices,
    ).ask()

    if not selected:
        return None

    if "__quit__" in selected:
        return None

    return selected


def ask_output_mode() -> tuple[str, Path | None]:
    mode = questionary.select(
        "Where should the processed images go?",
        choices=[
            questionary.Choice(
                title="Overwrite originals (backup created in .imagex_backup/)",
                value="overwrite",
            ),
            questionary.Choice(
                title="Save to ./output/ folder",
                value="output",
            ),
            questionary.Choice(
                title="Save to custom folder",
                value="custom",
            ),
        ],
    ).ask()

    output_dir = None
    if mode == "custom":
        custom = questionary.text(
            "Enter output folder path:",
            validate=lambda p: len(p.strip()) > 0 or "Path cannot be empty",
        ).ask()
        output_dir = Path(custom.strip())

    return mode, output_dir


def main():
    try:
        show_banner()

        selected = select_features()
        if selected is None:
            console.print("[yellow]No feature selected. Exiting.[/yellow]")
            return

        files = find_images(Path.cwd())
        if not files:
            console.print("[red]No image files found in current directory.[/red]")
            console.print("[dim]Supported: .jpg .jpeg .png .webp .tiff .tif .bmp .gif .ico[/dim]")
            return

        console.print(f"[green]Found {len(files)} image(s) to process[/green]")

        mode, output_dir = ask_output_mode()

        features = get_features()
        for feature_name in selected:
            info = features[feature_name]
            console.print(f"\n[bold]→ {info['name']}[/bold]")
            process_files(
                files=files,
                process_func=info["run"],
                feature_name=info["name"],
                output_mode=mode,
                output_dir=output_dir,
            )

        console.print("\n[bold green]✓ All done![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Exiting.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)
