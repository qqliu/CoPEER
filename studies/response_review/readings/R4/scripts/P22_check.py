# P22: exact check of the witness supplied by the critic's response.
# Line 17 asserts:  sum_{i=1}^r (5n/2 - 3i) - 3r + floor((n-3r)^2/4)  <=  floor(n^2/4).
# Witness: n = 10, r = 1 -> left side 31, right side 25.
from fractions import Fraction as F

def lhs(n, r):
    s = sum(F(5 * n, 2) - 3 * i for i in range(1, r + 1))
    return s - 3 * r + ((n - 3 * r) ** 2) // 4

def rhs(n):
    return (n * n) // 4

n, r = 10, 1
L, R = lhs(n, r), rhs(n)
print(f"n={n}, r={r}:  sum_i (5n/2 - 3i) = {sum(F(5*n,2)-3*i for i in range(1,r+1))}")
print(f"   left side = {L}   right side = floor(n^2/4) = {R}   inequality holds ? {L <= R}")
assert L == 31 and R == 25 and L > R
print("=> line 17's inequality is FALSE at n=10, r=1 (31 > 25).")

print()
print("the failure is not isolated; 'H' = holds, '.' = fails, for 3r <= n:")
print("   n \\ r " + "".join(f"{r:4d}" for r in range(1, 8)))
for n in range(6, 31, 2):
    row = ""
    for r in range(1, 8):
        row += "   -" if 3 * r > n else ("   H" if lhs(n, r) <= rhs(n) else "   .")
    print(f"   {n:5d} " + row)

print()
print("admissibility of the witness in the source's own setting (my own check, not the response's):")
print("  n = 10 needs a graph with floor(n^2/4)+1 = 26 edges whose maximal system of vertex-disjoint")
print("  triangles has r = 1.  K_{5,5} plus one edge uv inside a part has 25+1 = 26 edges, and every")
print("  triangle uses both u and v, so no two triangles are vertex-disjoint: r = 1, and deleting the")
print("  triangle's three vertices leaves K_{4,4}, triangle-free as line 8 requires.")
u_deg, v_deg, w_deg = 6, 6, 5   # degrees of u, v (5 cross + the new edge) and w (5 cross) in that G
print("  the contradiction hypothesis of line 12 also holds there: degree sum at i=1 is",
      u_deg + v_deg + w_deg, "<= 5n/2 - 3 =", F(5 * 10, 2) - 3)
print("  and line 16 then reads 26 <=", lhs(10, 1), "which is true, so no contradiction is reached.")
