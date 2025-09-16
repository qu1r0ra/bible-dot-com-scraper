import os
import re
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project-root/
RAW_DIR = BASE_DIR / "raw"
CLEANED_DIR = BASE_DIR / "cleaned"

# Separate step files
SENTENCE_STEPS_FILE = BASE_DIR / "config" / "sentence-cleaner.csv"
VERSE_STEPS_FILE = BASE_DIR / "config" / "verse-cleaner.csv"


def load_steps(filename):
    placeholder_map = {
        "<space>": " ",
        "$": "\\",  # convert `$1` → `\1`
    }

    steps = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            search = row["Search"].strip()
            replace = row["Replace"] if row["Replace"] else ""

            # Apply placeholder mapping to replacement string
            for placeholder, real in placeholder_map.items():
                replace = replace.replace(placeholder, real)

            if search and row["Mode / Remarks"].lower().startswith("regex"):
                steps.append((re.compile(search, re.MULTILINE), replace))
    return steps


def clean_text(text, steps):
    for pattern, repl in steps:
        text = pattern.sub(repl, text)
    return text


def process_files(raw_dir, cleaned_dir, steps):
    for txt_file in raw_dir.rglob("*.txt"):
        rel_path = txt_file.relative_to(raw_dir)
        out_path = cleaned_dir / rel_path

        # --- Adjust filename ---
        stem = out_path.stem  # filename without extension
        if stem.endswith("_raw"):
            new_stem = stem[:-4] + "_cleaned"  # replace _raw with _cleaned
        else:
            new_stem = stem + "_cleaned"  # fallback if no _raw
        out_path = out_path.with_name(new_stem + out_path.suffix)

        # --- Process text ---
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(txt_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text, steps)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"✔ Cleaned {txt_file} -> {out_path}")


if __name__ == "__main__":
    # --- Sentence cleaning ---
    sentence_steps = load_steps(SENTENCE_STEPS_FILE)
    process_files(RAW_DIR, CLEANED_DIR / "sentence", sentence_steps)

    # --- Verse cleaning ---
    verse_steps = load_steps(VERSE_STEPS_FILE)
    process_files(RAW_DIR, CLEANED_DIR / "verse", verse_steps)
