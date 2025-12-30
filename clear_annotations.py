import pymupdf

from instruction_utils import load_instructions, normalize_comment


def _load_keys(instructions_path: str) -> set[tuple[str, str]]:
    instructions = load_instructions(instructions_path)
    keys: set[tuple[str, str]] = set()
    for ins in instructions:
        comment = ins.get("comment", "")
        subject = ins.get("subject", "")
        normalized = normalize_comment(comment)
        raw = comment.strip()
        keys.add((normalized, subject))
        if raw and raw != normalized:
            keys.add((raw, subject))
    return keys


def clear_annotations(
    input_pdf: str,
    instructions_path: str = "instructions.json",
    output_pdf: str | None = None,
    in_place: bool = True,
) -> None:
    keys = _load_keys(instructions_path)
    if not keys:
        return

    doc = pymupdf.open(input_pdf)
    for page in doc:
        annot = page.first_annot
        while annot:
            next_annot = annot.next
            info = annot.info or {}
            content = info.get("content", "")
            subject = info.get("subject", "")
            if (content, subject) in keys:
                page.delete_annot(annot)
            annot = next_annot

    if in_place:
        doc.saveIncr()
    else:
        if not output_pdf:
            raise ValueError("output_pdf is required when in_place is False")
        doc.save(output_pdf)
    doc.close()


def main() -> None:
    clear_annotations("data/TableFormer_[12].pdf")


if __name__ == "__main__":
    main()
