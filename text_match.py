from __future__ import annotations

import re
from difflib import SequenceMatcher

import pymupdf

from constants import (
    MIN_FUZZY_RATIO,
    MIN_FUZZY_WORDS,
    MIN_SEGMENT_ALNUM,
    MIN_SEGMENT_WORDS,
    SEARCH_FLAGS,
    SPLIT_RE,
    WINDOW_STEP,
    WINDOW_WORDS,
    WORD_RE,
)

_SEARCH_FLAGS = getattr(pymupdf, SEARCH_FLAGS)
_SPLIT_RE = re.compile(SPLIT_RE)
_WORD_RE = re.compile(WORD_RE)
_SPACE_RE = re.compile(r"\s+")
_DEHYPHEN_RE = re.compile(r"(?<=\w)-\s+(?=\w)")


def normalize_key_text(text: str) -> str:
    return _DEHYPHEN_RE.sub("", _normalize_spaces(text))


def find_quads(page: pymupdf.Page, needle: str) -> list:
    for candidate in _candidate_texts(needle):
        quads = _search_quads(page, candidate)
        if quads:
            return quads

    segments: list[str] = []
    seen: set[str] = set()
    for candidate in _candidate_texts(needle):
        for seg in _split_text(candidate):
            if seg not in seen:
                seen.add(seg)
                segments.append(seg)

    quads = []
    for seg in segments:
        quads.extend(_search_quads(page, seg))
    if quads:
        return quads

    if not segments:
        return []
    page_text = page.get_text()
    fuzzy_target = max(segments, key=len)
    fuzzy_text = _fuzzy_span(page_text, fuzzy_target)
    if not fuzzy_text:
        return []
    return _search_quads(page, fuzzy_text)


def _normalize_spaces(text: str) -> str:
    return _SPACE_RE.sub(" ", text.strip())


def _candidate_texts(text: str) -> list[str]:
    if not text:
        return []
    candidates: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        val = value.strip()
        if val and val not in seen:
            seen.add(val)
            candidates.append(val)

    add(text)
    normalized = _normalize_spaces(text)
    add(normalized)

    dehyphen = _DEHYPHEN_RE.sub("", normalized)
    add(dehyphen)
    dehyphen_spaced = _normalize_spaces(dehyphen)
    add(dehyphen_spaced)

    keep_hyphen = _DEHYPHEN_RE.sub("-", normalized)
    add(keep_hyphen)
    keep_hyphen_spaced = _normalize_spaces(keep_hyphen)
    add(keep_hyphen_spaced)

    return candidates


def _is_matchable_segment(text: str) -> bool:
    words = _WORD_RE.findall(text)
    if len(words) < MIN_SEGMENT_WORDS:
        return False
    return sum(len(word) for word in words) >= MIN_SEGMENT_ALNUM


def _split_text(text: str) -> list[str]:
    cleaned = _normalize_spaces(text)
    if not cleaned:
        return []

    parts = [p.strip() for p in _SPLIT_RE.split(cleaned) if p.strip()]
    if not parts:
        parts = [cleaned]

    segments: list[str] = []
    for part in parts:
        words = part.split()
        if len(words) <= WINDOW_WORDS:
            segments.append(part)
            continue
        for i in range(0, len(words) - WINDOW_WORDS + 1, WINDOW_STEP):
            segments.append(" ".join(words[i : i + WINDOW_WORDS]))
        tail = " ".join(words[-WINDOW_WORDS:])
        if tail:
            segments.append(tail)

    seen: set[str] = set()
    result: list[str] = []
    for seg in segments:
        if seg not in seen:
            seen.add(seg)
            if _is_matchable_segment(seg):
                result.append(seg)
    return result


def _search_quads(page: pymupdf.Page, text: str) -> list:
    quads = page.search_for(text, quads=True, flags=_SEARCH_FLAGS)
    if quads or " " not in text:
        return quads
    tight = text.replace(" ", "")
    return page.search_for(tight, quads=True, flags=_SEARCH_FLAGS | pymupdf.TEXT_INHIBIT_SPACES)


def _fuzzy_span(page_text: str, target: str) -> str | None:
    target_words = [w.lower() for w in _WORD_RE.findall(target)]
    if len(target_words) < MIN_FUZZY_WORDS:
        return None

    spans = [(m.start(), m.end(), m.group()) for m in _WORD_RE.finditer(page_text)]
    if len(spans) < len(target_words):
        return None

    page_words = [word.lower() for _, _, word in spans]
    window = len(target_words)
    best_ratio = 0.0
    best_range = None
    for i in range(0, len(page_words) - window + 1):
        ratio = SequenceMatcher(None, target_words, page_words[i : i + window]).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_range = (i, i + window)

    if best_ratio < MIN_FUZZY_RATIO or best_range is None:
        return None

    start = spans[best_range[0]][0]
    end = spans[best_range[1] - 1][1]
    return page_text[start:end]
