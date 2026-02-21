import argparse
import logging
import re
import csv
from pathlib import Path


def load_steps(filename: str | Path) -> list[tuple[re.Pattern, str]]:
    placeholder_map = {
        "<space>": " ",
        "$": "\\",
    }

    steps = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            search = row["Search"].strip()
            replace = row["Replace"] if row["Replace"] else ""

            for placeholder, real in placeholder_map.items():
                replace = replace.replace(placeholder, real)

            if search and row["Mode / Remarks"].lower().startswith("regex"):
                steps.append((re.compile(search, re.MULTILINE), replace))
    return steps


def clean_text(text: str, steps: list[tuple[re.Pattern, str]]) -> str:
    for pattern, repl in steps:
        text = pattern.sub(repl, text)
    return text


def process_files(
    raw_dir: Path, cleaned_dir: Path, steps: list[tuple[re.Pattern, str]]
) -> None:
    for txt_file in raw_dir.rglob("*.txt"):
        rel_path = txt_file.relative_to(raw_dir)
        out_path = cleaned_dir / rel_path

        stem = out_path.stem
        if stem.endswith("_raw"):
            new_stem = stem[:-4] + "_cleaned"
        else:
            new_stem = stem + "_cleaned"
        out_path = out_path.with_name(new_stem + out_path.suffix)

        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(txt_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text, steps)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        logging.info(f"Cleaned {txt_file} -> {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Clean raw scraped TXT files.")
    parser.add_argument(
        "--raw-dir", required=True, help="Directory containing raw TXT files."
    )
    parser.add_argument(
        "--cleaned-dir", required=True, help="Directory to save cleaned TXT files."
    )
    parser.add_argument(
        "--sentence-config", required=True, help="Path to sentence-cleaner.csv"
    )
    parser.add_argument(
        "--verse-config", required=True, help="Path to verse-cleaner.csv"
    )
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    cleaned_dir = Path(args.cleaned_dir)

    sentence_steps = load_steps(args.sentence_config)
    process_files(raw_dir, cleaned_dir / "sentence", sentence_steps)
    verse_steps = load_steps(args.verse_config)
    process_files(raw_dir, cleaned_dir / "verse", verse_steps)
