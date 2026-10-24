r'''The equality asserted in line 19 is valid for every allowed natural number k.'''

import json


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def rational(numerator, denominator):
    assert denominator != 0
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    divisor = gcd(abs(numerator), denominator)
    return numerator // divisor, denominator // divisor


def add(first, second):
    a, b = first
    c, d = second
    return rational(a * d + c * b, b * d)


def factorial(n):
    assert n >= 0
    result = 1
    factor = 2
    while factor <= n:
        result *= factor
        factor += 1
    return result


def main():
    k = 1
    assert k >= 1

    left = rational(k * k + 4 * k + k + 4, k + 1)
    factorial_term = rational(factorial(k + 2), 2)
    polynomial_term = rational(k * k + 3 * k, k)
    right = add(factorial_term, polynomial_term)

    assert left == (5, 1)
    assert right == (7, 1)
    assert left != right

    result = {
        "record_id": "reddit_learnmath_azugr0",
        "verdict": "CONFIRMED",
        "notes": "Independent exact recomputation at the allowed natural number k = 1 gives left = 5 and right = 7, with both denominators nonzero. The universal equality is therefore false; this is a substantive mathematical error, not plainly a typo."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
