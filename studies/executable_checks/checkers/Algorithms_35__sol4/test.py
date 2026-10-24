"""Now consider the closed walk obtained by following Px from v to x, then the edge {x, y}, then Py in reverse from y back to v. This is a cycle in G."""

import itertools
import json


def is_simple_cycle(vertex_sequence):
    return (
        len(vertex_sequence) >= 4
        and vertex_sequence[0] == vertex_sequence[-1]
        and len(set(vertex_sequence[:-1])) == len(vertex_sequence) - 1
    )


def main():
    vertices_after_v = (1, 2, 3)
    paths = []
    for tail_length in range(1, 4):
        for tail in itertools.permutations(vertices_after_v, tail_length):
            paths.append((0,) + tail)

    total = 0
    cycles = 0
    failures = 0
    first_failure = None

    for px in paths:
        for py in paths:
            if px[-1] == py[-1]:
                continue
            total += 1
            closed_walk = px + tuple(reversed(py))
            if is_simple_cycle(closed_walk):
                cycles += 1
            else:
                failures += 1
                if first_failure is None:
                    first_failure = (px, py, closed_walk)

    assert total == 150
    assert cycles == 18
    assert failures == 132
    assert first_failure == ((0, 1), (0, 1, 2), (0, 1, 2, 1, 0))

    result = {
        "record_id": "Algorithms_35__sol4",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No claim-level witness is justified. The bounded encoding contains 132 walks with a repeated nonterminal vertex, including Px=(0,1), Py=(0,1,2), whose resulting sequence is (0,1,2,1,0), but the quote does not establish that this encoding represents its unspecified Px and Py.",
        "refutation_explanation": "The quote supplies neither definitions nor hypotheses fixing G, Px, Py, v, x, and y, and it does not state whether Px and Py may share vertices other than v. Both cycle-forming and non-cycle-forming illustrative completions therefore exist, so the assertion cannot be decided from the permitted data alone.",
        "search_space": "All 150 ordered pairs of individually vertex-distinct sequences Px and Py over vertices {0,1,2,3}, each of length 2, 3, or 4, both beginning at v=0 and having different endpoints x and y; the edge {x,y} is present by construction. Exactly 18 encoded walks satisfy the simple-cycle predicate and 132 do not."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
