"""Interactive prompt wrapper with real-time tool suggestions."""

import os
import sys
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .scanner import scan_all
from .catalog import Catalog
from .suggest import suggest


class ToolSuggest(AutoSuggest):
    """AutoSuggest that shows relevant AgentKit tools as ghost text."""

    def __init__(self, catalog: Catalog):
        self.catalog = catalog

    def get_suggestion(self, buffer, document):
        """Return a suggestion for the current buffer text."""
        text = document.text.strip()

        # Only suggest if 3+ characters typed
        if len(text) < 3:
            return None

        # Get top suggestion (use lower min_score for interactive mode)
        results = suggest(self.catalog, text, top_n=1, min_score=0.25)
        if not results:
            return None

        tool, score = results[0]

        # Format suggestion as gray ghost text after cursor
        suggestion_text = f"  →  {tool.invocation}"

        return Suggestion(suggestion_text)


def main():
    """Main entry point for akit wrapper."""
    import click

    # Check for akit-specific help/commands first
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            # Show akit help
            click.echo("akit — AI agent toolkit with prompt suggestions")
            click.echo("\nUsage:")
            click.echo("  akit                 Interactive prompt with suggestions")
            click.echo("  akit -p <prompt>     Pass prompt directly to claude")
            click.echo("  akit --install-alias Add 'alias claude=akit' to ~/.zshrc")
            click.echo("\nWhile typing in akit:")
            click.echo("  • Ghost text shows suggested tool (gray)")
            click.echo("  • Press Enter to submit prompt to claude")
            click.echo("  • Ctrl+C to exit")
            return

        if sys.argv[1] == '--install-alias':
            _install_alias()
            return

        # Check for direct passthrough (akit -p "task" or other claude args)
        if sys.argv[1] == '-p' or (sys.argv[1].startswith('-') and sys.argv[1] != '--version'):
            # Pass through to real claude unchanged
            _exec_claude(sys.argv[1:])
            return

        if sys.argv[1] == '--version':
            click.echo("akit 0.1.0")
            return

    # Interactive mode with suggestions
    _interactive_mode()


def _interactive_mode():
    """Launch interactive prompt session with tool suggestions."""
    # Load catalog
    tools = scan_all()
    catalog = Catalog(tools)

    # Create history file
    history_file = Path.home() / ".claude" / ".akit_history"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    # Custom style for ghost text
    style = Style.from_dict({
        'autosuggestion': 'fg:#888888 italic',  # Gray, italic
    })

    # Create prompt session
    session = PromptSession(
        message="claude > ",
        auto_suggest=ToolSuggest(catalog),
        history=FileHistory(str(history_file)),
        style=style,
    )

    try:
        # Get user input
        prompt_text = session.prompt()

        if prompt_text.strip():
            # Show brief flash of suggested tool
            results = suggest(catalog, prompt_text, top_n=1, min_score=0.4)
            if results:
                tool, _ = results[0]
                import click
                click.echo(f"💡 Suggested: {tool.invocation}", err=True)

        # Execute real claude with the prompt
        _exec_claude(['-p', prompt_text] if prompt_text.strip() else [])

    except KeyboardInterrupt:
        # User pressed Ctrl+C
        sys.exit(0)
    except EOFError:
        # User pressed Ctrl+D
        sys.exit(0)


def _exec_claude(args):
    """Execute the real claude binary, replacing current process."""
    try:
        os.execvp("claude", ["claude"] + args)
    except FileNotFoundError:
        import click
        click.echo("Error: 'claude' binary not found. Is Claude Code installed?", err=True)
        sys.exit(1)


def _install_alias():
    """Add 'alias claude=akit' to ~/.zshrc."""
    zshrc = Path.home() / ".zshrc"

    # Read existing content
    if zshrc.exists():
        content = zshrc.read_text()
    else:
        content = ""

    # Check if alias already exists
    if "alias claude=akit" in content:
        import click
        click.echo("✓ Alias 'claude=akit' already exists in ~/.zshrc")
        return

    # Add alias
    alias_line = "\n# AgentKit: interactive claude with tool suggestions\nalias claude=akit\n"

    with open(zshrc, 'a') as f:
        f.write(alias_line)

    import click
    click.echo("✓ Added 'alias claude=akit' to ~/.zshrc")
    click.echo("Run: source ~/.zshrc  (or restart terminal)")


if __name__ == '__main__':
    main()
