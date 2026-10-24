r"""The proof claims that $H_1 \cap N_2$ is normal in $H_1$ from the assumption that $N_2$ is normal only in $H_2$."""

import itertools
import json

RECORD_ID = "proofwiki_72228__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "In the ambient group S_3 on {0,1,2}, take H_1=S_3 and "
    "H_2=N_2={id,(0 1)}."
)
REFUTATION_EXPLANATION = (
    "N_2 is normal in H_2 because N_2=H_2. But H_1∩N_2=N_2 is not "
    "normal in H_1: conjugation of (0 1) by (1 2) gives (0 2), which "
    "is not in N_2."
)
SEARCH_SPACE = (
    "All 216 ordered triples (H_1,H_2,N_2) of the six subgroups of S_3, "
    "retaining those with N_2 normal in H_2 and testing whether H_1∩N_2 "
    "is normal in H_1."
)

ELEMENTS = tuple(itertools.permutations(range(3)))
IDENTITY = (0, 1, 2)


def compose(left, right):
    return tuple(left[right[index]] for index in range(3))


def inverse(permutation):
    result = [0, 0, 0]
    for index in range(3):
        result[permutation[index]] = index
    return tuple(result)


def conjugate(element, by_element):
    return compose(compose(by_element, element), inverse(by_element))


def is_subgroup(candidate):
    return (
        IDENTITY in candidate
        and all(
            compose(left, right) in candidate
            for left in candidate
            for right in candidate
        )
    )


def is_normal(candidate, group):
    return candidate.issubset(group) and all(
        conjugate(element, by_element) in candidate
        for element in candidate
        for by_element in group
    )


subgroups = []
for mask in range(1 << len(ELEMENTS)):
    candidate = frozenset(
        ELEMENTS[index]
        for index in range(len(ELEMENTS))
        if mask & (1 << index)
    )
    if is_subgroup(candidate):
        subgroups.append(candidate)

assert len(subgroups) == 6

counterexamples = []
examined = 0
for h1 in subgroups:
    for h2 in subgroups:
        for n2 in subgroups:
            examined += 1
            if is_normal(n2, h2):
                intersection = frozenset(h1.intersection(n2))
                if not is_normal(intersection, h1):
                    counterexamples.append((h1, h2, n2))

assert examined == 216

full_s3 = frozenset(ELEMENTS)
transposition_01_subgroup = frozenset((IDENTITY, (1, 0, 2)))
witness = (full_s3, transposition_01_subgroup, transposition_01_subgroup)
assert witness in counterexamples
assert conjugate((1, 0, 2), (0, 2, 1)) == (2, 1, 0)
assert (2, 1, 0) not in transposition_01_subgroup

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, sort_keys=False))
