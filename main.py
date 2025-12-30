import pymupdf

from core import annotate_pdf
from instruction_utils import load_instructions
from params import AnnotateParams


def main() -> None:
    pymupdf.TOOLS.mupdf_display_errors(False)
    instructions = load_instructions("instructions.json")
    params = AnnotateParams(
        input_pdf="data/TableFormer_[12].pdf",
        instructions=instructions,
    )
    matched, expected, added, duplicates = annotate_pdf(params)
    print(f"matched={matched}/{expected} added={added} duplicates={duplicates}")
    if matched != expected:
        raise ValueError(f"Annotation count mismatch: expected {expected}, matched {matched}")


if __name__ == "__main__":
    main()
