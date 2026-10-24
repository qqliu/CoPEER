"""For every clock c, (touch(c) → ¬stop(c)) → (start(c) → ¬touch(c))."""

import itertools
import json


def implies(antecedent, consequent):
    return (not antecedent) or consequent


def main():
    counterexamples = []
    for touch, stop, start in itertools.product((False, True), repeat=3):
        antecedent = implies(touch, not stop)
        consequent = implies(start, not touch)
        formula = implies(antecedent, consequent)
        if not formula:
            counterexamples.append((touch, stop, start))

    expected_witness = (True, False, True)
    if expected_witness not in counterexamples:
        raise AssertionError("expected counterexample was not found")

    result = {
        "record_id": "reddit_learnmath_sdnki8",
        "outcome": "WITNESS_FOUND",
        "witness_description": "In the one-clock domain {c0}, let touch(c0) be true, stop(c0) be false, and start(c0) be true.",
        "refutation_explanation": "For c0, touch(c0) → ¬stop(c0) is true because touch(c0) is true and stop(c0) is false. But start(c0) → ¬touch(c0) is false because both start(c0) and touch(c0) are true. Therefore the outer implication is false, refuting the universal claim.",
        "search_space": "All 8 Boolean interpretations of touch(c0), stop(c0), and start(c0) on the fixed one-clock domain {c0}, enumerated in lexicographic product order with false before true."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
