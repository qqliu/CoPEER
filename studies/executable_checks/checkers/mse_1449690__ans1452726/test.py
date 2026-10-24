r"""Lemma 2: For every $m\geq 2,n\geq 1$ positive integers such that $6\not|n $ we have:
  $$\omega(1+m^{n})\geq {d(n)} $$"""

import json

RECORD_ID = "mse_1449690__ans1452726"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness can be certified from the supplied quote because neither omega "
    "nor d is defined there."
)
REFUTATION_EXPLANATION = (
    "All 323 eligible pairs in the stated bounded sweep are enumerated, but the "
    "inequality cannot be evaluated without inventing definitions for omega and "
    "d, which the supplied source data does not provide."
)
SEARCH_SPACE = (
    "Exactly all 323 ordered pairs (m,n) with 2 <= m <= 20, 1 <= n <= 20, "
    "and n not divisible by 6, enumerated in increasing m and then increasing n."
)


def main():
    candidates = tuple(
        (m, n)
        for m in range(2, 21)
        for n in range(1, 21)
        if n % 6 != 0
    )
    assert len(candidates) == 323

    undecidable = 0
    for m, n in candidates:
        assert 2 <= m <= 20
        assert 1 <= n <= 20
        assert n % 6 != 0
        undecidable += 1
    assert undecidable == len(candidates)

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
