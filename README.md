<div align="center">

[中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

<!--
  COVER IMAGE — generate with this prompt, save as docs/cover.png, then uncomment the img tag below.

  Prompt (Midjourney / DALL-E 3 / Stable Diffusion XL):
  "A sleek dark terminal window filled with glowing cyan and blue search results streaming
  in real-time, abstract neural network nodes forming a luminous web in the background,
  minimalist developer aesthetic, pure black background, neon accent colors,
  wide cinematic banner, 2:1 aspect ratio, no text, no UI chrome"

  <img src="docs/cover.png" alt="exa-cli" width="100%">
-->

# exa-cli

**CLI for [Exa](https://exa.ai) — neural web search, URL crawling, and AI research tasks.**

[![PyPI](https://img.shields.io/pypi/v/exa-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/davidparker7966-design/exa-cli?style=social)](https://github.com/davidparker7966-design/exa-cli)

</div>

---

`exa-cli` wraps the [Exa API](https://exa.ai) in three terminal commands. Exa searches by meaning, not keywords — it understands what you're looking for, not just what you typed. Every command outputs clean `--json` for scripting, agents, and pipelines.

## Start in 60 seconds

**Step 1 — Install:**
```bash
uv tool install exa-cli
```

> No `uv`? Run `curl -LsSf https://astral.sh/uv/install.sh | sh` first, or use `pip install exa-cli`.

**Step 2 — Get your API key:**  
Go to [exa.ai](https://exa.ai) → sign up (free tier available) → Dashboard → API Keys.

**Step 3 — Set the key:**
```bash
export EXA_API_KEY=your-key-here
# Add to ~/.zshrc or ~/.bashrc to persist it
```

**Step 4 — Search:**
```bash
exa-search "how do transformers work" --category "research paper"
```

Done. You're searching the web with neural search.

## Commands

| Command | What it does |
|---|---|
| `exa-search <query>` | Search the web by meaning. Filter by type, date, domain. Find similar pages to any URL. |
| `exa-crawl <url>` | Fetch clean readable text from any URL. |
| `exa-research <topic>` | Submit a deep research task. Exa AI reads the web and synthesizes an answer. |

All commands accept `--json` for structured output (use with `jq` or pipe to AI agents).

## Examples

```bash
# Find pages similar to any URL — great for competitive research
exa-search --similar https://github.com/astral-sh/uv

# AI/ML research papers from 2025 only
exa-search "vision language models" --category "research paper" --start-date 2025-01-01

# Only GitHub repos, get URLs as JSON list
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# Crawl any page, get clean text (no HTML)
exa-crawl https://example.com -c 8000

# Deep research — Exa reads the web and writes a summary
exa-research "what is the current state of quantum error correction"

# Exclude noisy domains
exa-search "python tutorial" --exclude-domain medium.com,dev.to
```

## Options reference

**`exa-search`**

```
exa-search <query> [--similar <url>] [options]
```

| Flag | Default | Description |
|---|---|---|
| `-n` / `--num-results` | `8` | Number of results to return |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--text` | off | Fetch and print full page text |
| `--category` | — | `news` · `tweet` · `github` · `paper` · `company` · `research paper` · `financial report` · `personal site` · `pdf` · `linkedin profile` |
| `--start-date` | — | Published on or after `YYYY-MM-DD` |
| `--end-date` | — | Published on or before `YYYY-MM-DD` |
| `--include-domain` | — | Comma-separated domains to include only |
| `--exclude-domain` | — | Comma-separated domains to exclude |
| `--similar` | — | Find pages similar to this URL (replaces query) |
| `--json` | off | Raw JSON output |

**`exa-crawl`**

| Flag | Default | Description |
|---|---|---|
| `-c` / `--max-chars` | `5000` | Max characters to return |
| `--json` | off | Raw JSON output |

**`exa-research`**

| Flag | Default | Description |
|---|---|---|
| `-m` / `--model` | `exa-research` | `exa-research` or `exa-research-pro` |
| `--json` | off | Raw JSON output |

## For AI agents and scripts

`exa-cli` is designed to be called by AI coding assistants (Claude Code, Codex, Cursor, etc.). All commands are stateless, read-only, and exit cleanly.

```bash
# Agent-friendly pattern: search → extract URLs → crawl first result
exa-search "pytorch getting started" --json \
  | jq -r '.results[0].url' \
  | xargs exa-crawl -c 6000

# Feed results directly to an AI context
exa-search "topic" --json | jq '.results[] | {url, title}'
```

→ **[Full documentation](docs/USAGE.md)** — all flags, scripting recipes, and advanced usage.

---

<div align="center">
<sub>Built on the <a href="https://exa.ai">Exa API</a> · MIT License · <a href="https://github.com/davidparker7966-design/exa-cli/issues">Report an issue</a></sub>
</div>
