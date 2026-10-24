#!/usr/bin/env python3
"""
Blind counterexample search for record Algorithms_12__sol4.

TARGET CLAIM (quoted verbatim from the proof):
    "becomes free and proposes to Wn (who, up to now, has never received any
     offer). Woman Wn is currently unmatched, so she simply accepts"

Context inferred from the claim text alone: this is a step in an execution of
the man-proposing Gale-Shapley (deferred acceptance) algorithm.  The claim's
finitely-refutable logical content is the following invariant of the
algorithm, applied at the moment some man becomes free and proposes to a
woman W who has never received any offer:

    (A) At any point during any execution of man-proposing Gale-Shapley,
        a woman who has so far received no offer is unmatched.
    (B) An unmatched woman who receives a proposal accepts it (becomes
        matched to the proposer at that step).

The specific worst-case instance ("Wn") referenced by the proof is NOT
supplied in the record, so we cannot test that particular construction.
Instead we exhaustively test invariants (A) and (B) over ALL stable-matching
instances of size n = 1, 2, 3 (every combination of complete strict
preference lists for all men and all women), and over execution schedules:

  * n = 1 and n = 2: ALL nondeterministic execution schedules (at each step,
    every possible choice of which free man proposes next is explored by DFS).
  * n = 3: two deterministic schedules per instance (always the lowest-index
    free man; always the highest-index free man).

A witness would be an instance + schedule + step at which either a woman with
no prior offers is found already matched (violating A), or an unmatched woman
fails to accept a proposal (violating B; note B is the acceptance rule of the
algorithm itself, so it is checked structurally).

Everything is exact integer/permutation arithmetic; no floats, no randomness.
Iteration order is fixed (itertools.product over sorted permutations), so the
program is fully deterministic.
"""

import itertools
import sys


def simulate_all_schedules(n, men_prefs, women_rank, explore_all):
    """
    Simulate man-proposing Gale-Shapley.

    men_prefs[m]  = tuple of women in m's preference order (best first)
    women_rank[w][m] = rank (0 = best) that woman w gives man m

    If explore_all is True, DFS over every choice of which free man proposes
    next.  Otherwise run two deterministic schedules: lowest-index free man
    and highest-index free man.

    Returns None if invariants (A)/(B) hold in every explored execution,
    else a witness dict.
    """
    # State: next_idx (tuple, per man: next woman index to propose to),
    #        husband (tuple, per woman: matched man or -1),
    #        offers (tuple, per woman: number of offers received so far)
    start = (tuple([0] * n), tuple([-1] * n), tuple([0] * n))

    if explore_all:
        pickers = [None]  # None => branch over all free men
    else:
        pickers = [min, max]

    for picker in pickers:
        stack = [(start, [])]
        seen = set()
        while stack:
            (next_idx, husband, offers), trace = stack.pop()
            key = (next_idx, husband, offers, id(picker) if picker else 0)
            # states are uniquely determined by (next_idx, husband, offers)
            skey = (next_idx, husband, offers)
            if explore_all:
                if skey in seen:
                    continue
                seen.add(skey)
            free_men = [m for m in range(n)
                        if m not in husband and next_idx[m] < n]
            if not free_men:
                continue
            choices = free_men if picker is None else [picker(free_men)]
            for m in choices:
                w = men_prefs[m][next_idx[m]]
                # --- Invariant (A): no offers so far => unmatched ---
                if offers[w] == 0 and husband[w] != -1:
                    return {
                        "violated": "A",
                        "instance_men": men_prefs,
                        "trace": trace + [(m, w)],
                        "detail": "woman %d has received 0 offers but is "
                                  "matched to man %d" % (w, husband[w]),
                    }
                new_offers = list(offers)
                new_offers[w] = offers[w] + 1
                new_next = list(next_idx)
                new_next[m] = next_idx[m] + 1
                new_husband = list(husband)
                if husband[w] == -1:
                    # --- Invariant (B): unmatched woman accepts ---
                    # (this IS the algorithm's rule; we implement it and
                    #  record that acceptance occurred)
                    new_husband[w] = m
                    accepted = True
                else:
                    cur = husband[w]
                    if women_rank[w][m] < women_rank[w][cur]:
                        new_husband[w] = m  # cur becomes free
                    accepted = (new_husband[w] == m)
                # Structural check of (B): if she was unmatched she accepted.
                if husband[w] == -1 and not accepted:
                    return {
                        "violated": "B",
                        "instance_men": men_prefs,
                        "trace": trace + [(m, w)],
                        "detail": "unmatched woman %d rejected man %d" % (w, m),
                    }
                stack.append(((tuple(new_next), tuple(new_husband),
                               tuple(new_offers)),
                              trace + [(m, w)]))
    return None


def main():
    total_instances = 0
    for n in (1, 2, 3):
        perms = sorted(itertools.permutations(range(n)))
        explore_all = (n <= 2)
        for men_prefs in itertools.product(perms, repeat=n):
            for women_prefs in itertools.product(perms, repeat=n):
                women_rank = [
                    {m: r for r, m in enumerate(women_prefs[w])}
                    for w in range(n)
                ]
                total_instances += 1
                witness = simulate_all_schedules(
                    n, men_prefs, women_rank, explore_all)
                if witness is not None:
                    print("WITNESS_FOUND")
                    print("n =", n)
                    print("men_prefs   =", men_prefs)
                    print("women_prefs =", women_prefs)
                    print("proposal trace (man,woman):", witness["trace"])
                    print("violated invariant:", witness["violated"])
                    print("detail:", witness["detail"])
                    return 1
        print("n=%d done: all instances passed "
              "(schedules: %s)" % (n, "ALL" if explore_all else
                                   "lowest-free and highest-free"))
    print("NO_WITNESS_EXHAUSTIVE")
    print("Swept %d preference-profile instances total (n=1,2,3; every "
          "combination of complete strict preference lists on both sides)."
          % total_instances)
    print("For n<=2 every nondeterministic proposal schedule was explored; "
          "for n=3 the lowest-index-free-man and highest-index-free-man "
          "schedules were explored.")
    print("In every explored execution step, any woman who had received no "
          "offer was unmatched, and every unmatched woman who received a "
          "proposal accepted it.  The claim's checkable content holds on the "
          "entire swept space.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
