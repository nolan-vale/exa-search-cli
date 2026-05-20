# exa-cli

Command-line interface for [Exa](https://exa.ai) — the web search API built for AI applications.

Three commands: **search**, **crawl**, **research**.

## Install

```bash
# Recommended: uv tool (isolated, no venv needed)
uv tool install exa-cli

# Or pip
pip install exa-cli
```

## Setup

Get your API key at [exa.ai](https://exa.ai) and export it:

```bash
export EXA_API_KEY=your-key-here
```

Add to `~/.zshrc` or `~/.bashrc` to persist.

## Commands

### exa-search

```bash
# Basic search
exa-search "python async frameworks"

# Limit results
exa-search "rust web" -n 5

# Filter by content type
exa-search "latest AI papers" --category "research paper"
exa-search "AI startup news" --category news --start-date 2024-01-01

# Domain filters
exa-search "documentation" --include-domain docs.python.org,docs.rs
exa-search "tutorials" --exclude-domain medium.com,dev.to

# Find similar pages
exa-search --similar https://github.com/astral-sh/uv

# Fetch full page text
exa-search "transformer architecture" --text

# JSON output (for pipelines / jq)
exa-search "query" --json | jq '.'
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | 8 | Number of results |
| `-t` / `--type` | `auto` | Search type: `auto`, `keyword`, `neural` |
| `--text` | off | Fetch and show full page text |
| `--category` | — | Content type filter (see below) |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Raw JSON output |

**Categories:** `news`, `tweet`, `github`, `paper`, `company`, `research paper`, `financial report`, `personal site`, `pdf`, `linkedin profile`

### exa-crawl

Extract full content from a URL:

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

| Flag | Default | Description |
|---|---|---|
| `-c` / `--max-chars` | 5000 | Max characters to return |
| `--json` | off | Raw JSON output |

### exa-research

AI-powered deep research task:

```bash
exa-research "explain transformer attention mechanisms"
exa-research "quantum computing current state" --model exa-research-pro
exa-research "topic" --json
```

| Flag | Default | Description |
|---|---|---|
| `-m` / `--model` | `exa-research` | Model: `exa-research` or `exa-research-pro` |
| `--json` | off | Raw JSON output |

## Piping and scripting

```bash
# Extract URLs from search results
exa-search "rust async runtimes" --json | jq -r '.results[].url'

# Crawl multiple URLs from a list
cat urls.txt | xargs -I{} exa-crawl {}

# Search + crawl pipeline
exa-search "pytorch tutorial" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 8000
```

## Requirements

- Python 3.11+
- `EXA_API_KEY` environment variable
