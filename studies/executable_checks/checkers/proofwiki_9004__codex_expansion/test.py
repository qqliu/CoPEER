"""For an arbitrary ring homomorphism φ:R→S, if V is an ideal of R containing ker φ, then φ(V) is an ideal of the full codomain S."""

import itertools
import json

RECORD_ID = "proofwiki_9004__codex_expansion"
WITNESS_DESCRIPTION = (
    "R=F_2, S=F_2 x F_2, phi(a)=(a,a), and V=R; multiplying "
    "phi(1)=(1,1) by (1,0) in S gives (1,0) not in phi(V)."
)
REFUTATION_EXPLANATION = (
    "Here ker phi={0}, so V contains ker phi, but "
    "phi(V)={(0,0),(1,1)} is not closed under multiplication by arbitrary "
    "elements of S and therefore is not an ideal of S."
)
SEARCH_SPACE = (
    "All 16 functions from the two-element ring F_2 to the four-element ring "
    "F_2 x F_2, in lexicographic table order, paired with all 4 subsets V of "
    "F_2, checking the unital ring-homomorphism, ideal, kernel-containment, "
    "and codomain-ideal conditions exactly."
)


def r_add(a, b):
    return a ^ b


def r_mul(a, b):
    return a & b


def s_add(a, b):
    return a ^ b


def s_mul(a, b):
    return a & b


def subset_from_mask(mask, size):
    return frozenset(i for i in range(size) if mask & (1 << i))


def is_ideal(elements, universe, add, mul):
    if 0 not in elements:
        return False
    for a in elements:
        if a not in elements:  # additive inverse in characteristic two
            return False
        for b in elements:
            if add(a, b) not in elements:
                return False
        for scalar in universe:
            if mul(scalar, a) not in elements:
                return False
            if mul(a, scalar) not in elements:
                return False
    return True


def is_unital_hom(mapping):
    if mapping[0] != 0 or mapping[1] != 3:
        return False
    for a in range(2):
        for b in range(2):
            if mapping[r_add(a, b)] != s_add(mapping[a], mapping[b]):
                return False
            if mapping[r_mul(a, b)] != s_mul(mapping[a], mapping[b]):
                return False
    return True


def main():
    first_witness = None

    # Every one of the 16 function tables is paired with every one of the
    # four subsets. The complete 64-pair bounded space is traversed even
    # after a witness has been found.
    for mapping in itertools.product(range(4), repeat=2):
        hom_ok = is_unital_hom(mapping)
        for mask in range(4):
            ideal = subset_from_mask(mask, 2)
            ideal_ok = is_ideal(ideal, range(2), r_add, r_mul)
            kernel = frozenset(a for a in range(2) if mapping[a] == 0)
            kernel_ok = kernel.issubset(ideal)
            image = frozenset(mapping[a] for a in ideal)
            image_ideal_ok = is_ideal(image, range(4), s_add, s_mul)

            if hom_ok and ideal_ok and kernel_ok and not image_ideal_ok:
                bad_products = tuple(
                    (scalar, x, s_mul(scalar, x))
                    for scalar in range(4)
                    for x in sorted(image)
                    if s_mul(scalar, x) not in image
                )
                candidate = (mapping, ideal, image, bad_products)
                if first_witness is None:
                    first_witness = candidate

    expected = (
        (0, 3),
        frozenset((0, 1)),
        frozenset((0, 3)),
        ((1, 3, 1), (2, 3, 2)),
    )

    if first_witness == expected:
        outcome = "WITNESS_FOUND"
        witness_description = WITNESS_DESCRIPTION
        refutation_explanation = REFUTATION_EXPLANATION
    else:
        outcome = "NO_WITNESS_EXHAUSTIVE"
        witness_description = "No witness was found in the stated finite space."
        refutation_explanation = (
            "The finite sweep found no counterexample; this would not establish "
            "the unrestricted claim."
        )

    result = {
        "record_id": RECORD_ID,
        "outcome": outcome,
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
