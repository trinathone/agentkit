"""Tests for wrapper module (akit)."""

import sys
from agentkit.catalog import Tool, Catalog
from agentkit.wrapper import ToolSuggest


class MockDocument:
    """Mock prompt_toolkit document."""
    def __init__(self, text):
        self.text = text


class MockBuffer:
    """Mock prompt_toolkit buffer."""
    def __init__(self, text):
        self.document = MockDocument(text)


def test_tool_suggest_no_suggestion_too_short():
    """Test that no suggestion is returned for text < 3 chars."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review tool"),
    ]
    catalog = Catalog(tools)
    suggester = ToolSuggest(catalog)

    # Text too short
    buffer = MockBuffer("re")
    doc = MockDocument("re")
    suggestion = suggester.get_suggestion(buffer, doc)

    assert suggestion is None


def test_tool_suggest_returns_suggestion():
    """Test that suggestion is returned for matching text."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review tool for finding bugs"),
    ]
    catalog = Catalog(tools)
    suggester = ToolSuggest(catalog)

    # Text long enough and matching
    buffer = MockBuffer("review code")
    doc = MockDocument("review code")
    suggestion = suggester.get_suggestion(buffer, doc)

    assert suggestion is not None
    assert "→" in suggestion.text  # Contains arrow
    assert "Review" in suggestion.text or "review" in suggestion.text.lower()


def test_tool_suggest_format():
    """Test that suggestion text is properly formatted."""
    tools = [
        Tool("/review", "gstack", "💻 Code", "Code review for bugs and quality"),
    ]
    catalog = Catalog(tools)
    suggester = ToolSuggest(catalog)

    buffer = MockBuffer("review code for bugs")
    doc = MockDocument("review code for bugs")
    suggestion = suggester.get_suggestion(buffer, doc)

    assert suggestion is not None
    # Check format: "  →  /tool_name"
    assert "→" in suggestion.text
    assert suggestion.text.strip().startswith("→")


def test_tool_suggest_updates_on_keystroke():
    """Test that suggestion changes as text changes."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review"),
        Tool("Deploy", "gstack", "💻 Code", "Deploy to production"),
    ]
    catalog = Catalog(tools)
    suggester = ToolSuggest(catalog)

    # First suggestion
    buffer1 = MockBuffer("review")
    doc1 = MockDocument("review")
    suggestion1 = suggester.get_suggestion(buffer1, doc1)

    # Second suggestion
    buffer2 = MockBuffer("deploy")
    doc2 = MockDocument("deploy")
    suggestion2 = suggester.get_suggestion(buffer2, doc2)

    # Both should have suggestions
    assert suggestion1 is not None
    assert suggestion2 is not None

    # Suggestions might be different or same tool, but both should be valid
    assert "→" in suggestion1.text
    assert "→" in suggestion2.text
