# P16: the response's witness, checked exactly.
# G: V={a,b,c,d,e}, E={ab, cd, ac, ae};  S={a,b}, T={c,d,e}
V = set("abcde")
E = [frozenset(x) for x in ("ab", "cd", "ac", "ae")]
S, T = {"a", "b"}, {"c", "d", "e"}
print("S,T partition V and are non-empty?", bool(S | T == V and not (S & T) and S and T))

def components(W):                       # components of the induced subgraph G[W]
    W, out = set(W), []
    while W:
        v = W.pop(); comp, stack = {v}, [v]
        while stack:
            x = stack.pop()
            for e in E:
                if x in e:
                    y = next(iter(e - {x})) if len(e) == 2 else x
                    if y in W:
                        W.discard(y); comp.add(y); stack.append(y)
        out.append(comp)
    return out

Scomp, Tcomp = components(S), components(T)
print("components of G[S]:", Scomp, " components of G[T]:", Tcomp)

def cross(A, B): return {e for e in E if len(e & A) == 1 and len(e & B) == 1}

S1 = [c for c in Scomp if "a" in c][0]
T1 = [c for c in Tcomp if "c" in c][0]
T2 = [c for c in Tcomp if "e" in c][0]
C   = cross(S, T)                        # the cut delta(S), Definition 1
C11 = cross(S1, T1)                      # line 24
C12 = cross(S1, T2)
dS1 = cross(S1, V - S1)                  # delta(S_i) for the partition V = S1 + (V\S1), line 37
def show(s): return sorted("".join(sorted(e)) for e in s)
print("C = delta(S) =", show(C), " C11 =", show(C11), " C12 =", show(C12), " delta(S1) =", show(dS1))
print("C11 non-empty (hypothesis of line 35)?", bool(C11))
print("line 35's identity  C11 == delta(S1) ?", C11 == dS1, "   proper subset?", C11 < dS1)
