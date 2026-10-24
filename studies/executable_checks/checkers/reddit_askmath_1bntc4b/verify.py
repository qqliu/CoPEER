r"""The multiplicativity formula for Euler's phi function can be applied to the factorization 16 = 2^2 · 2^2."""

import json

RECORD_ID = "reddit_askmath_1bntc4b"
VERDICT = "CONFIRMED"
NOTES = "Exact independent recomputation gives 16 = 4·4, gcd(4,4) = 4, φ(16) = 8, and φ(4)φ(4) = 4, so the ordinary coprime multiplicativity formula does not apply. The refuted statement is a substantive mathematical error, not plainly a typo."


def integer_gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def totient(n):
    count = 0
    for residue in range(n):
        if integer_gcd(residue, n) == 1:
            count += 1
    return count


def main():
    factor = 2 ** 2
    whole = factor * factor
    common_divisor = integer_gcd(factor, factor)
    phi_factor = totient(factor)
    phi_whole = totient(whole)

    if whole != 16:
        raise AssertionError("The stated factors do not multiply to 16")
    if common_divisor != 4:
        raise AssertionError("Unexpected common divisor")
    if phi_factor != 2 or phi_whole != 8:
        raise AssertionError("Unexpected totient recomputation")
    if phi_whole == phi_factor * phi_factor:
        raise AssertionError("The reported counterexample was not reproduced")

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
