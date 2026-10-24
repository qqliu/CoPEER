"""For λ = ⌈(n−1)/2⌉, 2λ is always the largest even number in {1,2,…,n+1}."""

import json


def main():
    n = 3
    quotient, remainder = divmod(n - 1, 2)
    lam = quotient + (1 if remainder else 0)
    doubled = 2 * lam

    members = list(range(1, n + 2))
    even_members = [value for value in members if value % 2 == 0]
    largest_even = max(even_members)

    assert lam == 1
    assert doubled == 2
    assert 4 in members
    assert largest_even == 4
    assert doubled != largest_even

    result = {
        "record_id": "arxiv_0910.0923v4__source_enriched_codex",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation confirms the witness: for n = 3, λ = 1 and 2λ = 2, while direct enumeration of {1,2,3,4} gives largest even member 4. The statement is substantively false as written; the permitted evidence does not establish that it is plainly a typo.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
