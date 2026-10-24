# P18: exact check of the witness supplied by the critic's response.
# Witness: the 4x4 matrix with 0 at the four corners and 1 everywhere else.
# Response: true maximum sum is 4, the recurrence of line 39 yields 3.
from itertools import permutations
from functools import lru_cache

n = 4
A = [[0 if (i in (0, n-1) and j in (0, n-1)) else 1 for j in range(n)] for i in range(n)]
print("A =")
for row in A:
    print("   ", row)

# (a) the true optimum of the stated problem: one element per row and per column
best = max(sum(A[i][p[i]] for i in range(n)) for p in permutations(range(n)))
argbest = [p for p in permutations(range(n)) if sum(A[i][p[i]] for i in range(n)) == best][0]
print("true maximum over all permutations:", best, " attained e.g. by column choices", argbest,
      "-> cells", [(i, argbest[i]) for i in range(n)])

# (b) the value produced by the recurrence of lines 39-43 (S on contiguous equal-size row/col ranges,
#     base case S(i:i, j:j) = A_ij, four options taking a corner of the current subarray)
@lru_cache(maxsize=None)
def S(i1, i2, j1, j2):
    assert i2 - i1 == j2 - j1
    if i1 == i2:
        return A[i1][j1]
    return max(S(i1+1, i2, j1+1, j2) + A[i1][j1],      # + A_{1,1}
               S(i1+1, i2, j1, j2-1) + A[i1][j2],      # + A_{1,n}
               S(i1, i2-1, j1+1, j2) + A[i2][j1],      # + A_{n,1}
               S(i1, i2-1, j1, j2-1) + A[i2][j2])      # + A_{n,n}
rec = S(0, n-1, 0, n-1)
print("value of the recurrence S(1:n,1:n):", rec)
print("recurrence equals the optimum ?", rec == best)
assert best == 4 and rec == 3
print("=> line 39's identity FAILS on this A: its left side (the optimal sum, by the definition at")
print("   line 35) is 4 while its right side evaluates to 3.")

# (c) why: every optimal permutation avoids all four corners
opt = [p for p in permutations(range(n)) if sum(A[i][p[i]] for i in range(n)) == best]
corners = {(0, 0), (0, n-1), (n-1, 0), (n-1, n-1)}
uses_corner = [any((i, p[i]) in corners for i in range(n)) for p in opt]
print("number of optimal permutations:", len(opt), "; any of them uses a corner cell ?", any(uses_corner))
