"""Scanner for auto-detecting installed agents and skills."""

import json
from pathlib import Path
from typing import Generator

import frontmatter

from .catalog import Tool


def scan_claude_skills() -> Generator[Tool, None, None]:
    """Scan ~/.claude/skills/ for skill definitions."""
    skills_dir = Path.home() / ".claude" / "skills"
    if not skills_dir.exists():
        return

    for skill_path in skills_dir.rglob("SKILL.md"):
        try:
            with open(skill_path, 'r') as f:
                post = frontmatter.load(f)

            name = post.metadata.get('name', skill_path.parent.name)
            description = post.metadata.get('description', '')
            tags = post.metadata.get('tags', [])

            yield Tool(
                name=f"/{name}",
                agent="gstack",
                category="",  # Will be assigned by catalog
                description=description,
                tags=tags,
                invocation=f"/{name}",
                source="gstack-skills"
            )
        except Exception:
            pass


def scan_claude_agents() -> Generator[Tool, None, None]:
    """Scan ~/.claude/agents/ for agent definitions."""
    agents_dir = Path.home() / ".claude" / "agents"
    if not agents_dir.exists():
        return

    for agent_file in agents_dir.glob("*.md"):
        try:
            with open(agent_file, 'r') as f:
                post = frontmatter.load(f)

            name = post.metadata.get('name', agent_file.stem)
            description = post.metadata.get('description', '')

            yield Tool(
                name=name,
                agent="Claude Code (custom)",
                category="",
                description=description,
                tags=[],
                invocation=f"Agent({name})",
                source="claude-agents"
            )
        except Exception:
            pass


def scan_codex_skills() -> Generator[Tool, None, None]:
    """Scan ~/.codex/skills/ for skill definitions."""
    skills_dir = Path.home() / ".codex" / "skills"
    if not skills_dir.exists():
        return

    for skill_path in skills_dir.rglob("SKILL.md"):
        try:
            with open(skill_path, 'r') as f:
                post = frontmatter.load(f)

            name = post.metadata.get('name', skill_path.parent.name)
            description = post.metadata.get('description', '')
            tags = post.metadata.get('tags', [])

            yield Tool(
                name=f"/{name}",
                agent="Codex",
                category="",
                description=description,
                tags=tags,
                invocation=f"/{name}",
                source="codex-skills"
            )
        except Exception:
            pass


def scan_hermes_skills() -> Generator[Tool, None, None]:
    """Scan ~/.hermes/skills/ for skill definitions."""
    skills_dir = Path.home() / ".hermes" / "skills"
    if not skills_dir.exists():
        return

    for skill_path in skills_dir.rglob("*.md"):
        try:
            with open(skill_path, 'r') as f:
                post = frontmatter.load(f)

            name = post.metadata.get('name', skill_path.stem)
            description = post.metadata.get('description', '')
            tags = post.metadata.get('tags', [])

            yield Tool(
                name=f"/{name}",
                agent="Hermes",
                category="",
                description=description,
                tags=tags,
                invocation=f"/{name}",
                source="hermes-skills"
            )
        except Exception:
            pass


def scan_mcp_servers() -> Generator[Tool, None, None]:
    """Scan ~/.claude/settings.json for MCP servers and their tools."""
    settings_file = Path.home() / ".claude" / "settings.json"
    if not settings_file.exists():
        return

    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)

        mcp = settings.get('mcpServers', {})
        for server_name, server_config in mcp.items():
            if isinstance(server_config, dict):
                # Use server name as both tool and agent
                yield Tool(
                    name=server_name,
                    agent="MCP Server",
                    category="",
                    description=server_config.get('description', f'MCP server: {server_name}'),
                    tags=['mcp'],
                    invocation=f"MCP:{server_name}",
                    source="mcp-servers"
                )
    except Exception:
        pass


def scan_builtin_claude_code_tools() -> Generator[Tool, None, None]:
    """Yield built-in Claude Code tools."""
    builtin_tools = [
        Tool("Read", "Claude Code", "", "Read any file", [], "Read(file_path)", "builtin"),
        Tool("Write", "Claude Code", "", "Write or overwrite files", [], "Write(file_path, content)", "builtin"),
        Tool("Edit", "Claude Code", "", "Edit existing files with diffs", [], "Edit(file_path, old, new)", "builtin"),
        Tool("Bash", "Claude Code", "", "Execute bash commands", [], "Bash(command)", "builtin"),
        Tool("WebSearch", "Claude Code", "", "Search the web", [], "WebSearch(query)", "builtin"),
        Tool("WebFetch", "Claude Code", "", "Fetch web pages", [], "WebFetch(url)", "builtin"),
        Tool("Agent", "Claude Code", "", "Spawn subagents for tasks", [], "Agent(description, prompt)", "builtin"),
        Tool("Artifact", "Claude Code", "", "Publish HTML/Markdown artifacts", [], "Artifact(file_path, description)", "builtin"),
        Tool("AskUserQuestion", "Claude Code", "", "Ask user multiple-choice questions", [], "AskUserQuestion(questions)", "builtin"),
    ]
    for tool in builtin_tools:
        yield tool


def scan_all() -> list[Tool]:
    """Scan all sources and return complete tool list."""
    tools = []

    for scanner in [
        scan_builtin_claude_code_tools,
        scan_claude_skills,
        scan_claude_agents,
        scan_codex_skills,
        scan_hermes_skills,
        scan_mcp_servers,
    ]:
        tools.extend(scanner())

    return tools
