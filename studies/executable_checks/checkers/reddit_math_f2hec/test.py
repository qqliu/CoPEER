"""Closure under arbitrary intersections together with any nontrivial separation property forces the topology to be discrete."""

import json

RECORD_ID = "reddit_math_f2hec"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is certified because the permitted data gives no definition "
    "or decidable predicate for \u201cnontrivial separation property.\u201d"
)
REFUTATION_EXPLANATION = (
    "The bounded sweep can decide topology axioms, closure under every "
    "intersection of open sets, and nondiscreteness, but it cannot decide "
    "the claim\u2019s separation hypothesis without inventing a definition absent "
    "from the supplied quote."
)
SEARCH_SPACE = (
    "All 278 set-family encodings on the labeled carriers {0,...,n-1} for "
    "n = 0, 1, 2, 3 were examined in fixed order; topology axioms and every "
    "subfamily intersection were checked exactly. The undefined separation "
    "condition prevents witness certification."
)


def members_of_family(family_code, subset_count):
    return tuple(
        subset
        for subset in range(subset_count)
        if family_code & (1 << subset)
    )


def is_topology_and_arbitrary_intersection_closed(n, family_code):
    subset_count = 1 << n
    universe = subset_count - 1
    members = members_of_family(family_code, subset_count)
    member_set = set(members)

    if 0 not in member_set or universe not in member_set:
        return False

    subfamily_count = 1 << len(members)
    for selection in range(subfamily_count):
        union = 0
        intersection = universe
        for index, open_set in enumerate(members):
            if selection & (1 << index):
                union |= open_set
                intersection &= open_set
        if union not in member_set:
            return False
        if intersection not in member_set:
            return False
    return True


def sweep():
    family_encodings = 0
    qualifying_topologies = 0
    nondiscrete_candidates = 0

    for n in range(4):
        subset_count = 1 << n
        family_count = 1 << subset_count
        discrete_code = family_count - 1
        for family_code in range(family_count):
            family_encodings += 1
            if is_topology_and_arbitrary_intersection_closed(n, family_code):
                qualifying_topologies += 1
                if family_code != discrete_code:
                    nondiscrete_candidates += 1

    assert family_encodings == 278
    assert qualifying_topologies == 35
    assert nondiscrete_candidates == 31


def main():
    sweep()
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
