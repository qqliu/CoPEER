# P27: finite check of the witness the response supplies for line 17 -- "the map corresponding to
# the unique frame homomorphism from the two-element frame to the one-element frame".
# Verifies: both lattices are frames; the unique map 2 -> 1 is a frame homomorphism (preserves
# arbitrary joins, finite meets, bottom and top); it is not an isomorphism; and the two frames are
# not isomorphic, so no map between the corresponding locales can be an isomorphism either.
from itertools import combinations, chain

def powerset(s):
    s = list(s)
    return [frozenset(c) for r in range(len(s) + 1) for c in combinations(s, r)]

def frame_data(elems, leq):
    def ub(S):  return [x for x in elems if all(leq(y, x) for y in S)]
    def lb(S):  return [x for x in elems if all(leq(x, y) for y in S)]
    def sup(S):
        c = [x for x in ub(S) if all(leq(x, y) for y in ub(S))]
        return c[0] if len(c) == 1 else None
    def inf(S):
        c = [x for x in lb(S) if all(leq(y, x) for y in lb(S))]
        return c[0] if len(c) == 1 else None
    complete = all(sup(S) is not None and inf(S) is not None for S in powerset(elems))
    # frame law: x /\ \/S = \/{x /\ s}
    frame = complete and all(
        inf([x, sup(S)]) == sup([inf([x, s]) for s in S] or [sup([])])
        for x in elems for S in powerset(elems))
    return sup, inf, complete, frame

two = [0, 1];       leq2 = lambda x, y: x <= y
one = ['*'];        leq1 = lambda x, y: True
sup2, inf2, c2, f2 = frame_data(two, leq2)
sup1, inf1, c1, f1 = frame_data(one, leq1)
print("two-element lattice {0<1}: complete =", c2, " frame law =", f2)
print("one-element lattice {*}  : complete =", c1, " frame law =", f1)

h = {0: '*', 1: '*'}          # the unique map 2 -> 1
preserves_joins = all(h[sup2(S)] == sup1([h[s] for s in S]) for S in powerset(two))
preserves_meets = all(h[inf2(list(S))] == inf1([h[s] for s in S])
                      for S in powerset(two) if len(S) <= 2)
print("h =", h)
print("h preserves arbitrary joins (incl. bottom, S = {}):", preserves_joins)
print("h preserves finite meets (incl. top, S = {}):      ", preserves_meets)
print("h is a frame homomorphism:", preserves_joins and preserves_meets)
print("h injective?", len(set(h.values())) == len(h), "  h an isomorphism of frames?",
      len(two) == len(one))
print("are the two frames isomorphic at all? (equal cardinality needed):", len(two) == len(one))
print()
print("So h is a frame homomorphism that is not a frame isomorphism, and no isomorphism between")
print("these two frames exists; hence f = h^op is a continuous map of Loc (line 2: Loc is the dual")
print("of Frm; P4) satisfying line 17's right-hand side while failing to be a locale isomorphism.")
