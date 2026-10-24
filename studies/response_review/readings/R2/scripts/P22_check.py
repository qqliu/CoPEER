# P22: (a) the response's arithmetic witness n=10, r=1 for the line-17 inequality;
#      (b) whether (n,r) = (10,1) is admissible under the source's set-up.
from fractions import Fraction as F
import itertools

def lhs(n, r):
    s = sum(F(5 * n, 2) - 3 * i for i in range(1, r + 1))
    return s - 3 * r + ((n - 3 * r) ** 2) // 4
def rhs(n, r):
    return (n * n) // 4

n, r = 10, 1
print("n =", n, "r =", r, " LHS =", lhs(n, r), " RHS =", rhs(n, r),
      " line-17 inequality LHS <= RHS holds?", lhs(n, r) <= rhs(n, r))
print("other (n,r): ", [(N, R, str(lhs(N, R)), rhs(N, R), lhs(N, R) <= rhs(N, R))
                        for N, R in ((10, 2), (10, 3), (20, 1), (20, 4), (30, 1))])

# (b) a 10-vertex graph with floor(n^2/4)+1 = 26 edges whose maximal disjoint-triangle system has r = 1
T = ["a", "b", "c"]
L = ["x1", "x2", "x3"]; Rt = ["y1", "y2", "y3", "y4"]
V = T + L + Rt
E = set()
for u, v in itertools.combinations(T, 2): E.add(frozenset((u, v)))      # the triangle: 3 edges
for u in L:
    for v in Rt: E.add(frozenset((u, v)))                                # K_{3,4}: 12 edges, triangle-free
join = [("a", "x1"), ("a", "x2"), ("a", "x3"), ("a", "y1"), ("b", "x1"), ("b", "y1"),
        ("b", "y2"), ("c", "x2"), ("c", "y3"), ("c", "y4"), ("c", "x3")]  # 11 join edges
for u, v in join: E.add(frozenset((u, v)))
print("\n|V| =", len(V), " |E| =", len(E), " floor(n^2/4)+1 =", (len(V) ** 2) // 4 + 1,
      " edges match?", len(E) == (len(V) ** 2) // 4 + 1)

def triangles(vs):
    vs = list(vs)
    return [t for t in itertools.combinations(vs, 3)
            if all(frozenset(p) in E for p in itertools.combinations(t, 2))]
print("is {a,b,c} a triangle?", tuple(T) in [tuple(sorted(t)) for t in triangles(V)] or bool(triangles(T)))
rest = [v for v in V if v not in T]
print("triangles in G - {a,b,c}:", triangles(rest),
      " => {a,b,c} alone is a MAXIMAL system of disjoint triangles, i.e. r = 1?", triangles(rest) == [])
