# bible-dot-com-scraper-parser

A modular toolset for scraping, cleaning, parsing, and aligning parallel corpora from bible.com translations.

> [!CAUTION]
> **Disclaimer:** This is not necessarily the best or most efficient way to scrape data from bible.com. This toolset was developed and confirmed to work back in September 2025. Changes to the website's structure or API may affect its current functionality.

## Project Structure

- `src/scraper.py`: Fetches text from Next.js endpoints on bible.com and saves them as JSON/CSV/TXT.
- `src/cleaner.py`: Normalizes raw text based on regex configurations.
- `notebooks/parser.ipynb`: Interactive data parser for converting raw text files into structured formats or HTML.
- `notebooks/parallel_corpora.ipynb`: Helper script for creating parallel corpora by harmonizing verse or sentence boundaries.
- `configs/`: Contains regex mapping rules (`sentence-cleaner.csv`, `verse-cleaner.csv`).
- `raw/`: (Generated) default output location for `scraper.py`.
- `cleaned/`: (Generated) default output location for `cleaner.py`.

## Requirements

- Python 3.13+
- Install dependencies using [uv](https://docs.astral.sh/uv/):

  ```bash
  uv sync
  ```

## 1. Scraping

You can use `make` targets to run pre-configured scraping jobs defined in the `Makefile`.

```bash
make scrape-all
```

Individual language targets:

```bash
make iv   # Ivatan
make pa   # Pangasinense
make ta   # Tagalog
make ya   # Yami
```

**Cleaning up raw generated data:**

```bash
make scrape-clean
```

Alternatively, run `scraper.py` directly:

```bash
python src/scraper.py \
    --version-id 144 \
    --version-code MBB05 \
    --build-id [YOUR_BUILD_ID] \
    --locale en \
    --outdir ./raw/MBB05
```

_(Note: You will need to obtain the most recent `buildId` by inspecting the **NEXT_DATA** json on bible.com endpoints)_

## 2. Text Cleaning

By default, the Makefile has a configuration ready to clean the output text data directly from your `./raw/` directory into `./cleaned/`.

Run the `cleaner.py` using `make`:

```bash
make clean
```

This applies the rules from `./configs/sentence-cleaner.csv` and `./configs/verse-cleaner.csv` to format your raw text.

**Cleaning up generated cleaned data:**

```bash
make remove-clean
```

If you wish to use the tool manually:

```bash
python src/cleaner.py \
    --raw-dir ./raw \
    --cleaned-dir ./cleaned \
    --sentence-config ./configs/sentence-cleaner.csv \
    --verse-config ./configs/verse-cleaner.csv
```

## 3. Parsing and Parallel Corpora

For organizing structures or creating aligned sentence/verse datasets, there are Jupyter notebooks available in the `notebooks/` directory.

- **`notebooks/parser.ipynb`**: Perform parsing by sentences or verses and transform text to HTML. Requires adjusting source references directly in the notebook before execution.
- **`notebooks/parallel_corpora.ipynb`**: Creates cross-lingual sentence or verse mappings relying on common book codes and identifiers, bridging translations with missing verses or irregular splits.

Simply spin up a Jupyter ecosystem and run those depending on the translations you want to align.
