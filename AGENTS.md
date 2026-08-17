# Contributor Instructions

## Scope

`exa-search-cli` is a stateless Python CLI wrapping Exa search, crawl, and research APIs. User installation, authentication, command examples, and JSON schemas belong in `README.md`, `docs/USAGE.md`, and `llms.txt`, not here.

## Architecture

- Keep CLI entry points under `src/exa_cli` thin and script-friendly.
- Preserve command names and documented JSON schemas unless the task explicitly includes a breaking release.
- Emit machine output to stdout, diagnostics to stderr, and non-zero exit codes for failures.
- Never persist API keys, modify shell profiles, or print credentials.
- Keep commands stateless; do not add implicit local session storage.

## Verification

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run python -m unittest discover -s tests
uv build
```

Run affected tests and Ruff for normal changes. Run the full suite and build for packaging, entry-point, output-contract, or release changes. Update the relevant README/usage/`llms.txt` surface when public behavior changes.

## Delivery

- Verify locally before pushing; do not use GitHub Actions as the iterative debugger.
- CI should avoid duplicate `push` and PR runs, cancel superseded runs, ignore documentation-only changes, and use bounded timeouts.
- Publishing occurs only from an explicitly approved GitHub release.
