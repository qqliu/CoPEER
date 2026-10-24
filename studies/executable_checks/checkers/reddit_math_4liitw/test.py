"""(P⇒Q) ∧ (Q⇒R) is equivalent to P⇒R."""

import itertools
import json


def implies(antecedent, consequent):
    return (not antecedent) or consequent


def main():
    counterexamples = []
    for p, q, r in itertools.product((False, True), repeat=3):
        left = implies(p, q) and implies(q, r)
        right = implies(p, r)
        if left != right:
            counterexamples.append((p, q, r, left, right))

    if counterexamples:
        p, q, r, left, right = counterexamples[0]
        result = {
            "record_id": "reddit_math_4liitw",
            "outcome": "WITNESS_FOUND",
            "witness_description": (
                f"P={p}, Q={q}, R={r}; (P=>Q) and (Q=>R) is {left}, "
                f"while P=>R is {right}."
            ),
            "refutation_explanation": (
                "The two formulas have different truth values at this valuation, "
                "so they are not equivalent."
            ),
            "search_space": (
                "All 8 Boolean valuations (P, Q, R) in "
                "itertools.product((False, True), repeat=3), in fixed lexicographic order."
            ),
        }
    else:
        result = {
            "record_id": "reddit_math_4liitw",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found.",
            "refutation_explanation": (
                "The formulas agreed on every valuation in the finite Boolean domain."
            ),
            "search_space": (
                "All 8 Boolean valuations (P, Q, R) in "
                "itertools.product((False, True), repeat=3), in fixed lexicographic order."
            ),
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
