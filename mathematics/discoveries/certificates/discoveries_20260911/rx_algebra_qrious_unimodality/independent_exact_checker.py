#!/usr/bin/env python3
"""Independent exact audit of the submitted finite counterexample.

Run with Python 3. This standalone checker reads no input files and uses only
integer and Fraction arithmetic for mathematical decisions. It writes a JSON
certificate beside itself. It does not import or execute the draft's checker.

All-real Landau certificate: the intervals [u,v) partition [0,1). For each
interval and each tuple entry n, this program checks m <= n*u and n*v <= m+1,
where m=floor(n*u). Since n>0, these inequalities prove floor(n*x)=m for
EVERY real x in [u,v), not just rational sample points. The balance of the
tuples proves L(x+k)=L(x) for every integer k, by the integer-shift identity
for floors, and hence extends the certificate to every real x >= 0.
"""

from fractions import Fraction
from pathlib import Path
import json


A = (2, 3, 5, 12)
B = (1, 1, 1, 4, 6, 9)
EXPECTED_C = (
    1, 3, 4, 4, 5, 7, 9, 11, 13, 15, 16, 15, 14,
    15, 16, 15, 13, 11, 9, 7, 5, 4, 4, 3, 1,
)
EXPECTED_DENOMINATOR_VALUES = (
    (Fraction(1, 9), 0), (Fraction(1, 6), 0),
    (Fraction(2, 9), 0), (Fraction(1, 4), 0),
    (Fraction(1, 3), 0), (Fraction(4, 9), 1),
    (Fraction(1, 2), 1), (Fraction(5, 9), 0),
    (Fraction(2, 3), 2), (Fraction(3, 4), 2),
    (Fraction(7, 9), 1), (Fraction(5, 6), 2),
    (Fraction(8, 9), 1),
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def floor_fraction(x):
    return x.numerator // x.denominator


def landau(x):
    return sum(floor_fraction(n * x) for n in A) - sum(
        floor_fraction(n * x) for n in B
    )


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def multiply(p, q):
    result = [0] * (len(p) + len(q) - 1)
    for i, pi in enumerate(p):
        for j, qj in enumerate(q):
            result[i + j] += pi * qj
    return trim(result)


def q_factorial(n):
    result = [1]
    for h in range(1, n + 1):
        result = multiply(result, [1] * h)
    return result


def factorial_product(entries):
    result = [1]
    for n in entries:
        result = multiply(result, q_factorial(n))
    return result


def integer_polynomial_divmod(numerator, denominator):
    require(denominator != [0], "Zero polynomial denominator")
    remainder = trim(numerator)
    quotient = [0] * max(1, len(numerator) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        factor, residual = divmod(remainder[-1], denominator[-1])
        require(residual == 0, "Nonintegral polynomial division step")
        quotient[shift] += factor
        for j, coefficient in enumerate(denominator):
            remainder[shift + j] -= factor * coefficient
        remainder = trim(remainder)
    return trim(quotient), remainder


def check_landau():
    require(len(A) >= 1 and len(B) >= 1, "Empty tuple")
    require(all(type(n) is int and n > 0 for n in A + B),
            "Tuple entry is not a positive integer")
    require(sum(A) == sum(B) == 22, "Tuple balance failed")

    # Generate every possible floor discontinuity, with no sampling grid.
    breakpoints = sorted({
        Fraction(k, n) for n in A + B for k in range(n + 1)
    })
    require(breakpoints[0] == 0 and breakpoints[-1] == 1,
            "Incorrect endpoints")
    require(len(breakpoints) == 23, "Unexpected breakpoint count")
    cells = []
    for u, v in zip(breakpoints, breakpoints[1:]):
        require(u < v, "Invalid partition")
        floors = []
        for n in A + B:
            m = floor_fraction(n * u)
            require(m <= n * u and n * v <= m + 1,
                    "A floor is not constant on the entire interval")
            floors.append(m)
        value = sum(floors[:len(A)]) - sum(floors[len(A):])
        require(value == landau(u), "Floor sum mismatch")
        require(value >= 0, "Negative Landau value")
        cells.append({
            "left_inclusive": str(u), "right_exclusive": str(v),
            "numerator_floors": floors[:len(A)],
            "denominator_floors": floors[len(A):], "L": value,
        })

    require(landau(Fraction(0)) == landau(Fraction(1)) == 0,
            "Endpoint values failed")
    denominator_breakpoints = sorted({
        Fraction(k, n) for n in B for k in range(1, n)
    })
    denominator_values = tuple((x, landau(x)) for x in denominator_breakpoints)
    require(denominator_values == EXPECTED_DENOMINATOR_VALUES,
            "Draft's denominator breakpoint table is inaccurate")
    return {
        "tuple_sums": [sum(A), sum(B)],
        "periodicity_proof": (
            "For integer k and every real x, floor(n*(x+k))=floor(n*x)+n*k; "
            "thus L(x+k)=L(x)+k*(22-22)=L(x). For any real x>=0, "
            "use k=floor(x) and x-k in [0,1)."
        ),
        "all_real_cell_proof": (
            "The sorted intervals partition [0,1). Each recorded floor m "
            "satisfies m<=n*u and n*v<=m+1, so m<=n*x<m+1 on [u,v). "
            "Therefore the recorded nonnegative L is valid everywhere "
            "on that interval, including its left endpoint."
        ),
        "breakpoint_values": [[str(x), landau(x)] for x in breakpoints],
        "denominator_breakpoint_values": [
            [str(x), value] for x, value in denominator_values
        ],
        "cells": cells,
        "minimum_on_period": min(cell["L"] for cell in cells),
    }


def check_polynomials():
    numerator = factorial_product(A)
    denominator = factorial_product(B)
    quotient, remainder = integer_polynomial_divmod(numerator, denominator)
    require(remainder == [0], "Original factorial ratio is not polynomial")
    factored = multiply(multiply([1] * 10, [1] * 11), [1, 0, -1, 0, 1])
    require(quotient == factored, "Claimed factorization failed")
    require(multiply(denominator, factored) == numerator,
            "Original q-factorial cross multiplication failed")
    require(len(numerator) - 1 == sum(n * (n - 1) // 2 for n in A) == 80,
            "Numerator degree failed")
    require(len(denominator) - 1 == sum(n * (n - 1) // 2 for n in B) == 57,
            "Denominator degree failed")
    require(len(quotient) - 1 == 23, "D degree failed")
    coefficients = multiply([1, 1], quotient)
    require(tuple(coefficients) == EXPECTED_C, "Coefficient sequence failed")
    require(len(coefficients) - 1 == 24, "(1+q)D degree failed")
    require(sum(coefficients) == 220, "Coefficient sum cross-check failed")

    # Verify the coefficient formula in the proof sketch independently.
    def t(k):
        return min(k + 1, 10, 20 - k) if 0 <= k <= 19 else 0

    formula = [
        t(k) + t(k - 1) - t(k - 2) - t(k - 3) + t(k - 4) + t(k - 5)
        for k in range(25)
    ]
    require(formula == coefficients, "Coefficient formula failed")

    # Exhaust every h in the definition and retain a failing inequality.
    failed_peaks = []
    for h in range(len(coefficients)):
        bad_prefix = [i for i in range(h) if coefficients[i] > coefficients[i + 1]]
        bad_suffix = [
            i for i in range(h, len(coefficients) - 1)
            if coefficients[i] < coefficients[i + 1]
        ]
        require(bad_prefix or bad_suffix, "A unimodal peak exists")
        prefix_failure = bool(bad_prefix)
        i = bad_prefix[0] if prefix_failure else bad_suffix[0]
        failed_peaks.append({
            "proposed_peak": h,
            "failed_requirement": "nondecreasing prefix" if prefix_failure
                                  else "nonincreasing suffix",
            "indices": [i, i + 1],
            "coefficients": coefficients[i:i + 2],
        })
    require(coefficients[10] == coefficients[14] == 16,
            "Valley outer coefficients failed")
    require(coefficients[12] == 14, "Valley center coefficient failed")
    return {
        "numerator_coefficients": numerator,
        "denominator_coefficients": denominator,
        "numerator_degree": 80, "denominator_degree": 57,
        "D_coefficients": quotient, "D_degree": 23,
        "division_remainder": remainder,
        "factorization": "[10]_q [11]_q (1-q^2+q^4)",
        "one_plus_q_D_coefficients": coefficients,
        "one_plus_q_D_degree": 24,
        "failed_peaks": failed_peaks,
        "valley": {"indices": [10, 12, 14], "coefficients": [16, 14, 16]},
        "nonunimodality_proof": (
            "If a peak h>=12 existed, the nondecreasing prefix would force "
            "c_10<=c_12, contrary to 16>14. If h<12, the nonincreasing "
            "suffix would force c_12>=c_14, contrary to 14<16."
        ),
    }


def main():
    landau_certificate = check_landau()
    polynomial_certificate = check_polynomials()
    certificate = {
        "record_id": "rx_algebra_qrious_unimodality",
        "witness": {"a": A, "b": B},
        "arithmetic": "Python arbitrary-precision integers and exact Fraction",
        "landau": landau_certificate,
        "polynomials": polynomial_certificate,
        "verified_claim_indices": [0, 1, 2, 3, 4],
        "result": "PASS: complete counterexample to the exact recorded conjecture",
    }
    output = Path(__file__).resolve().with_name("independent_exact_certificate.json")
    output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    print(certificate["result"])
    print("Landau: 22 exact half-open cells, minimum 0, integer-shift period 1")
    print("Original q-factorials: degrees 80 and 57, exact quotient degree 23")
    print("Complete (1+q)D coefficients:", polynomial_certificate["one_plus_q_D_coefficients"])
    print("All 25 peak indices fail; c_10=16 > c_12=14 < c_14=16")
    print("Certificate:", output)


if __name__ == "__main__":
    main()
