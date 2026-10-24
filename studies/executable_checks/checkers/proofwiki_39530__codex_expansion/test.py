"""The asserted equivalence between membership in the interior of the closure of the complement of A's closure and membership in that complement is false in general."""

import json


def is_topology(opens, full):
    members = set(opens)
    if 0 not in members or full not in members:
        return False
    for left in opens:
        for right in opens:
            if (left | right) not in members:
                return False
            if (left & right) not in members:
                return False
    return True


def interior(subset, opens, full):
    result = 0
    outside = full ^ subset
    for open_set in opens:
        if open_set & outside == 0:
            result |= open_set
    return result


def closure(subset, opens, full):
    return full ^ interior(full ^ subset, opens, full)


def search():
    first_witness = None
    family_count = 0
    topology_count = 0
    case_count = 0

    for size in range(1, 3):
        subset_count = 1 << size
        full = subset_count - 1
        family_count_for_size = 1 << subset_count
        for family_mask in range(family_count_for_size):
            family_count += 1
            opens = tuple(
                subset
                for subset in range(subset_count)
                if family_mask & (1 << subset)
            )
            if not is_topology(opens, full):
                continue
            topology_count += 1
            for a_set in range(subset_count):
                closed_a = closure(a_set, opens, full)
                complement = full ^ closed_a
                left_set = interior(closure(complement, opens, full), opens, full)
                for point in range(size):
                    case_count += 1
                    point_bit = 1 << point
                    left = bool(left_set & point_bit)
                    right = bool(complement & point_bit)
                    if left != right and first_witness is None:
                        first_witness = (size, opens, a_set, point)

    assert family_count == 20
    assert topology_count == 5
    assert case_count == 34
    assert first_witness == (2, (0, 1, 3), 2, 1)

    return {
        "record_id": "proofwiki_39530__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "X={0,1}, topology={∅,{0},X}, A={1}, x=1. closure(A)={1}, X\\closure(A)={0}, closure({0})=X, and interior(X)=X.",
        "refutation_explanation": "Thus x=1 belongs to interior(closure(X\\closure(A))) but does not belong to X\\closure(A), so the asserted equivalence fails.",
        "search_space": "All 20 families of subsets on the labeled carriers X={0,...,n-1} for n=1,2 were checked; for each of the 5 valid topologies (1 for n=1 and 4 for n=2), every subset A and every point x were tested, totaling 34 topology-A-point cases."
    }


print(json.dumps(search(), ensure_ascii=True, separators=(",", ":")))
