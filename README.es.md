# exa-search-cli

**Integración de línea de comandos con Exa para investigación repetible: búsqueda, recuperación de texto y tareas de investigación.**

[English](README.md) · [中文](README.zh-CN.md) · [Русский](README.ru.md) · [Português](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Propósito y contribución

Conecta servicios existentes de Exa con scripts y agentes de IA. Exa proporciona la búsqueda y la investigación; este repositorio implementa una integración CLI, no un buscador ni un modelo de IA propios.

Creado con agentes de programación de IA como parte del trabajo independiente de [Nolan Vale](https://github.com/nolan-vale). Su contribución consiste en definir requisitos, dirigir la implementación, comprobar resultados e iterar.

## Instalación

```bash
uv tool install exa-search-cli
export EXA_API_KEY=your-key
exa-search "document review workflow" --json
```

También puede instalarse con `pip install exa-search-cli` en un entorno Python adecuado. Obtén una clave de Exa y no la guardes en el repositorio.

## Comandos

| Comando | Propósito |
|---|---|
| `exa-search <query>` | Buscar fuentes o páginas similares con filtros de fecha, dominio y categoría |
| `exa-crawl <url>` | Solicitar texto legible de una página a través de Exa |
| `exa-research <topic>` | Crear una tarea de investigación en Exa |
| `exa-research-status <research-id>` | Consultar el estado y recuperar el resultado |

Los comandos admiten `--json`. La búsqueda admite `--num-results`, `--type`, `--text`, `--category`, `--start-date`, `--end-date`, `--include-domain`, `--exclude-domain` y `--similar`.

```bash
exa-search --similar https://github.com/astral-sh/uv
exa-crawl https://example.com -c 8000
exa-research "document processing approaches" --json
exa-research-status <research-id> --json
exa-search "topic" --json | jq -r '(if type=="array" then . else (.results // []) end)[] | .url'
```

## Límites

Las solicitudes se envían a un servicio externo. Los comandos de investigación crean tareas en Exa; el flujo no es totalmente local ni de solo lectura. La recuperación depende del proveedor y del acceso a la página; no se garantiza para todas las URLs. Revisa las fuentes y los resultados generados antes de utilizarlos.

[Documentación completa](docs/USAGE.md) · [Resumen actualizado](README.md).

[MIT](LICENSE) — Nolan Vale. **Nolan Vale Tools** identifica sus proyectos públicos independientes.
