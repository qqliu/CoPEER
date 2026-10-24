# P09: check the supplied witness "choose any element a in M" inside the ambient family the
# response itself prescribes: "Let L be any distributive lattice ..., F = {top} ..., M a maximal
# ideal disjoint from F ..., Then pick a in M."  I instantiate the smallest member of that family
# (the 2-element chain) and verify every source hypothesis P2-P6 holds while line 14 fails.
from itertools import combinations, chain

def subsets(s):
    s = list(s)
    return [set(c) for r in range(len(s)+1) for c in combinations(s, r)]

def check(L, leq, join, meet, name):
    # distributivity
    dist = all(meet(x, join(y, z)) == join(meet(x, y), meet(x, z)) for x in L for y in L for z in L)
    def is_ideal(I):      # nonempty, downward closed, closed under join (order-theoretic ideal in a lattice)
        return bool(I) and all(y in I for x in I for y in L if leq(y, x)) and all(join(x, y) in I for x in I for y in I)
    def is_filter(F):     # nonempty, upward closed, closed under meet
        return bool(F) and all(y in F for x in F for y in L if leq(x, y)) and all(meet(x, y) in F for x in F for y in F)
    top = [t for t in L if all(leq(x, t) for x in L)][0]
    F = {top}
    ideals = [I for I in subsets(L) if is_ideal(I)]
    out = []
    for M in ideals:
        if M & F:
            continue
        if any((M < I) and not (I & F) for I in ideals):   # P5: no larger ideal disjoint from F
            continue
        for a in sorted(M):                                # the response's witness: a in M
            N = {x for x in L if any(leq(x, join(m, a)) for m in M)}
            out.append(dict(lattice=name, distributive=dist, F=sorted(F), M=sorted(M),
                            M_ideal=is_ideal(M), F_filter=is_filter(F), disjoint=not (M & F),
                            a=a, line14_a_notin_M=(a not in M), N=sorted(N),
                            line7_M_subseteq_N=M <= N, line17_M_proper_subset_N=(M < N)))
    return out

# 2-element chain 0 < 1
L2 = [0, 1]
r = check(L2, lambda x, y: x <= y, max, min, "2-chain 0<1")
# 3-element chain, and the 2x2 product (both distributive), for robustness of the same witness
L3 = [0, 1, 2]
r += check(L3, lambda x, y: x <= y, max, min, "3-chain 0<1<2")
P = [(i, j) for i in (0, 1) for j in (0, 1)]
r += check(P, lambda x, y: x[0] <= y[0] and x[1] <= y[1],
           lambda x, y: (max(x[0], y[0]), max(x[1], y[1])),
           lambda x, y: (min(x[0], y[0]), min(x[1], y[1])), "2x2 product")

for row in r:
    print(row)
print()
print("every row: hypotheses P2-P6 hold and line 14 (a notin M) is FALSE ->",
      all(row["distributive"] and row["M_ideal"] and row["F_filter"] and row["disjoint"]
          and not row["line14_a_notin_M"] for row in r))
print("in every row line 17 (M proper subset N) also fails ->",
      all(not row["line17_M_proper_subset_N"] for row in r))
