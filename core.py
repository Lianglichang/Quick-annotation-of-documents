from __future__ import annotations

import pymupdf

from annot_utils import existing_annots, quad_key
from constants import ACTION_METHODS, PREFIX_COLORS
from instruction_utils import parse_typed_comment, strip_typed_prefix
from params import AnnotateParams
from text_match import find_quads, normalize_key_text


def annotate_pdf(params: AnnotateParams) -> tuple[int, int, int, int]:
    doc = pymupdf.open(params.input_pdf)
    matched_count = 0
    expected_count = 0
    added_count = 0
    duplicate_count = 0
    seen: set[tuple[int | None, str, str, str, str, str]] = set()
    existing_by_page: dict[
        int, dict[tuple[str, str, str, str], set[tuple[float, float, float, float]]]
    ] = {}

    for ins in params.instructions:
        needle = strip_typed_prefix(ins["text"])
        if not needle:
            continue
        action = ins.get("action", "highlight").lower()
        method = ACTION_METHODS.get(action)
        if method is None:
            continue

        page_no = ins.get("page")
        pages = range(len(doc)) if page_no is None else [page_no - 1]
        kind, comment = parse_typed_comment(ins.get("comment", ""))
        subject = ins.get("subject", "")
        author = ins.get("author", params.default_author)
        key = (
            page_no,
            action,
            normalize_key_text(needle),
            comment,
            subject,
            author,
        )
        if key in seen:
            continue
        seen.add(key)
        expected_count += 1
        matched = False
        added = False

        for pno in pages:
            page = doc[pno]
            existing = existing_by_page.get(pno)
            if existing is None:
                existing = existing_annots(page)
                existing_by_page[pno] = existing

            quads = find_quads(page, needle)
            if not quads:
                continue

            matched = True
            info_key = (action, comment, subject, author)
            existing_quads = existing.setdefault(info_key, set())
            new_quads = [quad for quad in quads if quad_key(quad) not in existing_quads]
            if not new_quads:
                continue

            annot = getattr(page, method)(new_quads)
            annot.set_info(content=comment, subject=subject, title=author)
            if action == "highlight":
                annot.set_colors(stroke=PREFIX_COLORS[kind])

            if params.open_popup:
                rect = annot.rect
                popup_rect = pymupdf.Rect(rect.x1 + 10, rect.y0, rect.x1 + 260, rect.y0 + 120)
                annot.set_popup(popup_rect)
                annot.set_open(True)

            annot.update()
            for quad in new_quads:
                existing_quads.add(quad_key(quad))
            added = True

        if matched:
            matched_count += 1
            if added:
                added_count += 1
            else:
                duplicate_count += 1

    if params.in_place:
        doc.saveIncr()
    else:
        if not params.output_pdf:
            raise ValueError("output_pdf is required when in_place is False")
        doc.save(params.output_pdf)
    doc.close()
    return matched_count, expected_count, added_count, duplicate_count
