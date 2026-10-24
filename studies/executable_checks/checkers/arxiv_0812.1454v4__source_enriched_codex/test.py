r'''Let \(A\subset\mathbb C\) be finite with \(0\notin A\), and let \(A_2=A\times A\). Let \(T\) be the finite set of complex lines through the origin that support points of \(A_2\), and let \(\nu(t)\) be the number of points of \(A_2\) on the line indexed by \(t\). Thus the multiplicative energy is \(E(A)=\sum_{t\in T}\nu(t)^2\). Dyadically decompose the range \(\nu(t)\in\{1,\ldots,|A|\}\), and let \(T'\subseteq T\) be a dyadic class whose contribution \(\sum_{t\in T'}\nu(t)^2\) is maximal; in particular, the values \(\nu(t)\) for \(t\in T'\) differ by at most a factor of two. Under the standard embedding \(\mathbb C^2\cong\mathbb R^4\), let \(X\) be the image of \(A_2\), and let \(\pi_t\) be the real two-plane corresponding to the complex line indexed by \(t\). Suppose there is a subset \(T''\subseteq T'\) with \(|T''|\ge |T'|/2\) such that, for each \(t\in T''\), one can assign another \(t_1\in T''\) and retain at least half of the points of \(X\cap\pi_t\) and at least half of the points of \(X\cap\pi_{t_1}\), with every resulting vector sum \(x+x_1\) pairwise distinct across the construction. Then \[\sum_{t\in T'}\nu(t)^2\le \frac{1}{32}|X+X|.\] Here \(|\cdot|\) denotes finite-set cardinality, \(X+X=\{x+x_1:x,x_1\in X\}\), \(|X|=|A|^2\), and \(|X+X|=|A+A|^2\).'''

import json
from fractions import Fraction
from itertools import combinations, product

RECORD_ID = "arxiv_0812.1454v4__source_enriched_codex"
WITNESS_DESCRIPTION = "A={1,2,4}; T'=T'' consists of slopes 1/2, 1, and 2, with occupancies 2, 3, and 2. Assign 1/2→1, 1→2, and 2→1/2. Retain {(2,1)}, {(1,1),(2,2)}, and {(1,2)}, respectively. The resulting sums are (3,2), (4,3), (2,3), (3,4), and (3,3), all distinct."
REFUTATION_EXPLANATION = "The dyadic contributions are 2 from the two occupancy-1 lines and 17 from the occupancy-2-or-3 class, so T' is maximal and its squared-occupancy sum is 17. Also |A+A|=6, hence |X+X|=36. The claimed conclusion would require 17≤36/32=9/8, which is false."
SEARCH_SPACE = "Deterministic exhaustive search over all nonempty subsets A of {1,2,4,8}; for each A, dyadic classes [2^k,2^(k+1)) of line occupancies, every maximal-contribution class T', every T''⊆T' with |T''|≥ceil(|T'|/2), every assignment t↦t1 in T'' with t1≠t, and every retained subset of each line of size at least ceil(ν(t)/2), in lexicographic order, stopping at the first counterexample."


def retained_choices(points):
    minimum = (len(points) + 1) // 2
    return tuple(
        choice
        for size in range(minimum, len(points) + 1)
        for choice in combinations(points, size)
    )


def find_witness():
    universe = (1, 2, 4, 8)
    for size in range(1, len(universe) + 1):
        for a_set in combinations(universe, size):
            lines = {}
            for x in a_set:
                for y in a_set:
                    slope = Fraction(y, x)
                    lines.setdefault(slope, []).append((x, y))
            lines = {slope: tuple(sorted(points)) for slope, points in lines.items()}

            classes = {}
            for slope in sorted(lines):
                class_index = len(lines[slope]).bit_length() - 1
                classes.setdefault(class_index, []).append(slope)
            contributions = {
                class_index: sum(len(lines[slope]) ** 2 for slope in slopes)
                for class_index, slopes in classes.items()
            }
            maximum = max(contributions.values())

            x_points = tuple(product(a_set, repeat=2))
            x_sum_size = len({
                (p[0] + q[0], p[1] + q[1])
                for p in x_points
                for q in x_points
            })

            for class_index in sorted(classes):
                if contributions[class_index] != maximum:
                    continue
                t_prime = tuple(sorted(classes[class_index]))
                energy = contributions[class_index]
                minimum_t_double = (len(t_prime) + 1) // 2

                for double_size in range(minimum_t_double, len(t_prime) + 1):
                    for t_double in combinations(t_prime, double_size):
                        assignment_choices = tuple(
                            tuple(other for other in t_double if other != slope)
                            for slope in t_double
                        )
                        for assigned in product(*assignment_choices):
                            assignment = dict(zip(t_double, assigned))
                            retained_lists = tuple(
                                retained_choices(lines[slope])
                                for slope in t_double
                            )
                            for retained_tuple in product(*retained_lists):
                                retained = dict(zip(t_double, retained_tuple))
                                sums = []
                                for slope in t_double:
                                    other = assignment[slope]
                                    for point in retained[slope]:
                                        for other_point in retained[other]:
                                            sums.append((
                                                point[0] + other_point[0],
                                                point[1] + other_point[1],
                                            ))
                                if len(sums) != len(set(sums)):
                                    continue
                                if 32 * energy > x_sum_size:
                                    return (
                                        a_set,
                                        t_prime,
                                        t_double,
                                        assigned,
                                        retained_tuple,
                                        tuple(sums),
                                        energy,
                                        x_sum_size,
                                    )
    return None


witness = find_witness()
expected = (
    (1, 2, 4),
    (Fraction(1, 2), Fraction(1, 1), Fraction(2, 1)),
    (Fraction(1, 2), Fraction(1, 1), Fraction(2, 1)),
    (Fraction(1, 1), Fraction(2, 1), Fraction(1, 2)),
    (((2, 1),), ((1, 1), (2, 2)), ((1, 2),)),
    ((3, 2), (4, 3), (2, 3), (3, 4), (3, 3)),
    17,
    36,
)
assert witness == expected

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
