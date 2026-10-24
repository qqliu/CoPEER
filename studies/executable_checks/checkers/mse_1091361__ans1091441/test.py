"""So write $(23$, then notice $3$ is sent to $2$ by the rightmost cycle and the $2$ is sent to $1$ by the other cycle, so write $(321$. Notice $1$ must go to $3$ to finish the cycle as $(321)$."""

import json

RECORD_ID = "mse_1091361__ans1091441"
WITNESS_DESCRIPTION = (
    "x=3: applying the stated rightmost arrow and then the other arrow sends "
    "3 to 1, while (321) sends 3 to 2."
)
REFUTATION_EXPLANATION = (
    "For x=3, the quote states 3->2 under the rightmost cycle and 2->1 "
    "under the other cycle, so rightmost-first composition gives 3->1. "
    "But the cycle (321) gives 3->2. Thus (321) cannot represent the "
    "described composition."
)
SEARCH_SPACE = (
    "All x in the fixed tuple (1, 2, 3); for each x, the program checks the "
    "two-step composition when both required arrows occur in the quoted "
    "partial maps right={3: 2} and other={2: 1}, against cycle (3, 2, 1)."
)


def cycle_map(entries):
    result = {}
    for index in range(len(entries)):
        result[entries[index]] = entries[(index + 1) % len(entries)]
    return result


def main():
    symbols = (1, 2, 3)
    right = {3: 2}
    other = {2: 1}
    asserted = cycle_map((3, 2, 1))
    witnesses = []

    for x in symbols:
        if x in right and right[x] in other:
            composed_image = other[right[x]]
            if composed_image != asserted[x]:
                witnesses.append((x, composed_image, asserted[x]))

    expected = [(3, 1, 2)]
    if witnesses != expected:
        raise AssertionError("unexpected exhaustive-search result")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
