<div align="center">

← [English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# exa-cli

**CLI para [Exa](https://exa.ai) — búsqueda web neural, crawling de URLs y tareas de investigación con IA, desde el terminal.**

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli` envuelve la [Exa API](https://exa.ai) en tres comandos de terminal. Exa busca por significado, no por palabras clave. Todos los comandos soportan `--json` para scripts, agentes de IA y pipelines.

## Empieza en 60 segundos

**Paso 1 — Instala:**
```bash
uv tool install exa-cli
```

> ¿Sin `uv`? Ejecuta `curl -LsSf https://astral.sh/uv/install.sh | sh`, o usa `pip install exa-search-cli`.

**Paso 2 — Obtén tu clave de API:**  
Ve a [exa.ai](https://exa.ai) → regístrate (plan gratuito disponible) → Dashboard → API Keys.

**Paso 3 — Configura la clave:**
```bash
export EXA_API_KEY=tu-clave
# Añade a ~/.zshrc o ~/.bashrc para que persista
```

**Paso 4 — Busca:**
```bash
exa-search "cómo funcionan los transformers" --category "research paper"
```

## Comandos

| Comando | Qué hace |
|---|---|
| `exa-search <consulta>` | Búsqueda web por significado. Filtros por tipo, fecha, dominio. Encuentra páginas similares. |
| `exa-crawl <url>` | Extrae texto limpio de cualquier URL, sin HTML. |
| `exa-research <tema>` | Tarea de investigación profunda. La IA lee la web y sintetiza una respuesta. |

Todos los comandos aceptan `--json` para `jq`, scripts y agentes.

## Ejemplos

```bash
# Encontrar páginas similares a una URL
exa-search --similar https://github.com/astral-sh/uv

# Artículos de investigación de IA de 2025
exa-search "modelos de lenguaje visual" --category "research paper" --start-date 2025-01-01

# Solo repositorios de GitHub, lista de URLs
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# Texto limpio de cualquier página
exa-crawl https://example.com -c 8000

# Investigación profunda con IA
exa-research "estado actual de la corrección de errores cuánticos"
```

## Referencia de opciones

**`exa-search`**

| Flag | Defecto | Descripción |
|---|---|---|
| `-n` / `--num-results` | `8` | Número de resultados |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` etc. |
| `--start-date` | — | Publicado en o después de `YYYY-MM-DD` |
| `--end-date` | — | Publicado en o antes de `YYYY-MM-DD` |
| `--include-domain` | — | Incluir solo estos dominios (separados por coma) |
| `--exclude-domain` | — | Excluir estos dominios (separados por coma) |
| `--similar` | — | Encontrar páginas similares a esta URL |
| `--json` | off | Salida JSON en bruto |

→ **[Documentación completa](docs/USAGE.md)**（EN）

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
