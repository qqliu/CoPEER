# P36: check the supplied 4x4 witness against the recurrence of source lines 39-43.
from itertools import permutations
from functools import lru_cache
n = 4
A = [[0]*n for _ in range(n)]
for (i, j) in [(1,2),(2,4),(3,1),(4,3)]:      # 1-based positions given by the response
    A[i-1][j-1] = 100
print("witness matrix:"); [print("   ", row) for row in A]
# true optimum of the problem as stated (one element per row and per column)
best = max(sum(A[i][p[i]] for i in range(n)) for p in permutations(range(n)))
argbest = [p for p in permutations(range(n)) if sum(A[i][p[i]] for i in range(n)) == best][:3]
print("true optimum over all permutations:", best, " attained by (0-based col per row):", argbest)
# the source's recurrence: only the four corners of the current contiguous block may be taken
@lru_cache(maxsize=None)
def S(i1, i2, j1, j2):
    if i1 == i2 and j1 == j2: return A[i1][j1]          # line 46: S(i:i, j:j) = A_ij
    return max(S(i1+1, i2, j1+1, j2) + A[i1][j1],
               S(i1+1, i2, j1, j2-1) + A[i1][j2],
               S(i1, i2-1, j1+1, j2) + A[i2][j1],
               S(i1, i2-1, j1, j2-1) + A[i2][j2])
val = S(0, n-1, 0, n-1)
print("value produced by the recurrence of lines 39-43:", val)
print("recurrence equals the optimum?", val == best, "  gap:", best - val)
# the response's intermediate assertion: any solution that first takes a corner is worth at most 200
def opt_after_corner(r, c):
    rows = [i for i in range(n) if i != r]; cols = [j for j in range(n) if j != c]
    return A[r][c] + max(sum(A[rows[k]][p[k]] for k in range(n-1))
                         for p in permutations(cols))
corners = {(0,0):None,(0,n-1):None,(n-1,0):None,(n-1,n-1):None}
vals = {f"({r+1},{c+1})": opt_after_corner(r,c) for (r,c) in corners}
print("best full solution that uses a given corner:", vals, " max =", max(vals.values()),
      "<= 200 as the response says:", max(vals.values()) <= 200)
