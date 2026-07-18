"""Command-line interface for agentkit."""

import click
from rich.console import Console
from rich.panel import Panel
import json
import sys

from . import __version__
from .scanner import scan_all
from .catalog import Catalog
from .tui import show_table, show_tool_detail
from .suggest import suggest
from .installer import install_hook
from .hook import handle_user_prompt_submit


@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    """AgentKit — Discover AI coding tools and agents."""
    if ctx.invoked_subcommand is None:
        # No subcommand: show all tools
        ctx.invoke(show)


@main.command()
@click.argument('category', required=False)
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def show(category=None, output_json=False):
    """Show all tools in a table, optionally filtered by category."""
    tools = scan_all()
    catalog = Catalog(tools)

    if output_json:
        # JSON output
        if category:
            filtered = catalog.filter_by_category(category)
        else:
            filtered = catalog.tools

        data = [
            {
                'name': t.name,
                'agent': t.agent,
                'category': t.category,
                'description': t.description,
                'invocation': t.invocation,
                'tags': t.tags,
            }
            for t in filtered
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        # Rich TUI output
        show_table(catalog, category)


@main.command()
@click.argument('query')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def search(query, output_json=False):
    """Search tools by name or description."""
    tools = scan_all()
    catalog = Catalog(tools)
    results = catalog.search(query)

    if output_json:
        data = [
            {
                'name': t.name,
                'agent': t.agent,
                'category': t.category,
                'description': t.description,
                'invocation': t.invocation,
            }
            for t in results
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        console = Console()
        if results:
            for tool in results:
                console.print(f"[magenta]{tool.name}[/magenta] ({tool.category}) — {tool.description}")
        else:
            console.print(f"[dim]No tools found for '{query}'[/dim]")


@main.command()
@click.argument('prompt')
@click.option('--top', default=3, help='Number of suggestions to return')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def suggest_cmd(prompt, top, output_json=False):
    """Suggest tools for a prompt."""
    tools = scan_all()
    catalog = Catalog(tools)
    results = suggest(catalog, prompt, top_n=top)

    if output_json:
        data = [
            {
                'name': t.name,
                'agent': t.agent,
                'category': t.category,
                'description': t.description,
                'invocation': t.invocation,
                'score': float(score),
            }
            for t, score in results
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        console = Console()
        if results:
            console.print(f"[cyan]Suggestions for: {prompt}[/cyan]\n")
            for tool, score in results:
                console.print(f"  {tool.invocation:20s} {tool.category:15s} {tool.description[:45]}")
        else:
            console.print("[dim]No suggestions found[/dim]")


@main.command(name='suggest-hook')
def suggest_hook_cmd():
    """Hook handler for Claude Code (internal use)."""
    handle_user_prompt_submit()


@main.command()
def install_hook_cmd():
    """Install the suggestion hook into Claude Code."""
    install_hook()


@main.command()
def scan():
    """Re-scan all tool sources and show summary."""
    tools = scan_all()
    catalog = Catalog(tools)

    console = Console()
    by_category = catalog.by_category()

    total = len(tools)
    console.print(f"\n[bold]AgentKit Scan Summary[/bold]\n")
    console.print(f"Total tools found: [cyan]{total}[/cyan]\n")

    for category in sorted(by_category.keys()):
        tools_in_cat = by_category[category]
        console.print(f"{category}: {len(tools_in_cat)}")
        for tool in tools_in_cat[:3]:
            console.print(f"  • {tool.name} ({tool.agent})")
        if len(tools_in_cat) > 3:
            console.print(f"  ... and {len(tools_in_cat) - 3} more")

    console.print()


if __name__ == '__main__':
    main()
