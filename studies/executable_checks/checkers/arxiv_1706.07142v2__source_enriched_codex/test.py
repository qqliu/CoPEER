"""Let G be a finite non-abelian group, let Z(G) denote its center, and let Γ(G) be the graph whose vertex set is G \ Z(G), with two vertices x and y adjacent exactly when xy ≠ yx. A subset of the vertices is independent when its elements are pairwise non-adjacent, and it is maximal independent when it is maximal under inclusion. For an integer i, let m.i.s.(G,i) be the number of maximal independent subsets of V(Γ(G)) having cardinality i. A subgroup H ≤ G is maximal abelian when H is abelian and every abelian subgroup K satisfying H ≤ K ≤ G equals H. Let m.a.s.(G,i) be the number of maximal abelian subgroups of G having cardinality i. Here |X| denotes cardinality, so m and all size indices are integers. The claim is: for every finite non-abelian group G and every integer m ≥ |Z(G)|, m.i.s.(G,m) = m.a.s.(G,m−|Z(G)|)."""

import itertools
import json

RECORD_ID = "arxiv_1706.07142v2__source_enriched_codex"
WITNESS = "G=S3 acting on {0,1,2}, with m=1."
EXPLANATION = ("For m=1, |Z(S3)|=1, so m is permitted. The three "
               "transpositions are three distinct maximal independent singleton "
               "sets, hence m.i.s.(S3,1)=3. No subgroup has cardinality 0, "
               "hence m.a.s.(S3,0)=0; therefore 3 ≠ 0.")
SPACE = ("The program exhaustively enumerates all 64 subsets of S3 to identify "
         "subgroups and all 32 subsets of S3 \\ Z(S3) to identify maximal "
         "independent sets, then checks every integer m in {1,2,3,4,5,6}.")


def compose(left, right):
    return tuple(left[right[index]] for index in range(3))


def inverse(permutation):
    result = [0, 0, 0]
    for index, image in enumerate(permutation):
        result[image] = index
    return tuple(result)


def commute(left, right):
    return compose(left, right) == compose(right, left)


def all_subsets(items):
    ordered = tuple(items)
    for mask in range(1 << len(ordered)):
        yield frozenset(
            ordered[index]
            for index in range(len(ordered))
            if mask & (1 << index)
        )


def is_subgroup(candidate, identity):
    if identity not in candidate:
        return False
    for left in candidate:
        if inverse(left) not in candidate:
            return False
        for right in candidate:
            if compose(left, right) not in candidate:
                return False
    return True


def is_abelian(candidate):
    return all(commute(left, right) for left in candidate for right in candidate)


def is_independent(candidate):
    return all(commute(left, right) for left in candidate for right in candidate)


def main():
    group = tuple(itertools.permutations(range(3)))
    identity = (0, 1, 2)
    center = frozenset(
        element for element in group
        if all(commute(element, other) for other in group)
    )
    vertices = tuple(element for element in group if element not in center)

    subgroups = tuple(
        candidate for candidate in all_subsets(group)
        if is_subgroup(candidate, identity)
    )
    abelian_subgroups = tuple(
        candidate for candidate in subgroups if is_abelian(candidate)
    )
    maximal_abelian = tuple(
        candidate for candidate in abelian_subgroups
        if not any(candidate < larger for larger in abelian_subgroups)
    )

    independent_sets = tuple(
        candidate for candidate in all_subsets(vertices)
        if is_independent(candidate)
    )
    maximal_independent = tuple(
        candidate for candidate in independent_sets
        if all(
            frozenset(set(candidate) | {vertex}) not in independent_sets
            for vertex in vertices if vertex not in candidate
        )
    )

    mis_counts = {
        size: sum(1 for candidate in maximal_independent if len(candidate) == size)
        for size in range(len(vertices) + 1)
    }
    mas_counts = {
        size: sum(1 for candidate in maximal_abelian if len(candidate) == size)
        for size in range(len(group) + 1)
    }

    discrepancies = []
    for m_value in range(len(center), len(group) + 1):
        left_count = mis_counts.get(m_value, 0)
        right_count = mas_counts.get(m_value - len(center), 0)
        if left_count != right_count:
            discrepancies.append((m_value, left_count, right_count))

    assert len(group) == 6
    assert len(center) == 1
    assert len(tuple(all_subsets(group))) == 64
    assert len(tuple(all_subsets(vertices))) == 32
    assert discrepancies[0] == (1, 3, 0)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS,
        "refutation_explanation": EXPLANATION,
        "search_space": SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
