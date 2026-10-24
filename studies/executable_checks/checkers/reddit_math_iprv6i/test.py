"""By varying Monty's probability of choosing either losing door when the contestant initially chose correctly, the conditional probability of winning by switching can attain any value between 0 and 1."""

import json
from fractions import Fraction
from math import gcd


def rational_biases(max_denominator):
    biases = []
    for denominator in range(1, max_denominator + 1):
        for numerator in range(denominator + 1):
            if gcd(numerator, denominator) == 1:
                biases.append(Fraction(numerator, denominator))
    return tuple(biases)


def main():
    biases = rational_biases(12)
    assert len(biases) == 47
    for bias in biases:
        assert Fraction(0, 1) <= bias <= Fraction(1, 1)

    result = {
        "record_id": "reddit_math_iprv6i",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete counterexample can be certified from the supplied claim and quote.",
        "refutation_explanation": "The supplied data do not define the conditioning event, the initial prize distribution, Monty's complete door-opening protocol, or an exact map from Monty's door-selection bias to the conditional switching probability. Consequently, exact bias values can be enumerated, but the claimed attainable probabilities cannot be computed or checked without inventing absent assumptions.",
        "search_space": "All 47 reduced rational Monty door-selection biases p=a/b in [0,1] with 1 <= b <= 12, enumerated in fixed order by increasing b and then increasing a. This is only a bounded parameter sweep, not an exhaustive test of the continuum claimed."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
