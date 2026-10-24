# Figure sources

The PDFs in this directory are the exact external figure files used to build
the manuscript.

`source/plot_schur_template.py` renders the two-threshold coloring objective.
With the numerical and plotting dependencies in `tools/requirements-analysis.txt`,
run from the repository root:

```sh
python paper/figures/source/plot_schur_template.py --output /tmp/schur_template_structure.pdf
```

The script also writes a PNG and a JSON record of the objective, analytic
optimum, and output hashes. Its grid is used to draw the objective; the exact
optimality statement is established by the proofs in the manuscript and the
Lean sources under `mathematics/`.

The category-count figure is supported by the record-level census and its
aggregation code under `bugbank/annotations/records/`.
