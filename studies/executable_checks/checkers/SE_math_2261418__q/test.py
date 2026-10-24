r"""Assume, for the sake of contradiction, that both $G$ and $\bar G$ are nonplanar. Then $$\lvert{E(G)}\rvert+\lvert{E(\bar G)}\rvert \le (3\lvert{V(G)}\rvert-6)+(3\lvert{V(\bar G)}\rvert-6)=54. \Rightarrow\Leftarrow$$"""

import json
from itertools import combinations

RECORD_ID = "SE_math_2261418__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = ("On V={0,...,10}, let G have all 10 edges within {0,...,4} and "
                       "all 9 edges between {5,6,7} and {8,9,10}, with no other "
                       "edges. Then G contains K5, while its complement contains K3,3 "
                       "between {0,1,2} and {5,6,7}. Moreover, |E(G)|=19 and "
                       "|E(complement)|=36.")
REFUTATION_EXPLANATION = ("Both G and its complement are nonplanar: the former contains "
                          "K5, and the latter contains K3,3. Nevertheless, "
                          "|E(G)|+|E(complement)|=19+36=55>54, directly violating "
                          "the asserted inequality.")
SEARCH_SPACE = ("All 4,620 labeled simple graphs on vertex set {0,...,10} that are "
                "disjoint unions of a K5 and a K3,3, enumerated by every 5-subset A "
                "and every unordered 3+3 partition of its six-vertex complement. "
                "The entire family is swept in lexicographic order.")


def pair(u, v):
    return (u, v) if u < v else (v, u)


def contains_clique(edges, vertices):
    return all(pair(u, v) in edges for u, v in combinations(vertices, 2))


def contains_complete_bipartite(edges, left, right):
    return all(pair(u, v) in edges for u in left for v in right)


def main():
    vertices = tuple(range(11))
    universe = set(combinations(vertices, 2))
    first_witness = None
    swept = 0

    for a in combinations(vertices, 5):
        remaining = tuple(v for v in vertices if v not in a)
        for b in combinations(remaining, 3):
            c = tuple(v for v in remaining if v not in b)
            if b > c:
                continue

            swept += 1
            edges = set(combinations(a, 2))
            edges.update(pair(u, v) for u in b for v in c)
            complement = universe - edges

            g_has_k5 = contains_clique(edges, a)
            complement_has_k33 = contains_complete_bipartite(
                complement, a[:3], b
            )
            violates_bound = len(edges) + len(complement) > 54

            if (g_has_k5 and complement_has_k33 and violates_bound
                    and first_witness is None):
                first_witness = (a, b, c, len(edges), len(complement))

    assert swept == 4620
    assert first_witness == (
        (0, 1, 2, 3, 4),
        (5, 6, 7),
        (8, 9, 10),
        19,
        36,
    )

    payload = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
