"""Lemma 0 claims that if a finite graph has more than r^(n^k) vertices and at most n^k node labels, then some label class has more than r^(n^k) vertices."""

import itertools
import json

RECORD_ID = "arxiv_1505.06506v3__source_enriched_codex"
WITNESS_DESCRIPTION = (
    "n=2, k=2, r=2; the edgeless graph on vertices {0,...,16} has 17 "
    "vertices. With L={0,1}, label 0 is assigned to vertices {0,...,15} "
    "and label 1 to vertex 16, giving class sizes (16,1)."
)
REFUTATION_EXPLANATION = (
    "Here r^(n^k)=2^(2^2)=16, while the graph has 17>16 vertices and "
    "|L|=2<=4=n^k. Neither label class has more than 16 vertices, so "
    "the claimed conclusion is false."
)
SEARCH_SPACE = (
    "Exhaustive sweep of all 2^17=131072 labeling functions from the "
    "vertices {0,...,16} of the fixed edgeless graph to L={0,1}, at fixed "
    "n=2, k=2, r=2. The functions are visited in lexicographic order and "
    "the entire bounded space is swept."
)


def main():
    n = 2
    k = 2
    r = 2
    label_count = 2
    label_bound = n ** k
    threshold = r ** label_bound
    vertex_count = threshold + 1
    vertices = tuple(range(vertex_count))
    edges = ()

    first_witness = None
    examined = 0

    for labeling in itertools.product(range(label_count), repeat=vertex_count):
        examined += 1
        class_sizes = tuple(
            sum(1 for assigned_label in labeling if assigned_label == label)
            for label in range(label_count)
        )
        hypotheses_hold = (
            n >= 2
            and k > 1
            and r > 1
            and label_count <= label_bound
            and vertex_count > threshold
        )
        conclusion_holds = any(size > threshold for size in class_sizes)
        if hypotheses_hold and not conclusion_holds and first_witness is None:
            first_witness = (labeling, class_sizes)

    assert edges == ()
    assert vertices == tuple(range(17))
    assert examined == label_count ** vertex_count
    assert first_witness is not None
    assert first_witness[0] == (0,) * 16 + (1,)
    assert first_witness[1] == (16, 1)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
