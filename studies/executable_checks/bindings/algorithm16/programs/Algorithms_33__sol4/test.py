#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_33__sol4.

TARGET CLAIM (from triage, both passes):
  Under the solution's OWN definition of a cut -- "any set E of edges whose removal
  disconnects G (i.e. G-E has more connected components than G)" (lines 0002-0004) --
  the recursive decomposition described in the proof outputs a partition of any cut E
  into pairwise disjoint MINIMAL cuts (bonds) OF G.  Load-bearing sub-claims:
    line 0025: "because F is minimal, removing F splits G into exactly two components"
    line 0043: "G[A] - EA is disconnected.  Hence EA is a cut in the subgraph G[A]"
    line 0051: "a minimal cut in a subgraph like G[A] or G[B] is also a minimal cut in G"

WHAT THIS FILE DOES
  1. FAITHFUL IMPLEMENTATION of the proof's procedure, bugs included:
       - base case |E| = 1  -> emit E as a minimal cut
       - if E is already inclusion-minimal -> emit E
       - else peel edges off E one at a time until an inclusion-minimal cut-subset F
         remains, take the components A, B of G-F, split E\\F into E_A / E_B by
         component, recurse on G[A] with E_A and on G[B] with E_B, emit F plus the
         recursive results.
       The three sub-claims above are checked as ASSERTIONS at exactly the point the
       proof asserts them; a violation is reported, never repaired.
  2. BRUTE-FORCE ORACLE: enumerate every set partition of E and test whether ANY of
     them consists entirely of bonds of G (bond = nonempty cut no proper subset of
     which is a cut).  Exact combinatorics only -- no arithmetic, no floats anywhere.
     Because the oracle is exhaustive over ALL partitions, an oracle answer of "no
     decomposition exists" refutes the theorem for that input regardless of which
     inclusion-minimal F the (nondeterministic) proof would have picked.
  3. SEARCH: exhaustive over every simple graph on n = 3, 4, 5 labelled vertices and
     every edge subset E that is a cut under the solution's definition (input size
     |V| + |E| <= 12 throughout, capped at |E| <= 6 so the partition oracle stays
     exhaustive), plus the two adversarial constructions named in the triage sketches.
  4. DIAGNOSTIC: the same census restricted to connected G and cuts of the standard
     form delta(S) = {uv : u in S, v not in S}, to isolate whether the failure is the
     solution's over-broad definition of "cut" or a flaw in the recursion itself.

Deterministic: no randomness, no sampling, no timing.
"""

from itertools import combinations, chain


# ---------------------------------------------------------------------------
# graph primitives (exact, integer/set arithmetic only)
# ---------------------------------------------------------------------------

def n_components(vertices, edges):
    """Number of connected components of (vertices, edges).  Union-find."""
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = len(vertices)
    for (u, v) in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            count -= 1
    return count


def components(vertices, edges):
    """List of vertex-sets (frozensets) of the connected components."""
    adj = {v: set() for v in vertices}
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    seen = set()
    out = []
    for s in sorted(vertices):
        if s in seen:
            continue
        stack = [s]
        seen.add(s)
        comp = set()
        while stack:
            x = stack.pop()
            comp.add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        out.append(frozenset(comp))
    return out


def induced(vertices, edges, A):
    """Induced subgraph G[A]."""
    return frozenset(A), frozenset(e for e in edges if e[0] in A and e[1] in A)


def is_cut(vertices, edges, S):
    """The SOLUTION'S definition (lines 0002-0004): S disconnects G iff G-S has
    strictly more connected components than G.  (Empty S is never a cut.)"""
    if not S:
        return False
    return n_components(vertices, edges - frozenset(S)) > n_components(vertices, edges)


def is_bond(vertices, edges, S):
    """Minimal cut in the solution's sense (line 0004): S is a cut and no proper
    subset of S is a cut."""
    if not is_cut(vertices, edges, S):
        return False
    S = frozenset(S)
    for k in range(len(S)):
        for sub in combinations(sorted(S), k):
            if is_cut(vertices, edges, frozenset(sub)):
                return False
    return True


def fmt_edges(S):
    return "{" + ",".join(f"{u}{v}" for (u, v) in sorted(S)) + "}"


# ---------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION of the proof's decomposition procedure
# ---------------------------------------------------------------------------

class ProofViolation(Exception):
    """Raised when a step the proof explicitly asserts is false on this input."""

    def __init__(self, line, message):
        super().__init__(f"[line {line}] {message}")
        self.line = line
        self.message = message


def peel_to_inclusion_minimal_cut(vertices, edges, E):
    """Lines 0019-0022: 'remove edges from E one by one until reaching a minimal cut'.
    Deterministic order (sorted).  Peeling terminates at an inclusion-minimal cut
    because cut-ness is upward closed under adding edges to the removal set."""
    F = set(E)
    for e in sorted(E):
        if is_cut(vertices, edges, frozenset(F - {e})):
            F.discard(e)
    return frozenset(F)


def decompose(vertices, edges, E, trace=None, depth=0):
    """The proof's procedure, implemented exactly as written.  Returns the list of
    sets the proof claims are pairwise-disjoint minimal cuts of the ambient graph."""
    if trace is not None:
        trace.append("  " * depth + f"decompose(V={sorted(vertices)}, "
                                    f"|E_G|={len(edges)}, E={fmt_edges(E)})")

    # The proof's inductive hypothesis is applied only to sets it has just argued
    # are cuts of the current graph (lines 0037-0044).  Check that precondition.
    if not is_cut(vertices, edges, E):
        raise ProofViolation(
            "0043",
            f"the recursion was handed E={fmt_edges(E)} on G[{ ''.join(sorted(vertices)) }] "
            f"but G-E is NOT more disconnected than G, so 'E_A is a cut in G[A]' is false")

    # Base case, lines 0009-0012.
    if len(E) == 1:
        if trace is not None:
            trace.append("  " * depth + f"  base case |E|=1 -> emit {fmt_edges(E)}")
        return [frozenset(E)]

    # Case 1, lines 0015-0017.
    if is_bond(vertices, edges, E):
        if trace is not None:
            trace.append("  " * depth + f"  E already minimal -> emit {fmt_edges(E)}")
        return [frozenset(E)]

    # Case 2, lines 0018-0023: choose an inclusion-minimal cut-subset F of E.
    F = peel_to_inclusion_minimal_cut(vertices, edges, E)
    if not (F and F < frozenset(E)):
        raise ProofViolation("0021", "no proper inclusion-minimal cut-subset F of E exists")

    # Line 0024-0027: 'because F is minimal, removing F splits G into exactly two
    # connected components.'
    comps = components(vertices, edges - F)
    base_comps = n_components(vertices, edges)
    if trace is not None:
        trace.append("  " * depth + f"  F={fmt_edges(F)}  ->  components of G-F: "
                     + " ".join("{" + "".join(sorted(c)) + "}" for c in comps))
    if len(comps) != 2:
        raise ProofViolation(
            "0025",
            f"G-F has {len(comps)} components (G had {base_comps}), not the asserted 2")
    A, B = comps

    # Lines 0028-0036: E\F splits into E_A and E_B with nothing left crossing.
    rest = frozenset(E) - F
    EA = frozenset(e for e in rest if e[0] in A and e[1] in A)
    EB = frozenset(e for e in rest if e[0] in B and e[1] in B)
    if len(EA) + len(EB) != len(rest):
        raise ProofViolation("0031", "some edge of E\\F crosses between A and B")

    out = [F]
    for (side, ES) in ((A, EA), (B, EB)):
        if not ES:
            # The proof asserts E_A and E_B are cuts (lines 0037-0044); the empty set
            # is not.  We take the charitable reading (empty union) and continue --
            # this concession can only help the solution.
            continue
        gv, ge = induced(vertices, edges, side)
        out.extend(decompose(gv, ge, ES, trace=trace, depth=depth + 1))
    return out


def all_bond_subsets(vertices, edges, E):
    """Every set F the proof is allowed to pick at line 0019-0022: an inclusion-wise
    minimal cut-subset of E, i.e. every bond of the current graph contained in E."""
    E = sorted(E)
    out = []
    for r in range(1, len(E) + 1):
        for sub in combinations(E, r):
            if is_bond(vertices, edges, frozenset(sub)):
                out.append(frozenset(sub))
    return out


def all_outputs(vertices, edges, E, depth=0):
    """Every list of blocks the proof's procedure could produce, over ALL admissible
    choices of the inclusion-minimal cut-subset F.  Choices that hit an asserted-step
    violation yield nothing (the proof cannot continue there)."""
    if depth > 6 or not is_cut(vertices, edges, E):
        return
    if len(E) == 1 or is_bond(vertices, edges, E):
        yield [frozenset(E)]
        return
    for F in all_bond_subsets(vertices, edges, E):
        if F == frozenset(E):
            continue
        comps = components(vertices, edges - F)
        if len(comps) != 2:
            continue
        A, B = comps
        rest = frozenset(E) - F
        EA = frozenset(e for e in rest if e[0] in A and e[1] in A)
        EB = frozenset(e for e in rest if e[0] in B and e[1] in B)
        if len(EA) + len(EB) != len(rest):
            continue
        tails = [[]]
        ok = True
        for (side, ES) in ((A, EA), (B, EB)):
            if not ES:
                continue
            gv, ge = induced(vertices, edges, side)
            subs = list(all_outputs(gv, ge, ES, depth + 1))
            if not subs:
                ok = False
                break
            tails = [t + s for t in tails for s in subs]
        if ok:
            for t in tails:
                yield [F] + t


def some_choice_works(vertices, edges, E):
    """Is there ANY admissible sequence of F-choices for which the procedure's output
    is a genuine partition of E into bonds of the FULL graph G?"""
    for blocks in all_outputs(vertices, edges, E):
        if not check_impl_output(vertices, edges, E, blocks):
            return blocks
    return None


def run_implementation(vertices, edges, E):
    """Returns (status, payload).  status in {'OK','VIOLATION'}."""
    trace = []
    try:
        blocks = decompose(vertices, edges, E, trace=trace)
        return "OK", (blocks, trace)
    except ProofViolation as exc:
        return "VIOLATION", (str(exc), trace)


# ---------------------------------------------------------------------------
# 2. BRUTE-FORCE ORACLE
# ---------------------------------------------------------------------------

def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]
        yield [[first]] + part


def oracle_decomposition(vertices, edges, E):
    """Exhaustive: return a partition of E all of whose blocks are bonds of G, or None
    if no such partition exists."""
    E = sorted(E)
    for part in set_partitions(E):
        if all(is_bond(vertices, edges, frozenset(b)) for b in part):
            return [frozenset(b) for b in part]
    return None


def check_impl_output(vertices, edges, E, blocks):
    """Does the procedure's output actually satisfy the theorem's conclusion?"""
    problems = []
    seen = set()
    for b in blocks:
        if b & seen:
            problems.append(f"blocks not disjoint at {fmt_edges(b & seen)}")
        seen |= b
    if seen != frozenset(E):
        problems.append(f"union {fmt_edges(seen)} != E {fmt_edges(E)}")
    for b in blocks:
        if not is_cut(vertices, edges, b):
            problems.append(f"{fmt_edges(b)} is NOT a cut of G")
        elif not is_bond(vertices, edges, b):
            problems.append(f"{fmt_edges(b)} is a cut but NOT minimal in G")
    return problems


# ---------------------------------------------------------------------------
# 3. SEARCH
# ---------------------------------------------------------------------------

def all_graphs(n):
    verts = frozenset("abcdefghijkl"[:n])
    possible = sorted(combinations(sorted(verts), 2))
    for r in range(len(possible) + 1):
        for es in combinations(possible, r):
            yield verts, frozenset(es)


def delta(vertices, edges, S):
    return frozenset(e for e in edges if (e[0] in S) != (e[1] in S))


def evaluate(vertices, edges, E, label):
    """Run implementation + oracle on one instance; return a verdict dict."""
    status, payload = run_implementation(vertices, edges, E)
    oracle = oracle_decomposition(vertices, edges, E)
    rec = {"label": label, "V": sorted(vertices), "E_G": sorted(edges),
           "E": sorted(E), "status": status, "oracle": oracle}
    if status == "OK":
        blocks, trace = payload
        rec["blocks"] = blocks
        rec["trace"] = trace
        rec["problems"] = check_impl_output(vertices, edges, E, blocks)
    else:
        rec["reason"], rec["trace"] = payload
        rec["problems"] = [rec["reason"]]
    rec["bad"] = bool(rec["problems"]) or oracle is None
    return rec


def describe(rec):
    lines = []
    lines.append(f"    graph  V = {{{','.join(rec['V'])}}}   "
                 f"E(G) = {fmt_edges(rec['E_G'])}")
    lines.append(f"    cut    E = {fmt_edges(rec['E'])}   "
                 f"(G-E has more components than G: cut under the solution's def.)")
    if rec["status"] == "OK":
        lines.append("    procedure output: " +
                     " | ".join(fmt_edges(b) for b in rec["blocks"]))
    else:
        lines.append(f"    procedure ABORTED: {rec['reason']}")
    for t in rec["trace"]:
        lines.append("      " + t)
    for p in rec["problems"]:
        lines.append(f"    DEFECT: {p}")
    if rec["oracle"] is None:
        lines.append("    ORACLE (exhaustive over all set partitions of E): "
                     "NO partition of E into minimal cuts of G exists at all")
    else:
        lines.append("    ORACLE: a valid decomposition does exist: " +
                     " | ".join(fmt_edges(b) for b in rec["oracle"]))
    return lines


def main():
    print("=" * 78)
    print("Algorithms_33__sol4  --  blind test-search")
    print("claim kind: CORRECTNESS")
    print("=" * 78)

    # ---------------- adversarial constructions from the triage sketches ----------
    print()
    print("A. ADVERSARIAL CONSTRUCTIONS NAMED IN THE TRIAGE SKETCHES")
    print()

    adversarial = []

    V3 = frozenset("abc")
    K3 = frozenset([("a", "b"), ("b", "c"), ("a", "c")])
    adversarial.append(("pass-1 sketch: K3 with E = all three edges",
                        V3, K3, K3))

    V4 = frozenset("abcd")
    G4 = frozenset([("a", "b"), ("b", "c"), ("a", "c"), ("a", "d")])
    adversarial.append(("pass-0 sketch: triangle abc + pendant d, E = {ad, ab}",
                        V4, G4, frozenset([("a", "d"), ("a", "b")])))

    # Found by the exhaustive census below: a STANDARD cut delta(S) in a connected
    # graph, i.e. an instance where the theorem itself is unambiguously true.
    C4 = frozenset([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    adversarial.append(("census find: 4-cycle a-b-d-c-a, E = delta({b,c}) = all 4 edges "
                        "(a STANDARD cut, theorem true here)",
                        frozenset("abcd"), C4, C4))

    adv_recs = []
    for label, V, EG, E in adversarial:
        rec = evaluate(V, EG, E, label)
        adv_recs.append(rec)
        print(f"  {label}")
        for line in describe(rec):
            print(line)
        print(f"    VERDICT: {'COUNTEREXAMPLE' if rec['bad'] else 'consistent'}")
        print()

    # ---------------- exhaustive census -----------------------------------------
    print("B. EXHAUSTIVE CENSUS over all simple graphs on n = 3,4,5 labelled vertices")
    print("   and every cut E with |E| <= 6   (input size |V|+|E(G)| <= 15, |E| <= 6)")
    print()

    total = 0
    bad_total = 0
    bad_by_kind = {}
    smallest = None
    oracle_empty = 0
    std_total = 0
    std_bad = 0
    std_smallest = None

    for n in (3, 4, 5):
        n_total = n_bad = 0
        for V, EG in all_graphs(n):
            edge_list = sorted(EG)
            for r in range(1, min(len(edge_list), 6) + 1):
                for sub in combinations(edge_list, r):
                    E = frozenset(sub)
                    if not is_cut(V, EG, E):
                        continue
                    rec = evaluate(V, EG, E, f"n={n}")
                    total += 1
                    n_total += 1
                    if rec["bad"]:
                        bad_total += 1
                        n_bad += 1
                        if rec["oracle"] is None:
                            oracle_empty += 1
                        if rec["status"] != "OK":
                            kind = ("procedure aborted: " +
                                    rec["reason"].split("]")[0] + "] " +
                                    ("'E_A is a cut in G[A]' (line 0043) is false"
                                     if "0043" in rec["reason"]
                                     else rec["reason"].split("] ")[1][:60]))
                        elif any("NOT a cut of G" in p for p in rec["problems"]):
                            kind = ("output block is not even a cut of G "
                                    "(line-0051 lifting step false)")
                        elif any("NOT minimal" in p for p in rec["problems"]):
                            kind = "output block is a cut of G but not minimal"
                        else:
                            kind = ("procedure output is fine but NO decomposition "
                                    "into bonds exists (theorem false)")
                        bad_by_kind[kind] = bad_by_kind.get(kind, 0) + 1
                        size = (len(V), len(EG), len(E))
                        if smallest is None or size < smallest[0]:
                            smallest = (size, rec)
                    # diagnostic: standard-definition cuts delta(S) in connected G
                    if n_components(V, EG) == 1:
                        vs = sorted(V)
                        for m in range(1, 2 ** (len(vs) - 1)):
                            S = frozenset(vs[i] for i in range(len(vs)) if m >> i & 1)
                            if delta(V, EG, S) == E:
                                std_total += 1
                                if rec["bad"]:
                                    std_bad += 1
                                    size = (len(V), len(EG), len(E))
                                    if std_smallest is None or size < std_smallest[0]:
                                        std_smallest = (size, rec, sorted(S))
                                break
        print(f"   n = {n}: {n_total:6d} (graph, cut) instances tested, "
              f"{n_bad:6d} refute the claim")

    print()
    print(f"   TOTAL: {total} instances, {bad_total} counterexamples "
          f"({oracle_empty} of them have NO valid decomposition at all)")
    print("   failure modes:")
    for k, v in sorted(bad_by_kind.items(), key=lambda kv: -kv[1]):
        print(f"     {v:6d} x  {k}")

    print()
    print("C. DIAGNOSTIC: same procedure restricted to CONNECTED G and cuts of the")
    print("   standard form delta(S) = {uv : u in S, v not in S}, i.e. the reading")
    print("   under which the problem's statement is actually TRUE")
    print(f"   {std_total} such instances tested, {std_bad} counterexamples")
    if std_bad == 0:
        print("   -> procedure sound for standard cuts; the defect is the solution's")
        print("      OWN over-broad definition of 'cut' (line 0003).")
    else:
        print("   -> the procedure is UNSOUND even for standard cuts delta(S), where")
        print("      the theorem itself is true.  Smallest such instance:")
        size, rec, S = std_smallest
        print(f"      S = {{{','.join(S)}}}")
        for line in describe(rec):
            print("  " + line)

    # ---------------- choice robustness -----------------------------------------
    print()
    print("D. CHOICE ROBUSTNESS.  The proof's F is a nondeterministic choice ('choose")
    print("   one that is inclusion-wise minimal'), so we re-run each adversarial")
    print("   instance over EVERY admissible sequence of F-choices and ask whether any")
    print("   of them yields a genuine partition of E into bonds of the full graph G.")
    print()
    for label, V, EG, E in adversarial:
        witness = some_choice_works(V, EG, E)
        n_out = len(list(all_outputs(V, EG, E)))
        print(f"   {label}")
        print(f"     {n_out} distinct procedure outputs over all F-choices; "
              f"valid ones: {'NONE' if witness is None else fmt_edges(witness[0])}")

    # ---------------- verdict ----------------------------------------------------
    print()
    print("=" * 78)
    if bad_total == 0 and not any(r["bad"] for r in adv_recs):
        print("VERDICT: NO_BUG_FOUND")
    else:
        print("VERDICT: BUG_FOUND")
        print()
        print("SMALLEST COUNTEREXAMPLE FOUND BY THE EXHAUSTIVE SEARCH")
        if smallest:
            for line in describe(smallest[1]):
                print(line)
        print()
        print("HEADLINE FAILING INPUT (strongest: a STANDARD cut, theorem true there)")
        r = adv_recs[2]
        print("  G = 4-cycle a-b-d-c-a, E(G) = {ab,ac,bd,cd}; S = {b,c};")
        print("  E = delta(S) = {ab,ac,bd,cd} (all four edges) -- a cut on ANY reading.")
        print("  Procedure output: " + " | ".join(fmt_edges(b) for b in r["blocks"]))
        print("  Observed: blocks {ac} and {ab} are emitted as 'minimal cuts of G', but")
        print("            C4 minus a single edge is still connected, so neither is a cut")
        print("            of G at all -- the line-0051 lifting step is FALSE: {ac} is a")
        print("            bond of G[A] = G[{a,b,c}] only because the a-c reconnection")
        print("            through d was deleted along with F, and it comes back in G.")
        print("  Claimed:  'a minimal cut in a subgraph like G[A] ... is also a minimal")
        print("            cut in the entire graph G' (line 0051).")
        print("  Oracle:   a correct decomposition does exist here -- delta({a}) = {ab,ac}")
        print("            and delta({d}) = {bd,cd} -- so the procedure, not the theorem,")
        print("            is what fails; and no admissible F-choice repairs it (section D).")
        print()
        print("SECONDARY: the solution's own DEFINITION of cut (line 0003, 'more")
        print("  components than G') makes the theorem itself false: on K3 with")
        print("  E = {ab,bc,ca} the oracle shows NO partition of E into bonds exists.")
    print("=" * 78)


if __name__ == "__main__":
    main()
