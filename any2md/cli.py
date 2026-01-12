from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .converter import Any2MDConverter
from .unzipper import Unzipper

app = typer.Typer(name="any2md", help="批量转换文档为 Markdown")
console = Console()


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="输入文件/文件夹/ZIP路径"),
    output: Path = typer.Option("./output", "-o", "--output", help="输出目录"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="递归处理子目录"),
):
    converter = Any2MDConverter()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if input_path.suffix.lower() == ".zip":
            progress.add_task("解压 ZIP 文件...", total=None)
            with Unzipper() as unzipper:
                extracted = unzipper.extract_recursive(input_path)
                results = converter.convert_directory(extracted, output, recursive)
        elif input_path.is_dir():
            progress.add_task("转换文件夹...", total=None)
            results = converter.convert_directory(input_path, output, recursive)
        else:
            progress.add_task("转换文件...", total=None)
            results = [converter.convert_file(input_path, output)]

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    console.print(f"\n[green]✓ 成功: {success_count}[/green]")
    if fail_count:
        console.print(f"[red]✗ 失败: {fail_count}[/red]")
        for r in results:
            if not r.success:
                console.print(f"  [dim]{r.input_path}[/dim]: {r.error}")


@app.command()
def gui():
    from .gui import run_gui

    run_gui()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        from .gui import run_gui

        run_gui()


if __name__ == "__main__":
    app()
