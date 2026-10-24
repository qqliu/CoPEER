"""For every positive integer n and k, x^(n-k)y^k is among the expanded terms of (x+y)^n, without requiring k≤n."""

import json

RECORD_ID = "reddit_math_htizx"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "n=1, k=2: x^(n-k)y^k = x^-1y^2, while (x+y)^1 expands to x+y, whose monomials are x^1y^0 and x^0y^1."
REFUTATION_EXPLANATION = "The claimed monomial is not an expanded term because k=2 exceeds n=1; its x exponent is -1, whereas every term in the binomial expansion has exponent pair (n-j,j) for some integer j with 0<=j<=n."
SEARCH_SPACE = "Exhaustively swept all four positive-integer pairs (n,k) with 1<=n<=2 and 1<=k<=2, comparing (n-k,k) against every binomial exponent pair (n-j,j) for 0<=j<=n, in increasing n, k, and j order."


def main():
    violations = []
    for n in range(1, 3):
        expanded_exponents = []
        for j in range(n + 1):
            expanded_exponents.append((n - j, j))
        for k in range(1, 3):
            claimed_exponent = (n - k, k)
            if claimed_exponent not in expanded_exponents:
                violations.append((n, k))

    if not violations or violations[0] != (1, 2):
        raise AssertionError("deterministic exhaustive search did not find the expected witness")

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
