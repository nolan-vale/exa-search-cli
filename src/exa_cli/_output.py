"""Optional compact source output and diagnostics for bounded page text."""

import sys


DECORATIVE_FIELDS = {"image", "favicon", "highlight_scores"}


def _has_value(value) -> bool:
    return value is not None and value not in ("", [], {})


def _prune_empty(value):
    if isinstance(value, dict):
        cleaned = {key: _prune_empty(item) for key, item in value.items()}
        return {key: item for key, item in cleaned.items() if _has_value(item)}
    if isinstance(value, list):
        cleaned = [_prune_empty(item) for item in value]
        return [item for item in cleaned if _has_value(item)]
    return value


def compact_payload(payload: dict) -> dict:
    """Keep source evidence and API metadata, without decorative SDK fields."""
    results = []
    for item in payload["results"]:
        if isinstance(item, dict):
            item = {
                key: value
                for key, value in item.items()
                if key not in DECORATIVE_FIELDS
            }
            if item.get("id") == item.get("url"):
                item.pop("id", None)
        results.append(_prune_empty(item))
    metadata = {key: value for key, value in payload.items() if key != "results"}
    for alias in ("data", "items"):
        if (
            isinstance(metadata.get(alias), list)
            and metadata[alias] == payload["results"]
        ):
            metadata.pop(alias)
    return {"results": results, **_prune_empty(metadata)}


def warn_text_limit(payload: dict, max_chars: int) -> None:
    reached = sum(
        isinstance(item, dict)
        and isinstance(item.get("text"), str)
        and len(item["text"]) >= max_chars
        for item in payload["results"]
    )
    if reached:
        print(
            f"Text reached the {max_chars}-character limit for {reached} URL(s) "
            "and may be incomplete; use exa-crawl --query for focused excerpts "
            "or increase --max-chars.",
            file=sys.stderr,
        )
