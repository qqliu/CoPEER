r"""The proof asserts flatly that $a \notin M$ (line 0014), and uses this to upgrade $M \subseteq N$ to the strict inclusion $M \subsetneq N$. Nothing in the statement as given constrains $a$ at all, so this assertion is unjustified, and both it and the conclusion $M \subsetneq N$ fail on a concrete two-element distributive lattice."""

import itertools
import json

RECORD_ID = "proofwiki_105639"
WITNESS_DESCRIPTION = (
    "In the two-element chain L={0,1} with meet=min and join=max, "
    "take a=0 and M=N=L."
)
REFUTATION_EXPLANATION = (
    "The program exactly verifies that L is a distributive lattice. For the "
    "witness, M is a subset of N because M=N, but a belongs to M and M is "
    "not a proper subset of N. Thus both the assertion a notin M and the "
    "claimed strict inclusion fail."
)
SEARCH_SPACE = (
    "Exhaustively swept all 2*4*4=32 triples (a,M,N), where a is one of the "
    "two elements and M,N are all subsets of L; all 18 triples satisfying "
    "M subseteq N were tested. The lattice laws and both distributive laws "
    "were checked on all ordered pairs and all 8 ordered triples of elements."
)

L = (0, 1)


def meet(x, y):
    return x if x <= y else y


def join(x, y):
    return x if x >= y else y


def subset_from_mask(mask):
    return frozenset(x for x in L if mask & (1 << x))


# Verify exactly that the fixed operations form a distributive lattice.
for x, y in itertools.product(L, repeat=2):
    assert meet(x, y) in L
    assert join(x, y) in L
    assert meet(x, y) == meet(y, x)
    assert join(x, y) == join(y, x)
    assert meet(x, join(x, y)) == x
    assert join(x, meet(x, y)) == x

for x, y, z in itertools.product(L, repeat=3):
    assert meet(meet(x, y), z) == meet(x, meet(y, z))
    assert join(join(x, y), z) == join(x, join(y, z))
    assert meet(x, join(y, z)) == join(meet(x, y), meet(x, z))
    assert join(x, meet(y, z)) == meet(join(x, y), join(x, z))

# Sweep the complete bounded assignment space without early termination.
counterexamples = []
admissible_count = 0
for a in L:
    for m_mask in range(4):
        M = subset_from_mask(m_mask)
        for n_mask in range(4):
            N = subset_from_mask(n_mask)
            if not M.issubset(N):
                continue
            admissible_count += 1
            assertion_a_notin_M = a not in M
            strict_inclusion = M < N
            if not assertion_a_notin_M and not strict_inclusion:
                counterexamples.append((a, m_mask, n_mask))

assert admissible_count == 18
assert (0, 3, 3) in counterexamples

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False, separators=(",", ":")))
