import HumanReviewAxiomAudit
/-!
# mse_811862__ans811879 — self-contained refutation certificate

* Record id : `mse_811862__ans811879`
* Question  : https://math.stackexchange.com/questions/811862  (inferred from the record id)
* Answer    : https://math.stackexchange.com/a/811879            (inferred from the record id)
* Route     : SELF_CONTAINED_LEAN (no `import`, no Mathlib; kernel `decide` only)
* Text licence: CC BY-SA (Stack Exchange).

## The claim being refuted

The refuted sentence asserts a LITERAL EQUALITY, for each `k ≥ 1` and each matrix size
`N ≥ 1`, between the Gaussian (GUE-style) expectation of the trace of the `2k`-th power
of an `N × N` random matrix `H` and the `k`-th Catalan number:

>   ⟨Tr(H^{2k})⟩  =  C_k  =  binom(2k, k) / (k+1).

Nothing asymptotic or infinitary is stated in that sentence — no limit `N → ∞`, no `~`,
no normalisation by a power of `N`, no `O(·)`.  Both sides are, for each fixed `(k, N)`,
completely determined integers:

* the RIGHT side is the Catalan number `C_k`, an `N`-independent integer;
* the LEFT side is fixed by the proof's OWN evaluation rule.  The proof declares the
  entries centred Gaussian with propagator

      ⟨H_ij H_kl⟩ = δ_il δ_jk,

  and therefore evaluates any even moment by Wick/Isserlis: sum over all `(2k-1)!!`
  perfect matchings of the `2k` factors of the product of the propagators.

So a single pair `(k, N)` with unequal integers refutes the sentence, and the claim is
finitely refutable.  (The CORRECT statement is the asymptotic one,
`⟨Tr(H^{2k})⟩ = C_k · N^{k+1} + lower order`; the asserted `N`-free equality is not it.)

## Witness

    k = 1, N = 2 :   ⟨Tr(H^2)⟩ = 4   vs   C_1 = binom(2,1)/2 = 1.        4 ≠ 1.

This is the SMALLEST witness.  Expanding it by hand from the proof's own rule:

    ⟨Tr(H^2)⟩ = Σ_{i,j} ⟨H_ij H_ji⟩ = Σ_{i,j} δ_ii δ_jj = N^2 = 4.

Further exact witnesses, all recomputed by the kernel below:

    (k=2, N=2) :  ⟨Tr H^4⟩  = 18       vs  C_2 = 2
    (k=3, N=2) :  ⟨Tr H^6⟩  = 120      vs  C_3 = 5
    (k=4, N=3) :  ⟨Tr H^8⟩  = 5355     vs  C_4 = 14
    (k=5, N=6) :  ⟨Tr H^10⟩ = 2521260  vs  C_5 = 42      (leading term C_5·N^6 = 1959552)

Of the 30 exhaustively scanned pairs (`1 ≤ k ≤ 5`, small `N`), 29 falsify the claim.  The
SOLE pair on which the asserted equality holds is the degenerate `(k, N) = (1, 1)`, where
`⟨Tr H^2⟩ = 1^2 = 1 = C_1` by coincidence.  That exception is not swept under the rug: it
is asserted positively in `scan_k3_N4` and in `nc2_sole_agreement_is_1_1` below, so the
refutation predicate is demonstrably not a predicate that fires on everything.

## How the left side is computed here (exactly, in `Nat`, two independent ways)

Write the trace as `Tr(H^{2k}) = Σ_{i_0 … i_{2k-1}} H_{i_0 i_1} H_{i_1 i_2} ⋯ H_{i_{2k-1} i_0}`,
so factor `t` (for `t = 0, …, 2k-1`) is `H_{a_t b_t}` with `a_t = t`, `b_t = t+1 mod 2k`.
Under the proof's propagator, pairing factor `s` with factor `t` contributes
`δ_{a_s b_t} δ_{b_s a_t}`, i.e. it FORCES the two index identifications

    i_{a_s} = i_{b_t}      and      i_{b_s} = i_{a_t}
    (that is:  s ~ t+1 (mod 2k)   and   s+1 ~ t (mod 2k) ).

**METHOD A** (`wickTrace`, the primary definition).  For each perfect matching of the
`2k` factors, impose those `2·k` identifications on the `2k` index VARIABLES by
union–find, count the number `c` of resulting equivalence classes, and add `N^c` — the
exact number of index tuples in a set of size `N` satisfying every delta.  Sum over all
`(2k-1)!!` matchings.

**METHOD B** (`wickTraceBrute`, an independent recomputation).  Literally enumerate all
`N^{2k}` index tuples and, for each matching, count by hand how many satisfy every delta.
Method B is exponentially more expensive, so it is run only on the affordable pairs; the
file PROVES the two methods agree on each of those (`nc7_methods_agree`).  A slip in the
union–find/component count could therefore not by itself produce the refutation.

All arithmetic is `Nat` (arbitrary precision, exact).  No floats, no rationals, no
division appears anywhere in the computation of the left side.  The only division in the
file is the exact `binom(2k,k) / (k+1)` inside `catalan`, and that value is independently
cross-checked against `binom(2k,k) - binom(2k,k+1)` (`nc4_catalan_two_ways`).

## Why this is INTERNAL to the proof, not an outside standard imposed on it

The very same evaluator, run at `k = 1` and `k = 2`, reproduces the two moments the proof
itself computes explicitly and by hand:

    ⟨Tr H^2⟩ = N^2        and       ⟨Tr H^4⟩ = 2N^3 + N

for every `N = 1, …, 6` (e.g. `N = 3` gives 9 and 57; `N = 6` gives 36 and 438).  This is
proved as `nc1_reproduces_proofs_own_moments`.  Hence the refutation is not a dispute
about which random-matrix model is meant: the rule that yields the proof's own `N^2` and
`2N^3 + N` cannot simultaneously yield the `N`-independent `C_k`, and the proof's general
formula is inconsistent with the proof's own worked cases.

## Modelling judgments (the kernel checks the arithmetic, not the faithfulness of these)

1. **Propagator.**  `⟨H_ij H_kl⟩ = δ_il δ_jk` is taken verbatim from the proof (it is the
   GUE/Wigner normalisation with unit variance and no `1/N`).  Any overall variance
   rescaling `σ²` multiplies every `2k`-moment by the SAME constant `σ^{2k}`, so it cannot
   turn an `N`-dependent left side into the `N`-free `C_k`; the refutation is robust to
   that choice.  What it is NOT robust to is silently inserting the `1/N^{k+1}` (or
   `1/N` per entry) normalisation that the correct asymptotic statement carries — but the
   refuted sentence contains no such normalisation, which is precisely the error.
2. **Centred + Gaussian ⇒ Wick.**  Odd moments vanish and even moments are the sum over
   perfect matchings of products of pairwise covariances (Isserlis' theorem).  This is the
   proof's own stated evaluation method; the file implements it, it does not assume it.
3. **Index alphabet.**  Indices range over a set of size `N`; the file uses `{0,…,N-1}`.
   Only equalities between indices ever matter, so the labelling is immaterial.
4. **Union–find is by global relabelling** (`unite` rewrites every occurrence of the
   larger label), so after a single pass over the constraint list the labels are exactly
   the equivalence classes of the transitive closure.  `nc5_components_have_teeth` pins
   the component counter down on hand-checked cases (including a matching that collapses
   all four variables into ONE class), so it is not returning a constant.
5. **Matching enumeration is complete and duplicate-free** by the standard "pair the first
   element with each other element, recurse on the rest" scheme, run with explicit fuel
   (structural recursion, kernel-reducible).  Its cardinality is verified to be the double
   factorial `(2k-1)!! = 1, 3, 15, 105, 945` (`nc6_matching_counts`); an under- or
   over-counting enumeration would fail that test.
6. **Fail-closed fuel.**  `matchingsAux` with fuel `0` returns the EMPTY list of matchings,
   not `[[]]`; an under-fuelled call therefore yields the value `0`, which agrees with no
   Catalan number `C_k ≥ 1` for the wrong reason — but `nc6_matching_counts` and
   `nc7_methods_agree` both fail loudly in that case, so exhausted fuel cannot silently
   manufacture a refutation.  (`matchingsOf n` is called with fuel `n+1`, ample.)
7. **The claim's own conclusion is expressible and can be TRUE in this model** — it holds
   at `(k,N) = (1,1)` (`nc2_sole_agreement_is_1_1`).  `claimHolds` is not false by
   construction.
8. Everything is discharged by kernel `decide`.  No `native_decide`, no `axiom`, no
   `sorry`, no well-founded recursion, no `partial`.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace MSE_811862

/-! ## §0. Tiny list utilities (self-contained; no core `List` API relied upon) -/

def lmap {α β : Type} (f : α → β) : List α → List β
  | [] => []
  | a :: r => f a :: lmap f r

def lapp {α : Type} : List α → List α → List α
  | [], m => m
  | a :: r, m => a :: lapp r m

def joinL {α : Type} : List (List α) → List α
  | [] => []
  | l :: ls => lapp l (joinL ls)

def llen {α : Type} : List α → Nat
  | [] => 0
  | _ :: r => 1 + llen r

def allB {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | a :: r => p a && allB p r

def sumN : List Nat → Nat
  | [] => 0
  | a :: r => a + sumN r

/-- `[0, 1, …, n-1]`. -/
def upto : Nat → List Nat
  | 0 => []
  | k + 1 => lapp (upto k) [k]

/-- `i`-th entry of a `Nat` list; `0` out of range.  All indices used below come from
`upto m` applied to lists of length exactly `m`, so the default is never reached. -/
def getD : List Nat → Nat → Nat
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: r, k + 1 => getD r k

def memN (x : Nat) : List Nat → Bool
  | [] => false
  | a :: r => Nat.beq a x || memN x r

/-- Delete the first occurrence of `x`. -/
def removeFirst (x : Nat) : List Nat → List Nat
  | [] => []
  | a :: r => match Nat.beq a x with
    | true => r
    | false => a :: removeFirst x r

/-- Exact `b^e`, structurally recursive (kernel-reducible; `Nat.mul` is exact). -/
def npow (b : Nat) : Nat → Nat
  | 0 => 1
  | e + 1 => b * npow b e

/-- Number of distinct entries of a `Nat` list. -/
def distinctCount : List Nat → Nat
  | [] => 0
  | a :: r => (match memN a r with | true => 0 | false => 1) + distinctCount r

/-! ## §1. Perfect matchings of the `2k` matrix factors

Wick/Isserlis pairs up the `2k` factors of `Tr(H^{2k})` in every possible way.
`matchingsAux` is the textbook enumeration: pair the first element with each of the
others, recurse on the remainder.  It is complete and duplicate-free, and the fuel makes
it structurally recursive.  Fuel `0` returns NO matchings (fail-closed). -/

def matchingsAux : Nat → List Nat → List (List (Nat × Nat))
  | 0, _ => []
  | _ + 1, [] => [[]]
  | f + 1, x :: rest =>
      joinL (lmap (fun y =>
          lmap (fun m => (x, y) :: m) (matchingsAux f (removeFirst y rest)))
        rest)

/-- All perfect matchings of `{0, …, n-1}` (empty list when `n` is odd). -/
def matchingsOf (n : Nat) : List (List (Nat × Nat)) := matchingsAux (n + 1) (upto n)

/-! ## §2. The delta constraints imposed by one pairing

Factor `t` of `Tr(H^{2k})` is `H_{a_t b_t}` with `a_t = t`, `b_t = t+1 mod 2k`.
The proof's propagator `⟨H_ij H_kl⟩ = δ_il δ_jk` turns the pairing `{s, t}` into the two
index identifications `i_{a_s} = i_{b_t}` and `i_{b_s} = i_{a_t}`. -/

/-- Cyclic successor modulo `m` (`m = 2k`). -/
def nextIdx (m i : Nat) : Nat := (i + 1) % m

/-- The delta constraints (as pairs of index-variable names) of a whole matching. -/
def consOf (m : Nat) (mt : List (Nat × Nat)) : List (Nat × Nat) :=
  joinL (lmap (fun (p : Nat × Nat) => [(p.1, nextIdx m p.2), (nextIdx m p.1, p.2)]) mt)

/-! ## §3. METHOD A — union–find on the index variables, contribution `N^c`

`unite` merges by REWRITING every occurrence of the larger label with the smaller, so a
single pass over the constraint list leaves the labels equal to the equivalence classes
of the transitive closure of the constraints.  The number of index tuples over an
alphabet of size `N` satisfying all deltas is then exactly `N^{#classes}`. -/

def relabel (old new : Nat) (lbl : List Nat) : List Nat :=
  lmap (fun c => match Nat.beq c old with | true => new | false => c) lbl

def unite (lbl : List Nat) (x y : Nat) : List Nat :=
  let a := getD lbl x
  let b := getD lbl y
  match Nat.ble a b with
  | true => relabel b a lbl
  | false => relabel a b lbl

def uniteAll : List Nat → List (Nat × Nat) → List Nat
  | lbl, [] => lbl
  | lbl, p :: r => uniteAll (unite lbl p.1 p.2) r

/-- Number of independent index variables surviving one pairing. -/
def compOfMatching (m : Nat) (mt : List (Nat × Nat)) : Nat :=
  distinctCount (uniteAll (upto m) (consOf m mt))

/-- **`⟨Tr(H^{2k})⟩` for an `N × N` matrix, computed exactly (METHOD A).** -/
def wickTrace (k N : Nat) : Nat :=
  sumN (lmap (fun mt => npow N (compOfMatching (2 * k) mt)) (matchingsOf (2 * k)))

/-! ## §4. METHOD B — literal enumeration of all `N^{2k}` index tuples

Independent recomputation of the same quantity with no union–find and no exponentiation:
for every matching, walk the whole index space and count the tuples that satisfy every
delta.  Used only as a cross-check on affordable `(k, N)`. -/

def tuplesOf (N : Nat) : Nat → List (List Nat)
  | 0 => [[]]
  | len + 1 => joinL (lmap (fun t => lmap (fun v => v :: t) (upto N)) (tuplesOf N len))

def satisfies (v : List Nat) (cs : List (Nat × Nat)) : Bool :=
  allB (fun (p : Nat × Nat) => Nat.beq (getD v p.1) (getD v p.2)) cs

/-- **`⟨Tr(H^{2k})⟩` again (METHOD B): brute-force over the index space.** -/
def wickTraceBrute (k N : Nat) : Nat :=
  sumN (lmap (fun mt =>
      sumN (lmap (fun v => match satisfies v (consOf (2 * k) mt) with
              | true => 1
              | false => 0)
        (tuplesOf N (2 * k))))
    (matchingsOf (2 * k)))

def bruteAgrees (k N : Nat) : Bool := Nat.beq (wickTrace k N) (wickTraceBrute k N)

/-! ## §5. The right-hand side: Catalan numbers -/

/-- Pascal's rule; exact, no division. -/
def binom : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, r + 1 => binom n r + binom n (r + 1)

/-- `C_k = binom(2k, k) / (k+1)` — the claim's own right-hand side, verbatim.
The division is exact on these arguments (checked against `catalanAlt`). -/
def catalan (k : Nat) : Nat := binom (2 * k) k / (k + 1)

/-- Independent formula `C_k = binom(2k, k) - binom(2k, k+1)`, used only to certify that
the division in `catalan` is the exact one intended. -/
def catalanAlt (k : Nat) : Nat := binom (2 * k) k - binom (2 * k) (k + 1)

/-! ## §6. The claim, and the refutation predicate -/

/-- The refuted sentence, instantiated at `(k, N)`: `⟨Tr(H^{2k})⟩ = C_k`. -/
def claimHolds (k N : Nat) : Bool := Nat.beq (wickTrace k N) (catalan k)

/-- **Refutation predicate.**  True exactly when `(k, N)` is an admissible instance of the
claim (`k ≥ 1`, `N ≥ 1`) and the asserted equality FAILS there. -/
def refutesAt (k N : Nat) : Bool :=
  Nat.ble 1 k && Nat.ble 1 N && !(claimHolds k N)

/-! ## §7. THE WITNESS — `k = 1`, `N = 2` -/

/-- The left side is exactly 4: `⟨Tr(H^2)⟩ = Σ_{i,j} δ_ii δ_jj = N² = 4`. -/
theorem lhs_1_2 : Nat.beq (wickTrace 1 2) 4 = true := by decide

/-- The right side is exactly 1: `C_1 = binom(2,1)/2 = 1`. -/
theorem rhs_1 : Nat.beq (catalan 1) 1 = true := by decide

/-- The asserted equality fails at the witness. -/
theorem claim_fails_1_2 : claimHolds 1 2 = false := by decide

/-- **THE REFUTATION.** -/
theorem refuted_1_2 : refutesAt 1 2 = true := by decide

/-- The same refutation with both integers spelled out in one statement. -/
theorem refuted_1_2_explicit :
    (Nat.beq (wickTrace 1 2) 4 && Nat.beq (catalan 1) 1 && refutesAt 1 2) = true := by
  decide

/-! ## §8. Further exact witnesses from the same exhaustive scan -/

/-- `(k=2, N=2)`: `⟨Tr H^4⟩ = 18` against `C_2 = 2`. -/
theorem refuted_2_2 :
    (Nat.beq (wickTrace 2 2) 18 && Nat.beq (catalan 2) 2 && refutesAt 2 2) = true := by
  decide

/-- `(k=3, N=2)`: `⟨Tr H^6⟩ = 120` against `C_3 = 5`. -/
theorem refuted_3_2 :
    (Nat.beq (wickTrace 3 2) 120 && Nat.beq (catalan 3) 5 && refutesAt 3 2) = true := by
  decide

/-- `(k=4, N=3)`: `⟨Tr H^8⟩ = 5355` against `C_4 = 14`. -/
theorem refuted_4_3 :
    (Nat.beq (wickTrace 4 3) 5355 && Nat.beq (catalan 4) 14 && refutesAt 4 3) = true := by
  decide

/-- `(k=5, N=6)`: `⟨Tr H^10⟩ = 2521260` against `C_5 = 42`.  For scale, the leading term
of the CORRECT asymptotic statement is `C_5 · N^6 = 42 · 46656 = 1959552` — the same order
of magnitude as the exact value, and nothing like `42`.  (Heaviest kernel computation in
the file: 945 pairings on 10 factors.) -/
theorem refuted_5_6 :
    (Nat.beq (wickTrace 5 6) 2521260
      && Nat.beq (catalan 5) 42
      && Nat.beq (42 * npow 6 6) 1959552
      && refutesAt 5 6) = true := by
  decide

/-! ## §9. Exhaustive scan

Over `1 ≤ k ≤ 3` and `1 ≤ N ≤ 4`: every pair refutes the claim EXCEPT the degenerate
`(1,1)`, where the claim is asserted to HOLD.  A single statement therefore certifies both
halves of the record's finding. -/

def scanRow (k : Nat) (Ns : List Nat) : Bool :=
  allB (fun N =>
      match Nat.beq k 1 && Nat.beq N 1 with
      | true => claimHolds k N          -- the sole coincidence, asserted positively
      | false => refutesAt k N)
    Ns

theorem scan_k3_N4 : allB (fun k => scanRow k [1, 2, 3, 4]) [1, 2, 3] = true := by decide

/-! ## §10. NEGATIVE CONTROLS

If the modelling were vacuous — a Wick evaluator that returned a constant, a matching
enumerator that produced nothing (or everything), a component counter stuck at `2k`, a
`claimHolds` false by construction, or a Catalan function that was not Catalan — the
theorems below would fail and the file would not compile. -/

/-- **NC1 — THE DECISIVE CONTROL: the evaluator reproduces the PROOF'S OWN worked cases.**
The proof computes, by hand and explicitly, `⟨Tr H^2⟩ = N^2` and `⟨Tr H^4⟩ = 2N^3 + N`.
The very same code that produces the refutation reproduces both, for every `N = 1,…,6`
(e.g. `N=3`: 9 and 57; `N=6`: 36 and 438).  So the refutation is internal to the proof:
the rule that gives the proof its own `N`-dependent answers cannot also give the
`N`-independent `C_k`. -/
def reproducesProofOwnMoments (N : Nat) : Bool :=
  Nat.beq (wickTrace 1 N) (N * N) && Nat.beq (wickTrace 2 N) (2 * N * N * N + N)

theorem nc1_reproduces_proofs_own_moments :
    allB reproducesProofOwnMoments [1, 2, 3, 4, 5, 6] = true := by decide

/-- **NC2 — the claim CAN be true in this model.**  At the degenerate `(k,N) = (1,1)` the
asserted equality genuinely holds (`⟨Tr H^2⟩ = 1 = C_1`), so `claimHolds` is not a
predicate that is false by construction and `refutesAt` does not fire on everything. -/
theorem nc2_sole_agreement_is_1_1 :
    (claimHolds 1 1 && Nat.beq (wickTrace 1 1) 1 && !(refutesAt 1 1)) = true := by decide

/-- **NC3 — the left side genuinely depends on `N`, the right side genuinely does not.**
This is the exact shape of the error: an `N`-dependent quantity equated to an `N`-free
one.  All six values of `⟨Tr H^2⟩` for `N = 1,…,6` are pairwise distinct while `C_1` is a
single number. -/
theorem nc3_lhs_N_dependent :
    (Nat.beq (wickTrace 1 1) 1 && Nat.beq (wickTrace 1 2) 4
      && Nat.beq (wickTrace 1 3) 9 && Nat.beq (wickTrace 1 4) 16
      && Nat.beq (wickTrace 1 5) 25 && Nat.beq (wickTrace 1 6) 36
      && Nat.beq (catalan 1) 1) = true := by decide

/-- **NC4 — Catalan is really Catalan, and the division in `catalan` is exact.**  Two
independent formulas agree on `k = 0,…,8`, and the values are the familiar
`1, 1, 2, 5, 14, 42, 132, 429, 1430`. -/
theorem nc4_catalan_two_ways :
    (allB (fun k => Nat.beq (catalan k) (catalanAlt k)) [0, 1, 2, 3, 4, 5, 6, 7, 8]
      && Nat.beq (catalan 0) 1 && Nat.beq (catalan 1) 1 && Nat.beq (catalan 2) 2
      && Nat.beq (catalan 3) 5 && Nat.beq (catalan 4) 14 && Nat.beq (catalan 5) 42
      && Nat.beq (catalan 6) 132 && Nat.beq (catalan 7) 429
      && Nat.beq (catalan 8) 1430) = true := by decide

/-- **NC5 — the component counter has teeth.**  At `k = 1` the single pairing leaves both
index variables free (2 classes, hence `N^2`, exactly the proof's own `Σ_{i,j} δ_ii δ_jj`).
At `k = 2` the three pairings leave `3, 1, 3` classes: the CROSSING pairing `{0,2},{1,3}`
collapses all four index variables into ONE class, which is precisely where the `+N`
of `2N^3 + N` comes from.  A counter stuck at a constant would fail here. -/
theorem nc5_components_have_teeth :
    (Nat.beq (compOfMatching 2 [(0, 1)]) 2
      && Nat.beq (compOfMatching 4 [(0, 1), (2, 3)]) 3
      && Nat.beq (compOfMatching 4 [(0, 2), (1, 3)]) 1
      && Nat.beq (compOfMatching 4 [(0, 3), (1, 2)]) 3) = true := by decide

/-- **NC6 — the pairing enumeration is complete and duplicate-free**: its cardinality is
the double factorial `(2k-1)!! = 1, 3, 15, 105, 945` for `k = 1,…,5`, it is EMPTY on an
odd number of factors, and the fuel is not exhausted (fuel `0` would give `0` matchings
and this test would fail). -/
theorem nc6_matching_counts :
    (Nat.beq (llen (matchingsOf 2)) 1
      && Nat.beq (llen (matchingsOf 4)) 3
      && Nat.beq (llen (matchingsOf 6)) 15
      && Nat.beq (llen (matchingsOf 8)) 105
      && Nat.beq (llen (matchingsOf 10)) 945
      && Nat.beq (llen (matchingsOf 3)) 0
      && Nat.beq (llen (matchingsOf 5)) 0) = true := by decide

/-- **NC7 — the two independent methods agree.**  Method A (union–find, `N^c`) and
Method B (literal enumeration of all `N^{2k}` index tuples) return the same integer on
every pair cheap enough to run both.  A bug in the union–find could not survive this. -/
theorem nc7_methods_agree :
    (bruteAgrees 1 2 && bruteAgrees 1 4 && bruteAgrees 1 6
      && bruteAgrees 2 2 && bruteAgrees 2 3 && bruteAgrees 2 4
      && bruteAgrees 3 2) = true := by decide

/-- **NC8 — the index-space enumeration used by Method B is itself complete**: `N^{2k}`
tuples, each of length `2k`. -/
theorem nc8_tuple_space_complete :
    (Nat.beq (llen (tuplesOf 2 4)) 16
      && Nat.beq (llen (tuplesOf 3 4)) 81
      && Nat.beq (llen (tuplesOf 2 6)) 64
      && allB (fun v => Nat.beq (llen v) 4) (tuplesOf 3 4)) = true := by decide

/-- **NC9 — the delta constraints are the propagator's, not something weaker.**  At
`k = 1` the pairing `{0,1}` yields the constraints `i_0 = i_0`, `i_1 = i_1` (the two
deltas `δ_ii δ_jj` the proof writes down), while at `k = 2` the crossing pairing yields
four constraints that chain all four variables together.  A `consOf` that emitted no
constraints would make every count `N^{2k}` and NC1 would fail; one that emitted too many
would collapse everything and NC1 would fail too. -/
theorem nc9_constraints_are_the_propagators :
    (Nat.beq (llen (consOf 2 [(0, 1)])) 2
      && Nat.beq (llen (consOf 4 [(0, 2), (1, 3)])) 4
      && Nat.beq (nextIdx 2 1) 0 && Nat.beq (nextIdx 4 3) 0
      && Nat.beq (nextIdx 4 1) 2) = true := by decide

/-- **NC10 — the gap is not a rounding artefact of size 1**: at `(k,N) = (3,2)` the exact
left side is 24 TIMES the asserted right side, and at `(k,N) = (5,6)` it is 60030 times
it.  Meanwhile the CORRECT asymptotic leading term `C_k · N^{k+1}` is within a factor 2 of
the exact value at `(5,6)` — the claim's error is the missing `N^{k+1}`, exactly as the
record states. -/
theorem nc10_gap_is_structural :
    (Nat.beq (wickTrace 3 2) (24 * catalan 3)
      && Nat.beq (wickTrace 5 6) 2521260
      && Nat.beq 2521260 (60030 * catalan 5)
      && Nat.ble (catalan 5 * npow 6 6) 2521260
      && Nat.ble 2521260 (2 * (catalan 5 * npow 6 6))) = true := by decide

end MSE_811862

#human_review_axiom_audit
