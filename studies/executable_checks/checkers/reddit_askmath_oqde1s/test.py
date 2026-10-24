"""From dem = a and den = b, de is a common multiple of a and b."""

import itertools
import json

first_witness = None
for d, e, m, n in itertools.product(range(1, 3), repeat=4):
    a = d * e * m
    b = d * e * n
    de = d * e
    is_common_multiple = de % a == 0 and de % b == 0
    if not is_common_multiple and first_witness is None:
        first_witness = (d, e, m, n, a, b, de)

if first_witness is None:
    result = {
        "record_id": "reddit_askmath_oqde1s",
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "",
        "refutation_explanation": "No counterexample was found in the stated finite space.",
        "search_space": "All 16 ordered 4-tuples (d,e,m,n) in {1,2}^4, in itertools.product lexicographic order; a=dem and b=den were derived for every tuple, and every tuple was checked."
    }
else:
    d, e, m, n, a, b, de = first_witness
    result = {
        "record_id": "reddit_askmath_oqde1s",
        "outcome": "WITNESS_FOUND",
        "witness_description": f"d={d}, e={e}, m={m}, n={n}, a={a}, b={b}, and de={de}.",
        "refutation_explanation": f"The premises hold because dem={d}*{e}*{m}={a}=a and den={d}*{e}*{n}={b}=b. However, de={de} is not divisible by b={b}, so de is not a common multiple of a and b.",
        "search_space": "All 16 ordered 4-tuples (d,e,m,n) in {1,2}^4, in itertools.product lexicographic order; a=dem and b=den were derived for every tuple, and every tuple was checked."
    }

print(json.dumps(result))
