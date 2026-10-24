#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_11__sol4.

TARGET CLAIM (CORRECTNESS), quoted from the solution (lines 0103-0105):

    "This procedure produces a valid sequence of crossings using boat capacity k = K + 1.
     At every point, the bank without Charon holds either an independent set of H's vertices
     or is empty."

i.e. the explicit (<=)-direction schedule -- Initial Trip carrying all of C, then K
"Cover Delivery Rounds" (Trip A: carry C\\{c_i} right->left; Trip B: carry C\\{c_i}
left->right), then a Final Stage in which "Charon can return empty (or with some
non-conflicting passenger) to the left bank, then load up to K passengers from L1 and
ferry them to the right bank", repeated until L1 is exhausted -- is asserted to be a
*valid* (safety-respecting) crossing sequence.

WHAT THIS FILE CONTAINS
  1. FAITHFUL IMPLEMENTATION of the solution's schedule generator, exactly as written
     (including its bugs).  It emits the trip list; the solution asserts that list is valid.
  2. ORACLE #1: an exact simulator that replays any trip list and checks, at every moment,
     the problem's safety condition ("no pair of enemies may be present together on either
     riverbank unless Charon is also present at that location"), plus capacity/possession
     legality and the goal condition (all n passengers on the right bank at the end).
  3. ORACLE #2: an exhaustive BFS over the full state space of the river-crossing instance,
     which decides *exactly* whether a valid crossing sequence exists.  This separates
     "the schedule is broken" from "the decision answer is wrong".
  4. A SEARCH over all graphs on n = 4, 5, 6 vertices (all 2^C(n,2) edge sets, with at
     least one edge), taking K := size of a minimum vertex cover of H and k := K + 1 as
     the reduction prescribes, plus the adversarial constructions from the triage sketch
     (P4, K3, K4, K5).
  5. A GENEROUS VARIANT of the Final Stage that tries *every* legal return load (covering
     the solution's parenthetical "or with some non-conflicting passenger"), to show that
     no reading of the Final Stage rescues the schedule.

All arithmetic is exact (ints / set operations).  No floats, no randomness, no wall clock.
Deterministic output.

Model of a trip (standard, and the only reading consistent with the problem statement):
  Charon, standing on bank B with the boat, loads a subset S of the passengers currently
  on B with |S| <= k-1 (the boat holds k individuals *including* Charon) and crosses to
  the other bank.  While the boat is on the water, NEITHER bank has Charon, so BOTH banks
  must induce no edge of H.  On arrival, the bank Charon left must still induce no edge.
  Enemies may be together on Charon's own bank.
"""

from itertools import combinations
from collections import deque

LEFT, RIGHT = 'L', 'R'


# --------------------------------------------------------------------------------------
# graph helpers (exact, set-based)
# --------------------------------------------------------------------------------------

def induces_edge(vertexset, edges):
    """True iff the set of passengers `vertexset` contains both endpoints of some edge."""
    for (u, v) in edges:
        if u in vertexset and v in vertexset:
            return (u, v)
    return None


def all_graphs(n):
    """Yield (n, edges) for every graph on vertices 0..n-1, deterministically ordered."""
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = tuple(p for i, p in enumerate(pairs) if (mask >> i) & 1)
        yield edges


def min_vertex_covers(n, edges):
    """Exhaustive: return (size, [all minimum vertex covers as sorted tuples]) for H."""
    for size in range(0, n + 1):
        covers = []
        for cand in combinations(range(n), size):
            s = set(cand)
            if all((u in s) or (v in s) for (u, v) in edges):
                covers.append(tuple(sorted(cand)))
        if covers:
            return size, covers
    return n, [tuple(range(n))]


# --------------------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION of the solution's schedule (lines 0045-0102)
# --------------------------------------------------------------------------------------

def solution_schedule(n, C, K, final_return_load=None):
    """
    Generate the trip list exactly as the solution describes.

    C is the cover, listed as c1, c2, ..., cK (the solution's own labelling, line 0041).
    K = |C| (line 0038: "Without loss of generality, assume |C| = K").
    Boat capacity k = K + 1, so a trip may carry up to K passengers.

    Returns a list of trips; each trip is (direction, frozenset(load)).

    `final_return_load` is a hook for the GENEROUS variant: a function
    (right_bank_set) -> set to carry back on each Final-Stage return trip.  The literal
    text ("Charon can return empty") corresponds to always returning the empty set.
    """
    C = list(C)                      # c1 .. cK in the solution's order
    V = set(range(n))
    trips = []

    # 1. Initial Trip (Forward): Charon loads all cover vertices C, ferries L->R.
    trips.append((LEFT, frozenset(C)))

    # 2. For i = 1..K, Cover Delivery Rounds, two trips each.
    for ci in C:
        rest = frozenset(set(C) - {ci})
        trips.append((RIGHT, rest))   # Trip A (Backward): carry C\{ci} R->L, leave ci alone
        trips.append((LEFT, rest))    # Trip B (Forward):  carry C\{ci} L->R, leave L1 alone

    # 3. Final Stage: ferry L1 = V\C across, K at a time, Charon returning empty.
    L1 = sorted(V - set(C))
    right_bank = set(C)               # bookkeeping for the generous variant only
    left_bank = set(L1)
    i = 0
    while i < len(L1):
        back = frozenset() if final_return_load is None else frozenset(final_return_load(right_bank))
        trips.append((RIGHT, back))   # "Charon can return empty ... to the left bank"
        right_bank -= set(back)
        left_bank |= set(back)
        load = frozenset(L1[i:i + K])  # "then load up to K passengers from L1"
        trips.append((LEFT, load))
        left_bank -= set(load)
        right_bank |= set(load)
        i += K

    return trips


# --------------------------------------------------------------------------------------
# 2. ORACLE #1 -- exact simulator / safety checker
# --------------------------------------------------------------------------------------

def simulate(n, edges, trips, k):
    """
    Replay `trips` and verify legality.  Returns (ok, report_string).
    Checks, in order, for every trip:
      (a) Charon is on the departure bank named by the trip;
      (b) the load is a subset of that bank's passengers;
      (c) |load| <= k - 1 (boat holds k including Charon);
      (d) while the boat is on the water, BOTH banks induce no edge of H;
      (e) after arrival, the bank Charon left induces no edge of H.
    Finally checks that all n passengers are on the right bank.
    """
    left = set(range(n))
    right = set()
    charon = LEFT

    # initial safety: Charon is on the left, right bank is empty -> fine.
    for t, (depart, load) in enumerate(trips, start=1):
        src = left if depart == LEFT else right
        dst = right if depart == LEFT else left
        if charon != depart:
            return False, "trip %d: Charon is on bank %s but the trip departs from %s" % (t, charon, depart)
        if not load <= src:
            return False, "trip %d: load %s not present on bank %s" % (t, sorted(load), depart)
        if len(load) > k - 1:
            return False, "trip %d: load size %d exceeds capacity k-1 = %d" % (t, len(load), k - 1)

        src -= load
        # (d) boat on the water: neither bank has Charon.
        for name, bank in ((depart, src), (LEFT if depart == RIGHT else RIGHT, dst)):
            e = induces_edge(bank, edges)
            if e is not None:
                return False, ("trip %d (%s->%s, load %s): SAFETY VIOLATION -- while the boat is "
                               "on the water the %s bank holds %s, which contains the enemy pair %s "
                               "with Charon absent"
                               % (t, depart, LEFT if depart == RIGHT else RIGHT, sorted(load),
                                  name, sorted(bank), sorted(e)))
        dst |= load
        charon = LEFT if depart == RIGHT else RIGHT
        # (e) after arrival, the abandoned bank must still be safe (same set as in (d)).
        if depart == LEFT:
            left, right = src, dst
        else:
            right, left = src, dst

    if left or charon != RIGHT:
        return False, ("schedule ends with left bank = %s and Charon on %s: not all passengers "
                       "were transported" % (sorted(left), charon))
    return True, "schedule is valid (%d trips)" % len(trips)


# --------------------------------------------------------------------------------------
# 3. ORACLE #2 -- exhaustive BFS deciding whether ANY valid crossing sequence exists
# --------------------------------------------------------------------------------------

def solvable(n, edges, k, want_witness=False):
    """
    Exact decision by BFS over all states (frozenset(right bank), Charon side).

    While the boat is on the water the two unsupervised banks are exactly
      src - load   (the bank Charon left) and   dst   (the bank Charon has not reached yet;
    the passengers on the boat are NOT on it).  Both must induce no edge.  On arrival
    Charon is at dst, so dst | load needs no independence check.
    """
    V = frozenset(range(n))
    start = (frozenset(), LEFT)
    goal = (V, RIGHT)
    if start == goal:
        return (True, []) if want_witness else True
    seen = {start: None}          # state -> (parent, trip)
    q = deque([start])
    while q:
        cur = q.popleft()
        right, charon = cur
        left = V - right
        src = left if charon == LEFT else right
        dst = right if charon == LEFT else left
        if induces_edge(dst, edges) is not None:
            continue              # this bank is already unsafe unsupervised
        src_l = sorted(src)
        for sz in range(0, min(k - 1, len(src_l)) + 1):
            for load in combinations(src_l, sz):
                rem = src - set(load)
                if induces_edge(rem, edges) is not None:
                    continue      # bank Charon abandons would hold an enemy pair
                ncharon = RIGHT if charon == LEFT else LEFT
                nright = (dst | set(load)) if charon == LEFT else rem
                st = (frozenset(nright), ncharon)
                if st in seen:
                    continue
                seen[st] = (cur, (charon, frozenset(load)))
                if st == goal:
                    if not want_witness:
                        return True
                    path = []
                    node = st
                    while seen[node] is not None:
                        par, trip = seen[node]
                        path.append(trip)
                        node = par
                    return True, list(reversed(path))
                q.append(st)
    return (False, None) if want_witness else False


# --------------------------------------------------------------------------------------
# 5. GENEROUS variant of the Final Stage
# --------------------------------------------------------------------------------------

def generous_final_stage_rescues(n, edges, C, K):
    """
    The solution allows the Final-Stage return trip to carry "some non-conflicting
    passenger".  Try EVERY legal return load (any subset of the right bank of size <= K),
    used on every Final-Stage return trip, and see whether any choice yields a schedule
    that the simulator accepts.  Returns (rescued, witness_or_None).
    """
    k = K + 1
    right_after_rounds = sorted(set(C))
    for sz in range(0, min(K, len(right_after_rounds)) + 1):
        for back in combinations(right_after_rounds, sz):
            backset = set(back)
            trips = solution_schedule(n, C, K,
                                      final_return_load=lambda rb, b=backset: (b & rb))
            ok, _ = simulate(n, edges, trips, k)
            if ok:
                return True, sorted(backset)
    return False, None


# --------------------------------------------------------------------------------------
# 4. SEARCH
# --------------------------------------------------------------------------------------

def fmt_trips(trips):
    out = []
    for t, (d, load) in enumerate(trips, start=1):
        out.append("    trip %2d: %s -> %s carrying %s"
                   % (t, d, LEFT if d == RIGHT else RIGHT,
                      sorted(load) if load else "(empty)"))
    return "\n".join(out)


def analyse(n, edges, verbose=False, label=None, cover=None):
    """Run the faithful schedule through the oracles for one instance. Returns a dict."""
    K, covers = min_vertex_covers(n, edges)
    C = tuple(cover) if cover is not None else covers[0]  # default: lexicographically first
    K = len(C)                          # solution line 0038: "assume |C| = K"
    k = K + 1
    trips = solution_schedule(n, C, K)
    ok, report = simulate(n, edges, trips, k)
    exists = solvable(n, edges, k)
    res = dict(n=n, edges=edges, K=K, C=C, k=k, covers=covers,
               schedule_valid=ok, report=report, exists=exists, label=label)
    if verbose:
        print("  H = %s, edges = %s" % (label or ("n=%d" % n), list(edges)))
        print("  minimum vertex cover size = %d ; all minimum covers = %s" % (len(covers[0]), covers))
        print("  cover used C = %s (K = %d) ; reduction sets k = K+1 = %d ; L1 = %s"
              % (list(C), K, k, sorted(set(range(n)) - set(C))))
        print("  the solution's schedule (%d trips):" % len(trips))
        print(fmt_trips(trips))
        print("  ORACLE #1 (simulator): %s" % ("VALID" if ok else "INVALID -- " + report))
        ex, wit = solvable(n, edges, k, want_witness=True)
        print("  ORACLE #2 (exhaustive BFS over all states): a valid crossing sequence %s."
              % ("EXISTS" if ex else "DOES NOT EXIST"))
        if ex and not ok:
            print("    a genuinely valid schedule for this instance (found by BFS):")
            print(fmt_trips(wit))
        if cover is None:
            allfail = all(not simulate(n, edges, solution_schedule(n, cc, len(cc)),
                                       len(cc) + 1)[0] for cc in covers)
            print("  the schedule fails for EVERY minimum cover of H (not just the "
                  "lexicographic one): %s" % allfail)
        resc, wit2 = generous_final_stage_rescues(n, edges, C, K)
        print("  generous Final Stage (try every legal return load, covering the solution's "
              "'or with some\n    non-conflicting passenger'): %s"
              % ("RESCUED by carrying back %s" % wit2 if resc
                 else "NO return load yields a valid schedule"))
    return res


def named(name, n, edge_list):
    return (name, n, tuple(tuple(sorted(e)) for e in edge_list))


def main():
    print("=" * 88)
    print("record_id: Algorithms_11__sol4   |   claim_kind: CORRECTNESS")
    print("target claim (solution lines 0103-0105): the (<=)-direction schedule is a VALID")
    print("sequence of crossings; 'At every point, the bank without Charon holds either an")
    print("independent set of H's vertices or is empty.'")
    print("=" * 88)

    # ---------------- adversarial constructions from the triage sketch -----------------
    print("\n--- PART A: adversarial constructions named in the triage sketch ---")
    adversarial = [
        (named("P4 = path a-b-c-d, cover C = {b,c} (the minimum cover that contains an edge)",
               4, [(0, 1), (1, 2), (2, 3)]), (1, 2)),
        (named("P4 = path a-b-c-d, cover C = {a,c} (an independent minimum cover)",
               4, [(0, 1), (1, 2), (2, 3)]), (0, 2)),
        (named("K3 = triangle", 3, [(0, 1), (0, 2), (1, 2)]), None),
        (named("K4", 4, list(combinations(range(4), 2))), None),
        (named("K5", 5, list(combinations(range(5), 2))), None),
    ]
    headline = None
    for (label, n, edges), cov in adversarial:
        print("\n[%s]" % label)
        r = analyse(n, edges, verbose=True, label=label, cover=cov)
        if headline is None and (not r['schedule_valid']) and r['exists']:
            headline = r

    # ---------------- exhaustive search over all graphs, n = 4, 5, 6 ------------------
    print("\n--- PART B: exhaustive search over ALL graphs on n = 4, 5, 6 vertices ---")
    print("For every graph H with at least one edge (edgeless H gives K=0, k=1, a degenerate")
    print("instance where the boat cannot carry anyone), and for EVERY minimum vertex cover C")
    print("of H -- the solution's proof must work for an arbitrary given cover -- run the")
    print("solution's schedule generator with K=|C|, k=K+1 and check it with the simulator.")
    smallest = None
    for n in (4, 5, 6):
        tot = some_fail = all_fail = 0
        decision_ok = True
        for edges in all_graphs(n):
            if not edges:
                continue
            tot += 1
            K, covers = min_vertex_covers(n, edges)
            k = K + 1
            ex = solvable(n, edges, k)
            if not ex:
                decision_ok = False          # VC of size K exists but instance unsolvable
            fails = 0
            for C in covers:
                ok, rep = simulate(n, edges, solution_schedule(n, C, K), k)
                if not ok:
                    fails += 1
                    if ex and smallest is None:
                        smallest = dict(n=n, edges=edges, K=K, C=C, k=k,
                                        report=rep, exists=ex)
            if fails:
                some_fail += 1
            if fails == len(covers):
                all_fail += 1
        print("  n=%d : %5d graphs ; schedule INVALID for at least one minimum cover on %5d"
              " (%5.1f%%) ; INVALID for EVERY minimum cover on %5d (%5.1f%%)"
              % (n, tot, some_fail, 100.0 * some_fail / tot, all_fail, 100.0 * all_fail / tot))
        print("        decision-level (<=) direction 'min VC <= K  =>  solvable with k=K+1' "
              "held on all %d graphs: %s" % (tot, decision_ok))

    # ---------------- headline counterexample ----------------------------------------
    print("\n--- PART C: headline counterexample ---")
    r = headline if headline is not None else smallest
    n, edges, C, K, k = r['n'], r['edges'], r['C'], r['K'], r['k']
    print("  H: n=%d vertices, edges = %s" % (n, list(edges)))
    print("  C = %s is a vertex cover of H with |C| = K = %d, so the reduction sets k = K+1 = %d"
          % (list(C), K, k))
    print("  L1 = V \\ C = %s" % sorted(set(range(n)) - set(C)))
    print("  The solution's own schedule for this (H, K, C):")
    print(fmt_trips(solution_schedule(n, C, K)))
    print("  ORACLE #1 (simulator) rejects it:")
    print("    %s" % r['report'])
    print("  ORACLE #2 (exhaustive BFS): a valid crossing sequence for this instance %s,"
          % ("EXISTS" if r['exists'] else "DOES NOT EXIST"))
    print("    so the failure is in the solution's constructed schedule, not in the")
    print("    decision-level answer.")

    # ---------------- bonus: the decision-level (<=) direction also fails -------------
    print("\n--- PART D (bonus, strictly stronger than the target claim) ---")
    print("Part B also reports instances where H HAS a vertex cover of size <= K but the")
    print("river-crossing instance with G=H, k=K+1 has NO valid schedule at all.  Smallest:")
    found = None
    for n in (3, 4, 5):
        if found:
            break
        for edges in all_graphs(n):
            if not edges:
                continue
            K, covers = min_vertex_covers(n, edges)
            if not solvable(n, edges, K + 1):
                found = (n, edges, K, covers)
                break
    if found:
        n, edges, K, covers = found
        print("  H = star K_{1,%d}: n=%d, edges = %s" % (n - 1, n, list(edges)))
        print("  minimum vertex cover = %s, so K = %d and the reduction sets k = K+1 = %d"
              % (list(covers[0]), K, K + 1))
        print("  ORACLE #2 (exhaustive BFS over all %d states): NO valid crossing sequence"
              " exists." % (2 * 2 ** n))
        print("  Reason: with k=2 Charon can move only one passenger per trip, so the centre")
        print("  and any leaf can never both sit on the right bank while Charon leaves again.")
        print("  This refutes the solution's line 0106-0107 conclusion ('if H has a vertex")
        print("  cover of size K, then the river crossing problem with G=H and k=K+1 is")
        print("  solvable') and hence the Conclusion's biconditional -- a defect strictly")
        print("  stronger than, and containing, the target claim about the schedule.")

    print("\n--- NOTE ON READINGS OF THE SAFETY CONDITION ---")
    print("The violation is not an artefact of checking mid-crossing.  In the headline")
    print("counterexample, after trip 6 has COMPLETED Charon is at rest on the left bank and")
    print("the right bank holds C = {1,2} with the enemy edge (1,2).  So the schedule is")
    print("rejected whether one checks safety only in rest states or also in transit.")

    print("\n--- VERDICT ---")
    print("BUG_FOUND (CORRECTNESS).  The schedule the solution constructs in the (<=)")
    print("direction is not a valid sequence of crossings, and the quoted invariant")
    print("  'At every point, the bank without Charon holds either an independent set of H's")
    print("   vertices or is empty'")
    print("is false.  It fails in the Final Stage: after the K Cover Delivery Rounds the whole")
    print("cover C sits on the right bank, and when Charon returns (empty, as the text says) to")
    print("fetch members of L1 the right bank is left unsupervised holding all of C -- but a")
    print("vertex cover is in general NOT an independent set, so two enemies are alone together.")
    print("Trying every legal return load (the text's 'or with some non-conflicting passenger')")
    print("does not repair it.  Oracle #2 shows valid schedules do exist for these instances,")
    print("so what is refuted is the explicit construction and its invariant, not the theorem.")


if __name__ == '__main__':
    main()
