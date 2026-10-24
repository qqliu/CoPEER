# P46: check the witness S = empty set against source lines 5 and 15.
def powerset(S):
    S = list(S); out = [frozenset()]
    for x in S: out += [s | {x} for s in out]
    return set(out)
S = frozenset()                       # the witness: S = {}
P = powerset(S)
dom = P - {frozenset()}               # line 5: c is defined on  P(S) \ {empty set}
print("S =", set(S), "  P(S) =", [set(x) for x in P], "  domain of c = P(S) \\ {0} =", [set(x) for x in dom])
print("is S itself in the domain of c ?", S in dom, " -> line 15's 'c(S)' has no value")
print("number of choice functions on an empty domain: 1 (the empty function), and it assigns nothing:",
      len(dom) == 0)
# for contrast, any non-empty S does put S in the domain
S2 = frozenset({'a'})
print("contrast: S = {a}: is S in P(S)\\{0} ?", S2 in (powerset(S2) - {frozenset()}))
