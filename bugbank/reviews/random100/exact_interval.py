"""Exact analysis functions, extracted without changing their bodies from the study analyzer."""
from fractions import Fraction
from functools import lru_cache
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=None)
def hypergeom_interval(population, assigned, yes, confidence=Fraction(19, 20)):
    """Integer K with both inclusive hypergeometric tails >= (1-confidence)/2.

    All arithmetic in the acceptance decision is integer/rational. Keeping tail
    equality is conservative for this discrete confidence set.
    """
    require(all(type(v) is int for v in (population, assigned, yes)), "counts must be integers")
    require(0 <= yes <= assigned <= population, "invalid finite-population counts")
    require(isinstance(confidence, Fraction) and 0 < confidence < 1, "use exact Fraction confidence")
    tail = (1 - confidence) / 2
    denominator = comb(population, assigned)
    accepted = []
    for valid in range(population + 1):
        low = max(0, assigned - (population - valid))
        high = min(assigned, valid)
        lower = upper = 0
        for x in range(low, high + 1):
            mass = comb(valid, x) * comb(population - valid, assigned - x)
            if x <= yes:
                lower += mass
            if x >= yes:
                upper += mass
        if min(lower, upper) * tail.denominator >= denominator * tail.numerator:
            accepted.append(valid)
    require(bool(accepted), "empty exact confidence set")
    require(accepted == list(range(accepted[0], accepted[-1] + 1)), "noncontiguous confidence set")
    return accepted[0], accepted[-1]


def exact(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator,
            "decimal": float(value)}

