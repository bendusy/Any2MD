from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn

from .converter import Any2MDConverter
from .unzipper import Unzipper

app = typer.Typer(name="any2md", help="批量转换文档为 Markdown")
console = Console()


def _run_gui() -> None:
    try:
        from .gui import run_gui

        run_gui()
    except ImportError as e:
        console.print(
            "[red]GUI 依赖未安装[/red]：请使用 `pip install 'any2md[gui]'` 后再运行 GUI。\n"
            f"[dim]{e}[/dim]"
        )
        raise typer.Exit(code=1)


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="输入文件/文件夹/ZIP路径"),
    output: Path = typer.Option("./output", "-o", "--output", help="输出目录"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="递归处理子目录"),
):
    converter = Any2MDConverter()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        if input_path.suffix.lower() == ".zip":
            task = progress.add_task("解压 ZIP 文件...", total=1)
            with Unzipper() as unzipper:
                extracted = unzipper.extract_recursive(input_path)
                progress.update(task, completed=1)

                files = [
                    f
                    for f in extracted.rglob("*")
                    if f.is_file() and converter.can_convert(f)
                ]
                convert_task = progress.add_task("转换文件...", total=len(files))
                results = []
                for file_path in files:
                    rel_path = file_path.relative_to(extracted)
                    file_output_dir = output / rel_path.parent
                    result = converter.convert_file(file_path, file_output_dir)
                    results.append(result)
                    progress.update(convert_task, advance=1)
        elif input_path.is_dir():
            pattern = "**/*" if recursive else "*"
            files = [
                f
                for f in input_path.glob(pattern)
                if f.is_file() and converter.can_convert(f)
            ]
            task = progress.add_task("转换文件...", total=len(files))
            results = []
            for file_path in files:
                rel_path = file_path.relative_to(input_path)
                file_output_dir = output / rel_path.parent
                result = converter.convert_file(file_path, file_output_dir)
                results.append(result)
                progress.update(task, advance=1)
        else:
            task = progress.add_task("转换文件...", total=1)
            results = [converter.convert_file(input_path, output)]
            progress.update(task, completed=1)

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
    _run_gui()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        # For non-technical users: if GUI deps are installed, launch GUI by default.
        # Otherwise show CLI help (so `any2md` remains usable without PyQt6).
        import importlib.util

        if importlib.util.find_spec("PyQt6") is not None:
            _run_gui()
            return

        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
