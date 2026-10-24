# P05: check the response's supplied witness n=10, r=1 against line 17's inequality
# line 17 claims: sum_{i=1}^r (5n/2 - 3i) - 3r + floor((n-3r)^2/4)  <=  floor(n^2/4)
from fractions import Fraction as F

def lhs(n, r):
    s = sum(F(5*n,2) - 3*i for i in range(1, r+1))
    return s - 3*r + F((n-3*r)**2 // 4)

def rhs(n):
    return F(n*n // 4)

n, r = 10, 1
print("witness n=10,r=1: LHS =", lhs(n,r), " RHS =", rhs(n), " inequality holds?", lhs(n,r) <= rhs(n))
# the response's own intermediate numbers
print("response arithmetic: 5n/2-3 =", F(5*10,2)-3, "; -3r =", -3, "; floor(49/4) =", 49//4,
      "; total =", (F(5*10,2)-3) - 3 + 49//4)
# is the witness an isolated edge case? scan feasible (n,r) with 1<=r<=n//3
bad = [(n,r) for n in range(4,121) for r in range(1, n//3+1) if not lhs(n,r) <= rhs(n)]
allp = [(n,r) for n in range(4,121) for r in range(1, n//3+1)]
print("pairs scanned:", len(allp), " pairs where line 17 fails:", len(bad))
print("pairs where line 17 holds:", [p for p in allp if p not in set(bad)][:10])
