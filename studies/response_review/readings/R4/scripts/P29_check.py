# P29: arithmetic part of the witness supplied by the critic's response.
# Witness: n = 2, lambda = 1, w = x_O = s_1 s_3 (a type II element), claimed n(w) = 2 != lambda.
# Everything below is computed from the SOURCE's own formulas:
#   line 63: lambda = ceil((n-1)/2)
#   line 66: O = odd indices in {1,...,n+1};  E = even indices in {1,...,n+1}
#   lines 74/78: x_O = s_1 s_3 ... s_{2lambda+1},  x_E = s_2 s_4 ... s_{2lambda}
import math

def data(n):
    lam = math.ceil((n - 1) / 2)
    O = [i for i in range(1, n + 2) if i % 2 == 1]
    E = [i for i in range(1, n + 2) if i % 2 == 0]
    return lam, O, E

print("n | lambda | O (odd indices) | |O| | E | |E| | 2lam largest even? | 2lam+1 largest odd?")
for n in range(2, 11):
    lam, O, E = data(n)
    largest_even = max(i for i in range(1, n + 2) if i % 2 == 0)
    largest_odd = max(i for i in range(1, n + 2) if i % 2 == 1)
    print(n, "|", lam, "|", O, "|", len(O), "|", E, "|", len(E), "|",
          2 * lam == largest_even, "|", 2 * lam + 1 == largest_odd)

# the response's instance
n = 2
lam, O, E = data(n)
print()
print("response's instance: n =", n)
print("  lambda            =", lam, " (response says 1)")
print("  O                 =", O, "  so x_O = s_1 s_3 (response's w)")
print("  |O| = |x_O| = l(w)=", len(O))
assert lam == 1 and O == [1, 3] and len(O) == 2
# x_O is a product of generators with pairwise index gap >= 2 (same parity), i.e. pairwise
# non-adjacent in the linear Coxeter diagram of affine C_n, hence pairwise commuting; taking
# u = v = e and x = w in the definition of n(w) (source line 6) gives n(w) >= l(x) = |O|,
# and n(w) <= l(w) = |O|, so n(w) = |O| = lambda + 1.
gaps_ok = all(O[t + 1] - O[t] >= 2 for t in range(len(O) - 1))
print("  all index gaps in O are >= 2 (pairwise commuting generators):", gaps_ok)
print("  => n(x_O) = |O| =", len(O), " while lambda =", lam, " -> line 96 fails at this w")
assert len(O) == lam + 1 != lam

print()
print("general: |O| = lambda + 1 for every n tested:",
      all(len(data(n)[1]) == data(n)[0] + 1 for n in range(2, 51)))
print("general: |E| = lambda for every n tested:",
      all(len(data(n)[2]) == data(n)[0] for n in range(2, 51)))
