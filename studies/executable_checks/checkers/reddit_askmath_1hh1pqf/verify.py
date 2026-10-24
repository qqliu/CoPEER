"""Replacing any sub-proposition p of P with an arbitrary proposition p' always yields a proposition P' logically equivalent to P."""

import json


def truth_value(expression, assignment):
    operator = expression[0]
    if operator == "atom":
        return assignment[expression[1]]
    if operator == "negation":
        return not truth_value(expression[1], assignment)
    if operator == "conjunction":
        left = truth_value(expression[1], assignment)
        right = truth_value(expression[2], assignment)
        return left and right
    raise AssertionError("unsupported expression")


def replace_occurrence(expression, target, substitute):
    if expression == target:
        return substitute
    operator = expression[0]
    if operator == "atom":
        return expression
    if operator == "negation":
        return (operator, replace_occurrence(expression[1], target, substitute))
    if operator == "conjunction":
        return (
            operator,
            replace_occurrence(expression[1], target, substitute),
            replace_occurrence(expression[2], target, substitute),
        )
    raise AssertionError("unsupported expression")


p = ("atom", "p")
q = ("atom", "q")
proposition = ("conjunction", p, q)
substitute = ("negation", p)
changed_proposition = replace_occurrence(proposition, p, substitute)
assignment = {"p": False, "q": True}

original_result = truth_value(proposition, assignment)
changed_result = truth_value(changed_proposition, assignment)
witness_valid = (
    proposition[1] == p
    and changed_proposition == ("conjunction", substitute, q)
    and original_result is False
    and changed_result is True
)

if witness_valid:
    verdict = "CONFIRMED"
    notes = "The witness is valid: for P=(p ∧ q), replacing the sub-proposition p by ¬p and assigning p=False, q=True gives P=False and P'=True. Thus they are not logically equivalent. The refuted statement is substantive, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The independent exact recomputation did not validate the reported witness. The statement under review is substantive, not plainly a typo."

print(json.dumps({"record_id": "reddit_askmath_1hh1pqf", "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
