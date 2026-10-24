r"""Under the stated convention R^0 = R, the proof claims that R^(n+m) = R^n composed with R^m for natural numbers n and m."""

import json


def relational_product(first, second):
    result = set()
    for start, middle in first:
        for candidate, end in second:
            if middle == candidate:
                result.add((start, end))
    return result


def relation_power(relation, exponent):
    if exponent < 0:
        raise ValueError("exponent must be natural")
    if exponent == 0:
        return set(relation)
    result = set(relation)
    remaining = exponent - 1
    while remaining > 0:
        result = relational_product(result, relation)
        remaining -= 1
    return result


def main():
    relation = {(0, 1)}
    n = 0
    m = 0

    left = relation_power(relation, n + m)
    right = relational_product(
        relation_power(relation, n),
        relation_power(relation, m),
    )

    if left != {(0, 1)} or right != set() or left == right:
        raise AssertionError("the reported witness was not independently verified")

    output = {
        "record_id": "proofwiki_24804__codex_expansion",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation confirms the witness: with R={(0,1)} and n=m=0, the stipulated convention gives R^(n+m)=R, while R composed with itself is empty. The refuted statement is plainly a typo or convention error: the usual zero power is the identity relation, under which the exponent law has the expected base case.",
    }
    print(json.dumps(output, separators=(",", ":")))


if __name__ == "__main__":
    main()
