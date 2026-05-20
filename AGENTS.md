# AGENTS.md — exa-search-cli for AI Coding Agents

This file is for AI agents (Claude Code, Codex, Cursor, Windsurf, etc.) that need to install and use `exa-search-cli` on behalf of a user.

## Install & setup

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key   # get at exa.ai — free tier available
```

Persist the key:

```bash
echo 'export EXA_API_KEY=your-key' >> ~/.zshrc
```

## Commands

| Command | What it does |
|---|---|
| `exa-search <query>` | Neural web search. Understands meaning, not just keywords. |
| `exa-crawl <url>` | Fetch full readable text from a URL. No HTML. |
| `exa-research <topic>` | Submit a deep research task. Exa AI reads the web and synthesizes an answer. |

All commands support `--json` for structured output.

## Recommended agent patterns

```bash
# Search and get structured results
exa-search "topic" --json

# Extract just the URLs
exa-search "topic" --json | jq -r '.results[].url'

# Search + crawl the top result
exa-search "topic" --json | jq -r '.results[0].url' | xargs exa-crawl -c 6000

# Find pages similar to a URL (great for research)
exa-search --similar https://example.com --json

# Filter by content type
exa-search "AI benchmarks 2025" --category "research paper" --json

# Filter by domain
exa-search "query" --include-domain github.com --json

# Filter by date
exa-search "query" --start-date 2025-01-01 --json

# Deep research task
exa-research "topic" --json
```

## JSON output schemas

**exa-search --json**

```json
{
  "results": [
    {
      "title": "Page title",
      "url": "https://...",
      "published_date": "2025-01-15T00:00:00.000Z",
      "author": "Author name or null",
      "highlights": ["Relevant excerpt from the page..."],
      "text": "Full page text if --text was passed, else null"
    }
  ]
}
```

**exa-crawl --json**

```json
{
  "results": [
    {
      "url": "https://...",
      "title": "Page title",
      "text": "Full readable page content..."
    }
  ]
}
```

## All flags

**exa-search**

```
exa-search <query> [--similar <url>] [-n N] [-t auto|keyword|neural]
           [--text] [--json] [--category CATEGORY]
           [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
           [--include-domain d1,d2] [--exclude-domain d1,d2]
```

Categories: `news`, `tweet`, `github`, `paper`, `company`, `research paper`, `financial report`, `personal site`, `pdf`, `linkedin profile`

**exa-crawl**

```
exa-crawl <url> [-c MAX_CHARS] [--json]
```

**exa-research**

```
exa-research <topic> [-m exa-research|exa-research-pro] [--json]
```

## Rules for agents

- Keep CLI output stable and script-friendly.
- Do not break JSON output schemas without updating documentation.
- Prefer explicit errors over silent failures.
- Update `README.md`, `docs/USAGE.md`, and `llms.txt` when commands or install instructions change.
- Keep examples copy-pasteable.
- Do not rename terminal commands unless there is a strong reason.

## Properties

- **Stateless** — no local state written between calls
- **Read-only** — never modifies the web or local files
- **Exit codes** — `0` on success, non-zero on error (message printed to stderr)
- **Errors** — specific messages for auth failures, rate limits, network issues

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `EXA_API_KEY` | yes | API key from exa.ai |

## Documentation files

- `README.md`: human-facing overview and quickstart
- `llms.txt`: compact LLM-facing summary
- `docs/USAGE.md`: detailed command reference
- `CHANGELOG.md`: release notes
