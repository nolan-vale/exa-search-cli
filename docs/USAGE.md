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
| `--objective` | — | Broader search goal and source preferences; 1–4096 characters, not blank |
| `--max-age-hours` | — | Content freshness: `0` fresh fetch, `-1` cache only, `1–720` max age |
| `--category` | — | Content type filter (see below) |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include only |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Structured JSON output |
| `--compact` | off | One-line source JSON without empty/decorative fields; implies `--json` |
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
| `--query` | — | Query-focused highlights instead of opening page text; `-c` caps excerpts per URL |
| `--max-age-hours` | — | Content freshness: `0` fresh fetch, `-1` cache only, `1–720` max age |
| `--json` | off | Structured JSON output |
| `--compact` | off | One-line source JSON without empty/decorative fields; implies `--json` |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

**Examples:**

```bash
exa-crawl https://example.com
exa-crawl https://arxiv.org/abs/2303.08774 -c 10000
exa-crawl https://example.com --json
```

---

### exa-agent

```bash
exa-agent "Compare home watch providers in Tampa Bay" --max-cost 1 --dry-run
exa-agent "Compare home watch providers in Tampa Bay" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
exa-agent-cancel agent_run_REPLACE_WITH_RETURNED_ID --json
```

`exa-agent` creates an asynchronous run through `POST /agent/runs` and returns
immediately. No polling, retry, premium data source, or follow-up run is added
implicitly. The returned `id` is the identifier for status and cancellation.
Creating a run is usage-billed; dry runs do not authenticate or access the network.

| Flag | Default | Description |
|---|---|---|
| `--effort` | `auto` | `minimal`, `low`, `medium`, `high`, `xhigh`, `auto`, `ultra` |
| `--max-cost USD` | API default | Finite $1–$100 spend cap; only `auto` and `ultra` |
| `--system-prompt` | — | Source preferences and output instructions |
| `--output-schema FILE` | — | UTF-8 JSON Schema object for structured output |
| `--dry-run` | off | Print method/path/body without creating a run or reading credentials |
| `--json` | off | Native Agent API run object, including output, citations, cost and stop reason |
| `--timeout` | `60` | Network connect/read timeout; not the Agent's execution duration |
| `--version` | — | Local package version, not an API health check |

Exa currently defaults to a $5 cap for `auto` and $20 for `ultra` if the cap is
omitted; other effort tiers use provider pricing. `--output-schema` checks JSON
syntax and object shape locally; the server validates the schema itself.

### exa-agent-status and exa-agent-cancel

Both accept one Agent run ID and `--json`, `--timeout`, `--version`.
Status makes one `GET /agent/runs/{id}` call. Cancellation makes one
`POST /agent/runs/{id}/cancel` call. They do not start or continue a research task.

Agent states are `queued`, `running`, `completed`, `failed`, and `cancelled`.
Completed output is in `output.text`, `output.structured`, and `output.grounding`.
Agent JSON preserves API field names such as `costDollars` and `stopReason`.
`budget_reached` can accompany `completed` and partial results: inspect the stop
reason before treating the result as exhaustive. A failed run exits 1 after
printing its response; cancelled runs can be retrieved normally.

### Retired exa-research and exa-research-status

Exa retired `/research`; all three old model names used that endpoint.
These commands remain installed so existing scripts receive a clear migration
error (exit 1), with no authentication, network call, or automatic paid Agent run.
Old `research_id` values and `output.content` do not describe the new Agent API.
`--help` and `--version` still work locally and do not establish service health.

See [Exa changelog](https://exa.ai/docs/changelog),
[Agent guide](https://exa.ai/docs/agent/quickstart), and
[Create a run](https://exa.ai/docs/reference/agent-api/create-a-run).

Validation scope: create/get/cancel are covered by SDK wire-contract and response
tests; Agent API access was checked using a live read-only request. No paid Agent
run was submitted or completed as part of this release validation.

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

All commands support `--timeout SECONDS` (default 60, positive finite HTTP
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

## Focused retrieval and compact output

```bash
# Share the research goal with Exa as well as the literal query.
exa-search "home watch Tampa Bay pricing" -n 5 \
  --objective "Prefer original local provider pricing pages, not directories." \
  --compact

# Read the relevant passage even if it is far beyond the first 12000 characters.
exa-crawl https://www2.myfloridalicense.com/electrical-contractors/faqs/ \
  --query "Is a license required to install low voltage network wiring?" \
  -c 2500 --compact

# Refresh prices when content is older than a day; cache-only for repeatable reading.
exa-crawl https://example.com/pricing --max-age-hours 24 --json
exa-crawl https://example.com/article --max-age-hours -1 --compact
```

`--objective` describes the task beyond the query: preferred sources, exclusions,
and facts to extract. It is passed directly to the search API; it does not turn
preferences into hard filters or independently verify sources. It must not be
blank, is limited to 4096 characters, and is not supported with `--similar`.

`exa-crawl --query QUESTION` requests `highlights` with that question and the
`--max-chars` budget. It explicitly sets `text=false`, preventing the SDK from
also requesting full page text. The question is applied to every URL in a batch.
Without `--query`, the existing bounded full-text behavior remains. Excerpts can
omit qualifications; read more context before drawing conclusions. No summary
or separate research task is requested.

`--max-age-hours` sets the age of retrieved content, not its publication date.
Omitting it preserves the API cache/fetch default. `-1` uses cache only, `0`
requests a fresh fetch, and `1–720` uses cache only while younger than that many
hours. Fresh fetches can take longer or fail for an inaccessible page; inspect
the returned per-URL statuses. Search `--type lite` rejects this option before
making a request because that mode does not support it, including `-1`.

`--compact` is an opt-in JSON view for search and crawl, usable alone or with
`--json`. The top-level `results` array remains present, even when empty. Empty
strings, nulls, empty lists/dicts, duplicate `id=url`, `image`, `favicon`, and
`highlight_scores` are removed. Nonempty content, extended source fields,
warnings, notices, costs, and statuses remain; zero and false values are retained.
JSON is printed on one line. Standard `--json` keeps the full existing schema.

For explicitly capped search text and normal crawl text, reaching the character
limit produces an stderr diagnostic: the page may be incomplete. This is a
heuristic, not a claim that more content definitely exists. It does not trigger
another paid call or alter JSON. Use a focused question or increase the cap.
Highlights are excerpts by design, so they do not produce a full-page warning.

Parameters checked against [Search](https://exa.ai/docs/reference/search) and
[Contents](https://exa.ai/docs/reference/get-contents) on 2026-10-30.
