#!/usr/bin/env python3
"""Independent integer-arithmetic audit of the recorded fake Gaussian witness.

Run: python3 [operational path removed]
No external input, packages, floating point, or original submitted checker is used.
All polynomial lists are in ascending coefficient order.
"""

import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def trim(poly):
    poly = list(poly)
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def multiply(left, right):
    product = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            product[i + j] += x * y
    return trim(product)


def integer_divmod(numerator, denominator):
    """Exact polynomial division; every coefficient operation uses integers."""
    remainder = trim(numerator)
    denominator = trim(denominator)
    require(denominator != [0], "zero divisor")
    if len(remainder) < len(denominator):
        return [0], remainder
    quotient = [0] * (len(remainder) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        offset = len(remainder) - len(denominator)
        leading, residue = divmod(remainder[-1], denominator[-1])
        require(residue == 0, "nonintegral intermediate quotient coefficient")
        quotient[offset] += leading
        for j, value in enumerate(denominator):
            remainder[offset + j] -= leading * value
        remainder = trim(remainder)
    return trim(quotient), remainder


def one_minus_power(k):
    require(type(k) is int and k >= 1, "invalid positive exponent")
    return [1] + [0] * (k - 1) + [-1]


def product_of_factors(exponents):
    result = [1]
    for exponent in exponents:
        result = multiply(result, one_minus_power(exponent))
    return result


def build_cyclotomics(limit):
    cyclotomics = {}
    for d in range(1, limit + 1):
        proper_factors = [1]
        for j in range(1, d):
            if d % j == 0:
                proper_factors = multiply(proper_factors, cyclotomics[j])
        power_minus_one = [-x for x in one_minus_power(d)]
        cyclotomics[d], remainder = integer_divmod(power_minus_one, proper_factors)
        require(remainder == [0], "cyclotomic recurrence remainder")
        require(multiply(proper_factors, cyclotomics[d]) == power_minus_one,
                "cyclotomic recurrence identity")
    return cyclotomics


def main():
    n, m = 21, 22
    a = [0] * n
    for index, multiplicity in {6: 1, 14: 2, 18: 2, 20: 2, 21: 1}.items():
        a[index - 1] = multiplicity

    # Check every numerical hypothesis of the exact recorded source statement.
    require(type(n) is int and n >= 1, "n >= 1")
    require(type(m) is int and m >= n, "m >= n")
    require(len(a) == n, "vector length")
    require(all(type(value) is int and value >= 0 for value in a),
            "nonnegative integer entries")

    # Reconstruct numerator and denominator from the source definition.
    lower = [i for i, multiplicity in enumerate(a, 1) for _ in range(multiplicity)]
    upper = [m + i for i, multiplicity in enumerate(a, 1) for _ in range(multiplicity)]
    require(lower == [6, 14, 14, 18, 18, 20, 20, 21], "denominator substitution")
    require(upper == [28, 36, 36, 40, 40, 42, 42, 43], "numerator substitution")
    numerator = product_of_factors(upper)
    denominator = product_of_factors(lower)
    require(denominator[0] == 1, "formal series inverse exists")

    # This full identity is itself a finite certificate of polynomiality over Z.
    quotient, remainder = integer_divmod(numerator, denominator)
    require(remainder == [0], "F is a polynomial")
    require(multiply(denominator, quotient) == numerator, "D*Q=N")
    require(all(type(c) is int for c in quotient), "integer quotient coefficients")
    require(len(quotient) - 1 == m * sum(a) == 176, "quotient degree")

    # Independently audit every cyclotomic exponent, with a complete index bound.
    limit = max(lower + upper)
    valuations = {
        d: sum(k % d == 0 for k in upper) - sum(k % d == 0 for k in lower)
        for d in range(1, limit + 1)
    }
    nonzero_valuations = {d: e for d, e in valuations.items() if e}
    expected_valuations = {
        4: 3, 6: 1, 8: 2, 12: 2, 14: 1, 21: 1,
        28: 1, 36: 2, 40: 2, 42: 2, 43: 1,
    }
    require(nonzero_valuations == expected_valuations, "stated cyclotomic exponents")
    require(all(e >= 0 for e in valuations.values()), "nonnegative valuations")
    require(len(lower) == len(upper) == 8, "cyclotomic signs cancel")
    # d > limit cannot divide any positive exponent, so its valuation is zero.
    cyclotomics = build_cyclotomics(limit)
    cyclotomic_product = [1]
    for d, e in nonzero_valuations.items():
        for _ in range(e):
            cyclotomic_product = multiply(cyclotomic_product, cyclotomics[d])
    require(cyclotomic_product == quotient, "cyclotomic product equals exact quotient")

    # An independent exact geometric-series computation, including multiplicities.
    cutoff = 43
    reciprocal = [1] + [0] * cutoff
    for exponent in lower:
        for r in range(exponent, cutoff + 1):
            reciprocal[r] += reciprocal[r - exponent]
    # Verify each coefficient of D*(1/D)=1 through degree 43.
    for r in range(cutoff + 1):
        product_coefficient = sum(
            denominator[j] * reciprocal[r - j]
            for j in range(min(r, len(denominator) - 1) + 1)
        )
        require(product_coefficient == int(r == 0), "reciprocal series identity")
    expected_p = {0: 1, 43: 0, 15: 0, 7: 0, 3: 0, 1: 0}
    require(all(reciprocal[r] == value for r, value in expected_p.items()),
            "specified reciprocal coefficients")

    # Independently exhaust the finite nonnegative support equations.
    weights = [6, 14, 18, 20, 21]
    representation_counts = {}
    for target in [43, 15, 7, 3, 1]:
        ranges = [range(target // weight + 1) for weight in weights]
        representations = [
            counts for counts in itertools.product(*ranges)
            if sum(weight * count for weight, count in zip(weights, counts)) == target
        ]
        require(representations == [], "unexpected denominator support representation")
        representation_counts[target] = len(representations)

    expected_numerator_prefix = {0: 1, 28: -1, 36: -2, 40: -2, 42: -2, 43: -1}
    numerator_prefix = {r: c for r, c in enumerate(numerator[:cutoff + 1]) if c}
    require(numerator_prefix == expected_numerator_prefix, "numerator through degree 43")
    series_coefficient = sum(numerator[j] * reciprocal[cutoff - j]
                             for j in range(cutoff + 1))
    require(series_coefficient == quotient[43] == -1, "negative coefficient")

    # A further independent quotient extraction using D(0)=1 rather than leading terms.
    forward_quotient = []
    for r in range(len(quotient)):
        coefficient = numerator[r]
        coefficient -= sum(
            denominator[j] * forward_quotient[r - j]
            for j in range(1, min(r, len(denominator) - 1) + 1)
        )
        forward_quotient.append(coefficient)
    require(forward_quotient == quotient, "forward recurrence agrees with long division")
    require(quotient == quotient[::-1], "reciprocity in the draft's auxiliary check")
    negative_coefficients = {r: c for r, c in enumerate(quotient) if c < 0}
    require(negative_coefficients == {43: -1, 133: -1}, "full negative coefficient list")

    certificate = {
        "record_id": "rx_numbers_fake_gaussian_positive",
        "n": n,
        "m": m,
        "a": a,
        "numerator_factor_exponents": upper,
        "denominator_factor_exponents": lower,
        "numerator_degree": len(numerator) - 1,
        "denominator_degree": len(denominator) - 1,
        "quotient_degree": len(quotient) - 1,
        "numerator_coefficients_ascending": numerator,
        "denominator_coefficients_ascending": denominator,
        "quotient_coefficients_ascending": quotient,
        "division_remainder": remainder,
        "cyclotomic_valuations_1_through_43": valuations,
        "cyclotomic_valuations_above_43": 0,
        "reciprocal_coefficients_0_through_43": reciprocal,
        "specified_reciprocal_coefficients": expected_p,
        "support_representation_counts": representation_counts,
        "numerator_nonzero_terms_through_43": numerator_prefix,
        "negative_coefficients": negative_coefficients,
        "coefficient_43_from_series": series_coefficient,
        "all_five_claims_verified": True,
    }
    serialized = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    destination = Path(__file__).with_name("neutral_exact_certificate.json")
    destination.write_text(serialized, encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "n": n, "m": m, "sum_a": sum(a),
        "numerator_degree": len(numerator) - 1,
        "denominator_degree": len(denominator) - 1,
        "quotient_degree": len(quotient) - 1,
        "division_remainder": remainder,
        "nonzero_cyclotomic_valuations": nonzero_valuations,
        "specified_reciprocal_coefficients": expected_p,
        "support_representation_counts": representation_counts,
        "negative_coefficients": negative_coefficients,
        "certificate_path": str(destination.resolve()),
        "certificate_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
