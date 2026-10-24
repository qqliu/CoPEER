r"""Let G be a finite non-abelian group, let Z(G) denote its center, and let Γ(G) be the graph whose vertex set is G \ Z(G), with two vertices x and y adjacent exactly when xy ≠ yx. A subset of the vertices is independent when its elements are pairwise non-adjacent, and it is maximal independent when it is maximal under inclusion. For an integer i, let m.i.s.(G,i) be the number of maximal independent subsets of V(Γ(G)) having cardinality i. A subgroup H ≤ G is maximal abelian when H is abelian and every abelian subgroup K satisfying H ≤ K ≤ G equals H. Let m.a.s.(G,i) be the number of maximal abelian subgroups of G having cardinality i. Here |X| denotes cardinality, so m and all size indices are integers. The claim is: for every finite non-abelian group G and every integer m ≥ |Z(G)|, m.i.s.(G,m) = m.a.s.(G,m−|Z(G)|)."""

import json
from itertools import combinations

RECORD_ID = "arxiv_1706.07142v2__source_enriched_codex"
NOTES = ("Exact enumeration of S3 gives |Z(S3)|=1, m.i.s.(S3,1)=3, "
         "and m.a.s.(S3,0)=0, so the permitted case m=1 refutes the claim. "
         "The refuted statement is plainly an index-shift typo: maximal "
         "independent sets correspond to H minus Z(G), suggesting "
         "m.a.s.(G,m+|Z(G)|), not m−|Z(G)|.")

S3 = (
    (0, 1, 2),
    (0, 2, 1),
    (1, 0, 2),
    (1, 2, 0),
    (2, 0, 1),
    (2, 1, 0),
)
IDENTITY = (0, 1, 2)


def product(a, b):
    return tuple(a[b[position]] for position in range(3))


def reciprocal(a):
    return tuple(a.index(value) for value in range(3))


def commuting(a, b):
    return product(a, b) == product(b, a)


def subsets(elements):
    for size in range(len(elements) + 1):
        for choice in combinations(elements, size):
            yield frozenset(choice)


def subgroup(candidate):
    return (
        IDENTITY in candidate
        and all(reciprocal(a) in candidate for a in candidate)
        and all(product(a, b) in candidate for a in candidate for b in candidate)
    )


def pairwise_commuting(candidate):
    return all(commuting(a, b) for a in candidate for b in candidate)


def main():
    center = frozenset(
        a for a in S3 if all(commuting(a, b) for b in S3)
    )
    vertices = tuple(a for a in S3 if a not in center)

    independent = tuple(
        candidate for candidate in subsets(vertices)
        if pairwise_commuting(candidate)
    )
    maximal_independent = tuple(
        candidate for candidate in independent
        if not any(
            candidate < larger
            for larger in independent
        )
    )

    subgroups = tuple(candidate for candidate in subsets(S3) if subgroup(candidate))
    abelian_subgroups = tuple(
        candidate for candidate in subgroups if pairwise_commuting(candidate)
    )
    maximal_abelian = tuple(
        candidate for candidate in abelian_subgroups
        if not any(candidate < larger for larger in abelian_subgroups)
    )

    m = 1
    mis_at_m = sum(len(candidate) == m for candidate in maximal_independent)
    shifted_size = m - len(center)
    mas_at_shift = sum(
        len(candidate) == shifted_size for candidate in maximal_abelian
    )
    nonabelian = any(not commuting(a, b) for a in S3 for b in S3)

    confirmed = (
        len(S3) == 6
        and nonabelian
        and center == frozenset((IDENTITY,))
        and m >= len(center)
        and mis_at_m == 3
        and shifted_size == 0
        and mas_at_shift == 0
        and mis_at_m != mas_at_shift
    )
    if not confirmed:
        raise AssertionError("independent exact recomputation rejected the witness")

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED",
        "notes": NOTES,
    }, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
