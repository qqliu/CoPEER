#!/usr/bin/env python3
"""
Blind test-search for record Algorithms_11__sol1.

Target claim (from triage, lines 0061-0084 of the solution):
  "At every departure, the bank left behind is independent (either I with one
   fewer element, or a singleton {x}), so the safety constraint holds
   throughout by Lemma 1."
  and the resulting equivalence (1):
   G has a vertex cover of size <= K  <=>  river crossing instance (G, k=K+1)
   is feasible.

Contents:
  (A) FAITHFUL IMPLEMENTATION of the solution's explicit four-move schedule
      (Steps 1-4 of lines 0061-0074, repeated |I| times, then a final S-trip;
       plus the S = empty special case of lines 0054-0057). Bank contents are
      derived truthfully from the moves the solution prescribes; the only
      thing added is the safety audit the solution claims always passes.
  (B) BRUTE-FORCE ORACLE: exhaustive BFS over the full state space
      (left-bank subset, Charon's side) deciding real feasibility.
      Exact/discrete only -- sets and ints, no floats anywhere.
  (C) SEARCH: exhaustive over all labelled graphs on n <= 5 vertices and all
      capacities, plus adversarial families (paths, stars) up to n = 12.

Everything is deterministic; no randomness, no wall-clock, no floats.
"""

from itertools import combinations, chain, permutations

# ----------------------------------------------------------------------
# graph helpers (exact, set-based)
# ----------------------------------------------------------------------

def is_independent(vertices, edges):
    vs = set(vertices)
    for (u, v) in edges:
        if u in vs and v in vs:
            return False
    return True


def all_subsets(s, max_size=None):
    """All subsets of s of size <= max_size (all sizes if max_size is None)."""
    s = sorted(s)
    hi = len(s) if max_size is None else min(len(s), max_size)
    for r in range(hi + 1):
        for c in combinations(s, r):
            yield frozenset(c)


def min_vertex_cover_size(n, edges):
    """Exact tau(G) by exhaustive search over all subsets (n <= 12)."""
    V = list(range(n))
    for size in range(n + 1):
        for c in combinations(V, size):
            cs = set(c)
            if all((u in cs) or (v in cs) for (u, v) in edges):
                return size
    return n


def a_vertex_cover_of_size_at_most(n, edges, K):
    """Lexicographically first vertex cover of size <= K, or None."""
    V = list(range(n))
    for size in range(K + 1):
        for c in combinations(V, size):
            cs = set(c)
            if all((u in cs) or (v in cs) for (u, v) in edges):
                return frozenset(c)
    return None


# ----------------------------------------------------------------------
# (A) FAITHFUL IMPLEMENTATION of the solution's constructed schedule
# ----------------------------------------------------------------------

class SafetyViolation(Exception):
    pass


class CapacityViolation(Exception):
    pass


class Ferry:
    """Simulator of the river-crossing process.

    State: set of passengers on left bank, set on right bank, Charon's side.
    A move: Charon crosses with a set T of passengers (|T| <= k-1) from his
    current side.  Immediately after departure, the bank he left must be
    independent (Lemma 1); the bank he is heading to is unattended for the
    whole trip, and its contents do not change during the trip, so its
    independence was already enforced when he last departed from it -- but we
    re-check it anyway at departure time, which is exactly the condition the
    solution claims holds.
    """

    def __init__(self, n, edges, k, audit=True):
        self.n = n
        self.edges = edges
        self.k = k
        self.left = set(range(n))
        self.right = set()
        self.charon = 'L'
        self.log = []
        self.audit = audit

    def bank(self, side):
        return self.left if side == 'L' else self.right

    def cross(self, T, label=""):
        T = set(T)
        src = self.charon
        dst = 'R' if src == 'L' else 'L'
        srcbank = self.bank(src)
        if not T <= srcbank:
            raise CapacityViolation(
                "%s: passengers %s not on bank %s (bank=%s)"
                % (label, sorted(T), src, sorted(srcbank)))
        if len(T) > self.k - 1:
            raise CapacityViolation(
                "%s: boat carries %d passengers > k-1 = %d"
                % (label, len(T), self.k - 1))
        srcbank -= T
        self.bank(dst).update(T)
        self.charon = dst
        self.log.append((label, src, dst, tuple(sorted(T)),
                         tuple(sorted(self.left)), tuple(sorted(self.right))))
        if self.audit:
            left_behind = self.bank(src)
            if not is_independent(left_behind, self.edges):
                bad = [(u, v) for (u, v) in self.edges
                       if u in left_behind and v in left_behind]
                raise SafetyViolation(
                    "%s: Charon departed bank %s -> %s carrying %s, leaving "
                    "unattended set %s on %s which contains enemy edge(s) %s"
                    % (label, src, dst, sorted(T), sorted(left_behind),
                       src, bad))

    def done(self):
        return len(self.left) == 0


def run_solution_schedule(n, edges, k, S, j=None, I_order=None, audit=True):
    """Run EXACTLY the schedule the solution constructs.

    S: the vertex cover with |S| <= k-1 (lines 0051).
    Lines 0054-0057: if S is empty, shuttle <= k-1 passengers at a time.
    Lines 0058-0078: otherwise fix j in S, repeat the four-move cycle |I|
    times (each cycle permanently moves one x in I), then a final L->R trip
    carrying all of S.

    Returns (status, detail) with status in {"OK", "SAFETY", "CAPACITY",
    "NOT_ALL_ACROSS"}.
    """
    S = frozenset(S)
    I = sorted(set(range(n)) - S)
    if I_order is not None:
        I = list(I_order)
    f = Ferry(n, edges, k, audit=audit)
    try:
        if not S:
            # Lines 0054-0057: trivial shuttling.
            if k <= 1 and n > 0:
                # k-1 = 0 passengers per trip: the described shuttle never
                # terminates.  (The solution restricts (1) to K >= 1, i.e.
                # k >= 2, and treats K = 0 by a separate mapping, so this is
                # outside its claimed range; we simply report it.)
                return "NOT_ALL_ACROSS", ("k=1: boat carries 0 passengers, "
                                          "the described shuttle cannot move "
                                          "anyone")
            remaining = sorted(f.left)
            while remaining:
                batch = remaining[:k - 1]
                remaining = remaining[k - 1:]
                f.cross(batch, "shuttle L->R")
                if remaining:
                    f.cross([], "shuttle return R->L")
        else:
            jj = min(S) if j is None else j          # "fix any vertex j in S"
            for idx, x in enumerate(I):
                c = "cycle%d " % (idx + 1)
                # Step 1 (L->R): Charon takes the entire S to the right bank.
                f.cross(S, c + "Step1 L->R takes S=%s" % sorted(S))
                # Step 2 (R->L): Charon returns with S\J, leaving J={j} on R.
                f.cross(S - {jj},
                        c + "Step2 R->L takes S\\{j}=%s (leaves j=%d on R)"
                        % (sorted(S - {jj}), jj))
                # Step 3 (L->R): Charon takes S\J together with one x in I.
                f.cross((S - {jj}) | {x},
                        c + "Step3 L->R takes S\\{j} + x=%d" % x)
                # Step 4 (R->L): Charon returns with the entire S.
                f.cross(S, c + "Step4 R->L takes S=%s" % sorted(S))
            # Final trip L->R with all of S (line 0078).
            f.cross(S, "final L->R takes S=%s" % sorted(S))
    except SafetyViolation as e:
        return "SAFETY", str(e)
    except CapacityViolation as e:
        return "CAPACITY", str(e)
    if not f.done():
        return "NOT_ALL_ACROSS", "left bank still holds %s" % sorted(f.left)
    return "OK", ""


def schedule_safe_for_some_instantiation(n, edges, k, S, max_perms=5040):
    """Charitable variant: is the schedule safe for SOME choice of j in S and
    SOME order of I?  (The proof claims safety for arbitrary choices, but this
    tells us whether any repair-by-reordering exists.)"""
    S = frozenset(S)
    I = sorted(set(range(n)) - S)
    if not S:
        return run_solution_schedule(n, edges, k, S)[0] == "OK"
    perms = list(permutations(I)) if len(I) <= 7 else [tuple(I)]
    for jj in sorted(S):
        for p in perms[:max_perms]:
            if run_solution_schedule(n, edges, k, S, j=jj,
                                     I_order=list(p))[0] == "OK":
                return True
    return False


# ----------------------------------------------------------------------
# (B) BRUTE-FORCE ORACLE: exhaustive BFS feasibility
# ----------------------------------------------------------------------

def feasible_bruteforce(n, edges, k):
    """True iff SOME sequence of crossings gets all n passengers to the right
    bank, respecting capacity (<= k-1 passengers per trip) and the safety rule
    (the bank without Charon induces an independent set).

    Exhaustive BFS over the <= 2 * 2^n states.  Exact; no heuristics.
    """
    if k < 1:
        return False
    V = frozenset(range(n))
    cap = k - 1
    indep_cache = {}

    def indep(fs):
        r = indep_cache.get(fs)
        if r is None:
            r = is_independent(fs, edges)
            indep_cache[fs] = r
        return r

    start = (V, 'L')          # (left-bank set, Charon's side)
    if not indep(frozenset()):    # vacuously true; kept for symmetry
        return False
    seen = {start}
    frontier = [start]
    while frontier:
        nxt = []
        for (left, side) in frontier:
            right = V - left
            here = left if side == 'L' else right
            for T in all_subsets(here, cap):
                if side == 'L':
                    nleft, nright, nside = left - T, right | T, 'R'
                    departed = nleft
                else:
                    nleft, nright, nside = left | T, right - T, 'L'
                    departed = nright
                if not indep(frozenset(departed)):
                    continue
                if len(nleft) == 0:
                    return True
                st = (frozenset(nleft), nside)
                if st not in seen:
                    seen.add(st)
                    nxt.append(st)
        frontier = nxt
    return len(V) == 0


# ----------------------------------------------------------------------
# (C) SEARCH
# ----------------------------------------------------------------------

def all_graphs(n):
    """All labelled simple graphs on n vertices, as edge tuples."""
    pairs = list(combinations(range(n), 2))
    for r in range(len(pairs) + 1):
        for c in combinations(pairs, r):
            yield tuple(c)


def graph_name(n, edges):
    return "n=%d edges=%s" % (n, sorted(edges))


def check_instance(n, edges, K, charitable=True):
    """Return dict of findings for a single (G, K) pair, k = K+1.

    charitable: also test whether SOME choice of j / order of I makes the
    schedule safe (expensive; used on the named adversarial inputs and on the
    smallest counterexamples, not on every instance of the exhaustive sweep).
    """
    k = K + 1
    tau = min_vertex_cover_size(n, edges)
    vc_yes = (tau <= K)
    feas = feasible_bruteforce(n, edges, k)
    out = {"n": n, "edges": tuple(sorted(edges)), "K": K, "k": k,
           "tau": tau, "vc_yes": vc_yes, "feasible": feas,
           "equiv_holds": (vc_yes == feas),
           "sched_status": None, "sched_detail": "",
           "sched_any_instantiation_safe": None}
    if vc_yes:
        S = a_vertex_cover_of_size_at_most(n, edges, K)
        status, detail = run_solution_schedule(n, edges, k, S)
        out["S"] = tuple(sorted(S))
        out["sched_status"] = status
        out["sched_detail"] = detail
        if status != "OK" and charitable:
            out["sched_any_instantiation_safe"] = \
                schedule_safe_for_some_instantiation(n, edges, k, S)
    return out


def path_graph(n):
    return tuple((i, i + 1) for i in range(n - 1))


def star_graph(n):
    return tuple((0, i) for i in range(1, n))


def main():
    print("=" * 78)
    print("record_id: Algorithms_11__sol1")
    print("TARGET CLAIM: the explicitly constructed four-move schedule keeps")
    print("every Charon-free bank independent, hence")
    print("   tau(G) <= K   <=>   river-crossing instance (G, k=K+1) feasible")
    print("=" * 78)

    # ---------------- Part 1: the triage's named adversarial inputs --------
    print()
    print("--- Part 1: adversarial constructions from the triage sketch ---")
    for label, n, edges, K in [
        ("path a-b-c", 3, path_graph(3), 1),
        ("star K_{1,3}", 4, star_graph(4), 1),
        ("star K_{1,4}", 5, star_graph(5), 1),
    ]:
        r = check_instance(n, edges, K)
        print()
        print("[%s]  %s, K=%d, k=%d" % (label, graph_name(n, edges), K, r["k"]))
        print("  tau(G) = %d  -> vertex cover of size <= K exists: %s"
              % (r["tau"], r["vc_yes"]))
        print("  S chosen by the construction: %s" % (r.get("S"),))
        print("  solution's schedule verdict : %s" % r["sched_status"])
        if r["sched_detail"]:
            print("    %s" % r["sched_detail"])
        if r["sched_any_instantiation_safe"] is not None:
            print("  safe for ANY choice of j / order of I? %s"
                  % r["sched_any_instantiation_safe"])
        print("  brute-force oracle: instance actually feasible? %s"
              % r["feasible"])
        print("  equivalence (1) holds on this instance? %s" % r["equiv_holds"])

    # Show the full move log for the smallest failing case.
    print()
    print("--- Move-by-move log of the constructed schedule on the star "
          "K_{1,3}, k=2 (S={0}, I={1,2,3}) ---")
    n, edges, k = 4, star_graph(4), 2
    f = Ferry(n, edges, k, audit=False)
    S = frozenset({0})
    jj = 0
    for idx, x in enumerate([1, 2, 3]):
        c = "cycle%d " % (idx + 1)
        f.cross(S, c + "Step1 L->R (S)")
        f.cross(S - {jj}, c + "Step2 R->L (S\\{j})")
        f.cross((S - {jj}) | {x}, c + "Step3 L->R (S\\{j} + x=%d)" % x)
        f.cross(S, c + "Step4 R->L (S)")
    for entry in f.log:
        lbl, src, dst, T, L, R = entry
        left_behind = L if src == 'L' else R
        bad = [(u, v) for (u, v) in edges
               if u in left_behind and v in left_behind]
        print("  %-34s %s->%s boat=%s  L=%s R=%s   unattended %s=%s %s"
              % (lbl, src, dst, list(T), list(L), list(R), src,
                 list(left_behind),
                 ("<-- ENEMY EDGE %s UNSUPERVISED" % bad) if bad else ""))

    # ---------------- Part 2: exhaustive over all graphs n <= 5 -----------
    print()
    print("--- Part 2: exhaustive search over ALL labelled graphs, "
          "n = 1..5, K = 1..n ---")
    print("    (K >= 1 is exactly the range for which the solution asserts "
          "equivalence (1); K = 0 is handled by its separate remark.)")
    sched_fails = []
    equiv_fails = []
    total = 0
    for n in range(1, 6):
        for edges in all_graphs(n):
            for K in range(1, n + 1):
                total += 1
                r = check_instance(n, edges, K, charitable=False)
                if r["sched_status"] not in (None, "OK"):
                    sched_fails.append(r)
                if not r["equiv_holds"]:
                    equiv_fails.append(r)
    print("  instances checked: %d" % total)
    print("  instances where the CONSTRUCTED SCHEDULE is unsafe/invalid: %d"
          % len(sched_fails))
    print("  instances where EQUIVALENCE (1) itself fails: %d"
          % len(equiv_fails))

    def show(rs, title, limit=6):
        print("  %s (first %d):" % (title, min(limit, len(rs))))
        for r in rs[:limit]:
            print("    n=%d edges=%s K=%d k=%d tau=%d vc_yes=%s feasible=%s "
                  "sched=%s" % (r["n"], list(r["edges"]), r["K"], r["k"],
                                r["tau"], r["vc_yes"], r["feasible"],
                                r["sched_status"]))
            if r["sched_detail"]:
                print("        %s" % r["sched_detail"])

    if sched_fails:
        show(sched_fails, "smallest schedule failures")
        smallest = min(sched_fails, key=lambda r: (r["n"], len(r["edges"])))
        print("  SMALLEST schedule counterexample: n=%d edges=%s K=%d k=%d "
              "(safe for SOME j/order? %s)"
              % (smallest["n"], list(smallest["edges"]), smallest["K"],
                 smallest["k"],
                 schedule_safe_for_some_instantiation(
                     smallest["n"], smallest["edges"], smallest["k"],
                     smallest["S"])))
    if equiv_fails:
        d1 = [r for r in equiv_fails if r["vc_yes"] and not r["feasible"]]
        d2 = [r for r in equiv_fails if r["feasible"] and not r["vc_yes"]]
        print("    direction (<=) fails (tau<=K but INFEASIBLE): %d instances"
              % len(d1))
        print("    direction (=>) fails (feasible but tau>K):    %d instances"
              % len(d2))
        show(equiv_fails, "equivalence-(1) failures")
        smallest_e = min(equiv_fails, key=lambda r: (r["n"], len(r["edges"])))
        print("  SMALLEST equivalence counterexample: n=%d edges=%s K=%d k=%d "
              "tau=%d vc_yes=%s feasible=%s"
              % (smallest_e["n"], list(smallest_e["edges"]), smallest_e["K"],
                 smallest_e["k"], smallest_e["tau"], smallest_e["vc_yes"],
                 smallest_e["feasible"]))

    # ---------------- Part 3: adversarial families up to n = 12 -----------
    print()
    print("--- Part 3: adversarial families, n up to 12 ---")
    print("  stars K_{1,m} with K = 1, k = 2 (tau = 1 <= K always):")
    for n in range(3, 13):
        edges = star_graph(n)
        tau = min_vertex_cover_size(n, edges)
        S = a_vertex_cover_of_size_at_most(n, edges, 1)
        status, detail = run_solution_schedule(n, edges, 2, S)
        feas = feasible_bruteforce(n, edges, 2)
        print("    n=%2d tau=%d vc_yes=True  schedule=%-8s feasible=%-5s "
              "equivalence=%s" % (n, tau, status, feas,
                                  "HOLDS" if feas else "FAILS"))
    print("  paths P_n with K = tau(P_n), k = K+1:")
    for n in range(3, 13):
        edges = path_graph(n)
        tau = min_vertex_cover_size(n, edges)
        K = tau
        S = a_vertex_cover_of_size_at_most(n, edges, K)
        status, detail = run_solution_schedule(n, edges, K + 1, S)
        feas = feasible_bruteforce(n, edges, K + 1)
        print("    n=%2d tau=%d K=%d k=%d schedule=%-8s feasible=%-5s "
              "equivalence=%s" % (n, tau, K, K + 1, status, feas,
                                  "HOLDS" if feas else "FAILS"))

    # ---------------- verdict --------------------------------------------
    print()
    print("=" * 78)
    if sched_fails or equiv_fails:
        print("VERDICT: BUG_FOUND")
        if sched_fails:
            s = min(sched_fails, key=lambda r: (r["n"], len(r["edges"])))
            print("  (a) The constructed four-move schedule VIOLATES the "
                  "safety invariant it claims to maintain.")
            print("      Smallest failing input: n=%d, edges=%s, K=%d, k=%d, "
                  "S=%s"
                  % (s["n"], list(s["edges"]), s["K"], s["k"],
                     list(s.get("S", ()))))
            pab = check_instance(3, path_graph(3), 1)
            print("      Triage's named input (path a-b-c, K=1, k=2, S={b}): "
                  "schedule=%s, safe for ANY j/order=%s, instance actually "
                  "feasible=%s"
                  % (pab["sched_status"],
                     pab["sched_any_instantiation_safe"], pab["feasible"]))
            st = check_instance(4, star_graph(4), 1)
            print("      Star K_{1,3} (K=1, k=2, S={center}): schedule=%s, "
                  "safe for ANY j/order=%s, instance actually feasible=%s"
                  % (st["sched_status"],
                     st["sched_any_instantiation_safe"], st["feasible"]))
            print("      %s" % s["sched_detail"])
        if equiv_fails:
            e = min(equiv_fails, key=lambda r: (r["n"], len(r["edges"])))
            print("  (b) Equivalence (1) itself is FALSE: n=%d edges=%s K=%d "
                  "k=%d has tau=%d <= K yet the instance is INFEASIBLE "
                  "(brute-force BFS over the whole state space)."
                  % (e["n"], list(e["edges"]), e["K"], e["k"], e["tau"]))
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    main()
