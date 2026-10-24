r"""If L1 polynomial-time many-one reduces to an NP-complete problem, then that NP-complete problem polynomial-time many-one reduces to L1."""

import itertools
import json

RECORD_ID = "reddit_compsci_2p76am"
VERDICT = "CONFIRMED"
NOTES = ("The statement is substantively false, not plainly a typo. "
         "Independently taking A to be CNF-SAT, (x) AND (not x) is a "
         "no-instance and (x) is a yes-instance. The constant map from the "
         "empty language to the no-instance is a polynomial-time many-one "
         "reduction, while no map can reduce SAT to the empty language "
         "because the yes-instance would have to map to a member of the "
         "empty set.")


def cnf_is_satisfiable(clauses):
    variables = sorted({abs(literal) for clause in clauses for literal in clause})
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if all(any(assignment[abs(literal)] == (literal > 0)
                   for literal in clause)
               for clause in clauses):
            return True
    return False


# Literals k and -k denote variable k and its negation.
no_instance = ((1,), (-1,))
yes_instance = ((1,),)
no_instance_is_in_sat = cnf_is_satisfiable(no_instance)
yes_instance_is_in_sat = cnf_is_satisfiable(yes_instance)

# Membership in the empty source is false for every input. A constant map to
# no_instance therefore preserves membership for every possible source input.
empty_membership_for_every_string = False
forward_equivalence_is_universal = (
    empty_membership_for_every_string == no_instance_is_in_sat
)

# For any proposed reverse map g, g(yes_instance) is still some string, and
# every string has false membership in the empty language. Thus the required
# equivalence already fails at this single SAT yes-instance, independently of
# how g is computed or what string it returns.
reverse_equivalence_at_yes_instance = (
    yes_instance_is_in_sat == empty_membership_for_every_string
)

established = (
    not no_instance_is_in_sat
    and yes_instance_is_in_sat
    and forward_equivalence_is_universal
    and not reverse_equivalence_at_yes_instance
)
if not established:
    raise RuntimeError("independent witness verification failed")

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}, separators=(",", ":")))
