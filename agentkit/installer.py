"""Install the agentkit hook into Claude Code settings."""

import json
from pathlib import Path


def install_hook():
    """
    Install UserPromptSubmit hook into ~/.claude/settings.json

    Appends to existing hooks, never replaces.
    """
    settings_file = Path.home() / ".claude" / "settings.json"

    # Read existing settings (or create empty)
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}

    # Ensure hooks structure exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    if "UserPromptSubmit" not in settings["hooks"]:
        settings["hooks"]["UserPromptSubmit"] = []

    # Create the agentkit hook entry
    agentkit_hook = {
        "type": "command",
        "command": "agentkit suggest-hook",
        "timeout": 2
    }

    # Check if already installed
    existing = settings["hooks"]["UserPromptSubmit"]
    if not isinstance(existing, list):
        existing = []

    # Avoid duplicates
    for entry in existing:
        if isinstance(entry, dict) and entry.get("command") == "agentkit suggest-hook":
            print("Hook already installed.")
            return

    # Add the hook
    existing.append(agentkit_hook)
    settings["hooks"]["UserPromptSubmit"] = existing

    # Write back
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

    print(f"✓ Hook installed at {settings_file}")
    print("✓ AgentKit will now suggest tools as you type in Claude Code")
