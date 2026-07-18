# Contributing to AgentKit

Thanks for your interest in contributing! Here's how you can help.

## Adding a New Agent Scanner

The easiest way to contribute is to add support for a new AI agent or editor.

### Step 1: Write a Scanner Function

In `agentkit/scanner.py`, add a function that scans your agent's tool directory:

```python
def scan_myagent_skills() -> Generator[Tool, None, None]:
    """Scan ~/.myagent/skills/ for tool definitions."""
    skills_dir = Path.home() / ".myagent" / "skills"
    if not skills_dir.exists():
        return

    for skill_path in skills_dir.glob("*.md"):  # or .json, .yaml, etc.
        try:
            # Parse the skill file (adapt to your format)
            with open(skill_path, 'r') as f:
                post = frontmatter.load(f)  # or json.load(f)

            name = post.metadata.get('name', skill_path.stem)
            description = post.metadata.get('description', '')
            tags = post.metadata.get('tags', [])

            yield Tool(
                name=f"/{name}",
                agent="MyAgent",
                category="",  # Auto-assigned by catalog
                description=description,
                tags=tags,
                invocation=f"/{name}",
                source="myagent-skills"
            )
        except Exception:
            pass  # Silently skip malformed files
```

### Step 2: Register in `scan_all()`

At the bottom of `scanner.py`, add your scanner to the list:

```python
def scan_all() -> list[Tool]:
    """Scan all sources and return complete tool list."""
    tools = []

    for scanner in [
        scan_builtin_claude_code_tools,
        scan_claude_skills,
        scan_myagent_skills,  # ← Add here
        # ... other scanners
    ]:
        tools.extend(scanner())

    return tools
```

### Step 3: Write Tests

In `tests/test_scanner.py`, add a test:

```python
def test_scan_myagent_skills():
    """Test that MyAgent skills are scanned."""
    # Mock or create a test directory
    # Verify that scan_myagent_skills finds tools
    pass
```

### Step 4: Test Locally

```bash
pip install -e .
agentkit scan
agentkit suggest "your test prompt"
pytest tests/test_scanner.py::test_scan_myagent_skills -v
```

### Step 5: Open a PR

- Title: "Add support for MyAgent"
- Describe what tools MyAgent has and where they're found
- Include a screenshot of `agentkit scan` showing the new agent
- Ensure all tests pass: `pytest`

## Reporting Bugs

Found a bug? Open an issue with:
1. **What you did** — the command or action
2. **What happened** — error message or unexpected behavior
3. **What you expected** — what should have happened
4. **Environment** — Python version, OS, Claude Code version

```bash
agentkit --version
python --version
uname -a
```

## Improving Documentation

Typos, clarity issues, or examples? Edit `README.md` or `CONTRIBUTING.md` and open a PR.

## Code Style

We follow PEP 8 with:
- Type hints on function signatures
- Docstrings on public functions (one-liner OK)
- No comments unless the *why* is non-obvious

```python
# ✓ Good
def scan_tools() -> list[Tool]:
    """Scan and return all available tools."""
    ...

# ✗ Avoid
def scan_tools():
    # scan all tools and return them
    ...
```

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_scanner.py -v

# Check coverage
pytest --cov=agentkit tests/
```

All PRs must include tests and pass the full suite.

## Development Setup

```bash
git clone https://github.com/trinathone/agentkit
cd agentkit
pip install -e ".[dev]"
pytest
```

## Questions?

Open an issue or ask in a discussion. We're here to help!
