"""Every finite set equipped with an associative binary operation contains an idempotent element."""

import itertools
import json

RECORD_ID = "reddit_learnmath_y7cwe4"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take A to be the empty set and the operation to be the unique empty "
    "function from A x A to A."
)
REFUTATION_EXPLANATION = (
    "The empty operation is associative because there are no triples for which "
    "associativity could fail, but the empty set contains no element a and hence "
    "no idempotent element satisfying a * a = a."
)
SEARCH_SPACE = (
    "All binary operations on the canonical finite set {0, ..., n-1} for n = 0; "
    "this is exactly the unique empty operation on the empty set."
)


def is_associative(n, table):
    def op(left, right):
        return table[left * n + right]

    for first in range(n):
        for second in range(n):
            for third in range(n):
                if op(op(first, second), third) != op(first, op(second, third)):
                    return False
    return True


def has_idempotent(n, table):
    for element in range(n):
        if table[element * n + element] == element:
            return True
    return False


def main():
    candidates_checked = 0
    witness = None

    for n in range(1):
        for table in itertools.product(range(n), repeat=n * n):
            candidates_checked += 1
            if is_associative(n, table) and not has_idempotent(n, table):
                witness = (n, table)

    assert candidates_checked == 1
    assert witness == (0, ())

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
