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

Four commands wrap Exa services:

| Command | Purpose |
|---|---|
| `exa-search` | Search the web or find pages similar to a reference URL |
| `exa-crawl` | Retrieve readable page text through Exa |
| `exa-research` | Submit a research task to Exa |
| `exa-research-status` | Check the task and retrieve its result |

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
exa-search "AI papers" --category "research paper" --start-date 2025-01-01

# Include or exclude domains
exa-search "documentation" --include-domain docs.python.org,docs.rs
exa-search "tutorial" --exclude-domain medium.com,dev.to

# Retrieve page text
exa-crawl https://example.com -c 8000

# Submit and retrieve an external research task
exa-research "document review workflow approaches"
exa-research-status <research-id>

# Extract URLs from structured output
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

### Search flags

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | `8` | Number of results |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | off | Request and display page text |
| `--category` | — | Content category, subject to provider support |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Structured JSON output |

Other options:

- **`exa-crawl`:** `-c` / `--max-chars` (default `5000`), `--json`.
- **`exa-research`:** `-m` / `--model` (`exa-research-fast`, `exa-research`, `exa-research-pro`), `--json`. Model availability depends on Exa.
- **`exa-research-status`:** `--json`.

See [full usage documentation](docs/USAGE.md) and the installed commands' `--help` for additional details.

## AI-agent workflows

```bash
# Search and collect source URLs
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'

# Retrieve the first source
exa-search "topic" --json \
  | jq -r '(if type=="array" then . else (.results // []) end)[0].url // empty' \
  | xargs exa-crawl -c 6000

# Submit a research task, then retrieve the result
exa-research "topic" --json
exa-research-status <research-id> --json
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

See [AGENTS.md](AGENTS.md) for integration guidance and environment details.

## Scope and review

Queries and retrieval requests are sent to Exa. Research commands create tasks on that external service; this is not an entirely offline or read-only workflow. Keep API keys private, check source material, and review generated research before using it in a business decision.

This project demonstrates a practical AI-assisted integration. It does not claim independently measured time savings, enterprise deployments, or an independent security audit. The provider's capabilities and availability remain outside this repository's control.

## License

MIT — Nolan Vale. See [LICENSE](LICENSE).
