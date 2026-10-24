# P24: check the witness u=6, m=5, n=6 against source line 5.
from math import gcd
u, m, n = 6, 5, 6
print("u|mn ?", (m*n) % u == 0, f"  ({u} | {m*n})")
print("gcd(u,m) =", gcd(u, m))
print("m =", m, " is m = +-1 ?", m in (1, -1))
print("line 5 fails at this witness:", (m*n) % u == 0 and gcd(u, m) == 1 and m not in (1, -1))
