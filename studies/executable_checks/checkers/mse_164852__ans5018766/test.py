r"""Now let $n = p^k$, where $p$ is an odd prime and $k \geq 2$."""

import json


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def main():
    assignments = []
    for p in range(3, 102, 2):
        if is_prime(p):
            for k in range(2, 9):
                n = p ** k
                assignments.append((p, k, n))

    assert len(assignments) == 175
    assert all(n == p ** k for p, k, n in assignments)

    result = {
        "record_id": "mse_164852__ans5018766",
        "outcome": "CLAIM_NOT_FINITELY_REFUTABLE",
        "witness_description": "No counterexample can be defined from the supplied text: it introduces n by the assignment n = p^k under stated conditions, but makes no proposition about independently chosen values.",
        "refutation_explanation": "The target claim is a variable declaration, not a universally quantified assertion with a falsifiable conclusion. Every enumerated n is defined as p^k, so a finite search cannot refute the declaration without inventing an additional claim.",
        "search_space": "All 175 assignments obtained from every odd prime p with 3 <= p <= 101 and every integer k with 2 <= k <= 8, with n constructed exactly as p**k."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
