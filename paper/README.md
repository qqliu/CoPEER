# Paper

- `co-peer.pdf`: "Co-PEER: Auditing Mathematics with Proofs of Error", the verified build of the manuscript source (source commit `cb9312a` of the Overleaf project; 63 pages; main text ends on page 11).
- `co-peer-arxiv-source.tar.gz`: the arXiv source bundle of the same commit. It compiles with pdfLaTeX alone (`pdflatex main.tex` three times; `main.bbl` is included) and produces the same page text as `co-peer.pdf`.
- `source/`: the extracted contents of that bundle (`main.tex`, the embedded section and appendix files, the bibliography, the style files and `figures/`).
- `figures/`: the external figure files and the plotting source of the two-threshold Schur objective (`figures/source/plot_schur_template.py`, see `figures/README.md`). `figures/verified_counterexample_categories.pdf` is a release-only display of the earlier collection that no longer appears in the paper.
- `SHA256SUMS`: hashes of the PDF and the bundle.

The arXiv identifier is added here and on the website once the paper is posted.
