# P23: check the witness: fixed intervals [1,3] p=10, [0,2] p=9, [2,4] p=9, k=1.
from fractions import Fraction as F
from itertools import combinations
jobs = [((1,3), 10), ((0,2), 9), ((2,4), 9)]          # (interval, profit), as supplied
def overlap(a, b): return a[0] < b[1] and b[0] < a[1]  # touching endpoints do not conflict
lens = [b-a for (a,b), p in jobs]
print("job lengths:", lens, " max <= k*min with k=1 ?", max(lens) <= 1*min(lens))
# greedy of the source (line 6): repeatedly take the feasible job with the biggest profit
chosen, taken = [], []
for iv, p in sorted(jobs, key=lambda t: -t[1]):
    if all(not overlap(iv, q) for q in taken): taken.append(iv); chosen.append((iv,p))
print("greedy picks:", chosen, " greedy profit =", sum(p for _, p in chosen))
# optimum by exhaustive enumeration
best, arg = 0, None
for r in range(len(jobs)+1):
    for S in combinations(jobs, r):
        ivs = [iv for iv,_ in S]
        if all(not overlap(a,b) for a,b in combinations(ivs,2)):
            v = sum(p for _,p in S)
            if v > best: best, arg = v, S
print("optimum:", arg, " profit =", best)
g = sum(p for _, p in chosen)
print("ratio greedy/optimum =", F(g, best), "=", float(F(g,best)), " response says 5/9 =", float(F(5,9)))
print("k = 1, so the conjectured factor 1/(k-eps) = 1/(1-eps) is > 1 for 0 < eps < 1;")
print("observed ratio", F(g,best), "< 1, so no factor of that form is attained:", F(g,best) < 1)
