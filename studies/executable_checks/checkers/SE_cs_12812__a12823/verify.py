"""However, DNF-SAT is in L, by assigning variables to satisfy the first disjunct."""

import json

record_id = "SE_cs_12812__a12823"
first_disjunct = ((1, True), (1, False))
second_disjunct = ((1, True),)


def value_of_literal(literal, assignment):
    variable, positive = literal
    value = assignment[variable]
    return value if positive else not value


def value_of_conjunction(conjunction, assignment):
    return all(value_of_literal(literal, assignment) for literal in conjunction)


def value_of_formula(assignment):
    return value_of_conjunction(first_disjunct, assignment) or value_of_conjunction(second_disjunct, assignment)


reported_assignment = {1: True, 2: False}
assignments = []
for bits in range(4):
    assignments.append({1: bool(bits & 1), 2: bool(bits & 2)})

formula_holds_for_witness = value_of_formula(reported_assignment)
first_fails_for_witness = not value_of_conjunction(first_disjunct, reported_assignment)
first_is_unsatisfiable = all(
    not value_of_conjunction(first_disjunct, assignment)
    for assignment in assignments
)
second_supplies_satisfaction = value_of_conjunction(second_disjunct, reported_assignment)
established = (
    formula_holds_for_witness
    and first_fails_for_witness
    and first_is_unsatisfiable
    and second_supplies_satisfaction
)

if established:
    verdict = "CONFIRMED"
    notes = "Exact recomputation confirms that x1=True, x2=False satisfies (x1 ∧ ¬x1) ∨ x1, while exhaustive evaluation of both Boolean values of x1 shows that the first disjunct x1 ∧ ¬x1 is never satisfied. Thus the stated first-disjunct method fails, although this does not refute the separate conclusion DNF-SAT ∈ L. The refuted justification is substantive, not plainly a typo."
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The reported concrete witness could not be established by exact Boolean evaluation. The alleged issue would be substantive rather than plainly a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
