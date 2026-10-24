r"""The proof claims that H_1 ∩ N_2 is normal in H_1, although the hypotheses only establish that N_2 is normal in H_2."""

import itertools
import json


def product(first, second):
    return tuple(first[value] for value in second)


def reciprocal(permutation):
    return tuple(permutation.index(value) for value in range(3))


def conjugate(conjugator, element):
    return product(product(conjugator, element), reciprocal(conjugator))


def subgroup(candidate):
    identity = (0, 1, 2)
    return (
        identity in candidate
        and all(reciprocal(element) in candidate for element in candidate)
        and all(
            product(left, right) in candidate
            for left in candidate
            for right in candidate
        )
    )


def normal(candidate, ambient):
    return (
        candidate <= ambient
        and subgroup(candidate)
        and all(
            conjugate(conjugator, element) in candidate
            for conjugator in ambient
            for element in candidate
        )
    )


def main():
    identity = (0, 1, 2)
    swap_12 = (0, 2, 1)
    swap_01 = (1, 0, 2)
    swap_02 = (2, 1, 0)

    h1 = set(itertools.permutations(range(3)))
    h2 = {identity, swap_12}
    n2 = {identity, swap_12}
    intersection = h1 & n2

    verified = (
        len(h1) == 6
        and subgroup(h1)
        and h2 == n2
        and subgroup(h2)
        and normal(n2, h2)
        and intersection == n2
        and swap_01 in h1
        and conjugate(swap_01, swap_12) == swap_02
        and swap_02 not in intersection
        and not normal(intersection, h1)
    )
    if not verified:
        raise AssertionError("the concrete witness did not verify")

    result = {
        "record_id": "proofwiki_13715__codex_expansion",
        "verdict": "CONFIRMED",
        "notes": "Independent exact permutation computation confirms the witness: N_2 is normal in H_2=N_2, while H_1∩N_2=N_2 is not normal in H_1=S_3. The refuted statement is substantive, not plainly a typo."
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
