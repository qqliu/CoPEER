# P48: the response's witness G = claw K_{1,3} against line 127 ("G KK-free => B(G) triangle-free"),
# using the source's own definitions: line 47 (KK = 4 vertices, 5 edges), line 85 (e ~ e' iff the
# endpoints of e,e' span a clique), line 123 (B(G): vertices the ~-classes, joined when they meet).
from itertools import combinations

def analyse(name, V, E):
    E = [frozenset(e) for e in E]
    adj = lambda u, v: frozenset((u, v)) in E
    def induces_clique(S):
        return all(adj(u, v) for u, v in combinations(S, 2))
    # KK-freeness: some 4 vertices inducing exactly 5 edges
    kk = [S for S in combinations(V, 4)
          if sum(1 for u, v in combinations(S, 2) if adj(u, v)) == 5]
    # ~ and its classes
    rel = {(e, f) for e in E for f in E if induces_clique(set(e) | set(f))}
    classes = []
    for e in E:
        for c in classes:
            if (e, c[0]) in rel: c.append(e); break
        else:
            classes.append([e])
    spans = [frozenset().union(*c) for c in classes]     # the clique spanned by each class
    Bedges = [(i, j) for i, j in combinations(range(len(spans)), 2) if spans[i] & spans[j]]
    tri = [T for T in combinations(range(len(spans)), 3)
           if all((min(x, y), max(x, y)) in Bedges for x, y in combinations(T, 2))]
    print(name, " E =", [sorted(e) for e in E])
    print("   KK-free (no 4 vertices with 5 edges)?", not kk, kk if kk else "")
    print("   ~ is an equivalence relation on E?",
          all(((e, f) in rel) == ((f, e) in rel) for e in E for f in E) and all((e, e) in rel for e in E))
    print("   ~ classes (as spanned vertex sets):", [sorted(s) for s in spans])
    print("   B(G): edges between classes =", Bedges, "  triangles in B(G) =", tri)
    print("   B(G) triangle-free (what line 127 claims)?", not tri)

analyse("claw K_{1,3}", ["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("a", "d")])
analyse("triangle K_3 ", ["a", "b", "c"], [("a", "b"), ("b", "c"), ("a", "c")])
analyse("4-cycle C_4  ", ["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d"), ("a", "d")])
