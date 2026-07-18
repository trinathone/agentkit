"""Rich TUI for browsing tools."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .catalog import Catalog


def show_table(catalog: Catalog, category: str = None):
    """Display tools in a Rich table."""
    console = Console()

    # Filter tools
    if category:
        tools = catalog.filter_by_category(category)
        title = f"AgentKit v0.1.0 — {len(tools)} tools in {category}"
    else:
        tools = catalog.tools
        title = f"AgentKit v0.1.0 — {len(tools)} tools detected"

    # Create table
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="magenta", width=20)
    table.add_column("Agent", style="green", width=15)
    table.add_column("Category", width=12)
    table.add_column("Description", width=45)

    for tool in tools:
        table.add_row(
            tool.name,
            tool.agent,
            tool.category,
            tool.description[:45] + ("..." if len(tool.description) > 45 else ""),
        )

    console.print(table)

    # Footer
    footer = "Use arrow keys to navigate. q=quit, /=search, c=copy"
    console.print(f"\n[dim]{footer}[/dim]")


def show_tool_detail(tool):
    """Display full details for a single tool."""
    console = Console()

    content = f"""[bold]{tool.name}[/bold]
[dim]Agent:[/dim] {tool.agent}
[dim]Category:[/dim] {tool.category}

[bold]Description:[/bold]
{tool.description}

[bold]Invocation:[/bold]
[cyan]{tool.invocation}[/cyan]

[bold]Tags:[/bold] {', '.join(tool.tags) if tool.tags else '(none)'}
[bold]Source:[/bold] {tool.source}
"""

    console.print(Panel(content, title="Tool Details", expand=False))
