# P05: check exactly the supplied witness for line 17's inequality
#   sum_{i=1}^r (5n/2 - 3i) - 3r + floor((n-3r)^2/4)  <=  floor(n^2/4)
# witness: "For n=10 and r=1, the left side evaluates to 22-3+floor(49/4) = 31, which is not less
# than or equal to floor(100/4) = 25."
from fractions import Fraction as F

def lhs(n, r):
    s = sum(F(5 * n, 2) - 3 * i for i in range(1, r + 1))
    return s - 3 * r + ((n - 3 * r) ** 2) // 4

def rhs(n):
    return (n * n) // 4

n, r = 10, 1
print("n =", n, " r =", r)
print("sum_{i=1}^r (5n/2 - 3i) =", sum(F(5 * n, 2) - 3 * i for i in range(1, r + 1)))
print("floor((n-3r)^2/4) = floor(%d/4) =" % ((n - 3 * r) ** 2), ((n - 3 * r) ** 2) // 4)
print("LHS =", lhs(n, r), "   RHS = floor(n^2/4) =", rhs(n))
print("response's numbers reproduce (LHS = 31, RHS = 25)? ", lhs(n, r) == 31 and rhs(n) == 25)
print("inequality of line 17 holds here?", lhs(n, r) <= rhs(n))
print("3r <= n (the witness is an admissible triangle-packing size)?", 3 * r <= n)
print()
print("all r with 3r <= n, at n = 10:")
for rr in range(1, 10 // 3 + 1):
    print("   r =", rr, " LHS =", lhs(10, rr), " RHS =", rhs(10), " holds?", lhs(10, rr) <= rhs(10))
print()
fails = holds = 0
for nn in range(4, 61):
    for rr in range(1, nn // 3 + 1):
        if lhs(nn, rr) <= rhs(nn):
            holds += 1
        else:
            fails += 1
print("scan 4 <= n <= 60, 1 <= r <= n/3: instances where line 17 holds =", holds,
      ", where it fails =", fails)
print("(so the witness is not a boundary artefact; expanding, LHS - n^2/4 ~ n*r + 0.75 r^2 - 4.5 r)")
