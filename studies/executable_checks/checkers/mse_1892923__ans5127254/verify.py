r"""Let $f, g \in \mathbb{Z}[x]$ be s.t. $g(n)|f(n)$ for every $n \in \mathbb{N}$. Then, $f = rg$ for some $r \in \mathbb{Z}$."""

import json


def polynomial_product(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_coefficient in enumerate(left):
        for right_index, right_coefficient in enumerate(right):
            result[left_index + right_index] += left_coefficient * right_coefficient
    return tuple(result)


def affine_substitution(coefficients, scale, offset):
    result = [0]
    current_power = (1,)
    affine = (offset, scale)
    for coefficient in coefficients:
        if len(result) < len(current_power):
            result.extend([0] * (len(current_power) - len(result)))
        for index, value in enumerate(current_power):
            result[index] += coefficient * value
        current_power = polynomial_product(current_power, affine)
    return tuple(result)


def main():
    f = polynomial_product((0, 1), (-1, 1))
    g = (2,)

    residue_proofs = []
    for residue in range(2):
        expression_in_quotient = affine_substitution(f, 2, residue)
        residue_proofs.append(
            all(coefficient % g[0] == 0 for coefficient in expression_in_quotient)
        )

    premise_holds = f == (0, -1, 1) and g == (2,) and all(residue_proofs)
    scalar_multiple_is_impossible = any(coefficient != 0 for coefficient in f[1:])
    verified = premise_holds and scalar_multiple_is_impossible

    confirmed_notes = (
        "The witness is valid. Exact symbolic substitution into the two residue "
        "classes modulo 2 proves that 2 divides n(n-1) for every natural number n, "
        "while the nonzero quadratic coefficient rules out f=2r for any integer r. "
        "The refuted statement is substantive, not plainly a typo."
    )
    failed_notes = (
        "The independent exact recomputation did not validate the reported witness. "
        "The statement is substantive, not plainly a typo."
    )
    result = {
        "record_id": "mse_1892923__ans5127254",
        "verdict": "CONFIRMED" if verified else "CANNOT_REPRODUCE",
        "notes": confirmed_notes if verified else failed_notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
