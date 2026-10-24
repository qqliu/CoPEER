r"""The proof claims that $H_1 \cap N_2$ is normal in $H_1$ from the assumption that $N_2$ is normal only in $H_2$."""

import json

record_id = "proofwiki_72228__codex_expansion"
confirmed_notes = "Exact permutation arithmetic confirms the witness: N_2=H_2 is normal in H_2, while H_1∩N_2=N_2 is not normal in H_1=S_3 because conjugating (0 1) by (1 2) yields (0 2), outside N_2. The refuted statement is substantive, not plainly a typo."
invalid_notes = "Independent exact permutation arithmetic did not validate the reported witness. The proposed refutation concerns a substantive statement, not plainly a typo."

identity = (0, 1, 2)
s3 = frozenset({
    (0, 1, 2),
    (0, 2, 1),
    (1, 0, 2),
    (1, 2, 0),
    (2, 0, 1),
    (2, 1, 0),
})
transposition_01 = (1, 0, 2)
transposition_12 = (0, 2, 1)
transposition_02 = (2, 1, 0)
h1 = s3
h2 = frozenset({identity, transposition_01})
n2 = frozenset({identity, transposition_01})


def product(first, second):
    values = []
    for point in (0, 1, 2):
        values.append(first[second[point]])
    return tuple(values)


def reciprocal(permutation):
    values = [0, 0, 0]
    for point in (0, 1, 2):
        values[permutation[point]] = point
    return tuple(values)


def subgroup(candidate, ambient):
    if not candidate.issubset(ambient) or identity not in candidate:
        return False
    for member in candidate:
        if reciprocal(member) not in candidate:
            return False
        for other in candidate:
            if product(member, other) not in candidate:
                return False
    return True


def conjugated(member, conjugator):
    return product(product(conjugator, member), reciprocal(conjugator))


def normal(candidate, ambient):
    if not subgroup(candidate, ambient):
        return False
    for conjugator in ambient:
        for member in candidate:
            if conjugated(member, conjugator) not in candidate:
                return False
    return True


intersection = h1.intersection(n2)
image = conjugated(transposition_01, transposition_12)
witness_valid = (
    subgroup(h1, s3)
    and subgroup(h2, s3)
    and subgroup(n2, h2)
    and normal(n2, h2)
    and intersection == n2
    and transposition_12 in h1
    and transposition_01 in intersection
    and image == transposition_02
    and image not in intersection
    and not normal(intersection, h1)
)

if witness_valid:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_notes

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False))
