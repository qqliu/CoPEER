# P11: the response's witness p = x1^2 x2 + x1 x2^2 in K[x1,x2], degree reverse lexicographic order.
# grevlex (standard, Cox-Little-O'Shea): alpha > beta iff |alpha| > |beta|, or |alpha| = |beta|
# and the RIGHTMOST non-zero entry of alpha - beta is NEGATIVE.
from functools import cmp_to_key

def cmp_grevlex(a, b):
    if sum(a) != sum(b):
        return 1 if sum(a) > sum(b) else -1
    d = [x - y for x, y in zip(a, b)]
    for k in range(len(d) - 1, -1, -1):
        if d[k] != 0:
            return 1 if d[k] < 0 else -1      # rightmost non-zero negative => a > b
    return 0

mons = [(2, 1), (1, 2)]                        # the monomials of p, exponent vectors
srt = sorted(mons, key=cmp_to_key(cmp_grevlex), reverse=True)
print("p's monomials, grevlex-descending:", srt)
LM = srt[0]
print("LM(p) =", LM, " i.e. x1^%d x2^%d" % LM)
print("p is symmetric (monomial set closed under swapping x1,x2)?",
      sorted(mons) == sorted([(m[1], m[0]) for m in mons]))

a1, a2 = LM                                    # (a_1, a_2) of line 20
i, j = 1, 2
print("line 24's hypothesis a_i > a_j for i=1<j=2 holds?", a1 > a2)
swapped = (a2, a1)                             # line 27's monomial with a_i and a_j exchanged
print("line 27's monomial =", swapped, " does it appear in p?", swapped in mons)
c = cmp_grevlex(swapped, LM)
print("comparison of line-27 monomial with LM(p):",
      "larger" if c > 0 else ("smaller" if c < 0 else "equal"))
print("line 29's assertion ('it would be larger than LM p') holds?", c > 0)
