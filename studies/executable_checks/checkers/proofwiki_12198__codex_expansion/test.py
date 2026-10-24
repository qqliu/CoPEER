"""The formula sqrt(a_1^2+a_2^2) defines a norm on C^2, in particular satisfying norm(x)=0 iff x=0."""

import json


def gaussian_square(z):
    real, imag = z
    return (real * real - imag * imag, 2 * real * imag)


def gaussian_add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def is_zero(z):
    return z == (0, 0)


def main():
    candidates = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    witness = None

    for a_1 in candidates:
        for a_2 in candidates:
            radicand = gaussian_add(gaussian_square(a_1), gaussian_square(a_2))
            vector_is_nonzero = not (is_zero(a_1) and is_zero(a_2))
            if vector_is_nonzero and is_zero(radicand):
                witness = (a_1, a_2)
                break
        if witness is not None:
            break

    if witness != ((1, 0), (0, 1)):
        raise AssertionError("fixed exhaustive search did not find the expected first witness")

    result = {
        "record_id": "proofwiki_12198__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The vector (a_1, a_2) = (1, i) is nonzero, but a_1^2 + a_2^2 = 1^2 + i^2 = 1 + (-1) = 0, so the displayed formula gives norm((1, i)) = sqrt(0) = 0.",
        "refutation_explanation": "This violates the claimed implication norm(x)=0 only if x=0, so the displayed formula does not define a norm on C^2.",
        "search_space": "All 25 ordered pairs (a_1, a_2) in {0, 1, -1, i, -i}^2, traversed in that fixed displayed order and represented by exact Gaussian-integer coefficient pairs."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
