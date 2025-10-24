import re, pathlib

root = pathlib.Path(__file__).resolve().parents[1]
readme = root / "README.md"
files = list(root.glob("python/**/*.py"))

easy = sum(1 for f in files if "/easy/" in f.as_posix() or re.search(r"\b(Easy)\b", f.read_text(errors="ignore")))
medium = sum(1 for f in files if "/medium/" in f.as_posix() or re.search(r"\b(Medium)\b", f.read_text(errors="ignore")))
hard = sum(1 for f in files if "/hard/" in f.as_posix() or re.search(r"\b(Hard)\b", f.read_text(errors="ignore")))
total = easy + medium + hard

text = readme.read_text()
text = re.sub(r"Total solved:\s.*", f"Total solved: **{total}**", text)
text = re.sub(r"Easy \d+ · Medium \d+ · Hard \d+",
              f"Easy {easy} · Medium {medium} · Hard {hard}", text)
readme.write_text(text)
print(f"Updated: total={total}, E={easy}, M={medium}, H={hard}")
