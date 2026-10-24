#!/usr/bin/env python3
"""Render the analytic Schur template objective (requires NumPy/matplotlib).

The contour is a visualization; continuous optimality is proved in the
paper appendix. Its domain is the stated parity/two-threshold template.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="PDF output path")
    args = parser.parse_args()
    coordinates = np.linspace(0, 1, 601)
    a, b = np.meshgrid(coordinates, coordinates)
    positive = lambda x: np.maximum(x, 0)
    density = ((b-a)*(1-b+a)
               + ((1-a)**2-(1-b)**2-positive(1-2*a)**2
                  -positive(1-2*b)**2+2*positive(1-a-b)**2)/2)
    density = np.ma.masked_where(a > b, density)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.labelsize": 10, "pdf.fonttype": 42,
                         "ps.fonttype": 42, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(5.8, 3.45), layout="constrained")
    levels = np.linspace(0, float(Fraction(9, 22)), 17)
    field = ax.contourf(a, b, density, levels=levels, cmap="viridis")
    ax.contour(a, b, density, levels=[0.1, 0.2, 0.3],
               colors="white", linewidths=0.45, alpha=0.55)
    ax.contour(a, b, density, levels=[0.4], colors="#1b1b1b",
               linewidths=1.1, linestyles="--")
    ax.plot([0, 1], [0, 1], color="#5d6871", linewidth=0.7)
    ax.scatter([4/11], [10/11], marker="*", s=125, c="#ffcb61",
               edgecolors="#202020", linewidths=0.7, zorder=5)
    ax.annotate(r"Template optimum: $9/22$"+"\n"+r"$(a,b)=(4/11,10/11)$",
                xy=(4/11, 10/11), xytext=(0.58, 0.67),
                ha="left", va="center", fontsize=8.5,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.94,
                      "pad": 2.5},
                arrowprops={"arrowstyle": "-", "color": "#303030", "lw": 0.8})
    ax.scatter([0.4, 0], [1, 0.4], s=30, facecolors="white",
               edgecolors="#202020", linewidths=0.9, zorder=5, clip_on=False)
    ax.annotate(r"Contiguous odd blocks: best $2/5$",
                xy=(0.4, 1), xytext=(0.01, 1.065),
                ha="left", va="center", fontsize=8.5,
                arrowprops={"arrowstyle": "-", "color": "#303030", "lw": 0.8})
    ax.text(0.70, 0.47, r"Dashed contour: $D=2/5$", fontsize=8.5,
            ha="left", va="center")
    ax.set(xlim=(-0.02, 1.03), ylim=(-0.015, 1.13),
           xlabel=r"Lower odd threshold $a$", ylabel=r"Upper odd threshold $b$")
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.linspace(0, 1, 6))
    colorbar = fig.colorbar(field, ax=ax, fraction=0.045, pad=0.025,
                           ticks=[0, 0.1, 0.2, 0.3, 0.4])
    colorbar.set_label(r"Limiting rainbow fraction $D(a,b)$")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, metadata={"Title": "Schur parity-template density",
                "Subject": "Analytic template objective; not unrestricted optimality"})
    fig.savefig(args.output.with_suffix(".png"), dpi=180)
    plt.close(fig)
    metadata = {
        "figure": args.output.name,
        "objective": "positive-part area formula in structural proof appendix",
        "scope": "two-threshold parity template only; continuous optimum proved analytically",
        "grid_axis_points": len(coordinates), "grid_used_only_for_visualization": True,
        "analytic_optimum": {"a": "4/11", "b": "10/11", "density": "9/22"},
        "contiguous_odd_block_optimum": "2/5",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "pdf_sha256": sha256(args.output.read_bytes()).hexdigest(),
    }
    args.output.with_suffix(".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
