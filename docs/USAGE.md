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
| `-n` / `--num-results` | `8` | Number of results (1–100) |
| `-t` / `--type` | `auto` | `auto` · `lite` · `fast` · `instant` · `deep-lite` · `deep` · `deep-reasoning` · `keyword` · `neural` |
| `--text` | off | Fetch page text; terminal preview defaults to 2000 characters |
| `--max-chars` | — | Text limit per result, used with `--text` |
| `--category` | — | Content type filter (see below) |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include only |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Structured JSON output |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

**Categories:** `publication` · `people` · `company` · `news` · `personal site` · `financial report`. Legacy flags remain accepted; `paper` and `research paper` map to `publication`.

**Examples:**

```bash
exa-search "best rust web frameworks" -n 5
exa-search "AI agents 2025" --category news --start-date 2025-01-01
exa-search "pytorch docs" --include-domain pytorch.org
exa-search "startup pitch deck" --exclude-domain slideshare.net
exa-search --similar https://github.com/astral-sh/uv
exa-search "ml papers" --category publication --json | jq '.'
```

---

### exa-crawl

```
exa-crawl <url> [<url> ...] [options]
```

| Flag | Default | Description |
|---|---|---|
| `-c` / `--max-chars` | `5000` | Max characters to return |
| `--json` | off | Structured JSON output |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

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
| `-m` / `--model` | `exa-research` | `exa-research-fast` · `exa-research` · `exa-research-pro` |
| `--json` | off | Structured JSON output |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

**Examples:**

```bash
exa-research "explain transformer attention mechanisms"
exa-research "quantum computing current state" --model exa-research-pro
exa-research "topic" --json
```

`exa-research` only submits the task — it prints a `research_id` and returns immediately. Use `exa-research-status` to check progress and fetch the result.

---

### exa-research-status

```
exa-research-status <research-id> [options]
```

| Flag | Default | Description |
|---|---|---|
| `--json` | off | Structured JSON output |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

**Examples:**

```bash
exa-research-status r_01k...
exa-research-status r_01k... --json
```

Status is one of `pending`, `running`, `completed`, `failed`, `canceled`. When `completed`, the synthesized answer is printed (or available at `.output.content` in `--json` mode). When `failed`, the error message is printed (`.error` in JSON).

---

## Piping and scripting

```bash
# Extract all URLs from search results.
# The jq normalizer handles both the documented {"results": [...]} object
# and older/mixed top-level result arrays.
exa-search "rust async runtimes" --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'

# Find similar pages and collect their text
exa-search --similar https://example.com --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[] | .url' \
  | head -3 \
  | xargs -I{} exa-crawl {}

# Search + crawl first result
exa-search "pytorch tutorial" --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[0].url // empty' \
  | xargs exa-crawl -c 8000

# Bulk domain-filtered search to file
exa-search "API design" --include-domain github.com --json > results.json

# Filter results by domain in jq
exa-search "frameworks" --json \
  | jq '[(if type=="array" then . else (.results // []) end)[] | select(.url | test("github\\.com"))]'
```

## Environment

| Variable | Required | Description |
|---|---|---|
| `EXA_API_KEY` | yes | Your Exa API key from exa.ai |

## Research workflow and reliability (0.1.6)

```bash
# Scholarly publication index; legacy paper/research paper flags map to publication.
exa-search "artificial intelligence public procurement systematic review" --category publication -n 10 --json

# Retrieve bounded text directly, without a second content request.
exa-search "AI procurement risk assessment" --text --max-chars 8000 -n 5 --json

# Read several selected sources in one contents request (up to 100 URLs).
exa-crawl https://example.com/article-a https://example.com/article-b -c 12000 --json

exa-search --version
exa-crawl https://example.com --timeout 90
```

All four commands support `--timeout SECONDS` (default 60, positive finite HTTP
connect/read timeout) and `--version`. Exa calls are not automatically replayed.
Search defaults to `auto` and highlights only; `--text` requests text instead of
highlights. `lite` is the current low-latency mode. Older type and category flags
remain accepted. Current categories are `publication`, `people`, `company`,
`news`, `personal site`, and `financial report`; other legacy categories are API
hints. `paper` and `research paper` are aliases for `publication`.

`-n` accepts 1–100. Dates must be valid `YYYY-MM-DD` values in ascending order; the range includes
both complete days in UTC.
Company/people categories do not support date filters; people also disallows
excluded domains. Invalid arguments fail before authentication or network calls.
`--max-chars` requires `--text`. It caps requested text and the terminal preview;
without it the terminal search preview is 2000 characters. Crawl terminal output
honors `-c` and preserves paragraphs. JSON keeps the existing `{ "results": [...] }`
envelope and available API metadata, including per-URL `statuses`. Partial crawl
failures produce a diagnostic on stderr; if every URL fails, the exit code is 1.
API/network errors go to stderr with a nonzero exit and no traceback or API key.
Argument errors use exit code 2. A successful search with no matches remains
successful. Search discovers sources; verify titles, DOI, authors and dates at
the publisher or repository before citing them. Crawl extracts text and does not
save the original PDF.

API contract checked against [Exa Search](https://exa.ai/docs/reference/search)
and [Contents](https://exa.ai/docs/reference/contents) on 2026-10-28.
