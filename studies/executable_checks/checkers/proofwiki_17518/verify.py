r"""Proof 2's injectivity step asserts, for arbitrary a in S, that for all x_1, x_2 in S, (x_1, a circ x_1) in lambda_a AND (x_2, a circ x_2) in lambda_a implies x_1 = x_2. Since (x, a circ x) belongs to lambda_a for EVERY x by the definition of lambda_a, the antecedent is universally satisfied, so the stated claim literally asserts that S has at most one element. The preceding chain x_1 = a * lambda_a(x_1) = a * lambda_a(x_2) = x_2 uses an unjustified middle equality (many-to-one-ness of lambda_a only gives single-valuedness at a fixed argument, not lambda_a(x_1) = lambda_a(x_2))."""

import json

record_id = "proofwiki_17518"
notes = ("The concrete witness independently checks out: both graph-membership "
         "premises hold for distinct elements 0 and 1, so the stated implication "
         "is false. This is a substantive logical error, not plainly a typo; "
         "graph membership only establishes the function values associated with "
         "each input and does not force the inputs to be equal.")

carrier = (0, 1)
a = 0
x_1 = 0
x_2 = 1


def circ(left, right):
    if left not in carrier or right not in carrier:
        raise ValueError("operation argument outside carrier")
    return 0


lambda_a = set()
for x in carrier:
    lambda_a.add((x, circ(a, x)))

is_reported_relation = lambda_a == {(0, 0), (1, 0)}
antecedent = ((x_1, circ(a, x_1)) in lambda_a and
              (x_2, circ(a, x_2)) in lambda_a)
conclusion = x_1 == x_2
operation_is_closed = all(circ(left, right) in carrier
                          for left in carrier for right in carrier)

verified = (operation_is_closed and is_reported_relation and antecedent and
            not conclusion)
verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
