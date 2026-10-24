# P07: check the response's witness (n=2) against the source's own definitions.
# line 63: lambda = ceil((n-1)/2); line 66: O = {1,3,...,2L+1}, E = {2,4,...,2L}
# line 70/74: x_O = x_{1,2L+1} = s_1 s_3 ... s_{2L+1}; generators s_i, s_j of C_n commute iff |i-j| >= 2
import math
for n in range(2, 13):
    L = math.ceil((n-1)/2)
    O = list(range(1, 2*L+2, 2))
    E = list(range(2, 2*L+1, 2))
    assert max(O) <= n+1 and (not E or max(E) <= n+1)
    # largest set of pairwise commuting generators inside the block x_O: all of O (|i-j|>=2 pairwise)
    pairwise_commuting = all(abs(a-b) >= 2 for i, a in enumerate(O) for b in O[i+1:])
    print(f"n={n}: lambda={L} O={O} (|O|={len(O)}) E={E} (|E|={len(E)}) "
          f"x_O block pairwise commuting={pairwise_commuting} -> n(x_O)={len(O)} vs lambda={L}")
print()
n, L = 2, 1
print("witness n=2:", "lambda =", L, "; x_O = s_1 s_3 ; l(x_O) = 2 ; s_1,s_3 commute since |1-3|>=2 ;",
      "n(x_O) = 2 > lambda = 1 ->", 2 > L)
