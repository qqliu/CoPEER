# ADJ check for P23: exact arithmetic on the critic's supplied instance.
# Model taken from the source: each job is a fixed interval [s_i, s_i+|j_i|] = [s_i, f_i]
# (the source's own example has f_i = s_i + |j_i| for every job), single machine,
# no preemption, profit p_i.  Greedy = "takes a job with the biggest profit" (repeatedly,
# skipping jobs that no longer fit).
from fractions import Fraction
from itertools import combinations

# critic's witness: intervals [1,3],[0,2],[2,4] with profits 10,9,9
jobs = [("A", 1, 3, 10), ("B", 0, 2, 9), ("C", 2, 4, 9)]

lengths = [f - s for (_, s, f, _) in jobs]
print("lengths:", lengths, " max<=k*min with k =", Fraction(max(lengths), min(lengths)))

def overlap(x, y):
    return not (x[2] <= y[1] or y[2] <= x[1])

def feasible(sel):
    return all(not overlap(a, b) for a, b in combinations(sel, 2))

# greedy by biggest profit (ties: any; check all tie orders)
order = sorted(jobs, key=lambda j: (-j[3], j[0]))
sel = []
for j in order:
    if feasible(sel + [j]):
        sel.append(j)
greedy = sum(j[3] for j in sel)
print("greedy picks", [j[0] for j in sel], "profit", greedy)

best, bestsel = 0, None
for r in range(len(jobs) + 1):
    for c in combinations(jobs, r):
        if feasible(c):
            v = sum(j[3] for j in c)
            if v > best:
                best, bestsel = v, [j[0] for j in c]
print("optimum", best, "via", bestsel)
print("ratio greedy/opt =", Fraction(greedy, best))
print("claimed bound 1/(k-eps) for k=1, eps in (0,1): min over eps>0 is >1 ;",
      "ratio", Fraction(greedy, best), "< 1 -> bound violated:", Fraction(greedy, best) < 1)

# also verify the source's own example (lines 8-16): greedy w vs optimum 2(w-1), k=2
for w in (2, 3, 10, 1000):
    src = [("j1", 0, 2, w), ("j2", 0, 1, w - 1), ("j3", 1, 2, w - 1)]
    o = sorted(src, key=lambda j: (-j[3], j[0]))
    s = []
    for j in o:
        if feasible(s + [j]):
            s.append(j)
    g = sum(j[3] for j in s)
    b = max(sum(j[3] for j in c) for r in range(4) for c in combinations(src, r) if feasible(c))
    print("source example w=%s: greedy=%s opt=%s (claimed w vs 2(w-1)=%s)" % (w, g, b, 2 * (w - 1)))
