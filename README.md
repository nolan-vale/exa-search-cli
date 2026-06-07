<div align="center">

[中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

<!--
  COVER IMAGE — generate with this prompt, save as docs/cover.png, then uncomment below.

  Prompt (Midjourney / DALL-E 3 / Stable Diffusion XL):
  "A sleek dark terminal window filled with glowing cyan and blue search results streaming
  in real-time, abstract neural network nodes forming a luminous web in the background,
  minimalist developer aesthetic, pure black background, neon accent colors,
  wide cinematic banner, 2:1 aspect ratio, no text, no UI chrome"

  <img src="docs/cover.png" alt="exa-cli" width="100%">
-->

# exa-search-cli

CLI for [Exa](https://exa.ai) — neural web search, URL crawling, and AI deep research from the terminal.

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/nolan-vale/exa-search-cli?style=social)](https://github.com/nolan-vale/exa-search-cli)

</div>

---

## What it does

`exa-search-cli` wraps the [Exa API](https://exa.ai) in three terminal commands. Exa is a search API built for AI applications — it searches by meaning, not keywords, which means it finds relevant pages even when the exact words are not present in the content.

`exa-search` searches the web. `exa-crawl` extracts clean readable text from any URL without HTML. `exa-research` submits a deep research task where Exa AI reads the web and synthesizes a structured answer.

Every command outputs clean `--json` for use in scripts, pipelines, and AI agent workflows.

## Who it is for

- Developers who want web search access from shell scripts and automation pipelines
- AI agent developers who need structured, parseable web search output
- Researchers collecting, filtering, and crawling web content programmatically
- Anyone using Claude Code, Codex, Cursor, or Windsurf who wants to give their agent web access

## Features

- Neural (semantic) search — finds pages by meaning, not keyword matching
- Find pages similar to any URL
- Filter by content type: `news`, `tweet`, `github`, `research paper`, `pdf`, and more
- Filter by date range and domain
- Full page text extraction from any URL (no HTML)
- AI deep research tasks with synthesized answers
- Clean `--json` output for every command

## Installation

```bash
uv tool install exa-search-cli
```

> No `uv`? Run `curl -LsSf https://astral.sh/uv/install.sh | sh`, or use `pip install exa-search-cli`.

## Quick start

Get your API key at [exa.ai](https://exa.ai) (free tier available):

```bash
export EXA_API_KEY=your-key-here
exa-search "how do transformers work" --category "research paper"
```

## Usage

```bash
# Neural search
exa-search "vision language models 2025" -n 10

# Find similar pages to a URL
exa-search --similar https://github.com/astral-sh/uv

# Filter by content type and date
exa-search "AI papers" --category "research paper" --start-date 2025-01-01

# Only specific domains
exa-search "documentation" --include-domain docs.python.org,docs.rs

# Exclude noisy domains
exa-search "tutorial" --exclude-domain medium.com,dev.to

# Crawl a page, get clean text
exa-crawl https://example.com -c 8000

# Deep research task
exa-research "current state of quantum error correction"

# JSON output for pipelines
exa-search "topic" --json | jq -r '.results[].url'
```

**All flags — `exa-search`:**

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | `8` | Number of results |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | off | Fetch and show full page text |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` · `company` · `personal site` · `linkedin profile` · `financial report` |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include only |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL |
| `--json` | off | Raw JSON output |

**All flags — `exa-crawl`:** `-c` / `--max-chars` (default `5000`), `--json`

**All flags — `exa-research`:** `-m` / `--model` (`exa-research` or `exa-research-pro`), `--json`

## AI agent usage

`exa-search-cli` is stateless, read-only, and exits cleanly — designed to be called by AI coding assistants.

```bash
# Search and extract URLs (most common agent pattern)
exa-search "topic" --json | jq -r '.results[].url'

# Search → crawl first result
exa-search "topic" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 6000

# Find similar pages to a reference URL
exa-search --similar https://example.com --json

# Deep research, get synthesized answer
exa-research "topic" --json
```

JSON schema for `exa-search --json`:
```json
{
  "results": [
    {
      "title": "...",
      "url": "...",
      "published_date": "2025-01-15T00:00:00.000Z",
      "author": "...",
      "highlights": ["excerpt..."],
      "text": "full text if --text was passed"
    }
  ]
}
```

See [AGENTS.md](AGENTS.md) for full schemas, exit codes, and environment reference.

→ [Full documentation](docs/USAGE.md)

## Project metadata

- **Author:** Nolan Vale
- **Brand:** Nolan Vale Tools
- **Focus:** search automation, CLI workflows, AI-agent tooling, developer productivity
- **License:** MIT

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
