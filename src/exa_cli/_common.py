import argparse
import math
import os
import re
import sys
from datetime import date
from importlib.metadata import version
from urllib.parse import urlsplit

import requests
from exa_py.errors import ExaTimeoutError


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def result_count(value: str) -> int:
    parsed = positive_int(value)
    if parsed > 100:
        raise argparse.ArgumentTypeError("must be between 1 and 100")
    return parsed


def iso_date(value: str) -> str:
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a valid YYYY-MM-DD date") from exc
    return value


def http_url(value: str) -> str:
    try:
        url = urlsplit(value)
        valid = url.scheme in ("http", "https") and url.hostname and not url.username
    except ValueError:
        valid = False
    if not valid:
        raise argparse.ArgumentTypeError("must be an HTTP(S) URL without credentials")
    return value


def positive_seconds(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a finite number > 0")
    return parsed


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--timeout",
        type=positive_seconds,
        default=60,
        help="HTTP connect/read timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('exa-search-cli')}"
    )


def api_call(method, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except ExaTimeoutError:
        sys.exit("Exa request timed out; retry or increase --timeout")
    except requests.RequestException as exc:
        sys.exit(f"Exa request failed ({type(exc).__name__}); check your connection")
    except ValueError as exc:
        detail = str(exc)
        key = os.environ.get("EXA_API_KEY", "").strip()
        if key:
            detail = detail.replace(key, "[REDACTED]")
        sys.exit(f"Exa API error: {detail[:500]}")
