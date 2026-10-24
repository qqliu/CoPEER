# ADJ check for P35.  The supplied evidence is an exchange-property failure on the
# source's own three jobs; I check (1) that the failure is real, (2) what it does and
# does not establish about the source's k-parameterised claim, (3) whether the supplied
# instance itself violates the claimed factor 1/(k-eps).
from fractions import Fraction
from itertools import combinations

# j1 = [0,2] (length 2), j2 = [0,1], j3 = [1,2]  (the source's own example, k = 2)
J = {"j1": (0, 2), "j2": (0, 1), "j3": (1, 2)}
lens = {n: f - s for n, (s, f) in J.items()}
print("lengths", lens, "k = max/min =", Fraction(max(lens.values()), min(lens.values())))

def ok(names):
    iv = [J[n] for n in names]
    return all(a[1] <= b[0] or b[1] <= a[0] for a, b in combinations(iv, 2))

indep = [frozenset(c) for r in range(4) for c in combinations(J, r) if ok(c)]
print("feasible (independent) sets:", sorted(map(sorted, indep), key=lambda s: (len(s), s)))

# (1) matroid augmentation axiom: A={j1}, B={j2,j3}, |A| < |B|
A, B = frozenset({"j1"}), frozenset({"j2", "j3"})
print("A indep:", A in indep, " B indep:", B in indep, " |A|<|B|:", len(A) < len(B))
aug = [x for x in B - A if (A | {x}) in indep]
print("x in B\\A with A+x independent:", aug, "-> augmentation FAILS:", aug == [])
# so the system is not a matroid; confirm brute force over all pairs
viol = [(sorted(a), sorted(b)) for a in indep for b in indep
        if len(a) < len(b) and not any((a | {x}) in indep for x in b - a)]
print("all augmentation violations:", viol)

# (2) the same system IS an intersection of 2 matroids / a 2-extendible system in the
#     sense that matters for a 1/k greedy bound: adding any single job forces the removal
#     of at most k = 2 jobs from any feasible set.
worst = 0
for x in J:
    for S in indep:
        if x in S:
            continue
        need = min(len(Y) for Y in (frozenset(c) for r in range(len(S) + 1) for c in combinations(S, r))
                   if ((S - Y) | {x}) in indep)
        worst = max(worst, need)
print("max #jobs that must be dropped to insert one job:", worst, "(<= k = 2)")

# (3) does the supplied instance violate the claimed factor at its own k = 2?
for w in (3, 10, 100, 10**6):
    P = {"j1": w, "j2": w - 1, "j3": w - 1}
    order = sorted(J, key=lambda n: (-P[n], n))
    sel = []
    for n in order:
        if ok(sel + [n]):
            sel.append(n)
    g = sum(P[n] for n in sel)
    b = max(sum(P[n] for n in c) for r in range(4) for c in combinations(J, r) if ok(c))
    print("w=%-8s greedy=%-8s opt=%-8s ratio=%s  ratio>1/k=%s" %
          (w, g, b, Fraction(g, b), Fraction(g, b) > Fraction(1, 2)))
