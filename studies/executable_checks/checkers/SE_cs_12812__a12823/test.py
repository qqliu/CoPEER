"""However, DNF-SAT is in L, by assigning variables to satisfy the first disjunct."""

import itertools
import json

record_id = "SE_cs_12812__a12823"
literals = (1, -1, 2, -2)
terms = []
for length in (1, 2):
    terms.extend(itertools.product(literals, repeat=length))
assignments = tuple(itertools.product((False, True), repeat=2))


def literal_value(literal, assignment):
    value = assignment[abs(literal) - 1]
    return value if literal > 0 else not value


def term_value(term, assignment):
    return all(literal_value(literal, assignment) for literal in term)


first_counterexample = None
formulas_checked = 0
assignment_checks = 0

for first_term in terms:
    for second_term in terms:
        formulas_checked += 1
        first_is_satisfied = False
        formula_is_satisfied = False
        satisfying_assignment = None
        for assignment in assignments:
            assignment_checks += 1
            first_value = term_value(first_term, assignment)
            formula_value = first_value or term_value(second_term, assignment)
            if first_value:
                first_is_satisfied = True
            if formula_value:
                formula_is_satisfied = True
                if satisfying_assignment is None:
                    satisfying_assignment = assignment
        if (
            first_counterexample is None
            and not first_is_satisfied
            and formula_is_satisfied
        ):
            first_counterexample = (
                first_term,
                second_term,
                satisfying_assignment,
            )

assert formulas_checked == 400
assert assignment_checks == 1600
assert first_counterexample == ((1, -1), (1,), (True, False))

result = {
    "record_id": record_id,
    "outcome": "WITNESS_FOUND",
    "witness_description": "The DNF formula (x1 ∧ ¬x1) ∨ x1, with the concrete assignment x1=True, x2=False satisfying the whole formula. Its first disjunct is unsatisfiable.",
    "refutation_explanation": "No Boolean assignment can satisfy x1 ∧ ¬x1, so the claimed method of satisfying the first disjunct fails on this DNF. This witness refutes the stated justification, not the separate conclusion that DNF-SAT belongs to L.",
    "search_space": "All 400 ordered two-disjunct DNF formulas over x1 and x2 in which each disjunct is an ordered sequence of one or two literals drawn with repetition from (x1, ¬x1, x2, ¬x2); all 4 Boolean assignments were checked for every formula, for 1600 formula-assignment checks total.",
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
