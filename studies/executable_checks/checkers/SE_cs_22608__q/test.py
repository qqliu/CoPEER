r"""If $X$ is the maximum weight independent set of the circular-arc graph $A$, then for any clique $Z$ of $A$, we have that $\| X \cap Z\| = 1$."""

import json
from itertools import combinations, product

RECORD_ID = "SE_cs_22608__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The complete graph K_3 on vertices {0,1,2}, with respective weights "
    "(1,1,2), has the unique maximum weight independent set X={2}. The set "
    "Z={0,1} is a clique and X intersects Z in zero vertices."
)
REFUTATION_EXPLANATION = (
    "K_3 is circular-arc because three identical nonempty arcs have "
    "pairwise-intersection graph K_3. Every nonempty independent set in K_3 "
    "is a singleton, and vertex 2 has weight 2 while vertices 0 and 1 each "
    "have weight 1, so X={2} is the unique maximum weight independent set. "
    "However, Z={0,1} is a clique and |X intersect Z|=0, not 1."
)
SEARCH_SPACE = (
    "All 39 positively integer-weighted complete graphs K_n for 1 <= n <= 3, "
    "with labeled vertices 0,...,n-1 and weights in {1,2,3}; for each weighted "
    "graph, every vertex subset was checked for independence and maximum total "
    "weight, and every nonempty vertex subset was checked as a clique."
)


def vertex_subsets(n, include_empty):
    first_mask = 0 if include_empty else 1
    return tuple(
        tuple(vertex for vertex in range(n) if mask & (1 << vertex))
        for mask in range(first_mask, 1 << n)
    )


def adjacent(left, right):
    return left != right


def is_independent(vertices):
    return all(not adjacent(left, right) for left, right in combinations(vertices, 2))


def is_clique(vertices):
    return all(adjacent(left, right) for left, right in combinations(vertices, 2))


def has_identical_arc_certificate(n):
    arcs = tuple(frozenset((0, 1)) for _ in range(n))
    return all(
        bool(arcs[left].intersection(arcs[right])) == adjacent(left, right)
        for left, right in combinations(range(n), 2)
    )


def search():
    selected = None
    instance_count = 0

    for n in range(1, 4):
        assert has_identical_arc_certificate(n)
        all_subsets = vertex_subsets(n, True)
        nonempty_subsets = vertex_subsets(n, False)

        for weights in product(range(1, 4), repeat=n):
            instance_count += 1
            independent_sets = tuple(
                subset for subset in all_subsets if is_independent(subset)
            )
            clique_sets = tuple(
                subset for subset in nonempty_subsets if is_clique(subset)
            )
            maximum_weight = max(
                sum(weights[vertex] for vertex in subset)
                for subset in independent_sets
            )
            maximum_sets = tuple(
                subset
                for subset in independent_sets
                if sum(weights[vertex] for vertex in subset) == maximum_weight
            )

            for maximum_set in maximum_sets:
                for clique_set in clique_sets:
                    violates = len(set(maximum_set).intersection(clique_set)) != 1
                    robust = (
                        len(maximum_sets) == 1
                        and len(clique_set) >= 2
                        and not set(maximum_set).intersection(clique_set)
                    )
                    if selected is None and violates and robust:
                        selected = (n, weights, maximum_set, clique_set)

    assert instance_count == 39
    return selected


witness = search()
assert witness == (3, (1, 1, 2), (2,), (0, 1))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
