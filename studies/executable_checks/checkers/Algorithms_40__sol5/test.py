"""For the remaining edges in M1 (those in alternating paths or cycles), the
number is at most |M2| (since in each component, the number of M1 edges is
at most the number of M2 edges plus one, and summing over all components
gives at most |M2|)."""

import json

RECORD_ID = "Algorithms_40__sol5"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The simple path v0-v1-v2-v3 with M1={(v0,v1),(v2,v3)} and "
    "M2={(v1,v2)}. Its edge labels alternate M1,M2,M1."
)
REFUTATION_EXPLANATION = (
    "Both M1 edges are in an alternating path, so the claimed left side is 2, "
    "while |M2| is 1. Thus 2 <= 1 is false, even though this component "
    "satisfies the stated componentwise bound 2 <= 1+1."
)
SEARCH_SPACE = (
    "All 14 single connected labeled constructions consisting of a simple "
    "alternating path with 2 through 6 edges and either initial label, or a "
    "simple alternating cycle with 4 or 6 edges and either initial label; "
    "every construction was checked."
)


def construction(kind, edge_count, first_label):
    labels = tuple(
        first_label if index % 2 == 0 else 3 - first_label
        for index in range(edge_count)
    )
    if kind == "path":
        edges = tuple((index, index + 1) for index in range(edge_count))
    else:
        edges = tuple((index, (index + 1) % edge_count) for index in range(edge_count))
    return edges, labels


def is_matching(edges):
    used = set()
    for left, right in edges:
        if left in used or right in used:
            return False
        used.add(left)
        used.add(right)
    return True


def main():
    candidates = []
    for edge_count in range(2, 7):
        for first_label in (1, 2):
            candidates.append(("path", edge_count, first_label))
    for edge_count in (4, 6):
        for first_label in (1, 2):
            candidates.append(("cycle", edge_count, first_label))

    violations = []
    for kind, edge_count, first_label in candidates:
        edges, labels = construction(kind, edge_count, first_label)
        m1 = tuple(edge for edge, label in zip(edges, labels) if label == 1)
        m2 = tuple(edge for edge, label in zip(edges, labels) if label == 2)
        assert is_matching(m1)
        assert is_matching(m2)
        assert all(labels[index] != labels[index + 1] for index in range(edge_count - 1))
        if kind == "cycle":
            assert labels[-1] != labels[0]
        assert len(m1) <= len(m2) + 1
        if len(m1) > len(m2):
            violations.append((kind, edge_count, first_label, m1, m2))

    assert len(candidates) == 14
    assert violations
    first = violations[0]
    assert first == (
        "path",
        3,
        1,
        ((0, 1), (2, 3)),
        ((1, 2),),
    )

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
