# exa-search-cli

> Exa закрыла `/research`. В версии 0.1.7 используй `exa-agent`, `exa-agent-status` и `exa-agent-cancel`. Старые `exa-research*` завершаются с инструкцией перехода, без API-вызова и без автоматического создания платной задачи. `exa-agent --dry-run` показывает запрос без ключа и сети. [Миграция и параметры](docs/USAGE.ru.md).

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
| `exa-agent <query>` | Создать асинхронную задачу Exa Agent |
| `exa-agent-status <run-id>` | Получить результат Agent run |
| `exa-agent-cancel <run-id>` | Отменить Agent run |

Команды поддерживают `--json`, `--timeout` и `--version`. Для поиска доступны `--num-results`, `--type`, `--text`, `--max-chars`, `--category`, `--start-date`, `--end-date`, `--include-domain`, `--exclude-domain`, `--similar`, `--objective`, `--max-age-hours` и `--compact`. Для `exa-crawl` добавлены `--query`, `--max-age-hours` и `--compact`; несколько URL можно передать одним запросом.

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-agent "document processing approaches" --max-cost 1 --json
exa-agent-status agent_run_REPLACE_WITH_RETURNED_ID --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## Для исследовательского workflow

`--category publication` ищет научные публикации; `paper` и `research paper` остаются aliases. `--objective` передаёт цель поиска и предпочтения источников. `exa-crawl --query` извлекает фрагменты по вопросу со всей страницы, а `-c` ограничивает их объём. `--max-age-hours` управляет возрастом контента: `0` — свежий fetch, `-1` — только cache, `1–720` — допустимый возраст в часах. Search type `lite` не принимает этот параметр.

`--compact` возвращает JSON в одну строку без пустых и декоративных полей, сохраняя содержание, ссылки, стоимость и статусы. Обычный `--json` совместим с прежним форматом. При достижении лимита полного текста stderr предупреждает о возможной неполноте; дополнительных запросов автоматически не выполняется.

```bash
exa-crawl https://www2.myfloridalicense.com/electrical-contractors/faqs/ \
  --query "Is a license required to install low voltage network wiring?" \
  -c 2500 --compact
```

## Ограничения

Запросы передаются внешнему сервису. Исследовательские команды создают задачи у Exa, поэтому процесс нельзя считать полностью локальным или только читающим. Получение текста зависит от доступности страницы и возможностей провайдера; поддержка любого URL не гарантируется. Проверяйте источники и сгенерированные выводы перед использованием.

[Полная документация на русском](docs/USAGE.ru.md) · [English](docs/USAGE.md) · [Актуальный обзор](README.md).

[MIT](LICENSE) — Nolan Vale. **Nolan Vale Tools** — название независимых публичных проектов.
