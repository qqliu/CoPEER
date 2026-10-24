"""If F is not closed, then every convergent sequence in F has its limit in the complement F'."""

import json


def is_topology(n, family):
    full = (1 << n) - 1
    if not (family & 1):
        return False
    if not (family & (1 << full)):
        return False
    members = [subset for subset in range(1 << n) if family & (1 << subset)]
    for left in members:
        for right in members:
            if not (family & (1 << (left | right))):
                return False
            if not (family & (1 << (left & right))):
                return False
    return True


def constant_sequence_converges(family, value, limit, n):
    for open_set in range(1 << n):
        if family & (1 << open_set):
            contains_limit = bool(open_set & (1 << limit))
            contains_value = bool(open_set & (1 << value))
            if contains_limit and not contains_value:
                return False
    return True


violations = []
for n in range(1, 4):
    full = (1 << n) - 1
    for family in range(1 << (1 << n)):
        if not is_topology(n, family):
            continue
        for f_set in range(1 << n):
            complement = full ^ f_set
            f_is_closed = bool(family & (1 << complement))
            if f_is_closed:
                continue
            for value in range(n):
                if not (f_set & (1 << value)):
                    continue
                for limit in range(n):
                    converges = constant_sequence_converges(
                        family, value, limit, n
                    )
                    limit_in_complement = bool(complement & (1 << limit))
                    if converges and not limit_in_complement:
                        violations.append((n, family, f_set, value, limit))

assert violations
assert violations[0] == (2, 9, 1, 0, 0)

result = {
    "record_id": "reddit_learnmath_13tqavt",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take X = {0, 1} with the indiscrete topology {empty set, X}, F = {0}, and the constant sequence x_n = 0 with limit 0.",
    "refutation_explanation": "F is not closed because its complement F' = {1} is not open. The constant sequence lies in F and converges to 0, but 0 is in F and not in F', contradicting the claim.",
    "search_space": "Exhaustively swept every family of subsets of X as a topology candidate for X = {0, ..., n-1}, for n = 1, 2, 3; for every valid topology, every subset F, every constant sequence value x in F, and every possible limit y in X were tested exactly."
}
print(json.dumps(result, separators=(",", ":")))
