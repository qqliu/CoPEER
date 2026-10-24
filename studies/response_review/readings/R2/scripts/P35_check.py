# P35: check the factual content of the response's witness -- the source's own 3-job instance --
# i.e. which job sets are schedulable, and whether the exchange property fails.
from itertools import permutations, combinations
jobs = {"j1": dict(len=2, s=0, f=2), "j2": dict(len=1, s=0, f=1), "j3": dict(len=1, s=1, f=2)}

def feasible(S):
    """can all jobs in S be run on one machine, each in [s_i, f_i], no overlap?"""
    for order in permutations(S):
        t = 0; ok = True
        for j in order:
            start = max(t, jobs[j]["s"])
            if start + jobs[j]["len"] > jobs[j]["f"]: ok = False; break
            t = start + jobs[j]["len"]
        if ok: return True
    return False

allsets = [c for r in range(4) for c in combinations(jobs, r)]
F = [s for s in allsets if feasible(s)]
print("feasible sets:", F)
A, B = ("j1",), ("j2", "j3")
print("A =", A, "feasible?", feasible(A), "  B =", B, "feasible?", feasible(B))
print("|A| < |B|?", len(A) < len(B))
print("can any element of B \\ A be added to A?",
      {x: feasible(A + (x,)) for x in B if x not in A})
print("=> matroid exchange property fails, so the independence system is NOT a matroid:",
      all(not feasible(A + (x,)) for x in B if x not in A))
# the profit figures of lines 14-16, for context on the approximation ratio
for w in (3, 10, 100, 1000):
    greedy, opt = w, 2 * (w - 1)
    print("w =", w, " greedy =", greedy, " optimum =", opt, " ratio =", round(greedy / opt, 4),
          " (1/k with k = max|j|/min|j| = 2 is 0.5)")
