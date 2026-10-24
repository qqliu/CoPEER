# P46: check the supplied witness for line 15 ("Let s_0 = c(S)"):
# "If S = 0 (empty), then P(S) \ {0} = 0, the only choice function is the empty function, which does
#  not assign a value to 0; hence s_0 = c(S) cannot be formed."
# Line 5 fixes the domain of c: "a choice function c defined on P(S) \ {0}".
from itertools import combinations

def powerset(S):
    S = list(S)
    return {frozenset(c) for r in range(len(S) + 1) for c in combinations(S, r)}

for S in [frozenset(), frozenset({'a'}), frozenset({'a', 'b'})]:
    P = powerset(S)
    dom = P - {frozenset()}                      # P(S) \ {empty set}, the domain of c per line 5
    print("S =", set(S) or "{}",
          " |P(S)| =", len(P),
          " domain of c = P(S)\\{0} has", len(dom), "elements",
          " is S itself in dom(c)?", S in dom,
          " so c(S) defined?", S in dom)

print()
print("witness S = {}: dom(c) is empty, the only such function is the empty function,")
print("and S = {} is not in its domain, so the term c(S) of line 15 has no value.")
print("number of choice functions on an empty domain:", 1, "(the empty function)")
print("value they assign to the empty set:", "none")
