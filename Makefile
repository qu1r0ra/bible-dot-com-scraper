# Makefile for scraping multiple Bible versions

PYTHON = python
SCRIPT = main.py
OUTDIR = ./data

# === Individual scraping commands ===

# Ivatan
iv:
	$(PYTHON) $(SCRIPT) --version-id 1315 --version-code VTSP --build-id Gbf1VTI_yCzErvb8C5sg_ --locale en-GB --outdir $(OUTDIR)/VTSP

# Pangasinense
pa:
	$(PYTHON) $(SCRIPT) --version-id 2194 --version-code MBBPAN83 --build-id Gbf1VTI_yCzErvb8C5sg_ --locale en-GB --outdir $(OUTDIR)/MBBPAN83

# Tagalog
ta:
	$(PYTHON) $(SCRIPT) --version-id 144 --version-code MBB05 --build-id Gbf1VTI_yCzErvb8C5sg_ --locale en-GB --outdir $(OUTDIR)/MBB05

# Yami
ya:
	$(PYTHON) $(SCRIPT) --version-id 2364 --version-code SNT --build-id Gbf1VTI_yCzErvb8C5sg_ --locale en --outdir $(OUTDIR)/SNT

# === Aggregate commands ===
# Run all scraping jobs sequentially
all: iv pa ta ya

# Clean up all scraped data
clean:
	@echo "Cleaning all generated data..."
	rm -rf $(OUTDIR)/*
	@echo "Clean complete."
