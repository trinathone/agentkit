# AgentKit for AI Agents

This document explains how AI agents (like gstack, Codex, Hermes, and Claude Code agents) can use AgentKit to discover and suggest tools.

## What AgentKit Does

AgentKit scans your machine for all installed AI coding tools and skills, then:

1. **Provides tool discovery** — agents can query which tools are available
2. **Suggests relevant tools** — for a given task or prompt
3. **Integrates seamlessly** — with existing agent workflows without breaking anything

## For Agents & Agents

### Get All Available Tools

```python
from agentkit.scanner import scan_all
from agentkit.catalog import Catalog

tools = scan_all()
catalog = Catalog(tools)

for tool in catalog.tools:
    print(f"{tool.name}: {tool.description}")
    print(f"  Invoke as: {tool.invocation}")
    print(f"  Category: {tool.category}")
```

### Filter by Category

```python
# Get all security tools
security_tools = catalog.filter_by_category("🔒 Security")

# Get all file manipulation tools
file_tools = catalog.filter_by_category("🗂 File")

# Get all code-related tools
code_tools = catalog.filter_by_category("💻 Code")
```

### Search for Tools

```python
# Find tools related to testing
test_tools = catalog.search("test")

# Find deployment tools
deploy_tools = catalog.search("deploy")
```

### Get Suggestions for a Task

```python
from agentkit.suggest import suggest

prompt = "I need to find bugs in this code before deploying"
suggestions = suggest(catalog, prompt, top_n=3)

for tool, score in suggestions:
    print(f"{tool.name} (confidence: {score:.1%})")
    print(f"  {tool.description}")
```

## Integration Examples

### Example 1: Code Review Agent

An agent that needs to run code review can auto-detect the best tool:

```python
from agentkit.scanner import scan_all
from agentkit.catalog import Catalog
from agentkit.suggest import suggest

catalog = Catalog(scan_all())

# User asks: "review my code"
suggestions = suggest(catalog, "review my code for bugs", top_n=1)

if suggestions:
    tool, _ = suggestions[0]
    print(f"Invoking {tool.invocation}...")
    # Now invoke that tool
else:
    print("No review tools found")
```

### Example 2: Find Available Deployment Tools

```python
catalog = Catalog(scan_all())

deploy_tools = catalog.search("deploy")
for tool in deploy_tools:
    print(f"Can deploy via: {tool.invocation}")
```

### Example 3: Suggest Based on Task

```python
task = "test the app in a real browser"
suggestions = suggest(catalog, task, top_n=2)

for tool, score in suggestions:
    print(f"Suggested: {tool.name} (score: {score:.0%})")
    print(f"  Invoke: {tool.invocation}")
```

## Tool Structure

Each tool has:

- **name** — Display name (e.g., "Review", "WebSearch")
- **agent** — Which agent provides it (e.g., "gstack", "Claude Code", "MCP Server")
- **category** — What it does (File, Web, Code, Security, etc.)
- **description** — One-line summary
- **tags** — Keywords for searching (optional)
- **invocation** — How to call it (e.g., "/review", "Agent(name)", "MCP:server-name")
- **source** — Where it came from (e.g., "gstack-skills", "claude-agents", "mcp-servers")

## Adding Your Agent

If you're building an AI agent, you can make AgentKit aware of your tools:

1. Store tools in a standardized location (e.g., `~/.youragent/skills/`)
2. Use YAML frontmatter or JSON for metadata
3. Open a PR adding a scanner to `agentkit/scanner.py`

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## API Reference

### `scan_all() -> list[Tool]`

Scan all sources and return tools.

### `Catalog(tools: list[Tool])`

Create a filterable catalog.

Methods:
- `filter_by_category(category: str) -> list[Tool]`
- `search(query: str) -> list[Tool]`
- `get_categories() -> list[str]`
- `by_category() -> dict[str, list[Tool]]`

### `suggest(catalog: Catalog, prompt: str, top_n: int = 3, min_score: float = 0.6) -> list[tuple[Tool, float]]`

Suggest tools for a prompt. Returns tools with score >= min_score, sorted by score descending.

## Real-Time Suggestions in Claude Code

AgentKit installs a hook that suggests tools as you type in Claude Code:

```bash
agentkit install-hook
```

This adds a `UserPromptSubmit` hook to `~/.claude/settings.json` that:
1. Reads your prompt as you type
2. Fuzzy-matches against all available tools
3. Shows the top 2-3 suggestions in real-time

## Example Workflow

1. **Agent starts** — calls `scan_all()` to load tools
2. **User asks a question** — e.g., "review this for bugs"
3. **Agent queries** — `suggest(catalog, "review this for bugs", top_n=1)`
4. **Agent gets suggestion** — `("/review", 0.92)`
5. **Agent invokes tool** — calls or delegates to `/review`

## Performance Notes

- First `scan_all()` takes ~50-100ms (reads ~/.claude/*.md files)
- Subsequent calls are instant (no re-scanning)
- Suggestions are instant (~10ms even for 100+ tools)
- Zero network requests or external APIs

For long-running agents, cache the catalog:

```python
# Load once
catalog = Catalog(scan_all())

# Reuse for multiple queries
for prompt in prompts:
    suggestions = suggest(catalog, prompt)
    # ...
```

## Testing

AgentKit includes a test suite for all public APIs:

```bash
pytest tests/
```

All tests pass ✓

## Questions?

- Check [README.md](README.md) for usage examples
- See [CONTRIBUTING.md](CONTRIBUTING.md) for extending AgentKit
- Open an issue or discussion for questions
