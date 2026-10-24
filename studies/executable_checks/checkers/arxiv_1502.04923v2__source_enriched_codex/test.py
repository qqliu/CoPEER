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
from math import gcd

RECORD_ID = "arxiv_1502.04923v2__source_enriched_codex"
WITNESS_DESCRIPTION = ("For S={2}, take L(u,v)=u, Q(u,v)=u^4+v^4, lambda1=1, "
                       "and lambda2=2. The original discriminant is 256; the scaled "
                       "discriminant is 65536, while the claimed value is 1024.")
REFUTATION_EXPLANATION = ("Both coefficient lists generate the unit ideal in Z[1/2], and 256 "
                          "is an S-unit. Direct evaluation after scaling Q by 2 gives "
                          "65536=2^8*256, not 1024=2^2*256, so the claimed exponent of "
                          "lambda2 is false.")
SEARCH_SPACE = ("Exactly one candidate was exhaustively checked: S={2}, (b0,b1)=(1,0), "
                "(c0,c1,c2,c3,c4)=(1,0,0,0,1), lambda1=1, and lambda2=2.")


def quartic_discriminant(c):
    c0, c1, c2, c3, c4 = c
    return (
        c1**2 * c2**2 * c3**2
        - 4 * c0 * c2**3 * c3**2
        - 4 * c1**3 * c3**3
        + 18 * c0 * c1 * c2 * c3**3
        - 27 * c0**2 * c3**4
        - 4 * c1**2 * c2**3 * c4
        + 16 * c0 * c2**4 * c4
        + 18 * c1**3 * c2 * c3 * c4
        - 80 * c0 * c1 * c2**2 * c3 * c4
        - 6 * c0 * c1**2 * c3**2 * c4
        + 144 * c0**2 * c2 * c3**2 * c4
        - 27 * c1**4 * c4**2
        + 144 * c0 * c1**2 * c2 * c4**2
        - 128 * c0**2 * c2**2 * c4**2
        - 192 * c0**2 * c1 * c3 * c4**2
        + 256 * c0**3 * c4**3
    )


def evaluate_q(c, u, v):
    c0, c1, c2, c3, c4 = c
    return (c0 * u**4 + c1 * u**3 * v + c2 * u**2 * v**2
            + c3 * u * v**3 + c4 * v**4)


def pair_discriminant(b, c):
    b0, b1 = b
    return quartic_discriminant(c) * evaluate_q(c, -b1, b0)**2


def strip_s_factors(n, primes):
    n = abs(n)
    for prime in primes:
        while n != 0 and n % prime == 0:
            n //= prime
    return n


def generates_unit_ideal(coefficients, primes):
    common = 0
    for coefficient in coefficients:
        common = gcd(common, abs(coefficient))
    return strip_s_factors(common, primes) == 1


def is_s_unit_integer(value, primes):
    return value != 0 and strip_s_factors(value, primes) == 1


def main():
    prime_sets = ((2,),)
    linear_forms = ((1, 0),)
    quartic_forms = ((1, 0, 0, 0, 1),)
    lambda1_values = (1,)
    lambda2_values = (2,)
    witnesses = []

    for primes in prime_sets:
        for b in linear_forms:
            for c in quartic_forms:
                for lambda1 in lambda1_values:
                    for lambda2 in lambda2_values:
                        if not generates_unit_ideal(b, primes):
                            continue
                        if not generates_unit_ideal(c, primes):
                            continue
                        original = pair_discriminant(b, c)
                        if not is_s_unit_integer(original, primes):
                            continue
                        if not is_s_unit_integer(lambda1, primes):
                            continue
                        if not is_s_unit_integer(lambda2, primes):
                            continue
                        scaled_b = tuple(lambda1 * value for value in b)
                        scaled_c = tuple(lambda2 * value for value in c)
                        actual = pair_discriminant(scaled_b, scaled_c)
                        claimed = lambda1**8 * lambda2**2 * original
                        if actual != claimed:
                            witnesses.append((primes, b, c, lambda1, lambda2,
                                              original, actual, claimed))

    expected = ((2,), (1, 0), (1, 0, 0, 0, 1), 1, 2, 256, 65536, 1024)
    if witnesses == [expected]:
        result = {
            "record_id": RECORD_ID,
            "outcome": "WITNESS_FOUND",
            "witness_description": WITNESS_DESCRIPTION,
            "refutation_explanation": REFUTATION_EXPLANATION,
            "search_space": SEARCH_SPACE,
        }
    else:
        result = {
            "record_id": RECORD_ID,
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found.",
            "refutation_explanation": "The singleton search produced no violation.",
            "search_space": SEARCH_SPACE,
        }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
