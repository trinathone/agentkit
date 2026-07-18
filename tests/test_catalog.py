"""Tests for catalog module."""

from agentkit.catalog import Tool, Catalog


def test_tool_category_assignment():
    """Test that tools get appropriate categories."""
    # File tool
    file_tool = Tool("Read", "Claude Code", "", "Read any file")
    assert "File" in file_tool.category

    # Web tool
    web_tool = Tool("WebSearch", "Claude Code", "", "Search the web")
    assert "Web" in web_tool.category

    # Code tool
    code_tool = Tool("Bash", "Claude Code", "", "Execute bash commands")
    assert "Code" in code_tool.category or "System" in code_tool.category


def test_catalog_dedup():
    """Test that catalog removes duplicates."""
    tools = [
        Tool("Read", "Claude Code", "🗂 File", "Read files"),
        Tool("Read", "Claude Code", "🗂 File", "Read files"),  # duplicate
        Tool("Write", "Claude Code", "🗂 File", "Write files"),
    ]
    catalog = Catalog(tools)
    assert len(catalog.tools) == 2


def test_catalog_filter_by_category():
    """Test filtering by category."""
    tools = [
        Tool("Read", "Claude Code", "🗂 File", "Read files"),
        Tool("WebSearch", "Claude Code", "🌐 Web", "Search web"),
    ]
    catalog = Catalog(tools)
    file_tools = catalog.filter_by_category("🗂 File")
    assert len(file_tools) == 1
    assert file_tools[0].name == "Read"


def test_catalog_search():
    """Test search functionality."""
    tools = [
        Tool("Read", "Claude Code", "🗂 File", "Read any file"),
        Tool("Write", "Claude Code", "🗂 File", "Write files"),
        Tool("WebSearch", "Claude Code", "🌐 Web", "Search the web"),
    ]
    catalog = Catalog(tools)

    # Search by name
    results = catalog.search("read")
    assert len(results) == 1
    assert results[0].name == "Read"

    # Search by description
    results = catalog.search("file")
    assert len(results) >= 2

    # No results
    results = catalog.search("xyz123")
    assert len(results) == 0
