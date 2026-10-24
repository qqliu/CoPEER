# P36: check exactly the supplied witness for the recurrence on lines 39-43:
# "In the 4x4 matrix with 100 at positions (1,2), (2,4), (3,1), (4,3) and 0 elsewhere, the optimal
#  sum is 400 ..., but any solution that first picks a corner yields a sum of at most 200".
from itertools import permutations
from functools import lru_cache

n = 4
A = [[0] * n for _ in range(n)]
for (i, j) in [(1, 2), (2, 4), (3, 1), (4, 3)]:      # 1-indexed, as the response writes them
    A[i - 1][j - 1] = 100
for row in A:
    print(row)

# true optimum: one element per row and column (a permutation), maximise the sum
best = max(sum(A[i][p[i]] for i in range(n)) for p in permutations(range(n)))
argbest = [p for p in permutations(range(n)) if sum(A[i][p[i]] for i in range(n)) == best]
print("true optimal sum (max over all permutations) =", best)
print("optimal permutations (row -> col, 1-indexed):",
      [[(i + 1, p[i] + 1) for i in range(n)] for p in argbest])

# the source's recurrence, exactly as written on lines 39-46, over contiguous row/col intervals:
# S = max{ S(i1+1:i2, j1+1:j2)+A[i1][j1], S(i1+1:i2, j1:j2-1)+A[i1][j2],
#          S(i1:i2-1, j1+1:j2)+A[i2][j1], S(i1:i2-1, j1:j2-1)+A[i2][j2] },  S(i:i, j:j) = A[i][j]
@lru_cache(maxsize=None)
def S(i1, i2, j1, j2):
    if i1 == i2 and j1 == j2:
        return A[i1][j1]
    return max(S(i1 + 1, i2, j1 + 1, j2) + A[i1][j1],
               S(i1 + 1, i2, j1, j2 - 1) + A[i1][j2],
               S(i1, i2 - 1, j1 + 1, j2) + A[i2][j1],
               S(i1, i2 - 1, j1, j2 - 1) + A[i2][j2])

dp = S(0, n - 1, 0, n - 1)
print("value produced by the recurrence of lines 39-43 =", dp)
print("recurrence equals the optimum?", dp == best)

corners = {(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)}
with_corner = max(sum(A[i][p[i]] for i in range(n)) for p in permutations(range(n))
                  if any((i, p[i]) in corners for i in range(n)))
print("best sum among assignments that use at least one corner of the full matrix =", with_corner)
print()
print("response's three numbers reproduce (400, <=200 with a corner, recurrence short of optimum)?",
      best == 400 and with_corner <= 200 and dp == 200)
