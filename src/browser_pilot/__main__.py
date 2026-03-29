"""CLI entry point for BrowserPilot."""

import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from browser_pilot.config import get_settings
from browser_pilot.logging import configure_logging

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """BrowserPilot — Autonomous browser agent powered by local AI."""
    settings = get_settings()
    configure_logging(settings.log_level)


@cli.command()
@click.argument("instruction")
@click.option(
    "--provider",
    type=click.Choice(["gemini", "openrouter"]),
    default="gemini",
    help="LLM provider to use",
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode",
)
def run(
    instruction: str,
    provider: str,
    headless: bool,
) -> None:
    """Execute a browser task from a natural language instruction."""
    console.print(
        Panel(
            f"[bold cyan]Task:[/] {instruction}\n"
            f"[bold cyan]Provider:[/] {provider}\n"
            f"[bold cyan]Headless:[/] {headless}",
            title="BrowserPilot",
            border_style="cyan",
        )
    )

    async def _run() -> None:
        from browser_pilot.agent.action_loop import ActionLoop
        from browser_pilot.models.task import Task

        task = Task(instruction=instruction)
        loop = ActionLoop(provider=provider)

        with console.status("[bold green]Executing task..."):
            result = await loop.run(task)

        if result.success:
            console.print("\n[bold green]Task completed![/]")
        else:
            console.print("\n[bold red]Task failed.[/]")

        console.print(f"  Steps: {result.total_steps}")
        console.print(f"  Time: {result.total_time:.1f}s")

        if result.errors:
            console.print("\n[bold yellow]Errors:[/]")
            for err in result.errors:
                console.print(f"  - {err}")

        if result.screenshots:
            console.print(f"\n  Screenshots saved: {len(result.screenshots)}")

    asyncio.run(_run())


@cli.command()
@click.option("--port", default=8000, help="Server port")
@click.option("--host", default="0.0.0.0", help="Server host")
def serve(port: int, host: str) -> None:
    """Start the BrowserPilot API server."""
    import uvicorn

    console.print(
        Panel(
            f"[bold cyan]Starting server on {host}:{port}[/]",
            title="BrowserPilot Server",
            border_style="cyan",
        )
    )

    uvicorn.run(
        "browser_pilot.server.app:create_app",
        host=host,
        port=port,
        factory=True,
    )


@cli.command()
def config() -> None:
    """Show current configuration."""
    settings = get_settings()

    table = Table(title="BrowserPilot Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row(
        "Google API Key", "***" if settings.google_api_key else "(not set)"
    )
    table.add_row("Gemini Model", settings.gemini_model)
    table.add_row(
        "OpenRouter Key",
        "***" if settings.openrouter_api_key else "(not set)",
    )
    table.add_row("OpenRouter Model", settings.openrouter_model)
    table.add_row("Browser", settings.browser_type)
    table.add_row("Headless", str(settings.browser_headless))
    table.add_row("Max Steps", str(settings.max_steps))
    table.add_row("Step Timeout", f"{settings.step_timeout}s")
    table.add_row("API Host", settings.api_host)
    table.add_row("API Port", str(settings.api_port))
    table.add_row("Log Level", settings.log_level)
    table.add_row("Screenshot Dir", str(settings.screenshot_dir))

    console.print(table)


if __name__ == "__main__":
    cli()
