# P18: the response's witness -- 4x4 matrix, 0 at the four corners, 1 elsewhere.
# Compare (a) the true optimum over permutations with (b) the literal recurrence of lines 39-43,
# with the base case of line 46, S(i:i, j:j) = A_ij.
from itertools import permutations
from functools import lru_cache

n = 4
A = [[1] * n for _ in range(n)]
for (i, j) in ((0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)):
    A[i][j] = 0
print("A ="); [print("   ", row) for row in A]

best = max(sum(A[i][p[i]] for i in range(n)) for p in permutations(range(n)))
argmax = [p for p in permutations(range(n)) if sum(A[i][p[i]] for i in range(n)) == best][:3]
print("true optimum over all permutations:", best, " e.g. column choices (0-indexed):", argmax)

@lru_cache(maxsize=None)
def S(r1, r2, c1, c2):
    if r1 == r2:
        return A[r1][c1]
    return max(S(r1 + 1, r2, c1 + 1, c2) + A[r1][c1],     # drop row r1, col c1; take A_{1,1}
               S(r1 + 1, r2, c1, c2 - 1) + A[r1][c2],     # take A_{1,n}
               S(r1, r2 - 1, c1 + 1, c2) + A[r2][c1],     # take A_{n,1}
               S(r1, r2 - 1, c1, c2 - 1) + A[r2][c2])     # take A_{n,n}

val = S(0, n - 1, 0, n - 1)
print("value of the recurrence S(1:n,1:n):", val)
print("recurrence equals the true optimum?", val == best)
