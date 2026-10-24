"""Scheduling one iteration of an exponential-time algorithm every 18 months makes the algorithm run in linear time."""

import json

RECORD_ID = "reddit_compsci_ltkc0"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No concrete finite witness is justified by the supplied data; the tested "
    "T(n)=18*2^n schedule is a deliberately labeled illustrative model."
)
REFUTATION_EXPLANATION = (
    "The quote supplies neither a concrete algorithm, an input-size parameter, "
    "nor a formal time function. \"Linear time\" is asymptotic, so a finite "
    "observation cannot disprove O(n): every finite positive table is bounded "
    "by Cn for some C. The sweep's chosen T(n)=18*2^n is only illustrative and "
    "cannot be treated as supplied data or an exhaustive refutation of the "
    "unspecified claim."
)
SEARCH_SPACE = (
    "The Cartesian product C in {1,...,64} and n in {1,...,64} (4,096 pairs), "
    "using the illustrative exact sequence T(n)=18*2^n months; every pair was "
    "checked in fixed C-major, n-minor order."
)

# Exhaustively test the stated finite Cartesian product using integer arithmetic.
durations = {n: 18 * (2 ** n) for n in range(1, 65)}
checked_pairs = 0
candidate_bound_violated = {constant: False for constant in range(1, 65)}
for constant in range(1, 65):
    for n in range(1, 65):
        checked_pairs += 1
        if durations[n] > constant * n:
            candidate_bound_violated[constant] = True

assert checked_pairs == 4096
assert all(candidate_bound_violated.values())

# Any finite positive table nevertheless has some linear upper-bound constant.
finite_bound = max((durations[n] + n - 1) // n for n in range(1, 65))
assert all(durations[n] <= finite_bound * n for n in range(1, 65))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
