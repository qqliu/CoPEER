r"""Lemma 0 claims that if a finite graph has more than r^(n^k) vertices and at most n^k node labels, then some label class has more than r^(n^k) vertices."""

import json

RECORD_ID = "arxiv_1505.06506v3__source_enriched_codex"
NOTES = "Independent exact recomputation verifies the witness: the threshold is 16, the graph has 17 vertices, two labels satisfy the bound 2 <= 4, and the two class sizes are 16 and 1, so neither exceeds 16. The refuted statement is substantive as written, not plainly a typo; a valid pigeonhole premise would need to account for the number of label classes."


def main():
    n = 2
    k = 2
    r = 2

    exponent = n ** k
    threshold = r ** exponent

    vertices = tuple(range(threshold + 1))
    edges = frozenset()
    label_set = frozenset((0, 1))
    assignments = tuple(0 if vertex < threshold else 1 for vertex in vertices)

    class_sizes = {}
    for label in label_set:
        count = 0
        for assigned_label in assignments:
            if assigned_label == label:
                count += 1
        class_sizes[label] = count

    graph_is_valid = all(
        endpoint in vertices
        for edge in edges
        for endpoint in edge
    )
    labeling_is_total = (
        len(assignments) == len(vertices)
        and all(label in label_set for label in assignments)
    )
    hypotheses_hold = (
        graph_is_valid
        and labeling_is_total
        and len(label_set) > 0
        and n >= 2
        and k > 1
        and r > 1
        and len(label_set) <= exponent
        and len(vertices) > threshold
    )
    reported_values_match = (
        exponent == 4
        and threshold == 16
        and vertices == tuple(range(17))
        and edges == frozenset()
        and class_sizes.get(0) == 16
        and class_sizes.get(1) == 1
        and sum(class_sizes.values()) == len(vertices)
    )
    claimed_conclusion = any(
        class_sizes[label] > threshold for label in label_set
    )

    confirmed = hypotheses_hold and reported_values_match and not claimed_conclusion
    verdict = "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID"
    result = {
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
