"""Every associative, commutative, idempotent, internally bounded binary operation on the reals must select one of its two inputs."""

import json
from itertools import product

RECORD_ID = "reddit_math_1356bn"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Define F(x,y)=min(x,y) when x,y>=0, F(x,y)=max(x,y) when x,y<=0, and F(x,y)=0 otherwise. Then F(-1,1)=0, which is neither -1 nor 1."
REFUTATION_EXPLANATION = "F is commutative and idempotent. It is internally bounded because on a common side of 0 it returns an input, while for opposite signs it returns 0 between them. It is associative: triples entirely in [0,infinity) reduce to min, triples entirely in (-infinity,0] reduce to max, and any triple containing both a positive and a negative reduces to 0 under either parenthesization. Thus F has every stated property but does not always select an input."
SEARCH_SPACE = "The four globally defined candidates obtained by independently choosing min or max on nonnegative pairs and on nonpositive pairs, with 0 on opposite-sign pairs; candidates are tested in the fixed order (min,min), (min,max), (max,min), (max,max) on all 49 ordered pairs and all 343 ordered triples from {-3,-2,-1,0,1,2,3}. These representatives cover every sign and weak-order type of a pair or triple for this candidate family."
DOMAIN = tuple(range(-3, 4))


def operation(x, y, positive_uses_max, negative_uses_max):
    if x >= 0 and y >= 0:
        return max(x, y) if positive_uses_max else min(x, y)
    if x <= 0 and y <= 0:
        return max(x, y) if negative_uses_max else min(x, y)
    return 0


def passes(positive_uses_max, negative_uses_max):
    def candidate(x, y):
        return operation(x, y, positive_uses_max, negative_uses_max)

    for x, y in product(DOMAIN, repeat=2):
        value = candidate(x, y)
        if candidate(x, x) != x:
            return False
        if value != candidate(y, x):
            return False
        if not min(x, y) <= value <= max(x, y):
            return False

    for x, y, z in product(DOMAIN, repeat=3):
        if candidate(candidate(x, y), z) != candidate(x, candidate(y, z)):
            return False

    return candidate(-1, 1) not in (-1, 1)


def main():
    witness = None
    for choices in product((False, True), repeat=2):
        if passes(*choices):
            witness = choices
            break

    if witness != (False, True):
        raise AssertionError("expected exhaustive search witness was not found")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
