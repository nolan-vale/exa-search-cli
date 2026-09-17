# exa-search-cli

**Командная интеграция с Exa для повторяемых исследований: поиск источников, получение текста страниц и исследовательские задачи.**

[English](README.md) · [中文](README.zh-CN.md) · [Português](README.pt-BR.md) · [Español](README.es.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Назначение и вклад

Инструмент связывает существующие сервисы Exa со скриптами и AI-агентами. Поиск и исследовательские возможности предоставляет Exa; этот репозиторий — CLI-интеграция, а не собственная поисковая система или AI-модель.

Создан с coding-агентами в рамках независимых проектов [Nolan Vale](https://github.com/nolan-vale). Мой вклад: постановка задачи, требования к интерфейсу, направление реализации с AI, проверка результата и итерации.

## Установка

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

Можно использовать `pip install exa-search-cli` в подходящем Python-окружении. Получите ключ у Exa и не сохраняйте его в репозитории.

## Команды

| Команда | Назначение |
|---|---|
| `exa-search <query>` | Поиск и поиск похожих страниц; фильтры по дате, домену и категории |
| `exa-crawl <url>` | Запрос читаемого текста страницы через Exa |
| `exa-research <topic>` | Создание исследовательской задачи на стороне Exa |
| `exa-research-status <research-id>` | Проверка статуса и получение результата задачи |

Команды поддерживают `--json`. Для поиска доступны `--num-results`, `--type`, `--text`, `--category`, `--start-date`, `--end-date`, `--include-domain`, `--exclude-domain`, `--similar`.

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-research "document processing approaches" --json
exa-research-status <research-id> --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## Ограничения

Запросы передаются внешнему сервису. Исследовательские команды создают задачи у Exa, поэтому процесс нельзя считать полностью локальным или только читающим. Получение текста зависит от доступности страницы и возможностей провайдера; поддержка любого URL не гарантируется. Проверяйте источники и сгенерированные выводы перед использованием.

[Полная документация на русском](docs/USAGE.ru.md) · [English](docs/USAGE.md) · [Актуальный обзор](README.md).

[MIT](LICENSE) — Nolan Vale. **Nolan Vale Tools** — название независимых публичных проектов.
