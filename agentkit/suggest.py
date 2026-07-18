"""Suggest tools based on prompt text."""

from rapidfuzz import fuzz

from .catalog import Tool, Catalog


def score_tool(tool: Tool, keywords: list[str]) -> float:
    """Score how well a tool matches the keywords (0.0 to 1.0)."""
    if not keywords:
        return 0.0

    full_text = (
        f"{tool.name} {tool.description} {' '.join(tool.tags)}"
    ).lower()

    total_score = 0.0
    for keyword in keywords:
        keyword = keyword.lower()

        # Name match (weight 3x)
        if keyword in tool.name.lower():
            total_score += 0.3  # Out of 1.0 per keyword

        # Tag match (weight 2x)
        for tag in tool.tags:
            if keyword in tag.lower():
                total_score += 0.2

        # Description fuzzy match (weight 1x)
        sim = fuzz.partial_ratio(keyword, full_text) / 100.0
        total_score += sim * 0.5  # Cap at 0.5

    # Normalize to 0.0-1.0 by keyword count
    max_score = len(keywords)  # Each keyword can contribute up to 1.0
    normalized = min(1.0, total_score / len(keywords)) if keywords else 0.0
    return normalized


def suggest(catalog: Catalog, prompt: str, top_n: int = 3, min_score: float = 0.6) -> list[tuple[Tool, float]]:
    """
    Suggest tools for a prompt.

    Args:
        catalog: The tool catalog
        prompt: User's prompt text
        top_n: Return at most this many suggestions
        min_score: Only return tools with score >= this

    Returns:
        List of (Tool, score) tuples, sorted by score descending
    """
    # Extract simple keywords from prompt
    stop_words = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'for', 'from', 'to',
        'in', 'on', 'at', 'by', 'this', 'that', 'with', 'and', 'or', 'not',
        'i', 'you', 'we', 'they', 'my', 'your', 'should', 'could', 'would',
        'can', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'been',
    }

    words = prompt.lower().split()
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]

    # Score all tools
    scores = [
        (tool, score_tool(tool, keywords))
        for tool in catalog.tools
    ]

    # Filter and sort
    results = [
        (tool, score) for tool, score in scores
        if score >= min_score
    ]
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_n]
