"""Tests for scanner module."""

from agentkit.scanner import scan_builtin_claude_code_tools, scan_all


def test_scan_builtin_tools():
    """Test that built-in tools are scanned."""
    tools = list(scan_builtin_claude_code_tools())
    assert len(tools) > 0

    # Check for known tools
    names = [t.name for t in tools]
    assert "Read" in names
    assert "Write" in names
    assert "Bash" in names


def test_scan_all_returns_list():
    """Test that scan_all returns a list."""
    tools = scan_all()
    assert isinstance(tools, list)
    assert len(tools) > 0  # Should at least have built-in tools


def test_scan_all_includes_builtin():
    """Test that scan_all includes built-in tools."""
    tools = scan_all()
    names = [t.name for t in tools]
    assert "Read" in names or "Write" in names  # At least some built-in tools
