"""The central limit theorem makes everything converge to a normal curve."""

import json
from fractions import Fraction
from itertools import product


def convolve(left, right):
    result = {}
    for left_value in sorted(left):
        for right_value in sorted(right):
            total = left_value + right_value
            probability = left[left_value] * right[right_value]
            result[total] = result.get(total, Fraction(0, 1)) + probability
    return {value: result[value] for value in sorted(result) if result[value] != 0}


def main():
    support = (-1, 0, 1)
    denominator = 4
    laws = []
    for weights in product(range(denominator + 1), repeat=len(support)):
        if sum(weights) == denominator:
            law = {
                value: Fraction(weight, denominator)
                for value, weight in zip(support, weights)
                if weight != 0
            }
            laws.append(law)

    examined_pairs = 0
    point_mass_candidates = 0
    for law in laws:
        summed = {0: Fraction(1, 1)}
        for _n in range(1, 7):
            summed = convolve(summed, law)
            examined_pairs += 1
            if len(summed) == 1:
                point_mass_candidates += 1
            assert sum(summed.values(), Fraction(0, 1)) == Fraction(1, 1)

    assert len(laws) == 15
    assert examined_pairs == 90
    assert point_mass_candidates == 18

    result = {
        "record_id": "reddit_mathematics_1tfuvxv",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "None certified: the bounded sweep identifies exact finite discrete candidate laws, but the claim supplies no formal criterion by which any candidate violates it.",
        "refutation_explanation": "The quote does not specify what objects converge, the normalization, hypotheses, mode of convergence, or what counts as a normal curve. Moreover, inspecting finitely many convolution powers cannot decide an asymptotic convergence assertion. Therefore the illustrative exact sweep cannot honestly certify a counterexample.",
        "search_space": "All 15 probability mass functions on support {-1,0,1} whose weights are nonnegative multiples of 1/4 summing to 1, with every n-fold sum distribution for n=1,...,6; exactly 90 law/n pairs were swept in fixed lexicographic order. This is an illustrative bounded space, not an exhaustive space for the claim."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
