<div align="center">

← [English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# exa-search-cli

**CLI para [Exa](https://exa.ai) — busca web neural, crawling de URLs e pesquisa com IA, no terminal.**

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli` encapsula a [Exa API](https://exa.ai) em quatro comandos de terminal. Exa busca por significado, não por palavras-chave. Todos os comandos suportam `--json` para scripts, agentes de IA e pipelines.

## Comece em 60 segundos

**Passo 1 — Instale:**
```bash
uv tool install exa-search-cli
```

> Sem `uv`? Execute `curl -LsSf https://astral.sh/uv/install.sh | sh`, ou use `pip install exa-search-cli`.

**Passo 2 — Obtenha sua chave de API:**  
Acesse [exa.ai](https://exa.ai) → cadastre-se (plano gratuito disponível) → Dashboard → API Keys.

**Passo 3 — Configure a chave:**
```bash
export EXA_API_KEY=sua-chave
# Adicione ao ~/.zshrc ou ~/.bashrc para persistir
```

**Passo 4 — Pesquise:**
```bash
exa-search "como funcionam os transformers" --category "research paper"
```

## Comandos

| Comando | O que faz |
|---|---|
| `exa-search <consulta>` | Busca web por significado. Filtros por tipo, data, domínio. Encontra páginas similares. |
| `exa-crawl <url>` | Extrai texto limpo de qualquer URL, sem HTML. |
| `exa-research <tópico>` | Inicia uma tarefa de pesquisa profunda e retorna um `research_id` imediatamente. |
| `exa-research-status <research-id>` | Status / resultado de uma tarefa iniciada com `exa-research`. |

Todos os comandos aceitam `--json` para `jq`, scripts e agentes.

## Exemplos

```bash
# Encontrar páginas similares a uma URL
exa-search --similar https://github.com/astral-sh/uv

# Artigos de pesquisa de IA de 2025
exa-search "modelos de linguagem visual" --category "research paper" --start-date 2025-01-01

# Apenas repositórios GitHub, lista de URLs
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# Texto limpo de qualquer página
exa-crawl https://example.com -c 8000

# Pesquisa profunda com IA
exa-research "estado atual da correção de erros quânticos"
exa-research-status <research-id>   # verificar progresso / obter o resultado
```

## Referência de opções

**`exa-search`**

| Flag | Padrão | Descrição |
|---|---|---|
| `-n` / `--num-results` | `8` | Número de resultados |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` etc. |
| `--start-date` | — | Publicado em ou após `YYYY-MM-DD` |
| `--end-date` | — | Publicado em ou antes de `YYYY-MM-DD` |
| `--include-domain` | — | Incluir apenas esses domínios (separados por vírgula) |
| `--exclude-domain` | — | Excluir esses domínios (separados por vírgula) |
| `--similar` | — | Encontrar páginas similares a esta URL |
| `--json` | off | Saída JSON bruta |

→ **[Documentação completa](docs/USAGE.md)**（EN）

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
