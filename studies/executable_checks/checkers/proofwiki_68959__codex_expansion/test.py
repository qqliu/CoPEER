"""The substitution of the integer summation index by α+k is a valid reindexing of a sum over ℤ for arbitrary complex α."""

import json
from fractions import Fraction


def is_integer_complex(real_part, imaginary_part):
    return imaginary_part == 0 and real_part.denominator == 1


alphas = (
    (Fraction(0, 1), Fraction(0, 1)),
    (Fraction(1, 2), Fraction(0, 1)),
)
indices = (0,)
violations = []

for alpha_real, alpha_imaginary in alphas:
    for k in indices:
        translated_real = alpha_real + k
        translated_imaginary = alpha_imaginary
        if not is_integer_complex(translated_real, translated_imaginary):
            violations.append(
                (alpha_real, alpha_imaginary, k,
                 translated_real, translated_imaginary)
            )

expected = (
    Fraction(1, 2), Fraction(0, 1), 0,
    Fraction(1, 2), Fraction(0, 1)
)
assert violations == [expected]

result = {
    "record_id": "proofwiki_68959__codex_expansion",
    "outcome": "WITNESS_FOUND",
    "witness_description": "The bounded sweep found α = 1/2 + 0i and k = 0. The translated index α+k = 1/2 is not an integer.",
    "refutation_explanation": "Because α = 1/2 is a complex number and k = 0 belongs to ℤ, but α+k does not belong to ℤ, this substitution does not map the integer index set into itself and therefore is not a valid reindexing over ℤ for arbitrary complex α.",
    "search_space": "Exhaustively tested α in {0 + 0i, 1/2 + 0i} and k in {0}, using Fraction for both components and checking exactly whether α+k belongs to ℤ."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
