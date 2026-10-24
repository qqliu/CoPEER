"""For a mapping represented by graph R, the value f(a) is defined as the inverse image R^{-1}({a})."""

import itertools
import json

DOMAIN = (0, 1)
CODOMAIN = (0, 1)

first_witness = None
checked = 0

for outputs in itertools.product(CODOMAIN, repeat=len(DOMAIN)):
    graph = tuple((x, outputs[x]) for x in DOMAIN)
    for a in DOMAIN:
        checked += 1
        value = outputs[a]
        inverse_image = tuple(x for x, y in graph if y == a)
        singleton_value = (value,)
        if first_witness is None and inverse_image != singleton_value:
            first_witness = (outputs, graph, a, value, inverse_image)

assert checked == 8
assert first_witness == (
    (0, 0),
    ((0, 0), (1, 0)),
    0,
    0,
    (0, 1),
)

payload = {
    "record_id": "reddit_learnmath_b5iobo",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Let f:{0,1}->{0,1} be the constant-zero mapping, with graph R={(0,0),(1,0)}, and take a=0. Then f(a)=0, while R^{-1}({a})={0,1}. Even the singleton {f(a)}={0} differs from that inverse image.",
    "refutation_explanation": "The value of the mapping at 0 is the element 0, whereas the inverse image of {0} contains both domain elements. Thus f(0) cannot be defined as R^{-1}({0}) for this mapping.",
    "search_space": "All 4 functions f:{0,1}->{0,1} in lexicographic output-tuple order, and both inputs a in order 0,1 (8 function-input pairs total), using R={(x,f(x))} and R^{-1}({a})={x:f(x)=a}.",
}

print(json.dumps(payload, separators=(",", ":")))
