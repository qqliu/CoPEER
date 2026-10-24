r"""I therefore chose a value $c_1$ that respect the condition $0 \le M \le c_1$ in order to define the relation $0 \le c_1g(n)\le f(n)$ that proves that 
$f(n) = \Omega(g(n))$"""

import json
from itertools import product


values = range(-2, 3)
condition_and_relation = []
condition_and_failure = []

for M, c1, g_value, f_value in product(values, repeat=4):
    condition = 0 <= M <= c1
    relation = 0 <= c1 * g_value <= f_value
    if condition:
        if relation:
            condition_and_relation.append((M, c1, g_value, f_value))
        else:
            condition_and_failure.append((M, c1, g_value, f_value))

assert len(condition_and_relation) != 0
assert len(condition_and_failure) != 0
assert len(tuple(product(values, repeat=4))) == 625

result = {
    "record_id": "SE_cs_142560__q",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete counterexample can be certified from the supplied quote because it does not define M, f, g, the domain of n, or how M is related to f and g.",
    "refutation_explanation": "The bounded diagnostic sweep finds both successes and failures under a scalar interpretation of f(n) and g(n), so the condition 0 <= M <= c1 alone does not decide the displayed relation. That scalar interpretation is not supplied by the quote and therefore cannot furnish a valid witness. The quote also omits the quantifiers and threshold needed to check the Omega conclusion.",
    "search_space": "All 625 ordered integer quadruples (M, c1, g_value, f_value) in {-2,-1,0,1,2}^4, in itertools.product order; for each quadruple the program exactly tests 0 <= M <= c1 and 0 <= c1*g_value <= f_value as a diagnostic scalar completion.",
}

print(json.dumps(result, separators=(",", ":")))
