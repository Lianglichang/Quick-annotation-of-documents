from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnnotateParams:
    input_pdf: str
    instructions: list[dict]
    output_pdf: str | None = None
    in_place: bool = True
    default_author: str = "Dear.Lichang"
    open_popup: bool = False
