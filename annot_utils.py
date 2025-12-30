from __future__ import annotations

import pymupdf

_ANNOT_ACTIONS = {"highlight": "highlight", "underline": "underline"}
_QUAD_ROUND = 2


def quad_key(quad: pymupdf.Quad) -> tuple[float, float, float, float]:
    points = [quad.ul, quad.ur, quad.ll, quad.lr]
    return _points_key([(pt[0], pt[1]) for pt in points])


def existing_annots(
    page: pymupdf.Page,
) -> dict[tuple[str, str, str, str], set[tuple[float, float, float, float]]]:
    existing: dict[tuple[str, str, str, str], set[tuple[float, float, float, float]]] = {}
    annot = page.first_annot
    while annot:
        action = _annot_action(annot)
        if action:
            info = annot.info or {}
            key = (
                action,
                info.get("content", ""),
                info.get("subject", ""),
                info.get("title", ""),
            )
            existing.setdefault(key, set()).update(_annot_quad_keys(annot))
        annot = annot.next
    return existing


def _round_point(value: float) -> float:
    return round(value, _QUAD_ROUND)


def _points_key(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return (
        _round_point(min(xs)),
        _round_point(min(ys)),
        _round_point(max(xs)),
        _round_point(max(ys)),
    )


def _annot_quad_keys(annot: pymupdf.Annot) -> set[tuple[float, float, float, float]]:
    vertices = annot.vertices or []
    if not vertices:
        rect = annot.rect
        return {
            _points_key(
                [
                    (rect.x0, rect.y0),
                    (rect.x1, rect.y0),
                    (rect.x0, rect.y1),
                    (rect.x1, rect.y1),
                ]
            )
        }

    keys: set[tuple[float, float, float, float]] = set()
    for i in range(0, len(vertices) - 3, 4):
        points = vertices[i : i + 4]
        keys.add(_points_key(points))
    return keys


def _annot_action(annot: pymupdf.Annot) -> str | None:
    name = annot.type[1].lower()
    return _ANNOT_ACTIONS.get(name)
