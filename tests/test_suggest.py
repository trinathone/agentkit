"""Tests for suggest module."""

from agentkit.catalog import Tool, Catalog
from agentkit.suggest import suggest, score_tool


def test_score_tool_name_match():
    """Test that tool name matches score high."""
    tool = Tool("Review", "gstack", "💻 Code", "Code review tool")
    keywords = ["review"]
    score = score_tool(tool, keywords)
    assert score > 0.5  # Should score well for name match


def test_score_tool_description_match():
    """Test description matching."""
    tool = Tool("MyTool", "Agent", "📦 Other", "This tool helps with security audits")
    keywords = ["security"]
    score = score_tool(tool, keywords)
    assert score > 0.3  # Should score for description match


def test_suggest_returns_top_n():
    """Test that suggest returns top N results."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review tool for finding bugs"),
        Tool("CSO", "gstack", "🔒 Security", "OWASP security audit"),
        Tool("Deploy", "gstack", "💻 Code", "Deploy to production"),
        Tool("WebSearch", "Claude Code", "🌐 Web", "Search the web"),
    ]
    catalog = Catalog(tools)

    # Request top 2 suggestions
    results = suggest(catalog, "review my code for bugs", top_n=2)
    assert len(results) <= 2


def test_suggest_min_score_filter():
    """Test that min_score filters results."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review tool"),
    ]
    catalog = Catalog(tools)

    # With low threshold, should get suggestions
    results = suggest(catalog, "review code", top_n=5, min_score=0.1)
    assert len(results) > 0

    # With high threshold, might filter out
    results = suggest(catalog, "xyz abc def", top_n=5, min_score=0.9)
    # Should be empty or very few results


def test_suggest_returns_score():
    """Test that suggestions include scores."""
    tools = [
        Tool("Review", "gstack", "💻 Code", "Code review tool for finding bugs"),
    ]
    catalog = Catalog(tools)

    results = suggest(catalog, "review my code", top_n=5)
    for tool, score in results:
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
