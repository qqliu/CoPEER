# The project website

This folder is the website that GitHub Pages serves for the repository (Settings → Pages → Deploy from a branch → `main` / `/docs`); it also works offline by opening `index.html`.

- `index.html`: the project page with the interactive example, the workflow, BugBank, the benchmark, the studies and the mathematics laboratories.
- `bugbank.html`, `benchmark.html`, `mathematics.html`, `reproduce.html`, `tests.html`: the explorer, the complete benchmark results with an exercise, the mathematics with its statements and laboratories, the reproduction guide, and the self-checks.
- `data/`: the tables extracted from the paper source and the explorer data built from `bugbank/` and `benchmark/`; `data/MANIFEST.md` lists each file's origin and hash. `data/records/` holds one file per released dossier, loaded on demand.
- `assets/`: stylesheet, scripts, the laboratory mathematics, the checks, and the vendored KaTeX and fonts with their licences.
- `downloads/`: hash-checked copies of the paper PDF and the arXiv source bundle.
- `robots.txt` and `ai.txt`: the no-crawling and no-training policy for automated agents.

Rebuild the data from the repository root with `python3 tools/extract_paper_tables.py paper/source/main.tex docs/data`, `python3 -B tools/build_site_data.py` and `python3 -B tools/build_example_record.py`; check with `node tests/run_checks.mjs` and `python3 -B tools/check_site.py`.
