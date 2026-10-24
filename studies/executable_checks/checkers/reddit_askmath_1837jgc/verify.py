r'''If Σ(k≥1)|aₖ|=L and g:ℕ→ℕ is a bijection, then Σ(k≥1)a_{g(k)}=L.'''

import json

record_id = "reddit_askmath_1837jgc"
verdict = "CONFIRMED"
notes = ("Exact recomputation gives Σ|aₖ|=1 while the identity rearrangement gives "
         "Σa_{g(k)}=-1. Thus the premise holds with L=1 and the conclusion fails. "
         "As written, the refuted statement is substantive, not plainly a typo.")

def coefficient(index):
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("index must be a positive integer")
    return -1 if index == 1 else 0

def rearrangement(index):
    if not isinstance(index, int) or isinstance(index, bool) or index < 1:
        raise ValueError("index must be a positive integer")
    return index

def inverse_rearrangement(index):
    return rearrangement(index)

# The rearrangement and its displayed inverse are the identity on every
# positive integer by their definitions above, hence form a bijection on ℕ.
for index in (1, 2, 3, 17):
    assert inverse_rearrangement(rearrangement(index)) == index
    assert rearrangement(inverse_rearrangement(index)) == index

# The sequence is supported on {1}; all omitted terms are exactly zero.
support = (1,)
absolute_sum = sum(abs(coefficient(index)) for index in support)
rearranged_sum = sum(coefficient(rearrangement(index)) for index in support)
L = 1

assert coefficient(2) == 0
assert coefficient(19) == 0
assert absolute_sum == L
assert rearranged_sum == -1
assert rearranged_sum != L

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes},
                 ensure_ascii=False, separators=(",", ":")))
