"""Replacing any sub-proposition p of P with an arbitrary proposition p' always yields a proposition P' logically equivalent to P."""

import json
from itertools import product


def evaluate(formula, valuation):
    kind = formula[0]
    if kind == "var":
        return valuation[formula[1]]
    if kind == "not":
        return not evaluate(formula[1], valuation)
    if kind == "and":
        return evaluate(formula[1], valuation) and evaluate(formula[2], valuation)
    raise ValueError("unknown formula kind")


p = ("var", "p")
q = ("var", "q")
original = ("and", p, q)
replacements = (
    ("p", p),
    ("not p", ("not", p)),
)

violations = []
for replacement_name, replacement in replacements:
    replaced = ("and", replacement, q)
    for p_value, q_value in product((False, True), repeat=2):
        valuation = {"p": p_value, "q": q_value}
        original_value = evaluate(original, valuation)
        replaced_value = evaluate(replaced, valuation)
        if original_value != replaced_value:
            violations.append(
                (
                    replacement_name,
                    p_value,
                    q_value,
                    original_value,
                    replaced_value,
                )
            )

expected = ("not p", False, True, False, True)
if not violations or violations[0] != expected:
    raise AssertionError("deterministic counterexample search failed")

result = {
    "record_id": "reddit_askmath_1hh1pqf",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Let P=(p ∧ q), with its left sub-proposition p replaced by p'=¬p. Under the valuation p=False and q=True, P is False while P'=(¬p ∧ q) is True.",
    "refutation_explanation": "Logical equivalence requires equal truth values under every valuation. This valuation makes P and P' differ, so the claimed universal replacement property is false.",
    "search_space": "The full 8-case Cartesian product with fixed P=(p ∧ q), replacement p' in the ordered set {p, ¬p}, and (p,q) in the ordered set {(False,False), (False,True), (True,False), (True,True)} was swept.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
