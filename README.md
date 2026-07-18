# AgentKit

> You have 50+ tools. You remember 10. AgentKit shows you the rest.

**AgentKit** is a CLI toolkit for discovering AI coding tools and agents. It auto-detects everything you have installed across Claude Code, Codex, gstack, Hermes, and MCP servers — then suggests the right tool as you type.

## Problem

Developers using Claude Code, Codex, gstack, or Cursor have 50–200 tools/skills/agents available. They forget 80% of them. When stuck, they guess or Google instead of using the right tool.

## Solution

AgentKit scans your machine, builds a live table of every tool, and:
1. **Shows all tools** in a searchable, categorized TUI
2. **Suggests tools** as you type prompts in Claude Code
3. **Integrates seamlessly** with your existing workflow

## Quick Start

```bash
# Install
pip install -e .

# See all your tools
agentkit

# Search
agentkit search auth
agentkit search security

# Get suggestions for a prompt
agentkit suggest "review my code for bugs"

# Install Claude Code hook (real-time suggestions)
agentkit install-hook
```

## Features

### 1. Tool Discovery Table

```
agentkit              # show all tools
agentkit file         # filter by category
agentkit search auth  # search across all tools
```

Detects tools from:
- Claude Code built-ins (Read, Write, Edit, Bash, WebSearch, etc.)
- `~/.claude/skills/` (gstack skills)
- `~/.claude/agents/` (custom agents)
- `~/.codex/skills/` (Codex)
- `~/.hermes/skills/` (Hermes)
- `~/.claude/settings.json` (MCP servers)

### 2. Prompt Suggestions

As you type a prompt in Claude Code, AgentKit suggests the most relevant tool:

```
💡 For "check this code for security issues":
   → /cso  (OWASP + STRIDE security audit)
   → /review  (Pre-PR bug review)
Press Tab to accept, Esc to dismiss
```

Installs a hook into Claude Code that fuzzy-matches your prompt against all available tools.

### 3. JSON Output

All commands support `--json` for scripting:

```bash
agentkit --json
agentkit suggest "find bugs" --json
```

## Categories

Tools are auto-categorized:

- 🗂 **File** — read, write, edit, patch files
- 🌐 **Web** — fetch, search, browse, scrape
- 💻 **Code** — review, test, lint, build, deploy, git
- 🧠 **Memory** — save, recall, session, context
- 🔒 **Security** — audit, scan, OWASP, secrets
- 🎨 **Design** — UI, CSS, mockup, visual
- 🤖 **Agent** — spawn, orchestrate, delegate
- 📋 **Plan** — spec, review, architecture
- ⚙️ **System** — bash, terminal, process, shell

## Use Cases

### Use Case 1: Stuck on a Problem

**Problem:** You're writing tests and forget which tool runs browser tests.

```bash
agentkit suggest "run tests in a real browser"
```

Output:
```
/qa (real browser test + fix)
/run (launch and drive the app)
```

### Use Case 2: Onboarding

**Problem:** You joined a new team and don't know what tools are available.

```bash
agentkit           # See everything at once
agentkit search deploy  # Find deployment tools
```

### Use Case 3: Code Review

**Problem:** You're about to submit a PR but forget to check for security issues.

Claude Code suggests as you type:
```
💡 For "review this before I push":
   → /cso (security audit)
   → /review (pre-PR bugs)
```

### Use Case 4: Scripting

**Problem:** You're building automation and need all available tools as data.

```bash
agentkit --json | jq '.[] | select(.category | contains("Code"))'
```

## Architecture

```
agentkit/
├── cli.py       — Click CLI entry points
├── scanner.py   — Auto-detect installed tools
├── catalog.py   — Tool dataclass and filtering
├── tui.py       — Rich TUI for display
├── suggest.py   — Fuzzy matching and scoring
├── hook.py      — Claude Code hook handler
└── installer.py — Hook installation to settings.json
```

### Stack

- **Python 3.11+** — Modern, type-hinted
- **Rich** — Beautiful TUI tables and panels
- **Click** — CLI framework
- **python-frontmatter** — Parse YAML frontmatter from .md files
- **rapidfuzz** — Fast fuzzy matching for suggestions

### Zero External APIs

AgentKit is 100% offline. No LLM calls, no network requests, no tracking.

## Add Your Agent

Want AgentKit to discover tools from your AI agent/editor? Write a 20-line scanner.

Example: Detecting tools from `~/.myeditor/plugins/`:

```python
# In agentkit/scanner.py

def scan_myeditor_plugins() -> Generator[Tool, None, None]:
    """Scan ~/.myeditor/plugins/ for tools."""
    plugins_dir = Path.home() / ".myeditor" / "plugins"
    if not plugins_dir.exists():
        return

    for plugin_file in plugins_dir.glob("*.json"):
        try:
            with open(plugin_file, 'r') as f:
                config = json.load(f)

            yield Tool(
                name=config.get('name'),
                agent='MyEditor',
                category='',  # Auto-assigned
                description=config.get('description', ''),
                tags=config.get('tags', []),
                invocation=config.get('invoke', ''),
                source='myeditor-plugins'
            )
        except Exception:
            pass


# Register in scan_all():
def scan_all() -> list[Tool]:
    tools = []
    for scanner in [scan_builtin_claude_code_tools, scan_myeditor_plugins, ...]:
        tools.extend(scanner())
    return tools
```

Then open a PR! We welcome contributions from Cursor, Factory, Kiro, and other AI agent communities.

## Installation & Setup

```bash
# Install from source
git clone https://github.com/trinathone/agentkit
cd agentkit
pip install -e .

# Verify install
agentkit --version
agentkit scan

# Suggest tools for a prompt
agentkit suggest "review my code for bugs"

# Install Claude Code hook
agentkit install-hook

# Now open Claude Code — as you type, you'll see suggestions!
```

## Commands

| Command | Purpose |
|---------|---------|
| `agentkit` | Show all tools in a searchable table |
| `agentkit <category>` | Filter by category (File, Web, Code, etc.) |
| `agentkit search <query>` | Search tools by name/description |
| `agentkit suggest "<prompt>"` | Get tool suggestions for a prompt |
| `agentkit install-hook` | Wire into Claude Code for real-time suggestions |
| `agentkit scan` | Re-scan and show summary |

## Testing

```bash
pytest tests/
pytest --cov=agentkit tests/
```

All tests pass ✓

## License

MIT — see LICENSE

## Author

Trinath Reddy

## Contributing

Found a bug? Have a feature idea? Want to add support for your agent?

1. Fork the repo
2. Create a branch (`git checkout -b feature/xyz`)
3. Write a test and make it pass
4. Open a PR

To add a new agent:
1. Write a scanner function in `agentkit/scanner.py`
2. Add tests in `tests/test_scanner.py`
3. Register in `scan_all()`
4. Open a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## FAQ

**Q: Does AgentKit work with my editor?**  
A: If your editor has a settings file or skill directory, we can scan it. Open an issue or PR to add support.

**Q: Does it send data anywhere?**  
A: No. AgentKit is 100% offline. Everything runs locally.

**Q: What if I don't use Claude Code?**  
A: You can still use `agentkit` to discover tools, and the search API works anywhere. The real-time suggestions only work in Claude Code (for now).

**Q: Can I customize categories?**  
A: The category heuristic is in `catalog.py`. Fork and customize if needed.

**Q: Why Python 3.11+?**  
A: Type hints and modern stdlib features. If you need Python 3.9 support, open an issue.
