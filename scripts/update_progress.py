#!/usr/bin/env python3
import ast
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# Which files to scan
FILES = [p for p in ROOT.glob("python/**/*.py")
         if "tests" not in [x.lower() for x in p.parts]
         and "scripts" not in [x.lower() for x in p.parts]
         and not p.name.startswith("test_")]

# Difficulty detector — from TOP-LEVEL DOCSTRING ONLY
DIFFICULTY_RE = re.compile(
    r"""(?ix)
        \b(?:difficulty\s*[:\-]\s*)?(easy|medium|hard)\b
        |^\s*\[(easy|medium|hard)\]\s*$
        |^\s*(easy|medium|hard)\s*[—\-:\| ]    # e.g., "Easy — Hash Map"
    """,
    re.M,
)

def get_top_docstring(text: str) -> str | None:
    try:
        tree = ast.parse(text)
        doc = ast.get_docstring(tree)
        return doc
    except Exception:
        return None

def detect_difficulty_from_docstring(doc: str | None) -> str | None:
    if not doc:
        return None
    m = DIFFICULTY_RE.search(doc)
    if not m:
        return None
    # find first non-None group
    for g in m.groups():
        if g:
            return g.lower()
    return None

def classify_files():
    easy = medium = hard = 0
    for p in FILES:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        diff = detect_difficulty_from_docstring(get_top_docstring(text))
        if diff == "easy":
            easy += 1
        elif diff == "medium":
            medium += 1
        elif diff == "hard":
            hard += 1
        # files without a detectable difficulty are ignored
    return easy, medium, hard, easy + medium + hard

# README updating
def update_with_markers(s: str, total: int, easy: int, medium: int, hard: int) -> tuple[str, bool]:
    """Update lines that contain <!--count-total--> and <!--count-breakdown-->. Return (text, used_markers)."""
    used = False

    def repl_total(m):
        nonlocal used
        used = True
        prefix, _num = m.groups()
        return f"{prefix}{total}"

    def repl_breakdown(m):
        nonlocal used
        used = True
        g1, _e, g2, _m, g3, _h = m.groups()
        return f"{g1}{easy}{g2}{medium}{g3}{hard}"

    s = re.sub(r"(<!--count-total-->)(\d+)", repl_total, s, count=1)
    s = re.sub(r"(<!--count-breakdown-->.*?Easy\s+)(\d+)(\s*·\s*Medium\s+)(\d+)(\s*·\s*Hard\s+)(\d+)",
               repl_breakdown, s, count=1, flags=re.IGNORECASE | re.DOTALL)
    return s, used

def update_with_fallback_patterns(s: str, total: int, easy: int, medium: int, hard: int) -> str:
    # Total line like: "- **Total solved:** <!-- auto -->0" OR "Total solved: **0**"
    s = re.sub(
        r"(-\s+\*\*Total solved:\*\*.*?)(\d+)",
        lambda m: f"{m.group(1)}{total}",
        s,
        count=1,
        flags=re.IGNORECASE,
    )
    s = re.sub(
        r"(Total\s+solved:\s*\*\*)(\d+)(\*\*)",
        lambda m: f"{m.group(1)}{total}{m.group(3)}",
        s,
        count=1,
        flags=re.IGNORECASE,
    )
    # Breakdown like: "Easy 0 · Medium 0 · Hard 0"
    s = re.sub(
        r"(Easy\s+)\d+(\s*·\s*Medium\s+)\d+(\s*·\s*Hard\s+)\d+",
        lambda m: f"{m.group(1)}{easy}{m.group(2)}{medium}{m.group(3)}{hard}",
        s,
        count=1,
        flags=re.IGNORECASE,
    )
    return s

def main():
    easy, medium, hard, total = classify_files()
    text = README.read_text(encoding="utf-8", errors="ignore")
    text, used_markers = update_with_markers(text, total, easy, medium, hard)
    if not used_markers:
        text = update_with_fallback_patterns(text, total, easy, medium, hard)
    README.write_text(text, encoding="utf-8")
    print(f"Updated: total={total}, E={easy}, M={medium}, H={hard}")

if __name__ == "__main__":
    main()
