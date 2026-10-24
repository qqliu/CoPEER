/-!
# `mse_2605396__ans2605536` — the peeling step asserts teams with `k+1, …, n` wins;
  no tournament on `n` teams ever has a team with `n` wins

* **Record id:** `mse_2605396__ans2605536`
* **Question:** <https://math.stackexchange.com/questions/2605396>
  ("Proving that no two teams in a tournament win same number of games")
* **Answer (the flagged solution):** <https://math.stackexchange.com/a/2605536> (accepted)
* **Route:** `SELF_CONTAINED_LEAN`.  Chosen because the shared claim DSL
  `qedbench_certificate_availability_triage/lean_certificates/QEDTemplateV2.lean` has **no**
  constructor over tournaments / orientations of `K_n` and no notion of a win-count vector:
  its witness types are `BankGraph` (undirected simple graph), `WDG` (weighted digraph used
  only for shortest-path / MST claims) and auxiliary `Nat` lists, and grepping the whole
  `ClaimV2` constructor list turns up nothing about tournaments, out-degrees, win counts,
  top/bottom elements or `k`-absoluteness (the nearest neighbours are `degSeqEq` and
  `stronglyRegular`, both undirected).  There is therefore nothing to instantiate; this file
  stands alone.  It has **no `import` line at all** (core Lean 4 `Init` only), imports nothing
  from the trusted template, and modifies nothing outside itself.
* **Text licence:** CC BY-SA (Stack Exchange); the sentences below are quoted for
  identification.

## Verbatim claim being refuted

Line `0007` of the line-numbered solution text (the "Proof" paragraph).  The refuted
assertions are the two enumeration sentences and the pigeonhole tally that rests on them:

> "Repeat until you're left with $k$ elements. You are allowed to do this until you get to $k$
> by the "top" part of the top-bottom lemma. **This gives you that there are teams with
> $k+1, k+2, \dots, n$ wins.** Now, do the same for the least elements … You end up showing
> there are teams with $1, 2, \dots, k$ wins … **Together, then these results show that we have
> some team with $1$ win, another with $2$ etc. all the way up to $n$.** This implies uniqueness
> by the pigeonhole principle because we have $n$ pigeons (teams) and $n$ holes (number of
> wins) and there exists a team for each number of wins."

Its refutable arithmetic content, exactly as isolated by the search script
`partB_feasibility/counterexample_search_mined/mse_2605396__ans2605536.py`:

* **(A)** some team has `n` wins (every asserted top-peel set `{k+1, …, n}` contains `n`);
* **(B)** the `n` teams occupy the `n` holes `{1, 2, …, n}`, i.e. the win-count multiset is
  `{1, …, n}`;
* **(C)** hence the total number of wins is `1 + 2 + ⋯ + n = n(n+1)/2`.

All three are false for **every** tournament on `n` teams: each team plays exactly `n − 1`
games, so every win-count lies in `{0, …, n−1}`, the value `n` is unattainable, and the
tournament distributes exactly `C(n,2) = n(n−1)/2` wins, short of `n(n+1)/2` by exactly `n`.
The correct enumeration is shifted down by one: the top peel yields `{k, …, n−1}` and the
holes are `{0, 1, …, n−1}`.

### SCOPE — read before citing this file

Refuted here is the **enumeration/indexing step** of line `0007` only.  The answer's headline
conclusion — that in such a tournament no two teams win the same number of games — is
**true, and is positively certified below** (Part 4, `…_conclusion_of_the_answer_is_true`):
on both witnesses the win counts are pairwise distinct.  The Top/Bottom lemma of line `0009`
is untouched.  What fails is the arithmetic the pigeonhole argument is run on: the argument as
written needs a team with `n` wins, which no tournament has, and counts `n(n+1)/2` wins where
only `n(n−1)/2` exist.  This is an internal off-by-one in an otherwise sound proof sketch, not
a refutation of the theorem.

## Witnesses

1. **The triage witness** (`witness_description`): the transitive round-robin tournament on
   `n = 5` teams — `0` beats `1,2,3,4`; `1` beats `2,3,4`; `2` beats `3,4`; `3` beats `4`.
   Win vector `(4,3,2,1,0)`: five *distinct* win counts, so it cannot be dismissed as a
   degenerate configuration — it is exactly the "peeling" shape the proof describes.  With
   `k = 2` the proof asserts teams with `3, 4, 5` wins; the win counts present are
   `{0,1,2,3,4}`, so no team has `5`.  Total wins `10 = C(5,2)`, against the claimed
   `1+2+3+4+5 = 15`.
2. **An in-regime witness.**  The proof's standing hypothesis is `n ≥ 2k > 4`, which
   `n = 5, k = 2` does **not** satisfy (`2k = 4` is not `> 4`).  So the file also certifies the
   transitive tournament on `n = 6` with `k = 3`, where `6 ≥ 6 > 4` holds *and* the tournament
   is verified `3`-absolute (every 3-subset has a top and a bottom element) — i.e. every
   hypothesis of line `0007` is met and its conclusion still fails: no team has `6` wins,
   the asserted top peel `{4,5,6}` is not realized, total wins `15 ≠ 21`.

## Modelling judgments (the kernel checks the arithmetic, not the faithfulness of these)

1. **Tournament = orientation of `K_n`.**  `pairsLt n` lists the pairs `(i,j)`, `i < j`, in a
   fixed order; a tournament is a `List Bool` of that same length, entry `true` meaning "`i`
   beat `j`", `false` meaning "`j` beat `i`".  Every such list is a legal round-robin
   tournament and every round-robin tournament is such a list, so the encoding is exactly the
   set of tournaments — no well-formedness side condition can silently exclude a
   counterexample.  Ties are impossible by construction, matching the question's "only
   possible results for a match is win and lose".
2. **Win count = number of pairs whose winner is that team** (`winCount`), i.e. out-degree.
   `winVec n o` is the vector of win counts of teams `0, …, n−1`, in that order.
3. **Teams are 0-indexed**; the *win counts* are plain naturals, so the comparison with the
   proof's `1, …, n` is index-convention-free: the assertion "a team with `n` wins" is about
   a number of games won, not about a team label.
4. **The bottom-peel sentence is NOT claimed to fail.**  `{1, …, k}` is realizable (both
   witnesses do have teams with `1` and `2` wins), and this file makes no claim against it.
   What fails is the *top* peel `{k+1, …, n}` — for every `k` and every tournament — and
   therefore the union `{1, …, n}` and the pigeonhole tally.  The certificate is deliberately
   narrow on this point.
5. **`k`-absoluteness is modelled literally** from line `0003`: `kAbsolute n o k` says every
   `k`-element subset of the teams has a top element (beats all others in the subset) and a
   bottom element (loses to all others in the subset).  It is *discriminating*, not vacuously
   true: the 3-cycle tournament on 3 teams is shown to be non-`3`-absolute (Part 5, NC3).
6. **Exhaustive sweep budget.**  The kernel sweep covers every orientation of `K_n` for
   `n = 2,3,4,5` (2 + 8 + 64 + 1024 = 1098 tournaments, fully enumerated, no sampling).  The
   record's Python script additionally covered `n = 6` and `n = 7` (2,130,018 tournaments in
   total); those two sizes are **not** re-derived here — kernel budget only, not because they
   behave differently (the `n = 6` transitive witness *is* checked individually).
7. **Set-membership reading of "there are teams with `v₁, …, v_r` wins"**: `realizesSet`
   requires, for each listed value, *some* team with exactly that many wins.  This is the
   weakest reasonable reading — it does not demand distinct teams or an exact multiset — so
   refuting it refutes every stronger reading too.
8. Everything is discharged by kernel `decide` on closed `Bool`-valued terms.  No
   `native_decide`, no `sorry`, no axioms, no imports.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace mse_2605396__ans2605536

/-! ## Part 0. Encoding: tournaments as orientations of `K_n` -/

/-- All pairs `(i,j)` with `i < j < n`, in lexicographic order.  This is the game schedule of
a round-robin tournament on `n` teams; its length is `C(n,2)`. -/
def pairsLt (n : Nat) : List (Nat × Nat) :=
  (List.range n).foldr (fun i acc =>
    ((List.range n).filter (fun j => decide (i < j))).foldr
      (fun j acc2 => (i, j) :: acc2) acc) []

/-- The winner of each scheduled game: entry `true` at pair `(i,j)` means `i` beat `j`. -/
def winnersOf : List (Nat × Nat) → List Bool → List Nat
  | [], _ => []
  | (i, j) :: ps, bs =>
      match bs with
      | [] => []
      | b :: bs' => (if b then i else j) :: winnersOf ps bs'

/-- How many games team `t` won, given the winner list. -/
def winCount (ws : List Nat) (t : Nat) : Nat :=
  (ws.filter (fun w => w == t)).length

/-- The win vector of teams `0, …, n−1` from an already-computed winner list. -/
def winVecOf (n : Nat) (ws : List Nat) : List Nat :=
  (List.range n).map (fun t => winCount ws t)

/-- The win vector of the tournament `o` on `n` teams. -/
def winVec (n : Nat) (o : List Bool) : List Nat :=
  winVecOf n (winnersOf (pairsLt n) o)

/-- The transitive tournament on `n` teams: `i` beats `j` whenever `i < j`. -/
def transTour (n : Nat) : List Bool := (pairsLt n).map (fun _ => true)

/-! ### Small list utilities (kept first-order so every statement is a closed `Bool` term) -/

def natSum : List Nat → Nat
  | [] => 0
  | a :: as => a + natSum as

def natMax : List Nat → Nat
  | [] => 0
  | a :: as => let m := natMax as; if a ≤ m then m else a

def insSorted (x : Nat) : List Nat → List Nat
  | [] => [x]
  | a :: as => if x ≤ a then x :: a :: as else a :: insSorted x as

def sortNat : List Nat → List Nat
  | [] => []
  | a :: as => insSorted a (sortNat as)

/-- Equality of `Nat` lists, as a `Bool` function (no `DecidableEq` instance trusted). -/
def natListEq : List Nat → List Nat → Bool
  | [], [] => true
  | a :: as, b :: bs => (a == b) && natListEq as bs
  | _, _ => false

/-! ## Part 1. The claim, transcribed

`hasWinCount wv v` — some team has exactly `v` wins.
`realizesSet wv vs` — for every value in `vs` there is a team with that many wins:
the literal content of "there are teams with `v₁, v₂, …` wins" (modelling judgment 7). -/

def hasWinCount (wv : List Nat) (v : Nat) : Bool := wv.any (fun w => w == v)

def realizesSet (wv : List Nat) (vs : List Nat) : Bool := vs.all (fun v => hasWinCount wv v)

/-- The set the proof asserts the top peel produces: `{k+1, k+2, …, n}`. -/
def claimedTopPeel (k n : Nat) : List Nat := (List.range (n - k)).map (fun t => k + 1 + t)

/-- What the top peel actually produces: `{k, k+1, …, n−1}` (everything shifted down by one). -/
def correctTopPeel (k n : Nat) : List Nat := (List.range (n - k)).map (fun t => k + t)

/-- The proof's pigeonhole holes: `{1, 2, …, n}`. -/
def claimedHoles (n : Nat) : List Nat := (List.range n).map (fun t => t + 1)

/-- The holes that actually exist: `{0, 1, …, n−1}`. -/
def actualHoles (n : Nat) : List Nat := List.range n

/-- The total the proof's tally implies: `1 + 2 + ⋯ + n`. -/
def claimedTotalWins (n : Nat) : Nat := natSum (claimedHoles n)

/-- The number of wins actually distributed: one per game, i.e. `C(n,2)`. -/
def actualTotalWins (n : Nat) : Nat := (pairsLt n).length

/-! ## Part 2. Witness 1 — the transitive tournament on 5 teams (the triage witness) -/

/-- The witness's schedule and win vector are what the header says: 10 games, win vector
`(4,3,2,1,0)` — five distinct win counts, the "peeling" configuration itself. -/
theorem mse_2605396__ans2605536_witness5_shape :
    ((pairsLt 5).length = 10)
  ∧ ((transTour 5).length = 10)
  ∧ (natListEq (winVec 5 (transTour 5)) [4, 3, 2, 1, 0] = true)
  ∧ (natSum (winVec 5 (transTour 5)) = 10)
  ∧ (actualTotalWins 5 = 10) := by decide

/-- **Main certificate (witness 1).**  On the 5-team transitive tournament, with `k = 2`:

* (A) no team has `n = 5` wins — the maximum win count is `4`, so the asserted top peel
  `{3,4,5}` is *not* realized, while the true top peel `{2,3,4}` is;
* (B) the win-count multiset is `{0,1,2,3,4}`, not the asserted `{1,2,3,4,5}`;
* (C) the tournament distributes `10` wins, not the `1+2+3+4+5 = 15` the pigeonhole tally
  assumes — a shortfall of exactly `n = 5`. -/
theorem mse_2605396__ans2605536_witness5_refutes :
    -- (A) the asserted top peel for k = 2 is not realized; the shifted-down one is
    (natListEq (claimedTopPeel 2 5) [3, 4, 5] = true)
  ∧ (natListEq (correctTopPeel 2 5) [2, 3, 4] = true)
  ∧ (realizesSet (winVec 5 (transTour 5)) (claimedTopPeel 2 5) = false)
  ∧ (realizesSet (winVec 5 (transTour 5)) (correctTopPeel 2 5) = true)
  ∧ (hasWinCount (winVec 5 (transTour 5)) 5 = false)
  ∧ (hasWinCount (winVec 5 (transTour 5)) 4 = true)
  ∧ (natMax (winVec 5 (transTour 5)) = 4)
    -- (B) the holes are {0,…,4}, not {1,…,5}
  ∧ (natListEq (sortNat (winVec 5 (transTour 5))) (claimedHoles 5) = false)
  ∧ (natListEq (sortNat (winVec 5 (transTour 5))) (actualHoles 5) = true)
  ∧ (realizesSet (winVec 5 (transTour 5)) (claimedHoles 5) = false)
  ∧ (realizesSet (winVec 5 (transTour 5)) (actualHoles 5) = true)
    -- (C) the tally: 15 claimed, 10 actual
  ∧ (claimedTotalWins 5 = 15)
  ∧ (actualTotalWins 5 = 10)
  ∧ (natSum (winVec 5 (transTour 5)) = 10) := by decide

/-- The failure is not special to `k = 2`: for **every** `k ∈ {0,…,4}` the asserted top peel
`{k+1,…,5}` fails on this tournament, and for every such `k` the shifted-down set `{k,…,4}`
succeeds.  So no choice of `k` rescues the sentence. -/
theorem mse_2605396__ans2605536_witness5_every_k :
    ((List.range 5).all (fun k =>
        !realizesSet (winVec 5 (transTour 5)) (claimedTopPeel k 5)) = true)
  ∧ ((List.range 5).all (fun k =>
        realizesSet (winVec 5 (transTour 5)) (correctTopPeel k 5)) = true) := by decide

/-! ## Part 3. Witness 2 — inside the proof's own regime `n ≥ 2k > 4` (`n = 6`, `k = 3`)

Witness 1 sits at `n = 5, k = 2`, where `2k = 4` is not `> 4`; a reader could object that the
proof never claimed anything there.  This part removes the objection: the transitive
tournament on 6 teams is verified `3`-absolute, `6 ≥ 2·3 > 4` holds, and the conclusion of
line `0007` still fails. -/

/-- Did `i` beat `j` in tournament `o`?  Scans the schedule; `false` if `i`, `j` never met
(only when `i = j` or an index is out of range). -/
def arcLookup : List (Nat × Nat) → List Bool → Nat → Nat → Bool
  | [], _, _, _ => false
  | (a, b) :: ps, bs, i, j =>
      match bs with
      | [] => false
      | w :: bs' =>
          if (a == i && b == j) then w
          else if (a == j && b == i) then !w
          else arcLookup ps bs' i j

def beatsB (n : Nat) (o : List Bool) (i j : Nat) : Bool := arcLookup (pairsLt n) o i j

/-- All `k`-element sublists of `l` (order-preserving; structural in `l`). -/
def subsetsOfSize : Nat → List Nat → List (List Nat)
  | 0, _ => [[]]
  | _ + 1, [] => []
  | k + 1, x :: xs => ((subsetsOfSize k xs).map (fun s => x :: s)) ++ subsetsOfSize (k + 1) xs

/-- Line `0001`: `S` has a *top* element — a member beating every other member. -/
def hasTop (n : Nat) (o : List Bool) (S : List Nat) : Bool :=
  S.any (fun t => S.all (fun u => (u == t) || beatsB n o t u))

/-- Line `0001`: `S` has a *bottom* element — a member losing to every other member. -/
def hasBot (n : Nat) (o : List Bool) (S : List Nat) : Bool :=
  S.any (fun t => S.all (fun u => (u == t) || beatsB n o u t))

/-- Line `0003`: the team set is `k`-absolute — every `k`-subset has a top and a bottom. -/
def kAbsolute (n : Nat) (o : List Bool) (k : Nat) : Bool :=
  (subsetsOfSize k (List.range n)).all (fun S => hasTop n o S && hasBot n o S)

/-- The 6-team transitive tournament satisfies every hypothesis of line `0007` for `k = 3`:
it is `3`-absolute (and `4`- and `5`-absolute), and `n ≥ 2k > 4` holds numerically. -/
theorem mse_2605396__ans2605536_witness6_hypotheses_hold :
    (kAbsolute 6 (transTour 6) 3 = true)
  ∧ (kAbsolute 6 (transTour 6) 4 = true)
  ∧ (kAbsolute 6 (transTour 6) 5 = true)
  ∧ (6 ≥ 2 * 3) ∧ (2 * 3 > 4)
  ∧ ((pairsLt 6).length = 15)
  ∧ (natListEq (winVec 6 (transTour 6)) [5, 4, 3, 2, 1, 0] = true) := by decide

/-- **Main certificate (witness 2).**  With every hypothesis of line `0007` satisfied
(`n = 6 ≥ 2k = 6 > 4`, the set is `3`-absolute), its conclusion is false: no team has `6`
wins, the asserted top peel `{4,5,6}` is not realized, the holes are `{0,…,5}` not `{1,…,6}`,
and the tournament distributes `15` wins against the claimed `21`. -/
theorem mse_2605396__ans2605536_witness6_refutes :
    (natListEq (claimedTopPeel 3 6) [4, 5, 6] = true)
  ∧ (natListEq (correctTopPeel 3 6) [3, 4, 5] = true)
  ∧ (realizesSet (winVec 6 (transTour 6)) (claimedTopPeel 3 6) = false)
  ∧ (realizesSet (winVec 6 (transTour 6)) (correctTopPeel 3 6) = true)
  ∧ (hasWinCount (winVec 6 (transTour 6)) 6 = false)
  ∧ (natMax (winVec 6 (transTour 6)) = 5)
  ∧ (natListEq (sortNat (winVec 6 (transTour 6))) (claimedHoles 6) = false)
  ∧ (natListEq (sortNat (winVec 6 (transTour 6))) (actualHoles 6) = true)
  ∧ (realizesSet (winVec 6 (transTour 6)) (claimedHoles 6) = false)
  ∧ (claimedTotalWins 6 = 21)
  ∧ (actualTotalWins 6 = 15)
  ∧ (natSum (winVec 6 (transTour 6)) = 15)
  ∧ ((List.range 6).all (fun k =>
        !realizesSet (winVec 6 (transTour 6)) (claimedTopPeel k 6)) = true) := by decide

/-! ## Part 4. Exhaustive sweep: EVERY tournament refutes the enumeration step -/

/-- All `2^m` `Bool` lists of length `m` — i.e. all orientations of a schedule of `m` games. -/
def allBoolLists : Nat → List (List Bool)
  | 0 => [[]]
  | m + 1 => (allBoolLists m).foldr (fun l acc => (true :: l) :: (false :: l) :: acc) []

/-- The five checks, on a win vector: no team with `n` wins; every win count `< n`; the
multiset is not `{1,…,n}`; the total is exactly `C(n,2)`; and no `k` realizes `{k+1,…,n}`. -/
def sweepOkWv (n : Nat) (wv : List Nat) : Bool :=
  !hasWinCount wv n
  && decide (natMax wv < n)
  && !natListEq (sortNat wv) (claimedHoles n)
  && (natSum wv == actualTotalWins n)
  && (List.range n).all (fun k => !realizesSet wv (claimedTopPeel k n))

def sweepOk (n : Nat) (o : List Bool) : Bool := sweepOkWv n (winVec n o)

/-- Every orientation of `K_n` passes all five checks. -/
def allSweepOk (n : Nat) : Bool :=
  (allBoolLists (pairsLt n).length).all (fun o => sweepOk n o)

/-- **Exhaustive certificate.**  Over *all* 2 + 8 + 64 + 1024 = 1098 tournaments on
`n = 2,3,4,5` teams, without exception: no team ever has `n` wins, no win-count multiset is
ever `{1,…,n}`, the total is always `C(n,2)`, and the asserted top-peel set `{k+1,…,n}` is
realized for no `k` whatsoever.  The refutation is therefore universal, not a lucky witness:
*every* round-robin tournament refutes the enumeration step. -/
theorem mse_2605396__ans2605536_exhaustive_sweep :
    (allSweepOk 2 = true)
  ∧ (allSweepOk 3 = true)
  ∧ (allSweepOk 4 = true)
  ∧ (allSweepOk 5 = true) := by decide

/-- Non-vacuity of the sweep: the enumerated families really have `2^C(n,2)` members, so the
theorem above is not true merely because the quantified list is empty or truncated. -/
theorem mse_2605396__ans2605536_sweep_nonvacuous :
    ((allBoolLists (pairsLt 2).length).length = 2)
  ∧ ((allBoolLists (pairsLt 3).length).length = 8)
  ∧ ((allBoolLists (pairsLt 4).length).length = 64)
  ∧ ((allBoolLists (pairsLt 5).length).length = 1024)
  ∧ ((allBoolLists 3).all (fun l => l.length == 3) = true) := by decide

/-- **The answer's actual conclusion is TRUE on both witnesses** — this file attacks the
enumeration step, not the theorem.  On each witness the win counts are pairwise distinct
(`sorted win vector = {0,…,n−1}`, which has no repeats), exactly as the question asks. -/
theorem mse_2605396__ans2605536_conclusion_of_the_answer_is_true :
    (natListEq (sortNat (winVec 5 (transTour 5))) (actualHoles 5) = true)
  ∧ (natListEq (sortNat (winVec 6 (transTour 6))) (actualHoles 6) = true)
  ∧ ((List.range 5).all (fun v => winCount (winVec 5 (transTour 5)) v == 1) = true)
  ∧ ((List.range 6).all (fun v => winCount (winVec 6 (transTour 6)) v == 1) = true) := by decide

/-! ## Part 5. NEGATIVE CONTROLS

Each conjunct below would fail to compile if the modelling were vacuous or rigged.  Together
they rule out the ways this certificate could be hollow: a `realizesSet` that never returns
`true`, a `winVec` that is constant or ignores the orientation, a `kAbsolute` that is
trivially true, and an encoding that cannot express a team with `n` wins at all. -/

/-- (NC1) `realizesSet` is **not** constantly false: on the very same witness, with the very
same evaluator, the *repaired* claim (every index shifted down by one) comes out `true` — for
the top peel at every `k`, for the full hole set, and for each individual value `0,…,4`.  The
refutation is therefore located precisely at the `+1`, not in a broken predicate. -/
theorem mse_2605396__ans2605536_nc1_repaired_claim_succeeds :
    (realizesSet (winVec 5 (transTour 5)) (actualHoles 5) = true)
  ∧ (realizesSet (winVec 5 (transTour 5)) [0, 1, 2, 3, 4] = true)
  ∧ ((List.range 5).all (fun v => hasWinCount (winVec 5 (transTour 5)) v) = true)
  ∧ (realizesSet (winVec 6 (transTour 6)) (actualHoles 6) = true)
  ∧ (realizesSet (winVec 5 (transTour 5)) [] = true) := by decide

/-- The reversed tournament: `j` beats `i` whenever `i < j`. -/
def revTour (n : Nat) : List Bool := (pairsLt n).map (fun _ => false)

/-- The 3-cycle: `0` beats `1`, `2` beats `0`, `1` beats `2`. -/
def cycle3 : List Bool := [true, false, true]

/-- (NC2) `winVec` genuinely reads the orientation and is not constant: reversing every game
of the 5-team witness reverses the win vector, and the 3-cycle tournament on 3 teams has win
vector `(1,1,1)` — repeated win counts, so nothing in the encoding forces distinctness (which
is exactly why the `k`-absoluteness hypothesis is needed at all). -/
theorem mse_2605396__ans2605536_nc2_winvec_is_not_constant :
    (natListEq (winVec 5 (revTour 5)) [0, 1, 2, 3, 4] = true)
  ∧ (natListEq (winVec 5 (revTour 5)) (winVec 5 (transTour 5)) = false)
  ∧ (natListEq (winVec 3 cycle3) [1, 1, 1] = true)
  ∧ (natSum (winVec 3 cycle3) = 3)
  ∧ (actualTotalWins 3 = 3) := by decide

/-- (NC3) `kAbsolute` / `hasTop` / `hasBot` are discriminating, not trivially true: the
3-cycle has neither a top nor a bottom element, so it is **not** `3`-absolute (whereas
`2`-absoluteness is automatic for every tournament, since one of any two teams beat the
other — which is why line `0005` insists on `k > 2`).  Hence Part 3's verification
that the 6-team witness *is* `3`-absolute carries real content. -/
theorem mse_2605396__ans2605536_nc3_kabsolute_discriminates :
    (hasTop 3 cycle3 [0, 1, 2] = false)
  ∧ (hasBot 3 cycle3 [0, 1, 2] = false)
  ∧ (kAbsolute 3 cycle3 3 = false)
  ∧ (kAbsolute 3 cycle3 2 = true)
  ∧ (hasTop 3 (transTour 3) [0, 1, 2] = true)
  ∧ (hasBot 3 (transTour 3) [0, 1, 2] = true)
  ∧ ((subsetsOfSize 3 (List.range 6)).length = 20) := by decide

/-- (NC4) `beatsB` really is a tournament relation on the witness: for every ordered pair of
distinct teams exactly one of `beatsB i j`, `beatsB j i` holds, and no team beats itself.  A
lookup that always returned `false` (which would make `hasTop` false and `kAbsolute` vacuous)
is ruled out. -/
theorem mse_2605396__ans2605536_nc4_beats_is_a_tournament :
    ((List.range 6).all (fun i => (List.range 6).all (fun j =>
        if i == j then !beatsB 6 (transTour 6) i j
        else (beatsB 6 (transTour 6) i j) != (beatsB 6 (transTour 6) j i))) = true)
  ∧ (beatsB 5 (transTour 5) 0 4 = true)
  ∧ (beatsB 5 (transTour 5) 4 0 = false)
  ∧ (beatsB 5 (revTour 5) 0 4 = false)
  ∧ (beatsB 5 (revTour 5) 4 0 = true) := by decide

/-- (NC5) The unattainable value `n` is not unattainable *in the encoding*: `hasWinCount` and
`realizesSet` happily return `true` for `5` on a hand-written vector containing `5`, and the
claimed hole multiset `{1,…,5}` is matched exactly by the (non-tournament) vector
`[1,2,3,4,5]`.  So the sweep's failures are facts about tournaments, not about a predicate
that can never fire. -/
theorem mse_2605396__ans2605536_nc5_claimed_values_are_expressible :
    (hasWinCount [5, 3, 2, 1, 0] 5 = true)
  ∧ (realizesSet [5, 4, 3, 2, 1] (claimedTopPeel 2 5) = true)
  ∧ (realizesSet [1, 2, 3, 4, 5] (claimedHoles 5) = true)
  ∧ (natListEq (sortNat [5, 4, 3, 2, 1]) (claimedHoles 5) = true)
  ∧ (natSum [1, 2, 3, 4, 5] = claimedTotalWins 5)
  ∧ (sweepOkWv 5 [1, 2, 3, 4, 5] = false) := by decide

/-- (NC6) The sweep predicate is not a tautology: `sweepOkWv` returns `false` on the
hypothetical win vector the proof describes (`{1,…,5}`, previous theorem) and `true` on the
real witness — the same five checks separate the two. -/
theorem mse_2605396__ans2605536_nc6_sweep_predicate_discriminates :
    (sweepOk 5 (transTour 5) = true)
  ∧ (sweepOk 5 (revTour 5) = true)
  ∧ (sweepOkWv 5 [1, 2, 3, 4, 5] = false)
  ∧ (sweepOkWv 5 [5, 3, 2, 1, 0] = false) := by decide

end mse_2605396__ans2605536

#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_witness5_shape
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_witness5_refutes
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_witness5_every_k
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_witness6_hypotheses_hold
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_witness6_refutes
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_exhaustive_sweep
#print axioms mse_2605396__ans2605536.above
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_sweep_nonvacuous
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_conclusion_of_the_answer_is_true
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc1_repaired_claim_succeeds
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc2_winvec_is_not_constant
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc3_kabsolute_discriminates
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc4_beats_is_a_tournament
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc5_claimed_values_are_expressible
#print axioms mse_2605396__ans2605536.mse_2605396__ans2605536_nc6_sweep_predicate_discriminates
