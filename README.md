# exa-search-cli

**Research automation through a command-line integration with [Exa](https://exa.ai): search, page-text retrieval, and research tasks.**

[中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=334155&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-334155.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-6B705C.svg)](LICENSE)

## Practical purpose

Turn recurring web research into a repeatable workflow: find relevant sources, retrieve readable text, and pass structured results to scripts or AI agents. Potential uses include gathering background information, comparing sources, and preparing research inputs for a document or decision.

Exa supplies the underlying search and research services. This repository is a focused CLI integration, not a new search engine or AI model.

## Project contribution

Built with AI coding agents as part of [Nolan Vale's](https://github.com/nolan-vale) independent product and workflow-automation work. My contribution is defining the task and interface, directing AI-assisted implementation, checking results, and iterating. **Nolan Vale Tools** is the label for these independent public projects.

## What it does

Five active commands wrap Exa services; two retired Research commands remain as migration helpers:

| Command | Purpose |
|---|---|
| `exa-search` | Search the web or find pages similar to a reference URL |
| `exa-crawl` | Retrieve readable page text or query-focused excerpts through Exa |
| `exa-agent` | Create an asynchronous, usage-billed Agent run |
| `exa-agent-status` | Retrieve an Agent run, its output, sources, and cost |
| `exa-agent-cancel` | Cancel a queued or running Agent run |
| `exa-research`, `exa-research-status` | Retired API; exit with migration guidance without a network call |

The commands support `--json` for scripts and AI-agent workflows. Search can be narrowed by date, domain, and content category. Retrieval depends on the provider and the accessibility of the source; it is not guaranteed to work for every URL.

## Installation

```bash
uv tool install exa-search-cli
```

Alternatively, use `pip install exa-search-cli` in a suitable Python environment.

## Quick start

Obtain an Exa API key and keep it out of source control:

```bash
export EXA_API_KEY=your-key-here
exa-search "document processing workflow" --json
```

## Usage

```bash
# Search
exa-search "vision language models" -n 10

# Find similar pages
exa-search --similar https://github.com/astral-sh/uv

# Filter by content type and publication date
exa-search "AI papers" --category publication --start-date 2025-01-01

# Include or exclude domains
exa-search "documentation" --include-domain docs.python.org,docs.rs
exa-search "tutorial" --exclude-domain medium.com,dev.to

# Retrieve page text
exa-crawl https://example.com -c 8000

# Submit and retrieve an external research task
exa-agent "document review workflow approaches" --max-cost 1
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID

# Extract URLs from structured output
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

### Search flags

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | `8` | Number of results (1–100) |
| `-t` / `--type` | `auto` | `auto` · `lite` · `fast` · `instant` · `deep-lite` · `deep` · `deep-reasoning` · `keyword` · `neural` |
| `--text` | off | Fetch page text; terminal preview defaults to 2000 characters |
| `--max-chars` | — | Text limit per result, used with `--text` |
| `--objective` | — | Broader search goal and source preferences, up to 4096 characters |
| `--max-age-hours` | — | Content freshness: `0` fresh fetch, `-1` cache only, `1–720` max age |
| `--category` | — | `publication` · `people` · `company` · `news` · `personal site` · `financial report`; legacy flags remain accepted |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Structured JSON output |
| `--compact` | off | Compact source JSON; implies `--json` |
| `--timeout` | `60` | HTTP connect/read timeout in seconds |
| `--version` | — | Show package version without authentication |

Other options:

- **`exa-crawl`:** `-c` / `--max-chars` (default `5000`), `--query`, `--max-age-hours`, `--json`, `--compact`, `--timeout`, `--version`.
- **`exa-agent`:** `--effort`, `--max-cost`, `--system-prompt`, `--output-schema`, `--dry-run`, `--json`.
- **`exa-agent-status`, `exa-agent-cancel`:** Agent run ID, `--json`, `--timeout`, `--version`.
- **`exa-research`, `exa-research-status`:** deprecated migration helpers; they never create Agent runs.

See [full usage documentation](docs/USAGE.md) and the installed commands' `--help` for additional details.

## Research API migration

Exa retired `/research`; a working search key does not restore that endpoint.
Use `exa-agent` for new asynchronous Agent runs. Old Research model names and IDs
are not automatically converted into a differently billed Agent request.
See [Exa's changelog](https://exa.ai/docs/changelog) and
[Agent guide](https://exa.ai/docs/agent/quickstart).

```bash
# Preview the exact create body without a key or network call.
exa-agent "Compare local home watch providers" --max-cost 1 --dry-run

# Explicitly submit a billed run, then save the returned ID.
exa-agent "Compare local home watch providers" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
```

Agent creation returns immediately and does not poll or retry automatically.
Completed output uses `output.text`, `output.structured`, and `output.grounding`;
JSON also retains cost and stop-reason metadata. `--max-cost` accepts $1–$100 for
`auto` and `ultra` effort. Without it, Exa currently defaults to $5 for `auto` and
$20 for `ultra`. Other effort tiers use their provider pricing.

Validation scope: search/crawl have live API checks. Agent create/get/cancel have
SDK request/response contract tests, credential-free dry runs, and a live read-only
Agent API access check. A paid Agent run was not submitted or completed in this
validation; `--version` alone is not an API functionality test.

## AI-agent workflows

```bash
# Search and collect source URLs
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'

# Retrieve the first source
exa-search "topic" --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[0].url // empty' \
  | xargs exa-crawl -c 6000

# Submit a research task, then retrieve the result
exa-agent "topic" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
```

Example search output:

```json
{
  "results": [
    {
      "title": "...",
      "url": "...",
      "published_date": "2025-01-15T00:00:00.000Z",
      "author": "...",
      "highlights": ["excerpt..."],
      "text": "page text when requested and available"
    }
  ]
}
```

See [the usage guide](docs/USAGE.md) for schemas, exit codes, and environment reference.

## Focused source reading
```bash
# Tell search what the broader task needs, without expanding the query itself.
exa-search "home watch Tampa Bay pricing" \
  --objective "Prefer local providers with published prices; exclude directories." \
  -n 5 --compact

# Extract relevant passages across a long page instead of only its opening text.
exa-crawl https://www2.myfloridalicense.com/electrical-contractors/faqs/ \
  --query "Is a license required to install low voltage network wiring?" \
  -c 2500 --compact

# Refresh a changing pricing page if cached content is older than a day.
exa-crawl https://example.com/pricing --max-age-hours 24 --compact
```

`--query` requests highlights only and explicitly disables full text. Excerpts
help locate evidence; they do not replace a full reading when context matters.
When bounded full text reaches its limit, stderr warns that it may be incomplete.
`--max-age-hours` is available on search and crawl; omit it to keep existing API
defaults. Search mode `lite` does not accept freshness controls. `--objective`
cannot be combined with `--similar`.

`--compact` uses one-line JSON, removes empty values, duplicate URL IDs and
decorative fields, and retains substantive data, costs, warnings and per-URL
statuses. Existing `--json` output is unchanged. Neither mode saves state or
automatically repeats a request. See [full details](docs/USAGE.md#focused-retrieval-and-compact-output).

## Scope and review

Queries and retrieval requests are sent to Exa. Agent creation creates tasks on that external service; this is not an entirely offline or read-only workflow. Keep API keys private, check source material, and review generated research before using it in a business decision.

This project demonstrates a practical AI-assisted integration. It does not claim independently measured time savings, enterprise deployments, or an independent security audit. The provider's capabilities and availability remain outside this repository's control.

## License

MIT — Nolan Vale. See [LICENSE](LICENSE).
