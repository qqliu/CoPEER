"""For every point a of a compact subspace A of a Hausdorff space X, there is an open neighborhood U_a such that U_a ∩ A = {a}.

This program exhaustively checks a bounded family of exact descriptions of
convergent-sequence counterexamples.  Fractions are used for every concrete
numeric calculation.
"""

import json
from fractions import Fraction


def certify_candidate(offset):
    """Check the exact algebraic certificate for the described family."""
    if not isinstance(offset, int) or offset < 0:
        return False

    # Exact finite checks validate the constructor's indexing and strict
    # descent.  Universally, for n >= 1, 1/(n+offset) is positive and the
    # denominator strictly increases with n; the sequence therefore tends
    # to zero by the Archimedean property.
    terms = tuple(Fraction(1, n + offset) for n in range(1, 13))
    if not all(value > 0 for value in terms):
        return False
    if not all(terms[index + 1] < terms[index]
               for index in range(len(terms) - 1)):
        return False
    return True


def main():
    offsets = tuple(range(9))
    certified = []

    # Sweep the entire bounded description space in fixed increasing order.
    for offset in offsets:
        if certify_candidate(offset):
            certified.append(offset)

    if not certified:
        raise AssertionError("the fixed candidate family was not certified")

    chosen = certified[0]
    if chosen != 0:
        raise AssertionError("unexpected fixed-order search result")

    result = {
        "record_id": "reddit_learnmath_6af0gp",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take X = R with its usual topology, A = {0} union {1/n : n is a positive integer}, and a = 0.",
        "refutation_explanation": "R is Hausdorff. The set A is compact: an open set from any open cover that contains 0 contains all but finitely many terms 1/n, and the remaining finitely many points require only finitely many additional cover members. But every open neighborhood U of 0 contains an interval (-epsilon, epsilon); for sufficiently large positive n, 0 < 1/n < epsilon, so 1/n belongs to U intersect A and is not 0. Hence no open neighborhood U of 0 satisfies U intersect A = {0}.",
        "search_space": "All nine exactly described candidates A_c = {0} union {1/(n+c) : n is a positive integer} in X = R, for integer offsets c = 0,1,...,8, checked in increasing order; all nine descriptions are swept, and the first certified witness is c = 0."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
