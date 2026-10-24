# P07: check the supplied witness for line 96 ("type II => n(w) = lambda"):
# "For n=2, lambda=1, the element w = s1 s3 (= x_O) is a type II element but n(w)=2 > lambda."
# Definitions used, all from the packet: line 63, lambda = ceil((n-1)/2); line 66, O = {1,3,...,
# 2*lambda+1}, E = {2,4,...,2*lambda}; line 74, x_O = s_1 s_3 ... s_{2lambda+1}; line 6, n(w) is the
# max l(x) over reduced w = u x v with x a product of commuting generators, equivalently (line 6)
# "the size of a maximal antichain in the heap poset for w".
# Coxeter data for affine C_n with generators s_1..s_{n+1}: a path with a bond at each end, so
# s_i and s_j commute exactly when |i-j| >= 2 (this is what the packet's own x_{i,j} = s_i s_{i+2}...
# "product of commuting generators" and z_{i,j} = s_i s_{i+1}... presuppose).
from math import ceil
from itertools import combinations

def commute(i, j): return abs(i - j) >= 2

def max_antichain(word):
    m = len(word)
    less = [[False] * m for _ in range(m)]
    for p in range(m):
        for q in range(p + 1, m):
            if not commute(word[p], word[q]):
                less[p][q] = True
    for k in range(m):                       # transitive closure
        for p in range(m):
            for q in range(m):
                if less[p][k] and less[k][q]:
                    less[p][q] = True
    best = 0
    for r in range(m, 0, -1):
        for S in combinations(range(m), r):
            if all(not (less[p][q] or less[q][p]) for p, q in combinations(S, 2)):
                return r
    return best

print(" n  lambda   O            E         |O|  |E|   n(x_O)  n(x_O x_E)   line63 ok?")
for n in range(2, 13):
    lam = ceil((n - 1) / 2)
    O = list(range(1, 2 * lam + 2, 2))
    E = list(range(2, 2 * lam + 1, 2))
    xO, xE = O[:], E[:]
    idx = list(range(1, n + 2))
    line63 = (2 * lam == max(i for i in idx if i % 2 == 0)) and \
             (2 * lam + 1 == max(i for i in idx if i % 2 == 1))
    print("%2d   %3d   %-12s %-9s %3d  %3d   %5d   %8d      %s"
          % (n, lam, O, E, len(O), len(E),
             max_antichain(xO), max_antichain(xO + xE), line63))

print()
n, lam = 2, ceil((2 - 1) / 2)
print("the witness: n = 2, lambda =", lam, " x_O = s_1 s_3, l(x_O) = 2")
print("n(x_O) =", max_antichain([1, 3]), " lambda =", lam,
      " so n(w) = lambda ?", max_antichain([1, 3]) == lam)
print("s_1 and s_3 commute (|1-3| >= 2):", commute(1, 3),
      "  so x_O is a product of commuting generators and n(x_O) = l(x_O) = 2")
print()
print("systematically |O| = lambda + 1 and |E| = lambda, so any type II word containing an x_O")
print("block has n(w) >= lambda + 1 > lambda.")
