# ADJ check for P09.  The critic's witness is schematic ("choose any element a in M").
# I do not replace it; I check that it is realisable, i.e. that all of the source's
# hypotheses (P2-P5) can hold simultaneously with a in M, and what then happens to
# lines 0014 and 0017.  Exhaustive over the two- and four-element Boolean lattices.
from itertools import product, combinations

def lattice(elems, leq):
    join = {(x, y): min([z for z in elems if leq(x, z) and leq(y, z)],
                        key=lambda z: sum(1 for w in elems if leq(w, z)))
            for x in elems for y in elems}
    meet = {(x, y): max([z for z in elems if leq(z, x) and leq(z, y)],
                        key=lambda z: sum(1 for w in elems if leq(w, z)))
            for x in elems for y in elems}
    return join, meet

def report(name, elems, leq):
    join, meet = lattice(elems, leq)
    distributive = all(meet[(x, join[(y, z)])] == join[(meet[(x, y)], meet[(x, z)])]
                       for x, y, z in product(elems, repeat=3))
    def is_ideal(S):   # nonempty, down-closed, join-closed
        return S and all(y in S for x in S for y in elems if leq(y, x)) \
               and all(join[(x, y)] in S for x in S for y in S)
    def is_filter(S):  # nonempty, up-closed, meet-closed
        return S and all(y in S for x in S for y in elems if leq(x, y)) \
               and all(meet[(x, y)] in S for x in S for y in S)
    subsets = [frozenset(c) for r in range(len(elems) + 1) for c in combinations(elems, r)]
    ideals = [S for S in subsets if is_ideal(S)]
    filters = [S for S in subsets if is_filter(S)]
    print("== %s  distributive=%s  #ideals=%d #filters=%d" % (name, distributive, len(ideals), len(filters)))
    for F in filters:
        for M in ideals:
            if M & F:
                continue
            maximal = not any(M < I and not (I & F) for I in ideals)   # P5
            if not maximal:
                continue
            for a in sorted(M):                                        # the critic's choice a in M
                N = frozenset(x for x in elems if any(leq(x, join[(m, a)]) for m in M))
                print("   F=%s M=%s (maximal, disjoint)  a=%s in M  ->  N=%s  "
                      "line0014 (a notin M)=%s  line0017 (M proper subset N)=%s"
                      % (sorted(F), sorted(M), a, sorted(N), a not in M, M < N))
                # lines 0004/0010/0012 hold regardless:
                assert all(leq(m, join[(m, a)]) for m in M)
                assert all(leq(a, join[(m, a)]) for m in M)
                assert a in N and M <= N

# two-element Boolean lattice 0 < 1
report("B1 = {0,1}", [0, 1], lambda x, y: x <= y)
# four-element Boolean lattice on subsets of {1,2}
E = [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})]
report("B2 = 2^{1,2}", E, lambda x, y: x <= y)
