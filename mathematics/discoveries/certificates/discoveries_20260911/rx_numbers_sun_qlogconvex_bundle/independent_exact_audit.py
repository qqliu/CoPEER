#!/usr/bin/env python3
"""Exact independent verification of the submitted q-log-convexity witness.

Run with Python 3. All mathematical decisions use integers. Only the two
authorized audit inputs are read; no submitted checker is used.
"""

import hashlib
import json
from math import factorial
from pathlib import Path


SOURCE = Path(__file__).with_name("source_input.json")
DRAFT = Path(__file__).with_name("baseline.json")
PARENT_SHA256 = "e87d896924bf8698866ff98e03405567e4ae685f9d00af56bae3dcc46343433d"
CLAIM_HASHES = [
    "94705f91824b3b965e3e4b577ea6ede2f0ea1b29dd89f266b5264de1f2cb3806",
    "b223b70296f6dcc78f94a0fc06c1dcb77e28d5b9e6a4fa335d4ea9685c1cf4c2",
    "e564f1e409471b41ef08ec63b8ae99105a34a34cff09a87bcc9d7f1eacb04db8",
    "e55d7a135c8289e3f48c0f3d0487fc5d3036e9f019a40c8e1615c6f59bec224b",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def binomial_factorial(n, k):
    require(type(n) is int and type(k) is int and 0 <= k <= n,
            "Invalid factorial binomial arguments")
    value, remainder = divmod(factorial(n), factorial(k) * factorial(n - k))
    require(remainder == 0, "Nonintegral factorial quotient")
    return value


def binomial_pascal(n, k):
    row = [1]
    for _ in range(n):
        row = [1] + [row[j - 1] + row[j] for j in range(1, len(row))] + [1]
    return row[k]


def polynomial(index, exponent, binomial):
    return [binomial(index + j, j) ** exponent for j in range(index + 1)]


def multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def main():
    source_bytes = SOURCE.read_bytes()
    draft_bytes = DRAFT.read_bytes()
    source = json.loads(source_bytes)
    draft = json.loads(draft_bytes)
    require(hashlib.sha256(draft_bytes).hexdigest() == PARENT_SHA256,
            "Draft parent SHA-256 mismatch")
    require(len(draft["results"]) == len(CLAIM_HASHES), "Claim count mismatch")
    for idx, expected_hash in enumerate(CLAIM_HASHES):
        actual_hash = hashlib.sha256(draft["results"][idx]["claim"].encode("utf-8")).hexdigest()
        require(actual_hash == expected_hash, "Claim binding mismatch: " + str(idx))

    # Bind the definition, index conventions, and conjunction to the source.
    exact_conjecture = "All four assertions hold: (U_r(q))_(r>=8) is q-log-convex; for every integer m>=2, (V_r,m(q))_(r>=0) is q-log-convex; (S_r^(2)(q))_(r>=0) is q-log-convex; and (S_r^(3)(q))_(r>=2) is q-log-convex. Equivalently, the central-index ranges are r>=9, r>=1, r>=1, and r>=3 respectively."
    require(source["source_open_excerpt"] == exact_conjecture, "Conjecture mismatch")
    require(exact_conjecture in source["source_paper_text"], "Restatement mismatch")
    require("V_r,m(q)=sum_{j=0}^r binom(r+j,j)^m q^j." in source["source_paper_text"],
            "Polynomial definition mismatch")
    require("Binomial coefficients have their ordinary factorial definition." in source["source_paper_text"],
            "Binomial definition mismatch")
    require("For a sequence (P_r(q)) indexed by r>=a, q-log-convexity means every coefficient of P_(r-1)(q)P_(r+1)(q)-P_r(q)^2 is nonnegative at each r>=a+1." in source["source_paper_text"],
            "q-log-convexity definition mismatch")

    m, r, degree, first_index = 11, 3, 2, 0
    require(type(m) is int and m >= 2, "Exponent outside source domain")
    require(type(r) is int and r >= first_index + 1, "Central index outside source domain")
    indices = (r - 1, r, r + 1)
    require(all(type(n) is int and n >= first_index for n in indices),
            "Neighboring index outside sequence domain")

    expected_bases = {2: [1, 3, 6], 3: [1, 4, 10, 20], 4: [1, 5, 15, 35, 70]}
    polys = {}
    for n in indices:
        bases = [binomial_factorial(n + j, j) for j in range(n + 1)]
        require(bases == expected_bases[n], "Incorrect listed polynomial: " + str(n))
        polys[n] = polynomial(n, m, binomial_factorial)
        require(polys[n] == polynomial(n, m, binomial_pascal), "Pascal cross-check failed")
        require(polys[n] == [b ** m for b in expected_bases[n]], "Expansion mismatch")

    neighbor_product = multiply(polys[r - 1], polys[r + 1])
    central_square = multiply(polys[r], polys[r])
    require(len(neighbor_product) == len(central_square) == 2 * r + 1,
            "Product degree mismatch")
    difference = [a - b for a, b in zip(neighbor_product, central_square)]
    require(0 <= degree < len(difference), "Coefficient degree outside product")

    # Separate coefficient extraction from the original factorial-defined sums.
    direct_neighbor = sum(
        binomial_factorial(r - 1 + i, i) ** m
        * binomial_factorial(r + 1 + degree - i, degree - i) ** m
        for i in range(r)
        if 0 <= degree - i <= r + 1
    )
    direct_square = sum(
        binomial_factorial(r + i, i) ** m
        * binomial_factorial(r + degree - i, degree - i) ** m
        for i in range(r + 1)
        if 0 <= degree - i <= r
    )
    require(neighbor_product[degree] == direct_neighbor == 2 * 15 ** 11 + 6 ** 11 == 17299874515806,
            "Neighbor product coefficient mismatch")
    require(central_square[degree] == direct_square == 2 * 10 ** 11 + 16 ** 11 == 17792186044416,
            "Central square coefficient mismatch")
    require(difference[degree] == direct_neighbor - direct_square == -492311528610,
            "Claimed difference mismatch")
    require(difference[degree] < 0, "No violation of coefficientwise nonnegativity")

    # An admissible (m,r,degree) with a negative coefficient falsifies the
    # second universal assertion. A false conjunct falsifies the exact source
    # conjunction; there is no need to settle its other conjuncts separately.
    print(json.dumps({
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "parent_sha256": PARENT_SHA256,
        "claims_checked": [0, 1, 2, 3],
        "witness": {"m": m, "r": r, "degree": degree, "neighboring_indices": list(indices)},
        "binomial_bases": expected_bases,
        "neighbor_product_coefficient": neighbor_product[degree],
        "central_square_coefficient": central_square[degree],
        "violated_coefficient": difference[degree],
        "second_universal_assertion_false": True,
        "source_conjunction_false": True,
        "all_checks_passed": True,
    }, indent=2))


if __name__ == "__main__":
    main()
