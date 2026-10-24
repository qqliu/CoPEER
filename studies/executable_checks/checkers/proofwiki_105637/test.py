r'''The proof's "Distributing" step claims that from $\paren{\paren{m \vee n} \vee b} \wedge \paren{\paren{n \vee m} \vee a} \in F$ one may conclude $\paren{m \vee n} \wedge \paren{b \vee a} \in F$. This inverts the distributive law: in a distributive lattice $(x \vee b) \wedge (x \vee a) = x \vee (a \wedge b)$, not $x \wedge (a \vee b)$. The two expressions are not equal and the second is not above the first (it is in fact $\le x \le x \vee (a\wedge b)$), so upward closure of the filter does not license the step.'''

import itertools
import json


def join(left, right):
    return max(left, right)


def meet(left, right):
    return min(left, right)


def is_filter(subset, elements):
    return (
        bool(subset)
        and all(
            upper in subset
            for lower in elements
            if lower in subset
            for upper in elements
            if lower <= upper
        )
        and all(
            meet(left, right) in subset
            for left in subset
            for right in subset
        )
    )


elements = (0, 1)
filter_f = frozenset((1,))
assert is_filter(filter_f, elements)

witnesses = []
for m, n, a, b in itertools.product(elements, repeat=4):
    premise_value = meet(join(join(m, n), b), join(join(n, m), a))
    conclusion_value = meet(join(m, n), join(b, a))
    if premise_value in filter_f and conclusion_value not in filter_f:
        witnesses.append((m, n, a, b, premise_value, conclusion_value))

assert witnesses
assert witnesses[0] == (0, 0, 1, 1, 1, 0)

result = {
    "record_id": "proofwiki_105637",
    "outcome": "WITNESS_FOUND",
    "witness_description": "In the two-element Boolean lattice {0,1} with F={1}, take m=0, n=0, a=1, b=1.",
    "refutation_explanation": "The premise evaluates to ((0∨0)∨1)∧((0∨0)∨1)=1∈F, while the claimed conclusion evaluates to (0∨0)∧(1∨1)=0∉F.",
    "search_space": "All 16 ordered quadruples (m,n,a,b) in {0,1}^4, in itertools.product order, in the two-element Boolean lattice, with the fixed filter F={1}; every quadruple was evaluated.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
