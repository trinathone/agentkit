"""Tool catalog with category assignment and filtering."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Tool:
    """A single tool/skill available to the user."""
    name: str
    agent: str
    category: str
    description: str
    tags: list[str] = field(default_factory=list)
    invocation: str = ""
    source: str = ""

    def __post_init__(self):
        """Auto-assign category if empty."""
        if not self.category:
            self.category = self._assign_category()

        if not self.invocation:
            self.invocation = self.name

    def _assign_category(self) -> str:
        """Assign category based on tags and description."""
        full_text = (
            f"{self.name} {self.description} {' '.join(self.tags)}"
        ).lower()

        # File operations
        if any(w in full_text for w in ['read', 'write', 'edit', 'file', 'patch', 'save']):
            return "🗂 File"

        # Web operations
        if any(w in full_text for w in ['web', 'fetch', 'search', 'browse', 'scrape', 'http', 'url']):
            return "🌐 Web"

        # Code operations
        if any(w in full_text for w in ['code', 'review', 'test', 'lint', 'build', 'deploy', 'git', 'commit']):
            return "💻 Code"

        # Memory/context
        if any(w in full_text for w in ['memory', 'save', 'recall', 'session', 'context', 'note']):
            return "🧠 Memory"

        # Security
        if any(w in full_text for w in ['security', 'audit', 'scan', 'owasp', 'secret', 'password']):
            return "🔒 Security"

        # Design/UI
        if any(w in full_text for w in ['design', 'ui', 'css', 'mockup', 'visual', 'layout']):
            return "🎨 Design"

        # Agents/orchestration
        if any(w in full_text for w in ['agent', 'spawn', 'orchestrate', 'delegate', 'subagent']):
            return "🤖 Agent"

        # Planning
        if any(w in full_text for w in ['plan', 'spec', 'architecture', 'design', 'strategy']):
            return "📋 Plan"

        # System/shell
        if any(w in full_text for w in ['bash', 'terminal', 'process', 'system', 'shell', 'command']):
            return "⚙️ System"

        # Default
        return "📦 Other"


class Catalog:
    """Manages the tool catalog."""

    def __init__(self, tools: list[Tool]):
        self.tools = tools
        self._dedup()

    def _dedup(self):
        """Remove duplicate tools, keeping first occurrence."""
        seen = set()
        unique = []
        for tool in self.tools:
            key = (tool.name.lower(), tool.agent.lower())
            if key not in seen:
                seen.add(key)
                unique.append(tool)
        self.tools = unique

    def filter_by_category(self, category: str) -> list[Tool]:
        """Get tools by category."""
        return [t for t in self.tools if t.category == category]

    def search(self, query: str) -> list[Tool]:
        """Search tools by name/description."""
        query = query.lower()
        return [
            t for t in self.tools
            if query in t.name.lower()
            or query in t.description.lower()
            or any(query in tag.lower() for tag in t.tags)
        ]

    def get_categories(self) -> list[str]:
        """Get all categories in use."""
        categories = set(t.category for t in self.tools)
        return sorted(categories)

    def by_category(self) -> dict[str, list[Tool]]:
        """Group tools by category."""
        result = {}
        for category in self.get_categories():
            result[category] = self.filter_by_category(category)
        return result
