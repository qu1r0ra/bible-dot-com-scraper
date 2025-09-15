#!/usr/bin/env python3
import argparse
import json
import time
import os
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import sys
import html

# ---------------------------
# Configuration / Defaults
# ---------------------------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.6533.120 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}
DEFAULT_LOCALE = "en-GB"
DEFAULT_SLEEP = 0.8  # seconds between requests (be polite)
MAX_RETRIES = 3


# ---------------------------
# Helpers
# ---------------------------
def get_build_id_from_page(sample_page_url: str) -> Optional[str]:
    """
    Fetch sample page HTML and extract the Next.js buildId from __NEXT_DATA__.
    Returns the buildId string or None if not found.
    """
    try:
        r = requests.get(sample_page_url, headers=REQUEST_HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch page: {sample_page_url} — {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")

    if not script or not script.string:
        print(f"⚠️ No __NEXT_DATA__ script found at {sample_page_url}")
        return None

    try:
        # Parse JSON safely
        data = json.loads(script.string.strip())
        # Primary way to get buildId
        build_id = data.get("buildId")
        if build_id:
            return build_id

        # Fallback: Sometimes buildId is nested deeper
        def find_build_id(d):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k == "buildId" and isinstance(v, str):
                        return v
                    found = find_build_id(v)
                    if found:
                        return found
            elif isinstance(d, list):
                for item in d:
                    found = find_build_id(item)
                    if found:
                        return found
            return None

        build_id = find_build_id(data)
        if build_id:
            return build_id

        print(f"⚠️ Could not find buildId in JSON for {sample_page_url}")
        return None

    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to decode JSON from __NEXT_DATA__ at {sample_page_url} — {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error parsing __NEXT_DATA__ at {sample_page_url} — {e}")
        return None


def construct_json_url(
    build_id: str,
    locale: str,
    version_id: str,
    book: str,
    chapter: int,
    version_code: str,
    route: str = "bible",
) -> tuple[str, dict]:
    """
    Build the JSON endpoint URL for Bible.com.
    """
    book_ch = f"{book}.{chapter}.{version_code}"
    url = f"https://www.bible.com/_next/data/{build_id}/{locale}/{route}/{version_id}/{book_ch}.json"
    params = {"versionId": version_id, "usfm": book_ch}
    return url, params


def fetch_json_with_retries(url, params=None, retries=3, backoff=5):
    """
    Fetch JSON from a URL with retries and throttling detection.
    Prints the full response for debugging.
    """
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.1 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)

            print(f"\n--- Response Debug (Attempt {attempt + 1}) ---")
            print(f"Status Code: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('Content-Type')}")
            print(
                f"Response Text:\n{resp.text[:1000]}"
            )  # Print first 1000 chars to avoid huge output

            # --- Detect throttling ---
            # if resp.status_code == 429:
            #     print("⚠️  Throttled: HTTP 429 Too Many Requests.")
            #     wait = backoff * (attempt + 1)
            #     print(f"   Waiting {wait} seconds before retrying...")
            #     time.sleep(wait)
            #     continue

            # if resp.status_code == 403:
            #     print("⚠️  Access denied (HTTP 403). Likely temporary throttling.")
            #     wait = backoff * (attempt + 1)
            #     print(f"   Waiting {wait} seconds before retrying...")
            #     time.sleep(wait)
            #     continue

            # --- Try parsing JSON ---
            try:
                data = resp.json()
            except json.JSONDecodeError:
                print("⚠️  Failed to parse JSON. Possibly throttled or got HTML.")
                wait = backoff * (attempt + 1)
                print(f"   Waiting {wait} seconds before retrying...")
                time.sleep(wait)
                continue

            return data

        except requests.RequestException as e:
            print(f"⚠️  Network error: {e}. Retrying in {backoff} seconds...")
            time.sleep(backoff)

    print("❌ Giving up on this request after multiple retries.")
    return None


def extract_verses_from_chapter_html(html_content: str) -> List[Dict]:
    """Given the chapter HTML (the 'content' field), return list of {verse, text} dicts."""
    soup = BeautifulSoup(html_content, "html.parser")
    verses = []
    # Each verse appears in a span.verse; label in span.label; text in span.content
    for v in soup.select("span.verse"):
        # remove footnote spans inside the verse to avoid capturing footnote text
        for note in v.select("span.note"):
            note.decompose()
        label_tag = v.select_one("span.label")
        content_tag = v.select_one("span.content")
        if not content_tag:
            # sometimes content may be directly in v
            text = v.get_text(separator=" ", strip=True)
            num = label_tag.text.strip() if label_tag else None
        else:
            text = content_tag.get_text(separator=" ", strip=True)
            num = label_tag.text.strip() if label_tag else None
        # skip empty lines
        if text:
            verses.append({"verse": num, "text": text})
    return verses


def save_raw_json_txt(
    data: dict, outdir: str, version_code: str, book: str, chapter: int
):
    """
    Save the raw JSON response to a .txt file for reference or later processing.
    """
    os.makedirs(outdir, exist_ok=True)
    raw_out_path = os.path.join(outdir, f"{version_code}_{book}_{chapter}_raw.txt")
    try:
        with open(raw_out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved raw JSON to {raw_out_path}")
    except Exception as e:
        print(f"Failed to save raw JSON for {book} {chapter}: {e}")


def fetch_books_and_chapters(version_id: str):
    """
    Fetch all available books and chapters for a given Bible version.
    Uses the Bible.com internal API endpoint.
    """
    url = f"https://www.bible.com/api/bible/version/{version_id}"
    print(f"Fetching book/chapter list from {url} ...")
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch version metadata (status {response.status_code}). "
            f"Double-check version_id: {version_id}"
        )

    data = response.json()
    books = data.get("books", [])

    result = []
    for book in books:
        chapters = []
        for ch in book.get("chapters", []):
            ch_num = ch.get("human", "").strip()
            # Keep only canonical, numeric chapters
            if ch.get("canonical", True) and ch_num.isdigit():
                chapters.append(int(ch_num))

        result.append(
            {
                "book_code": book["usfm"],
                "book_name": book["human"],
                "chapters": chapters,
            }
        )

    return result


# ---------------------------
# Main scraping flow
# ---------------------------
def scrape_version(
    version_id: str,
    version_code: str,
    build_id: str,
    locale: str = DEFAULT_LOCALE,
    books: Optional[List[str]] = None,
    outdir: str = "./output",
    route: str = "bible",
    sleep_between: float = DEFAULT_SLEEP,
):
    """
    Scrape all specified books for a given version.
    - version_id: numeric id shown in bible.com URLs (e.g. 144)
    - version_code: short code (e.g. MBB05)
    - route: 'bible' or 'audio-bible' depending on endpoint
    """
    os.makedirs(outdir, exist_ok=True)
    print("Using buildId:", build_id)

    if books is None:
        books = [b["book_code"] for b in fetch_books_and_chapters(version_id)]

    print("\nBooks available in this version:")
    for b in fetch_books_and_chapters(version_id):
        print(f"{b['book_code']} ({b['book_name']}): {len(b['chapters'])} chapters")

    for book in books:
        print(f"\n=== Processing book {book} ===")
        book_out = []
        raw_html_accumulator = []  # collect raw HTML per book

        # Get the valid chapter numbers for this book
        book_meta = next(
            b for b in fetch_books_and_chapters(version_id) if b["book_code"] == book
        )
        valid_chapters = book_meta["chapters"]

        print(f"Processing {book}: {len(valid_chapters)} chapters -> {valid_chapters}")

        for chapter in valid_chapters:
            json_url, params = construct_json_url(
                build_id, locale, version_id, book, chapter, version_code, route=route
            )
            data = fetch_json_with_retries(json_url, params=params)
            if not data:
                print(f"⚠️ Failed to fetch {book} {chapter}, skipping.")
                time.sleep(sleep_between)
                continue

            # reset not found counter
            consecutive_not_found = 0

            # where the HTML is stored can vary slightly; we expect pageProps.chapterInfo.content
            html_content = None
            try:
                html_content = (
                    data.get("pageProps", {}).get("chapterInfo", {}).get("content")
                )
                # sometimes content may appear under other keys; check quickly
                if not html_content:
                    # try searching the JSON for a key named 'content'
                    def find_content(d):
                        if isinstance(d, dict):
                            for k, v in d.items():
                                if k == "content" and isinstance(v, str):
                                    return v
                                else:
                                    found = find_content(v)
                                    if found:
                                        return found
                        elif isinstance(d, list):
                            for item in d:
                                found = find_content(item)
                                if found:
                                    return found
                        return None

                    html_content = find_content(data)
            except Exception as e:
                print("Error extracting html_content:", e)
                html_content = None

            if not html_content:
                # No content found — assume stop if a few in a row
                print(f"No content found for {book} {chapter}. Stopping this book.")
                break

            # Append raw HTML for this chapter to accumulator
            # raw_html_accumulator.append(f"\n<!-- {book} Chapter {chapter} -->\n")
            raw_html_accumulator.append(html_content)

            # Extract verses to be used by .csv and .json files
            verses = extract_verses_from_chapter_html(html_content)
            if not verses:
                print(f"No verses found for {book} {chapter}.")
                chapter += 1
                time.sleep(sleep_between)
                continue

            # store structured data for JSON/CSV
            book_out.append(
                {
                    "book": book,
                    "chapter": chapter,
                    "verses": verses,
                    "raw_json_url": json_url,
                }
            )

            print(f"Saved {book} chapter {chapter} ({len(verses)} verses).")
            chapter += 1
            time.sleep(sleep_between)

        # save book_out to JSON and CSV
        if book_out:
            out_json_path = os.path.join(outdir, f"{version_code}_{book}.json")
            with open(out_json_path, "w", encoding="utf-8") as f:
                json.dump(book_out, f, ensure_ascii=False, indent=2)
            # also save a flat CSV: columns book,chapter,verse,text
            rows = []
            for entry in book_out:
                for v in entry["verses"]:
                    rows.append(
                        {
                            "book": entry["book"],
                            "chapter": entry["chapter"],
                            "verse": v.get("verse"),
                            "text": v.get("text"),
                        }
                    )
            df = pd.DataFrame(rows)
            out_csv_path = os.path.join(outdir, f"{version_code}_{book}.csv")
            df.to_csv(out_csv_path, index=False, encoding="utf-8-sig")

            # --- NEW: Save the entire raw HTML for the book into a single .txt ---
            raw_txt_path = os.path.join(outdir, f"{version_code}_{book}_raw.txt")
            with open(raw_txt_path, "w", encoding="utf-8") as f:
                f.write(html.unescape("\n".join(raw_html_accumulator)))
            print(f"Wrote {out_json_path}, {out_csv_path}, and {raw_txt_path}")
        else:
            print(f"No data collected for {book}")

    print("\nAll done.")


# ---------------------------
# CLI
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Bible.com chapter JSONs and extract verses."
    )
    parser.add_argument(
        "--version-id", required=True, help="Numeric version id e.g. 144"
    )
    parser.add_argument(
        "--version-code", required=True, help="Version short code e.g. MBB05"
    )
    parser.add_argument(
        "--build-id",
        required=True,
        help="Next.js build ID. Must be supplied manually.",
    )
    parser.add_argument(
        "--locale",
        default=DEFAULT_LOCALE,
        help="Locale used in JSON URL (default en-GB)",
    )
    parser.add_argument(
        "--books",
        nargs="*",
        help="List of book USFM codes to download (default: common books order)",
    )
    parser.add_argument("--outdir", default="./output", help="Output directory")
    parser.add_argument(
        "--route",
        default="bible",
        help="Route segment: 'bible' or 'audio-bible' (default: bible)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=DEFAULT_SLEEP,
        help="Seconds to wait between requests",
    )
    args = parser.parse_args()

    # If books not specified, fetch them dynamically from Bible.com API
    if args.books is None or len(args.books) == 0:
        print("\nNo books provided. Fetching valid book codes from Bible.com API...")
        try:
            all_books = fetch_books_and_chapters(args.version_id)
            args.books = [b["book_code"] for b in all_books]
            print(f"Found {len(args.books)} books: {', '.join(args.books)}")
        except Exception as e:
            print(f"Failed to fetch books dynamically: {e}")
            sys.exit(1)

    # Call main scraper
    scrape_version(
        args.version_id,
        args.version_code,
        build_id=args.build_id,
        locale=args.locale,
        books=args.books,
        outdir=args.outdir,
        route=args.route,
        sleep_between=args.sleep,
    )
