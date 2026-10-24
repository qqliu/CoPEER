r"""The proof asserts flatly that $a \notin M$ (line 0014), and uses this to upgrade $M \subseteq N$ to the strict inclusion $M \subsetneq N$. Nothing in the statement as given constrains $a$ at all, so this assertion is unjustified, and both it and the conclusion $M \subsetneq N$ fail on a concrete two-element distributive lattice."""

import json

record_id = "proofwiki_105639"
verdict = "CONFIRMED"
notes = ("Exact recomputation validates the two-element distributive lattice and "
         "the witness a=0, M=N={0,1}: M is a subset of N, while a is in M "
         "and M is not a proper subset of N. The refuted statement is a "
         "substantive logical error, not plainly a typo.")

carrier = (0, 1)
order = frozenset(((0, 0), (0, 1), (1, 1)))
meet_values = ((0, 0), (0, 1))
join_values = ((0, 1), (1, 1))


def leq(x, y):
    return (x, y) in order


def meet(x, y):
    return meet_values[x][y]


def join(x, y):
    return join_values[x][y]


valid = True

for x in carrier:
    valid = valid and leq(x, x)
    for y in carrier:
        if leq(x, y) and leq(y, x):
            valid = valid and x == y
        for z in carrier:
            if leq(x, y) and leq(y, z):
                valid = valid and leq(x, z)

for x in carrier:
    for y in carrier:
        m = meet(x, y)
        j = join(x, y)
        valid = valid and m in carrier and j in carrier

        lower_bounds = tuple(u for u in carrier if leq(u, x) and leq(u, y))
        greatest_lower_bounds = tuple(
            u for u in lower_bounds
            if all(leq(v, u) for v in lower_bounds)
        )
        upper_bounds = tuple(u for u in carrier if leq(x, u) and leq(y, u))
        least_upper_bounds = tuple(
            u for u in upper_bounds
            if all(leq(u, v) for v in upper_bounds)
        )
        valid = valid and greatest_lower_bounds == (m,)
        valid = valid and least_upper_bounds == (j,)

        for z in carrier:
            valid = valid and meet(x, join(y, z)) == join(meet(x, y), meet(x, z))
            valid = valid and join(x, meet(y, z)) == meet(join(x, y), join(x, z))

M = frozenset((0, 1))
N = frozenset((0, 1))
a = 0

valid = valid and a in carrier and M <= frozenset(carrier) and N <= frozenset(carrier)
for subset in (M, N):
    for x in subset:
        for y in subset:
            valid = valid and meet(x, y) in subset and join(x, y) in subset

premise = M <= N
assertion_a_not_in_M = a not in M
strict_inclusion = M < N
witness_refutes_both = premise and not assertion_a_not_in_M and not strict_inclusion

if not (valid and witness_refutes_both):
    raise SystemExit(1)

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
