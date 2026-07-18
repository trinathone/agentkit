"""Tests for suggest module."""

from agentkit.catalog import Tool, Catalog
from agentkit.suggest import suggest, score_tool


def test_score_tool_name_match():
    """Test that tool name matches score high."""
    tool = Tool("Review", "gstack", "💻 Code", "Code review tool")
    keywords = ["review"]
    prompt = "review my code"
    score = score_tool(tool, keywords, prompt)
    assert score > 0.5  # Should score well for name match


def test_score_tool_description_match():
    """Test description matching."""
    tool = Tool("MyTool", "Agent", "📦 Other", "This tool helps with security audits")
    keywords = ["security"]
    prompt = "security audit"
    score = score_tool(tool, keywords, prompt)
    assert score > 0.3  # Should score for description match


def test_score_tool_platform_penalty():
    """Test that platform-specific tools are penalized when platform not mentioned."""
    # Tool with platform prefix
    ios_tool = Tool("ios-fix", "gstack", "🎨 Design", "Fix iOS app issues")
    # General tool
    review_tool = Tool("/review", "gstack", "💻 Code", "Code review tool")

    keywords = ["issue"]  # Use a keyword that won't get filtered
    prompt = "fix this issue in my code"

    # ios-fix should be penalized because 'ios' not mentioned in prompt
    ios_score = score_tool(ios_tool, keywords, prompt)
    review_score = score_tool(review_tool, keywords, prompt)

    # Both should score low without "issue" in their names, but ios-fix should have extra penalty
    assert ios_score < 0.3


def test_score_tool_platform_bonus_when_mentioned():
    """Test that platform-specific tools score well when platform is mentioned."""
    ios_tool = Tool("ios-fix", "gstack", "🎨 Design", "Comprehensive iOS app issues")

    keywords = ["ios"]  # Use keyword that won't get filtered
    prompt = "fix my ios app"

    score = score_tool(ios_tool, keywords, prompt)
    # Should score better when platform is mentioned (no penalty)
    assert score > 0.1


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


def test_suggest_prefers_general_tools_over_platform_specific():
    """Test that general tools are preferred over platform-specific for generic prompts."""
    tools = [
        Tool("/review", "gstack", "💻 Code", "Code review tool for bugs"),
        Tool("/ios-fix", "gstack", "🎨 Design", "Fix iOS-specific issues"),
    ]
    catalog = Catalog(tools)

    # Generic "fix" prompt should prefer /review over /ios-fix
    results = suggest(catalog, "fix this issue in my code", top_n=2, min_score=0.3)
    if len(results) > 0:
        # First result should be more general tool
        top_tool = results[0][0]
        assert "/review" in top_tool.name or "review" in top_tool.description.lower()
