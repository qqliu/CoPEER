"""If we use 11->88 (gain 77), then q = 3: 31->93 with a gain of 62; total gain 139. If we use 11->99 (gain 88) then q = 2: 23->92 (gain 69) has a total gain of 157. So optimal for N = 100 is

    S = { 1, 99, 91, 17, 95, 92, 29, 31, 37, 41, ,,, }"""

import json


def main():
    transitions = (
        (11, 88, 77),
        (31, 93, 62),
        (11, 99, 88),
        (23, 92, 69),
    )
    totals = (
        (77, 62, 139),
        (88, 69, 157),
    )

    failures = []
    for index, (start, end, stated_gain) in enumerate(transitions):
        actual_gain = end - start
        if actual_gain != stated_gain:
            failures.append(
                "transition %d: %d->%d has gain %d, not %d"
                % (index + 1, start, end, actual_gain, stated_gain)
            )
    for index, (left, right, stated_total) in enumerate(totals):
        actual_total = left + right
        if actual_total != stated_total:
            failures.append(
                "total %d: %d+%d equals %d, not %d"
                % (index + 1, left, right, actual_total, stated_total)
            )

    search_space = (
        "Exactly the four ordered transitions (11,88), (31,93), (11,99), "
        "and (23,92), checked against stated gains 77, 62, 88, and 69 in "
        "that order, followed by exactly the two stated sums 77+62=139 and "
        "88+69=157 in that order. No candidate-set optimality space is "
        "defined by the quote."
    )
    if failures:
        outcome = "WITNESS_FOUND"
        witness_description = failures[0]
        refutation_explanation = (
            "The named arithmetic equality is explicitly asserted by the "
            "claim and fails under exact integer arithmetic."
        )
    else:
        outcome = "NO_WITNESS_INCONCLUSIVE"
        witness_description = (
            "No counterexample was found among the six explicit arithmetic "
            "equalities in the quote; the asserted optimality cannot be "
            "tested from the supplied data."
        )
        refutation_explanation = (
            "All four stated transition gains and both stated total gains "
            "are arithmetically correct. However, the quote supplies no "
            "definition of feasible sets, no objective function, no role "
            "for q, and only an incomplete displayed set S, so it does not "
            "determine a finite search space in which optimality for N = 100 "
            "can be checked."
        )

    result = {
        "record_id": "SE_cs_60677__a60690",
        "outcome": outcome,
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": search_space,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
