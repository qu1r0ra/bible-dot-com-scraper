# Scraping variables

SCRAPE_SCRIPT = src/main.py
SCRAPE_OUTDIR = ./raw

# === Individual scraping commands ===

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

# === Aggregate commands ===
# Run all scraping jobs sequentially
scrape-all: iv pa ta ya

# Clean up all scraped data
scrape-clean:
	@echo "Cleaning all generated data..."
	rm -rf $(OUTDIR)/*
	@echo "Clean complete."

# Cleaning variables

CLEAN_SCRIPT = src/cleaner.py
CLEAN_OUTDIR = cleaned

# === Individual cleaning commands ===

clean:
	python ${CLEAN_SCRIPT}

remove-clean:
	@echo "Cleaning all cleaned data..."
	rm -rf $(CLEAN_OUTDIR)/*
	@echo "Clean complete."
