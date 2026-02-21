SCRAPE_SCRIPT = src/scraper.py
SCRAPE_OUTDIR = ./raw

CLEAN_SCRIPT = src/cleaner.py
CLEAN_OUTDIR = ./cleaned
CONFIG_DIR = ./configs

# --- Individual scraping commands

# Ivatan
iv:
	python $(SCRAPE_SCRIPT) --version-id 1315 --version-code VTSP --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir $(SCRAPE_OUTDIR)/VTSP

# Pangasinense
pa:
	python $(SCRAPE_SCRIPT) --version-id 1166 --version-code PNPV --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir $(SCRAPE_OUTDIR)/PNPV

# Tagalog
ta:
	python $(SCRAPE_SCRIPT) --version-id 144 --version-code MBB05 --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir $(SCRAPE_OUTDIR)/MBB05

# Yami
ya:
	python $(SCRAPE_SCRIPT) --version-id 2364 --version-code SNT --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir $(SCRAPE_OUTDIR)/SNT

# Aggregate cleaning

scrape-all: iv pa ta ya

scrape-clean:
	@echo "Cleaning all generated data..."
	rm -rf $(SCRAPE_OUTDIR)/*
	@echo "Clean complete."

# Individual cleaning

clean:
	python $(CLEAN_SCRIPT) --raw-dir $(SCRAPE_OUTDIR) --cleaned-dir $(CLEAN_OUTDIR) --sentence-config $(CONFIG_DIR)/sentence-cleaner.csv --verse-config $(CONFIG_DIR)/verse-cleaner.csv

remove-clean:
	@echo "Cleaning all cleaned data..."
	rm -rf $(CLEAN_OUTDIR)/*
	@echo "Clean complete."
