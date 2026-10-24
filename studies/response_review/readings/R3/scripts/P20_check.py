# P20: check the witness (n=2, x_1^2 x_2 vs its swap x_1 x_2^2) in degree reverse lexicographic order.
from itertools import combinations
def drl_greater(a, b):        # standard degrevlex: bigger total degree wins; ties broken by the
    if sum(a) != sum(b):      # RIGHTMOST nonzero entry of a-b being negative
        return sum(a) > sum(b)
    d = [x-y for x, y in zip(a, b)]
    for v in reversed(d):
        if v != 0: return v < 0
    return False
a, b = (2, 1), (1, 2)         # x_1^2 x_2  and its exponent-swap x_1 x_2^2
print("x_1^2 x_2 =", a, " swap =", b)
print("a_1 =", a[0], "> a_2 =", a[1], "so the witness is in line 24's assumed case a_i > a_j with i<j")
print("is the swap LARGER, as line 29 asserts?", drl_greater(b, a))
print("is the swap SMALLER?", drl_greater(a, b), " (a-b =", tuple(x-y for x,y in zip(a,b)),
      ", rightmost nonzero -1 < 0, so x_1^2 x_2 wins)")
# confirm the packet's order convention from its own line 9-13: LM(sigma_k) = x_1...x_k
def lm_sigma(n, k):
    best = None
    for S in combinations(range(n), k):
        e = tuple(1 if i in S else 0 for i in range(n))
        if best is None or drl_greater(e, best): best = e
    return best
for n in (2, 3, 4):
    print(f"n={n}: LM(sigma_k) under this order:",
          {k: lm_sigma(n, k) for k in range(1, n+1)},
          "-> equals x_1...x_k as source line 9 states:",
          all(lm_sigma(n,k) == tuple(1 if i<k else 0 for i in range(n)) for k in range(1, n+1)))
