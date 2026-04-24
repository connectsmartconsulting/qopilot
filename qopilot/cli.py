"""Qopilot CLI."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from qopilot import __version__
from qopilot.author import render_markdown as render_author_md
from qopilot.author import run as run_author
from qopilot.core import autodetect_provider
from qopilot.interpret import render_markdown as render_interpret_md
from qopilot.interpret import run as run_interpret

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Qopilot: AI copilot for AI assurance. Works with aigrc.",
)
console = Console()


@app.command("version")
def _version():
    console.print(f"qopilot v{__version__}")


@app.command("author")
def author(
    input: Path = typer.Option(..., "--input", help="Markdown file describing the client system"),
    out: Path = typer.Option(None, "--out", help="Output path for recommendation markdown"),
    offline: bool = typer.Option(False, "--offline", help="Use deterministic offline renderer"),
):
    """Recommend aigrc checks for a given client system."""
    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=2)

    description = input.read_text()
    provider = autodetect_provider(offline=offline)
    console.print(f"[dim]Provider: {provider.name}[/dim]")

    result = run_author(description, provider)
    md = render_author_md(result)

    out_path = out or input.with_suffix(".qopilot-recs.md")
    out_path.write_text(md)
    console.print(f"[green]Recommendations written to:[/green] {out_path}")

    # Also emit a brief console summary
    console.print("")
    console.print(f"[bold]Recommended checks ({len(result.recommended_checks)}):[/bold]")
    for rec in result.recommended_checks:
        status = "LIVE" if rec.aigrc_status == "live" else "PLANNED"
        console.print(f"  - {rec.check_id}  [{status}]  priority: {rec.priority}")


@app.command("interpret")
def interpret(
    report: Path = typer.Option(..., "--report", help="aigrc JSON report path"),
    out: Path = typer.Option(None, "--out", help="Output path for narrative markdown"),
    offline: bool = typer.Option(False, "--offline", help="Use deterministic offline renderer"),
):
    """Translate an aigrc JSON report into a business-language audit narrative."""
    if not report.exists():
        console.print(f"[red]Report not found: {report}[/red]")
        raise typer.Exit(code=2)

    try:
        data = json.loads(report.read_text())
    except Exception as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(code=2)

    provider = autodetect_provider(offline=offline)
    console.print(f"[dim]Provider: {provider.name}[/dim]")

    result = run_interpret(data, provider)
    md = render_interpret_md(result, data)

    out_path = out or report.with_suffix(".qopilot-narrative.md")
    out_path.write_text(md)
    console.print(f"[green]Narrative written to:[/green] {out_path}")

    # Brief console summary
    console.print("")
    console.print(f"[bold]Executive summary:[/bold] {result.executive_summary[:200]}...")
    console.print(f"[bold]Findings:[/bold] {len(result.findings)}")
    console.print(f"[bold]Next engagement:[/bold] {result.next_engagement[:120]}...")


if __name__ == "__main__":
    app()
