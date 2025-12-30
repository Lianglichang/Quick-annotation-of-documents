ACTION_METHODS = {
    "highlight": "add_highlight_annot",
    "underline": "add_underline_annot",
}

PREFIX_COLORS = {
    "key": (1.0, 0.97, 0.7),
    "detail": (0.85, 0.98, 0.85),
    "parameter": (0.82, 0.9, 1.0),
}

SEARCH_FLAGS = "TEXT_DEHYPHENATE"
SPLIT_RE = r"[.!?;:]+"
WORD_RE = r"[A-Za-z0-9]+"
MIN_FUZZY_WORDS = 6
MIN_FUZZY_RATIO = 0.75
MIN_SEGMENT_WORDS = 2
MIN_SEGMENT_ALNUM = 6
WINDOW_WORDS = 8
WINDOW_STEP = 6
