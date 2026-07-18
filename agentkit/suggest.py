"""Suggest tools based on prompt text."""

from rapidfuzz import fuzz

from .catalog import Tool, Catalog


# Platform keywords
PLATFORMS = {'ios', 'macos', 'android', 'windows', 'linux', 'web', 'mobile'}

# Intent anchors: keywords that strongly indicate a tool category
# Maps intent keywords to tool name patterns that should be boosted
INTENT_BOOSTERS = {
    # Fix/bug/issue → investigation and review tools
    frozenset(['fix', 'bug', 'issue', 'broken', 'error', 'crash']): frozenset(['investigate', 'review']),
    # Security/audit → security tools (CSO is the primary security tool)
    frozenset(['security', 'audit', 'vulnerability', 'owasp', 'scan']): frozenset(['cso', 'security-audit']),
    # Test/QA → testing tools
    frozenset(['test', 'qa', 'browser', 'click', 'e2e', 'integration']): frozenset(['qa', 'test']),
    # Review/PR → code review tools
    frozenset(['review', 'pr', 'pull', 'request', 'diff', 'merge']): frozenset(['review']),
    # Deploy/ship → deployment tools
    frozenset(['deploy', 'ship', 'push', 'release', 'production']): frozenset(['ship', 'deploy']),
}


def _is_platform_mentioned(prompt: str, platform: str) -> bool:
    """Check if a platform is explicitly mentioned in the prompt."""
    return platform.lower() in prompt.lower()


def _has_platform_prefix(tool_name: str) -> str:
    """Return the platform prefix if tool has one, else None."""
    tool_lower = tool_name.lower().lstrip('/')  # Remove leading slash if present
    for platform in PLATFORMS:
        if tool_lower.startswith(platform + '-'):
            return platform
    return None


def _get_intent_boost(prompt: str, tool: Tool) -> float:
    """Return a boost score if tool matches detected intents in prompt."""
    prompt_lower = prompt.lower()
    tool_lower = tool.name.lower().lstrip('/')

    boost = 0.0
    for intent_keywords, tool_patterns in INTENT_BOOSTERS.items():
        # Check if any intent keywords are in the prompt
        if any(keyword in prompt_lower for keyword in intent_keywords):
            # Check if tool matches any of the patterns
            for pattern in tool_patterns:
                pattern_clean = pattern.lstrip('/')
                # Exact word match in tool name is strong signal
                if pattern_clean in tool_lower.split('-'):
                    # Special case: CSO for security gets highest boost
                    if pattern_clean == 'cso':
                        boost = max(boost, 0.5)
                    else:
                        boost = max(boost, 0.4)  # Strong boost for primary intent tool
                    break
                # Substring match also gets a boost
                elif pattern_clean in tool_lower:
                    boost = max(boost, 0.3)
                    break

    return boost


def score_tool(tool: Tool, keywords: list[str], prompt: str) -> float:
    """Score how well a tool matches the keywords (0.0 to 1.0)."""
    if not keywords:
        # Even with no keywords, check intent boosters
        return min(1.0, _get_intent_boost(prompt, tool))

    full_text = (
        f"{tool.name} {tool.description} {' '.join(tool.tags)}"
    ).lower()

    total_score = 0.0
    for keyword in keywords:
        keyword = keyword.lower()

        # Name match (weight 3x) — but penalize very short substring matches
        if keyword in tool.name.lower():
            # Exact word match in name is strong signal
            if keyword in tool.name.lower().split('-'):
                total_score += 0.3
            # Substring match (e.g., "fix" in "ios-fix") is weaker
            elif len(keyword) >= 4:
                total_score += 0.2
            # Very short substrings are often noise (e.g., "fix" matching many tools)
            else:
                total_score += 0.05

        # Tag match (weight 2x)
        for tag in tool.tags:
            if keyword in tag.lower():
                total_score += 0.2

        # Description fuzzy match (weight 1x)
        sim = fuzz.partial_ratio(keyword, full_text) / 100.0
        total_score += sim * 0.5  # Cap at 0.5

    # Normalize to 0.0-1.0 by keyword count
    normalized = min(1.0, total_score / len(keywords)) if keywords else 0.0

    # Apply platform penalty: if tool has platform prefix and platform not mentioned, penalize
    platform = _has_platform_prefix(tool.name)
    if platform and not _is_platform_mentioned(prompt, platform):
        # Apply 50% penalty for platform-specific tools when platform not mentioned
        normalized *= 0.5

    # Apply intent boost
    normalized = min(1.0, normalized + _get_intent_boost(prompt, tool))

    return normalized


def suggest(catalog: Catalog, prompt: str, top_n: int = 3, min_score: float = 0.15) -> list[tuple[Tool, float]]:
    """
    Suggest tools for a prompt.

    Args:
        catalog: The tool catalog
        prompt: User's prompt text
        top_n: Return at most this many suggestions
        min_score: Only return tools with score >= this (default: 0.15)

    Returns:
        List of (Tool, score) tuples, sorted by score descending
    """
    # Extract simple keywords from prompt
    stop_words = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'for', 'from', 'to',
        'in', 'on', 'at', 'by', 'this', 'that', 'with', 'and', 'or', 'not',
        'i', 'you', 'we', 'they', 'my', 'your', 'should', 'could', 'would',
        'can', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'been', 'issue',
        'code', 'help', 'check', 'fix',  # Common words that aren't discriminating
    }

    words = prompt.lower().split()
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]

    # Score all tools
    scores = [
        (tool, score_tool(tool, keywords, prompt))
        for tool in catalog.tools
    ]

    # Filter and sort
    results = [
        (tool, score) for tool, score in scores
        if score >= min_score
    ]
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_n]
