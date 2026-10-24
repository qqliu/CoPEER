# P35: exact check of the witness supplied by the critic's response, on the source's own instance.
# Source lines 8-14: j1 len 2, s=0, f=2 ; j2 len 1, s=0, f=1 ; j3 len 1, s=1, f=2 ;
#                    p1 = w, p2 = p3 = w-1.   Source line 4: max len <= k * min len, so k = 2 here.
# Response's witness: "the feasible sets {j2,j3} and {j1} violate the matroid exchange property,
# showing the problem is not a matroid."
from itertools import combinations
from fractions import Fraction

jobs = {"j1": (2, 0, 2), "j2": (1, 0, 1), "j3": (1, 1, 2)}   # (length, start, deadline)

def slots(j):
    L, s, f = jobs[j]
    return [(t, t + L) for t in range(s, f - L + 1)]          # integral start times, finish by deadline

def feasible(S):
    """single machine, no overlap; each job in its own window"""
    S = list(S)
    def rec(i, used):
        if i == len(S):
            return True
        for (a, b) in slots(S[i]):
            if all(b <= c or d <= a for (c, d) in used):
                if rec(i + 1, used + [(a, b)]):
                    return True
        return False
    return rec(0, [])

names = list(jobs)
print("feasible slots per job:", {j: slots(j) for j in names})
ind = [frozenset(c) for r in range(len(names) + 1) for c in combinations(names, r) if feasible(c)]
print("independent (schedulable) sets:", sorted(map(sorted, ind), key=lambda x: (len(x), x)))
maximal = [A for A in ind if not any(A < B for B in ind)]
print("maximal independent sets:", sorted(map(sorted, maximal), key=lambda x: (len(x), x)))

A, B = frozenset({"j1"}), frozenset({"j2", "j3"})
print()
print("A =", sorted(A), "feasible:", A in ind, "| B =", sorted(B), "feasible:", B in ind, "| |A| < |B|:", len(A) < len(B))
aug = [x for x in B - A if frozenset(A | {x}) in ind]
print("elements of B\\A that can be added to A keeping feasibility:", aug)
assert A in ind and B in ind and len(A) < len(B) and aug == []
print("=> the matroid augmentation/exchange property FAILS: the response's stated fact is correct,")
print("   the system of schedulable sets on this instance is not a matroid.")

# ---- but does that refute line 20, which says 'k-Matroid' with k = 2 (line 4) ? -------------
print()
sizes = sorted(len(A) for A in maximal)
print("sizes of maximal independent sets:", sizes, " ratio max/min =", Fraction(max(sizes), min(sizes)))
kk = max(l for l, _, _ in jobs.values()) / min(l for l, _, _ in jobs.values())
print("k from line 4 (max length / min length) =", kk)
print("the instance is a k-system in the usual sense (every two maximal independent sets differ in")
print("size by a factor at most k):", Fraction(max(sizes), min(sizes)) <= Fraction(int(kk)))
print("so failing the matroid exchange property is exactly what a k-relaxation permits;")
print("it does not contradict 'the problem is a k-Matroid' for k = 2.")

print()
print("greedy (largest profit first) vs optimum on the source's instance:")
for w in (3, 5, 10, 100, 1000):
    greedy = w                 # takes j1, which blocks j2 and j3
    opt = max(w, 2 * (w - 1))
    print(f"   w={w:5d}: greedy={greedy:6d}  opt={opt:6d}  ratio={Fraction(greedy, opt)} = {float(Fraction(greedy,opt)):.4f}"
          f"   (1/k = 0.5)")
