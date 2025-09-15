# Makefile for scraping multiple Bible versions

PYTHON = python
SCRIPT = main.py
OUTDIR = ./data

# === Individual scraping commands ===

# Ivatan
iv:
	$(PYTHON) $(SCRIPT) --version-id 1315 --version-code VTSP --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir backup/VTSP

# Pangasinense
pa:
	$(PYTHON) $(SCRIPT) --version-id 1166 --version-code PNPV --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir backup/PNPV

# Tagalog
ta:
	$(PYTHON) $(SCRIPT) --version-id 144 --version-code MBB05 --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir backup/MBB05

# Yami
ya:
	$(PYTHON) $(SCRIPT) --version-id 2364 --version-code SNT --build-id 9su_rXNs9ssXM9qYjdWxG --locale en --outdir backup/SNT

# === Aggregate commands ===
# Run all scraping jobs sequentially
all: iv pa ta ya

# Clean up all scraped data
clean:
	@echo "Cleaning all generated data..."
	rm -rf $(OUTDIR)/*
	@echo "Clean complete."
