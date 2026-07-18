"""Claude Code hook handler for suggesting tools."""

import json
import os
import sys

from .scanner import scan_all
from .catalog import Catalog
from .suggest import suggest
from rich.console import Console


def handle_user_prompt_submit():
    """
    Hook handler for Claude Code UserPromptSubmit event.

    Reads CLAUDE_TOOL_INPUT env var (JSON), extracts prompt text,
    suggests relevant tools, prints suggestions to stderr.
    """
    # Read the prompt from environment
    input_json = os.environ.get('CLAUDE_TOOL_INPUT', '{}')

    try:
        data = json.loads(input_json)
    except json.JSONDecodeError:
        return  # Silently fail if JSON is malformed

    # Extract prompt text
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return  # No prompt, no suggestions

    # Build catalog and get suggestions
    try:
        tools = scan_all()
        catalog = Catalog(tools)
        suggestions = suggest(catalog, prompt, top_n=2, min_score=0.5)

        if suggestions:
            # Print to stderr so Claude Code shows it as status
            console = Console(file=sys.stderr)

            tools_text = "\n".join(
                f"   → {tool.invocation:20s} ({tool.description[:50]})"
                for tool, score in suggestions
            )

            panel_text = f"""💡 For "{prompt[:50]}{'...' if len(prompt) > 50 else ''}":
{tools_text}
Press Tab to accept, Esc to dismiss"""

            console.print(f"[blue]{panel_text}[/blue]")
    except Exception:
        pass  # Silently fail, never block the prompt


if __name__ == '__main__':
    handle_user_prompt_submit()
