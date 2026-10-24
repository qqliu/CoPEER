r"""First, note that P -C = {x : Ax <=b}, since if x in P and c in C, then
A(x -c) = Ax -Ac <=b -0 = b"""

import itertools
import json

REPORT = {
    "record_id": "Algorithms_48__sol3",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No claim-level witness is reported. The sweep found no scalar arithmetic violation, but it cannot instantiate the asserted set equality from the supplied text.",
    "refutation_explanation": "The quote does not define P, C, the operation P -C, the dimensions, or the membership conditions needed to evaluate the equality. Its displayed calculation checks only the forward implication under Ax <= b and Ac >= 0; it supplies no finitely checkable reverse inclusion. Therefore the bounded negative result is inconclusive, not evidence that the equality holds.",
    "search_space": "All 81 ordered integer quadruples (A,b,x,c) in {-1,0,1}^4 were tested for (A*x <= b and A*c >= 0) implying A*(x-c) <= b. This is exhaustive only for that scalar arithmetic implication, not for the undefined set equality."
}

VALUES = (-1, 0, 1)
for A, b, x, c in itertools.product(VALUES, repeat=4):
    ax = A * x
    ac = A * c
    if ax <= b and ac >= 0:
        lhs = A * (x - c)
        nonnegative_slack = (b - ax) + ac
        assert b - lhs == nonnegative_slack
        assert nonnegative_slack >= 0
        assert lhs <= b

print(json.dumps(REPORT, separators=(",", ":")))
