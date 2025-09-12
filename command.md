# Format

```bash
python main.py --version-id [version id] --version-code [version code] --build-id [build id] --locale [locale] --outdir [output directory]
```

where

- `version id`, `version code`, `build id`, and `locale` are obtained from a sample webpage of the language of choice
- `output directory` leads to an output directory of choice

---

## Examples

### Ivatan

```bash
python main.py --version-id 1315 --version-code VTSP --build-id Gbf1VTI*yCzErvb8C5sg* --locale en-GB --outdir data/VTSP
```

### Pangasinense

```bash
python main.py --version-id 2194 --version-code MBBPAN83 --build-id Gbf1VTI*yCzErvb8C5sg* --locale en-GB --outdir data/MBBPAN83
```

### Tagalog

```bash
python main.py --version-id 144 --version-code MBB05 --build-id Gbf1VTI*yCzErvb8C5sg* --locale en-GB --outdir data/MBB05
```

### Yami

```bash
python main.py --version-id 2364 --version-code SNT --build-id Gbf1VTI*yCzErvb8C5sg* --locale en --outdir data/SNT
```
