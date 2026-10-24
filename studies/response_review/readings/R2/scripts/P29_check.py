# P29: arithmetic of the source's own definitions at the response's witness n = 2
# lambda = ceil((n-1)/2) (line 63);  O = {1,3,...,2*lambda+1},  E = {2,4,...,2*lambda} (line 66)
# x_O = s_1 s_3 ... s_{2 lambda + 1}   (line 74),  x_E = s_2 s_4 ... s_{2 lambda}  (line 78)
from math import ceil
for n in (2, 3, 4, 5, 6):
    lam = ceil((n - 1) / 2)
    O = list(range(1, 2 * lam + 2, 2))
    E = list(range(2, 2 * lam + 1, 2))
    print("n =", n, " lambda =", lam,
          " O =", O, "(|O| =", len(O), ")  E =", E, "(|E| =", len(E), ")",
          " | line-63 checks: 2lam largest even in 1..n+1?", 2 * lam == max(k for k in range(1, n + 2) if k % 2 == 0),
          " 2lam+1 largest odd?", 2 * lam + 1 == max(k for k in range(1, n + 2) if k % 2 == 1))
    print("      x_O is a product of", len(O), "generators with pairwise non-adjacent (same parity) indices",
          "-> n(x_O) >=", len(O), " versus the claimed n(w) =", lam,
          " => line 96 fails for w = x_O?", len(O) > lam)
