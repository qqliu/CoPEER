"""The proof claims that hgP = gP is equivalent to ghg^(-1) belonging to P; in fact, the corresponding condition is g^(-1)hg belonging to P."""

import itertools
import json


def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def inverse(p):
    result = [0] * len(p)
    for i, value in enumerate(p):
        result[value] = i
    return tuple(result)


def generated_subgroup(identity, generators):
    result = set(generators)
    result.add(identity)
    while True:
        before = len(result)
        current = tuple(sorted(result))
        for a in current:
            for b in current:
                result.add(compose(a, b))
        if len(result) == before:
            return frozenset(result)


def all_subgroups(elements, identity):
    trivial = frozenset((identity,))
    found = {trivial}
    pending = [trivial]
    position = 0
    while position < len(pending):
        subgroup = pending[position]
        position += 1
        for element in elements:
            if element not in subgroup:
                extension = generated_subgroup(identity, tuple(subgroup) + (element,))
                if extension not in found:
                    found.add(extension)
                    pending.append(extension)
    return tuple(sorted(found, key=lambda group: (len(group), tuple(sorted(group)))))


def main():
    expected_subgroup_counts = (1, 2, 6, 30)
    checked = 0
    witness = None

    for n in range(1, 5):
        elements = tuple(itertools.permutations(range(n)))
        identity = tuple(range(n))
        subgroups = all_subgroups(elements, identity)
        assert len(subgroups) == expected_subgroup_counts[n - 1]

        for subgroup in subgroups:
            for g in elements:
                inverse_g = inverse(g)
                right_coset = frozenset(compose(g, p) for p in subgroup)
                for h in elements:
                    checked += 1
                    hg = compose(h, g)
                    left_coset = frozenset(compose(hg, p) for p in subgroup)
                    conjugate = compose(compose(inverse_g, h), g)
                    cosets_equal = left_coset == right_coset
                    corrected_condition = conjugate in subgroup
                    if cosets_equal != corrected_condition:
                        witness = (n, subgroup, g, h, cosets_equal, corrected_condition)
                        break
                if witness is not None:
                    break
            if witness is not None:
                break
        if witness is not None:
            break

    assert checked == 17505
    assert witness is None

    result = {
        "record_id": "reddit_askmath_1tiz0hm",
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "None in the bounded sweep.",
        "refutation_explanation": "The program checked whether (hgP = gP) differs from (g^(-1)hg belonging to P) for every listed triple. No difference occurred, so it found no counterexample within this finite space; this does not establish the unbounded group-theoretic claim.",
        "search_space": "All triples (n,P,g,h) with n in {1,2,3,4}, P any subgroup of S_n, and g,h in S_n: 1, 2, 6, and 30 subgroups respectively, totaling 17,505 triples."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
