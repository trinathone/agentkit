# AgentKit — Build Spec

## What is this
A CLI toolkit for AI coding agents. Two features:
1. `agentkit` — TUI table of every tool/skill the user actually has installed (auto-detected)
2. Popup suggestion hook — as user types a prompt in Claude Code, suggests relevant skills in real time

## The Problem
Developers using Claude Code, Codex, gstack, Cursor etc have 50-200 tools/skills available.
They forget 80% of them. When stuck, they guess or Google instead of using the right tool.
Nobody has built a cross-agent tool discovery layer.

## Part 1: `agentkit` CLI — Dynamic TUI Tool Table

### What it does
- Scans the user's machine for installed agents/skills
- Auto-detects: `~/.claude/skills/`, `~/.codex/`, `~/.hermes/skills/`, gstack skills, MCP servers in `~/.claude/settings.json`, Claude Code agents in `~/.claude/agents/`
- Builds a live Rich TUI table organized by category
- Filterable: `agentkit` (all), `agentkit file`, `agentkit web`, `agentkit code`, `agentkit memory`
- Works inside tmux split pane
- Shows: Tool name | Agent | Category | What it does (1 line) | How to invoke

### Scanner logic
For each source:
- `~/.claude/skills/*/SKILL.md` → parse frontmatter (name, description, tags)
- `~/.claude/agents/*.md` → parse frontmatter (name, description)
- `~/.claude/settings.json` → extract MCP server names + tools
- `~/.codex/skills/*/SKILL.md` → same as claude skills
- `~/.hermes/skills/**/*.md` → parse frontmatter
- gstack: `~/.claude/skills/gstack/*/SKILL.md` → name, description
- Built-in Claude Code tools: hardcoded list (Read, Write, Edit, Bash, WebSearch, WebFetch, etc.)
- Built-in Codex tools: hardcoded list

### Categories (auto-assigned by tags or keywords in description)
- 🗂 File — read, write, edit, patch files
- 🌐 Web — fetch, search, browse, scrape
- 💻 Code — review, test, lint, build, deploy
- 🧠 Memory — save, recall, session, context
- 🔒 Security — audit, scan, OWASP, secrets
- 🎨 Design — UI, CSS, mockup, visual
- 🤖 Agent — spawn, orchestrate, delegate subagents
- 📋 Plan — spec, review, architecture, plan mode
- ⚙️ System — bash, terminal, process, file system

### TUI Layout (Rich library)
```
┌─────────────────────────────────────────────────────────────────────┐
│  AgentKit v0.1 — 47 tools detected   filter: all   [q]quit [/]search│
├──────────────┬────────────┬──────────┬─────────────────────────────┤
│ Tool         │ Agent      │ Category │ What it does                │
├──────────────┼────────────┼──────────┼─────────────────────────────┤
│ /review      │ gstack     │ 💻 Code  │ Pre-PR bug review           │
│ /qa          │ gstack     │ 💻 Code  │ Real browser test + fix     │
│ /cso         │ gstack     │ 🔒 Sec   │ OWASP + STRIDE audit        │
│ Read         │ Claude Code│ 🗂 File  │ Read any file               │
│ Bash(git *)  │ Claude Code│ 💻 Code  │ Git commands only           │
│ WebSearch    │ Claude Code│ 🌐 Web   │ Search the web              │
│ agent-reach  │ Hermes     │ 🌐 Web   │ Reddit/Twitter/HN scraping  │
│ ...          │ ...        │ ...      │ ...                         │
└──────────────┴────────────┴──────────┴─────────────────────────────┘
Use arrow keys to navigate. Press Enter for full skill details.
```

### Interaction
- Arrow keys to navigate
- `/` to search/filter live
- Enter → shows full SKILL.md content for that tool
- `c` → copies invocation syntax to clipboard
- `q` → quit
- `agentkit <category>` → pre-filtered view

## Part 2: Prompt Suggestion Hook (Claude Code UserPromptSubmit hook)

### What it does
As the user finishes typing a prompt in Claude Code — before Claude processes it —
the hook reads the prompt text, fuzzy-matches it against all known skills,
and if confident (score > 0.6) shows a suggestion box:

```
┌─ AgentKit suggests ──────────────────────────────┐
│ 💡 For "check this code for security issues":     │
│   → /cso  (OWASP + STRIDE security audit)         │
│   → /review  (Pre-PR bug review)                  │
│ Press Tab to accept, Esc to dismiss               │
└──────────────────────────────────────────────────┘
```

### How the hook works
File: `~/.claude/hooks/agentkit-suggest.sh`

1. Reads `CLAUDE_TOOL_INPUT` env var (contains the prompt JSON)
2. Calls `agentkit suggest "<prompt text>"` which:
   - Loads the tool catalog
   - Scores each tool against the prompt using keyword + TF-IDF matching
   - Returns top 2-3 matches as JSON if score > 0.6
3. If suggestions found: prints them to stderr (Claude Code shows stderr as status messages)
4. Always exits 0 (never blocks the prompt)

### Scoring algorithm (no LLM, pure keyword matching)
- Extract keywords from prompt
- Match against: tool name, description, tags, category
- Score = (keyword_hits / total_keywords) * weight
  - Name match: weight 3x
  - Tag match: weight 2x  
  - Description match: weight 1x
- Return tools where score > 0.6
- Cap at 3 suggestions

### Hook installation
The `agentkit install-hook` command adds to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "agentkit suggest-hook",
        "timeout": 2
      }]
    }]
  }
}
```

IMPORTANT: Must APPEND to existing UserPromptSubmit hooks, never replace.
Read existing settings.json, merge the new hook into the array, write back.

## File Structure
```
agentkit/
├── agentkit/
│   ├── __init__.py
│   ├── cli.py          — click CLI entry point
│   ├── scanner.py      — auto-detect installed agents/skills
│   ├── catalog.py      — Tool dataclass, category assignment, catalog builder  
│   ├── tui.py          — Rich TUI table with navigation
│   ├── suggest.py      — fuzzy match prompt → suggest tools
│   ├── hook.py         — Claude Code hook handler (reads CLAUDE_TOOL_INPUT)
│   └── installer.py    — install-hook command, modifies settings.json safely
├── tests/
│   ├── test_scanner.py
│   ├── test_suggest.py
│   └── test_catalog.py
├── pyproject.toml      — pip installable, entry point: agentkit = agentkit.cli:main
├── README.md
└── .gitignore
```

## Stack
- Python 3.11
- `rich` — TUI table, live display, panels
- `click` — CLI
- `textual` — if we want full TUI app with keyboard nav (optional, try rich first)
- `frontmatter` — parse SKILL.md YAML headers
- `rapidfuzz` — fast fuzzy matching for search
- NO external API calls, NO LLM, fully offline

## Entry points (pyproject.toml)
```
[project.scripts]
agentkit = "agentkit.cli:main"
```

Install: `pip install -e .` or `pipx install .`

## Commands
```
agentkit              # show all tools TUI
agentkit file         # filter by category
agentkit search auth  # search across all tools
agentkit suggest "check for security issues"   # get suggestions for a prompt
agentkit install-hook  # wire into Claude Code UserPromptSubmit
agentkit scan         # re-scan and refresh catalog
agentkit --version
```

## README style
- Plain English first
- Lead with: "You have 50+ tools. You remember 10. AgentKit shows you the rest."
- 4 real use cases
- Quick start under 3 commands
- Stack at bottom
- MIT license

## Git identity
- user.name = Trinath Reddy
- user.email = trinath.mih@gmail.com

## Priority
- Part 1 (TUI) must fully work end-to-end with real scanning
- Part 2 (hook) must work — test it with a real Claude Code session
- ALL tests must pass
- README must be complete
- Push to GitHub as `trinathone/agentkit`

## After build
1. `pip install -e .` in the repo
2. Run `agentkit` — must show real tools from this machine
3. Run `agentkit suggest "review my code for bugs"` — must return /review and /cso
4. Run `agentkit install-hook` — must add hook to ~/.claude/settings.json WITHOUT breaking zap/ponytail hooks
5. Push to GitHub
6. Print the GitHub URL

## ADDITIONAL: Open Source + gstack team mode integration

### Open Source setup (do this after the build)
1. Create `LICENSE` — MIT license, copyright "Trinath Reddy"
2. Create `.github/workflows/ci.yml` — runs tests on push (python 3.11, pip install -e ., pytest)
3. Create `CONTRIBUTING.md` — how to add a new agent scanner (simple: write a scanner class, register it)
4. Create `AGENTS.md` — explain how agentkit works for AI agents (like gstack's AGENTS.md)
5. Add gstack team mode: run `~/.claude/skills/gstack/bin/gstack-team-init optional` from ~/repos/agentkit — this adds `.claude/` dir with gstack skills for anyone who clones the repo

### gstack team mode integration
Run this from ~/repos/agentkit:
```bash
~/.claude/skills/gstack/bin/gstack-team-init optional
git add .claude/ CLAUDE.md
```
This means anyone who clones agentkit and uses Claude Code gets gstack skills automatically.

### GitHub repo setup
```bash
gh repo create trinathone/agentkit --public --description "Cross-agent tool discovery CLI — see all your AI coding tools in one place, get suggestions while you type" --push
```
Add topics: `claude-code`, `codex`, `ai-agents`, `developer-tools`, `cli`, `python`, `open-source`

### The open source angle in README
Add a section: "Add your agent"
Show how to write a 20-line scanner class to support a new agent.
This invites contributions from Cursor users, Factory users, Kiro users, etc.
Each contributed scanner = that agent's community discovers agentkit.

## PART 3 — Real-time ghost text suggestions (PRIORITY — build this next)

### What it is
A wrapper CLI called `akit` that replaces typing `claude` directly.
User types `akit` → gets a custom prompt input → as they type their prompt,
ghost text appears AFTER their cursor in gray showing best tool suggestion.
Suggestion updates on every keystroke. On Enter — real `claude` runs with their prompt.

### Tech: prompt_toolkit
Use Python `prompt_toolkit` library — same library fish shell uses for ghost completions.
It has native AutoSuggest support that shows dimmed text after cursor.

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion

class ToolSuggest(AutoSuggest):
    def get_suggestion(self, buffer, document):
        text = document.text
        if len(text) < 3:
            return None
        tools = suggest(text, catalog, top_n=1)
        if tools:
            return Suggestion(f"  →  {tools[0].invoke}")
        return None
```

### UX behavior
- Fewer than 3 chars typed: no suggestion
- 3+ chars: gray ghost text after cursor: `  →  /review`
- Multiple tools: `  →  /review, /cso`
- User keeps typing: suggestion updates live every keystroke
- Tab: accepts suggestion (appends it to prompt? or just shows it?)
- Enter: runs real claude with the original prompt (NOT the suggestion — suggestion is informational only)
- Ctrl+C: exits

### The akit command flow
```
akit                    → launches custom prompt session with ghost suggestions
akit -p "task"          → passes directly to claude -p (no interactive, no suggestions needed)
akit --install-alias    → adds `alias claude=akit` to ~/.zshrc
```

### After prompt submitted
1. Show which tool was suggested (brief flash: "💡 Suggested: /review")
2. Launch real claude with the user's prompt: `os.execvp("claude", ["claude"] + original_args)`
3. `execvp` replaces the process — user is now inside real Claude Code, no wrapper overhead

### Add to pyproject.toml entry points
```
[project.scripts]
agentkit = "agentkit.cli:main"
akit = "agentkit.wrapper:main"
```

### File to create: agentkit/wrapper.py
Full prompt_toolkit session with ToolSuggest class.
Load catalog once at startup (fast — filesystem scan ~100ms).
Pass all sys.argv after prompt to real claude binary.

### Dependencies to add to pyproject.toml
```
"prompt_toolkit>=3.0",
```

### Test
```
pip install -e .
akit
# Type "check my code" → should see →  /review in gray after cursor
# Type "security audit" → should see →  /cso in gray
# Press Enter → real claude launches
```

### DO NOT break existing agentkit command. This is additive only.
