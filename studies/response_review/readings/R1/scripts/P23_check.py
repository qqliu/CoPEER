# P23: run exactly the supplied witness: "For k=1, three jobs with exact intervals [1,3], [0,2],
# and [2,4] and profits 10, 9, and 9 ... greedy returns 10 while the optimal schedule gives 18,
# yielding a ratio of 5/9".  Greedy is the source's line 6 rule: "Greedy takes a job with the
# biggest profit" (repeatedly, among those still schedulable).
from fractions import Fraction
from itertools import combinations

jobs = [("A", 1, 3, 10), ("B", 0, 2, 9), ("C", 2, 4, 9)]   # (name, s_i, f_i, p_i), length = f_i - s_i

def conflict(u, v):
    return max(u[1], v[1]) < min(u[2], v[2])               # open-interval overlap on one machine

lengths = [j[2] - j[1] for j in jobs]
print("lengths:", lengths, " max <= k*min with k=1 ?", max(lengths) <= 1 * min(lengths),
      "  (source line 4)")

# greedy: biggest profit first, keep if compatible with what is already scheduled
sched = []
for j in sorted(jobs, key=lambda t: -t[3]):
    if all(not conflict(j, s) for s in sched):
        sched.append(j)
greedy = sum(j[3] for j in sched)
print("greedy picks", [j[0] for j in sched], "profit", greedy)

# optimum: exhaustive over all subsets
best, bestset = 0, None
for r in range(len(jobs) + 1):
    for S in combinations(jobs, r):
        if all(not conflict(u, v) for u, v in combinations(S, 2)):
            if sum(j[3] for j in S) > best:
                best, bestset = sum(j[3] for j in S), S
print("optimum  picks", [j[0] for j in bestset], "profit", best)
print("ratio greedy/OPT =", Fraction(greedy, best), "=", float(Fraction(greedy, best)))
print("response's stated numbers reproduce (10, 18, 5/9)? ",
      greedy == 10 and best == 18 and Fraction(greedy, best) == Fraction(5, 9))
print()
for eps in (Fraction(1, 2), Fraction(1, 10), Fraction(1, 100)):
    claimed = Fraction(1, 1) / (1 - eps)     # line 20's 1/(k-eps) at k=1
    print("  eps =", eps, " claimed factor 1/(k-eps) =", claimed,
          " greedy/OPT >= claimed ? ", Fraction(greedy, best) >= claimed)
print()
# for reference, the source's own example at lines 8-16 has k=2 (lengths 2,1,1)
print("source's own 3-job example: lengths 2,1,1 -> k = 2; its ratio w/(2(w-1)) tends to 1/2,")
for w in (10, 100, 10000):
    print("   w =", w, " ratio =", float(Fraction(w, 2 * (w - 1))),
          " < 1/(2-eps) for eps=1/100 ?", Fraction(w, 2 * (w - 1)) < Fraction(1, 1) / (2 - Fraction(1, 100)))
