<div align="center">

← [English](README.md) · [中文](README.zh-CN.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# exa-cli

**CLI для [Exa](https://exa.ai) — нейронный поиск, краулинг URL и AI-исследования из терминала.**

[![PyPI](https://img.shields.io/pypi/v/exa-search-cli?color=0ea5e9&label=PyPI)](https://pypi.org/project/exa-search-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-0ea5e9.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5e9.svg)](../LICENSE)

</div>

---

`exa-cli` оборачивает [Exa API](https://exa.ai) в три команды терминала. Exa ищет по смыслу, а не по ключевым словам. Все команды поддерживают `--json` для скриптов, AI-агентов и пайплайнов.

## Запустить за 60 секунд

**Шаг 1 — Установка:**
```bash
uv tool install exa-cli
```

> Нет `uv`? Запусти `curl -LsSf https://astral.sh/uv/install.sh | sh`, или используй `pip install exa-search-cli`.

**Шаг 2 — Получи API-ключ:**  
Зайди на [exa.ai](https://exa.ai) → зарегистрируйся (есть бесплатный тариф) → Dashboard → API Keys.

**Шаг 3 — Укажи ключ:**
```bash
export EXA_API_KEY=твой-ключ
# Добавь в ~/.zshrc или ~/.bashrc чтобы не вводить каждый раз
```

**Шаг 4 — Поиск:**
```bash
exa-search "как работают трансформеры" --category "research paper"
```

## Команды

| Команда | Что делает |
|---|---|
| `exa-search <запрос>` | Веб-поиск по смыслу. Фильтры по типу, дате, домену. Поиск похожих страниц. |
| `exa-crawl <url>` | Чистый текст любой страницы без HTML. |
| `exa-research <тема>` | Задача глубокого исследования. Exa AI читает сеть и пишет синтез. |

Все команды принимают `--json` — для `jq`, скриптов и агентов.

## Примеры

```bash
# Найти похожие страницы по URL
exa-search --similar https://github.com/astral-sh/uv

# Исследовательские статьи 2025 года
exa-search "vision language models" --category "research paper" --start-date 2025-01-01

# Только GitHub-репозитории, список URL
exa-search "async rust runtime" --include-domain github.com --json | jq -r '.results[].url'

# Получить текст страницы без HTML
exa-crawl https://example.com -c 8000

# Глубокое AI-исследование темы
exa-research "текущее состояние квантовой коррекции ошибок"
```

## Параметры

**`exa-search`**

| Флаг | По умолчанию | Описание |
|---|---|---|
| `-n` / `--num-results` | `8` | Количество результатов |
| `-t` / `--type` | `auto` | `auto` · `keyword` · `neural` |
| `--category` | — | `news` · `tweet` · `github` · `research paper` · `pdf` и др. |
| `--start-date` | — | Опубликовано после `YYYY-MM-DD` |
| `--end-date` | — | Опубликовано до `YYYY-MM-DD` |
| `--include-domain` | — | Только эти домены (через запятую) |
| `--exclude-domain` | — | Исключить эти домены (через запятую) |
| `--similar` | — | Найти похожие страницы по URL |
| `--json` | off | Сырой JSON-вывод |

→ **[Полная документация](docs/USAGE.ru.md)** · [English](docs/USAGE.md)

---

Built by [Nolan Vale](https://github.com/nolan-vale)  
Part of **Nolan Vale Tools** — practical open-source utilities for search, automation, AI agents, and developer workflows.
