# exa-search-cli — Full Documentation

← [Back to README](../README.md)

## Install

```bash
uv tool install exa-search-cli   # recommended
pip install exa-search-cli       # or pip
```

```bash
export EXA_API_KEY=your-key   # exa.ai → API Keys
```

## Commands

### exa-search

```
exa-search [query] [options]
exa-search --similar <url> [options]
```

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | `8` | Number of results |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | off | Fetch and display full page text |
| `--category` | — | Content type filter (see below) |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include only |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Raw JSON output |

**Categories:** `news` · `tweet` · `github` · `paper` · `company` · `research paper` · `financial report` · `personal site` · `pdf` · `linkedin profile`

**Examples:**

```bash
exa-search "best rust web frameworks" -n 5
exa-search "AI agents 2025" --category news --start-date 2025-01-01
exa-search "pytorch docs" --include-domain pytorch.org
exa-search "startup pitch deck" --exclude-domain slideshare.net
exa-search --similar https://github.com/astral-sh/uv
exa-search "ml papers" --category "research paper" --json | jq '.'
```

---

### exa-crawl

```
exa-crawl <url> [options]
```

| Flag | Default | Description |
|---|---|---|
| `-c` / `--max-chars` | `5000` | Max characters to return |
| `--json` | off | Raw JSON output |

**Examples:**

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

---

### exa-research

```
exa-research <topic> [options]
```

| Flag | Default | Description |
|---|---|---|
| `-m` / `--model` | `exa-research` | `exa-research` or `exa-research-pro` |
| `--json` | off | Raw JSON output |

**Examples:**

```bash
exa-research "explain transformer attention mechanisms"
exa-research "quantum computing current state" --model exa-research-pro
exa-research "topic" --json
```

---

## Piping and scripting

```bash
# Extract all URLs from search results
exa-search "rust async runtimes" --json | jq -r '.results[].url'

# Find similar pages and collect their text
exa-search --similar https://example.com --json \
  | jq -r '.results[].url' \
  | head -3 \
  | xargs -I{} exa-crawl {}

# Search + crawl first result
exa-search "pytorch tutorial" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 8000

# Bulk domain-filtered search to file
exa-search "API design" --include-domain github.com --json > results.json

# Filter results by domain in jq
exa-search "frameworks" --json \
  | jq '[.results[] | select(.url | test("github\\.com"))]'
```

## Environment

| Variable | Required | Description |
|---|---|---|
| `EXA_API_KEY` | yes | Your Exa API key from exa.ai |
