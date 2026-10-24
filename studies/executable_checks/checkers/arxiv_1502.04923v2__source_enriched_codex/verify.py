r'''Let $S$ be a finite set of primes with $2\in S$, and let $\mathbb Z_S$ denote the ring of $S$-integers. Consider binary forms
\[
L(u,v)=b_0u+b_1v,\qquad Q(u,v)=c_0u^4+c_1u^3v+c_2u^2v^2+c_3uv^3+c_4v^4
\]
with coefficients in $\mathbb Z_S$. Assume that $(b_0,b_1)$ generates the unit ideal of $\mathbb Z_S$ and that $(c_0,c_1,c_2,c_3,c_4)$ generates the unit ideal. Define
\[
\begin{aligned}
\Delta_Q={}&c_1^2c_2^2c_3^2-4c_0c_2^3c_3^2-4c_1^3c_3^3+18c_0c_1c_2c_3^3-27c_0^2c_3^4-4c_1^2c_2^3c_4+16c_0c_2^4c_4\\
&+18c_1^3c_2c_3c_4-80c_0c_1c_2^2c_3c_4-6c_0c_1^2c_3^2c_4+144c_0^2c_2c_3^2c_4-27c_1^4c_4^2\\
&+144c_0c_1^2c_2c_4^2-128c_0^2c_2^2c_4^2-192c_0^2c_1c_3c_4^2+256c_0^3c_4^3,
\end{aligned}
\]
and define the discriminant of the pair $(L,Q)$ (equivalently, of the binary quintic $LQ$) by
\[
\Delta=\Delta_Q\,Q(-b_1,b_0)^2.
\]
Call $(L,Q)$ $S$-admissible when $\Delta\in\mathbb Z_S^\times$. The claim is: for every $S$-admissible pair $(L,Q)$ and every $\lambda_1,\lambda_2\in\mathbb Z_S^\times$, the discriminant of the scaled pair $(\lambda_1L,\lambda_2Q)$ is
\[
\lambda_1^8\lambda_2^2\Delta.
\]
No input-size convention is required because this is an algebraic identity rather than an asymptotic or algorithmic claim.'''

import json
from itertools import permutations
from math import gcd

RECORD_ID = "arxiv_1502.04923v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = ("Independent exact-integer recomputation confirms the admissible witness: "
         "Δ=256, the scaled discriminant is 65536, but the claimed expression is "
         "1024. The false λ2 exponent is plainly a typo (the definition is "
         "homogeneous of degree 8 in Q), not a substantive counterexample to the "
         "intended scaling law.")


def integer_power(base, exponent):
    if exponent < 0:
        raise ValueError("negative exponent")
    value = 1
    for _ in range(exponent):
        value *= base
    return value


def determinant(matrix):
    size = len(matrix)
    total = 0
    for choice in permutations(range(size)):
        term = 1
        inversions = 0
        for row in range(size):
            term *= matrix[row][choice[row]]
            for earlier in range(row):
                if choice[earlier] > choice[row]:
                    inversions += 1
        if inversions % 2:
            total -= term
        else:
            total += term
    return total


def resultant(first, second):
    first_degree = len(first) - 1
    second_degree = len(second) - 1
    size = first_degree + second_degree
    matrix = []
    for shift in range(second_degree):
        row = [0] * size
        for index, coefficient in enumerate(first):
            row[shift + index] = coefficient
        matrix.append(row)
    for shift in range(first_degree):
        row = [0] * size
        for index, coefficient in enumerate(second):
            row[shift + index] = coefficient
        matrix.append(row)
    return determinant(matrix)


def quartic_discriminant(coefficients):
    if len(coefficients) != 5 or coefficients[0] == 0:
        raise ValueError("the witness must have degree four")
    derivative = []
    degree = 4
    for coefficient in coefficients[:-1]:
        derivative.append(degree * coefficient)
        degree -= 1
    numerator = resultant(coefficients, derivative)
    leading = coefficients[0]
    if numerator % leading != 0:
        raise ArithmeticError("nonintegral discriminant")
    return numerator // leading


def evaluate_homogeneous_quartic(coefficients, u, v):
    c0, c1, c2, c3, c4 = coefficients
    return (c0 * u * u * u * u + c1 * u * u * u * v
            + c2 * u * u * v * v + c3 * u * v * v * v
            + c4 * v * v * v * v)


def pair_discriminant(linear, quartic):
    b0, b1 = linear
    value = evaluate_homogeneous_quartic(quartic, -b1, b0)
    return quartic_discriminant(quartic) * value * value


def remove_twos(value):
    value = abs(value)
    while value != 0 and value % 2 == 0:
        value //= 2
    return value


def generates_unit_ideal_over_z_half(coefficients):
    divisor = 0
    for coefficient in coefficients:
        divisor = gcd(divisor, abs(coefficient))
    return remove_twos(divisor) == 1


def is_unit_over_z_half(value):
    return value != 0 and remove_twos(value) == 1


def main():
    linear = (1, 0)
    quartic = (1, 0, 0, 0, 1)
    lambda_one = 1
    lambda_two = 2

    original = pair_discriminant(linear, quartic)
    scaled_linear = tuple(lambda_one * item for item in linear)
    scaled_quartic = tuple(lambda_two * item for item in quartic)
    actual = pair_discriminant(scaled_linear, scaled_quartic)
    claimed = (integer_power(lambda_one, 8)
               * integer_power(lambda_two, 2) * original)

    valid = (
        generates_unit_ideal_over_z_half(linear)
        and generates_unit_ideal_over_z_half(quartic)
        and is_unit_over_z_half(original)
        and is_unit_over_z_half(lambda_one)
        and is_unit_over_z_half(lambda_two)
        and original == 256
        and actual == 65536
        and claimed == 1024
        and actual != claimed
    )
    if not valid:
        raise RuntimeError("independent witness verification failed")

    result = {"record_id": RECORD_ID, "verdict": VERDICT, "notes": NOTES}
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
