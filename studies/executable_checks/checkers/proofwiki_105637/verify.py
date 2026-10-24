r'''The proof's "Distributing" step claims that from $\paren{\paren{m \vee n} \vee b} \wedge \paren{\paren{n \vee m} \vee a} \in F$ one may conclude $\paren{m \vee n} \wedge \paren{b \vee a} \in F$. This inverts the distributive law: in a distributive lattice $(x \vee b) \wedge (x \vee a) = x \vee (a \wedge b)$, not $x \wedge (a \vee b)$. The two expressions are not equal and the second is not above the first (it is in fact $\le x \le x \vee (a\wedge b)$), so upward closure of the filter does not license the step.'''

import json

universe = (0, 1)
chosen_filter = frozenset({1})


def lattice_join(x, y):
    return x | y


def lattice_meet(x, y):
    return x & y


def below(x, y):
    return lattice_meet(x, y) == x


# Check the finite algebra used by the witness is a distributive lattice.
for x in universe:
    for y in universe:
        assert lattice_join(x, y) in universe
        assert lattice_meet(x, y) in universe
        assert lattice_join(x, y) == lattice_join(y, x)
        assert lattice_meet(x, y) == lattice_meet(y, x)
        for z in universe:
            assert lattice_meet(x, lattice_join(y, z)) == lattice_join(
                lattice_meet(x, y), lattice_meet(x, z)
            )
            assert lattice_join(x, lattice_meet(y, z)) == lattice_meet(
                lattice_join(x, y), lattice_join(x, z)
            )

# Independently check that {1} is nonempty, meet-closed, and upward-closed.
assert chosen_filter
for x in chosen_filter:
    for y in chosen_filter:
        assert lattice_meet(x, y) in chosen_filter
    for y in universe:
        if below(x, y):
            assert y in chosen_filter

m = 0
n = 0
a = 1
b = 1

premise = lattice_meet(
    lattice_join(lattice_join(m, n), b),
    lattice_join(lattice_join(n, m), a),
)
conclusion = lattice_meet(
    lattice_join(m, n),
    lattice_join(b, a),
)

assert premise == 1
assert conclusion == 0
assert premise in chosen_filter
assert conclusion not in chosen_filter

result = {
    "record_id": "proofwiki_105637",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation in the two-element Boolean lattice verifies that F={1} is a filter, the stated premise has value 1 in F, and the stated conclusion has value 0 outside F. The refuted distributing step is a substantive proof error, not plainly a typo.",
}
print(json.dumps(result, separators=(",", ":")))
