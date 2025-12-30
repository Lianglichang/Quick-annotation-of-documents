from __future__ import annotations

import json
from pathlib import Path

from constants import PREFIX_COLORS


def load_instructions(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def strip_typed_prefix(text: str) -> str:
    if ":" in text:
        prefix, rest = text.split(":", 1)
        if prefix.strip().lower() in PREFIX_COLORS:
            rest = rest.strip()
            if rest:
                return rest
    return text


def parse_typed_comment(comment: str) -> tuple[str, str]:
    raw = comment.strip()
    if ":" in raw:
        prefix, rest = raw.split(":", 1)
        kind = prefix.strip().lower()
        if kind in PREFIX_COLORS:
            return kind, f"{kind.title()}:{rest.lstrip()}"
    return "detail", f"Detail:{raw}" if raw else "Detail:"


def normalize_comment(comment: str) -> str:
    return parse_typed_comment(comment)[1]
