# P28: the response's witness u=2, m=3, n=2 against line 5
# ("If u|mn and gcd(u,m)=1, then m = +or-1", with u,m,n integers per line 1)
from math import gcd
u, m, n = 2, 3, 2
print("u,m,n =", (u, m, n))
print("u | m*n ?", (m * n) % u == 0, "  (m*n =", m * n, ")")
print("gcd(u,m) =", gcd(u, m))
print("m in {1,-1}?", m in (1, -1))
print("hypotheses hold and conclusion fails ->", ((m * n) % u == 0) and gcd(u, m) == 1 and m not in (1, -1))
