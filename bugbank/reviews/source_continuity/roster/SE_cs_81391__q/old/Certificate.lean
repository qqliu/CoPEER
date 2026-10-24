/-!
# SE_cs_81391__q -- self-contained Lean 4 refutation certificate

RECORD ID : `SE_cs_81391__q`
QUESTION  : https://cs.stackexchange.com/questions/81391
            (URL inferred mechanically from the record id `SE_cs_<id>__q`; the record itself
            carries no URL field.  The flagged proof lives in the QUESTION body -- this is a
            `__q` record -- so what is refuted below is the asker's own argument.)
ROUTE     : SELF_CONTAINED_LEAN (no imports at all; Lean core `Init` only; kernel `decide`
            throughout -- no `native_decide`, no `partial`, no `sorry`, no `axiom`,
            no well-founded recursion)

## Route note (why not the V2 claim DSL)

`qedbench_certificate_availability_triage/lean_certificates/QEDTemplateV2.lean` was checked
constructor-by-constructor.  `WitnessV2` carries graphs, a weighted digraph, `Nat` lists and
pair lists, and the only sorting-flavoured constructor is `quicksortSortedNLogN (n c : Nat)`,
whose semantics (`quicksortSortedNLogNB`) is a COMPARISON-COUNT bound for first-pivot
quicksort on the already-sorted input `[0 .. n-1]`; it takes no witness array at all.  There
is no constructor mentioning a gap/increment, no constructor whose hypothesis is "positions
0 and m exchange during the first insertion pass", and no constructor whose conclusion reads
off an entry of an algorithm's OUTPUT array.  Neither hypothesis nor conclusion of the claim
under test is expressible over the existing constructors, so the route is
SELF_CONTAINED_LEAN rather than V2_DSL.  (Nothing in the template is modified or imported.)

## The claim being refuted

The record supplies no verbatim source sentence; what is formalised here is the record's own
precise rendering of the flagged inference, quoted verbatim from `refutation_explanation`:

    "The asserted implication is: if during the first insertion step of m-sorting x_0 and
     x_m exchange places (equivalently x_m < x_0), then the final m-sorted array B satisfies
     B[0] = x_m."

Here "m-sorting" is the gap-`m` (increment-`m`) insertion pass of Shellsort: for
`i = m, m+1, ..., N-1`, insert `x_i` backwards along its residue chain `i, i-m, i-2m, ...`.
The record also states the flaw and the true value, again verbatim:

    "m-sorting sorts each gap-m residue chain, so B[0] = min{x_0, x_m, x_{2m}, x_{3m}, ...}
     -- the minimum over the entire chain through position 0, not merely the smaller of x_0
     and x_m.  Whenever some later chain element is smaller than x_m, the element x_m is
     itself displaced further right by a subsequent insertion, and it is that later element
     that ends up in position 0.  The parenthetical in the proof ('which can further switch
     place with x_{2m} and so on') tracks x_0 moving right but overlooks that x_m moves
     right in exactly the same way."

Both halves are certified below: the claim's conclusion is refuted (`claim_false_on_witness`)
AND the record's diagnosis `B[0] = min(chain through 0)` is confirmed, on the witness and
across every exhaustive sweep in this file (`witness_diagnosis`, `nc_repaired_*`).

## Witness (the record's `witness_description`, transcribed unchanged)

    N = 5,  m = 2,  A = (x_0, ..., x_4) = [3, 4, 2, 5, 1]

  * Gap-2 chain through position 0 is `x_0, x_2, x_4 = 3, 2, 1`.
  * HYPOTHESIS HOLDS.  At the first insertion step (`i = m = 2`) we compare `x_2 = 2` with
    `x_0 = 3`; since `2 < 3` they exchange places.  The state after that single step is
    `[2, 4, 3, 5, 1]` -- position 0 now holds `x_m = 2` and position `m` holds `x_0 = 3`, so
    the exchange is exhibited by RUNNING the algorithm, not asserted
    (`first_step_really_exchanges`).
  * CONCLUSION FAILS.  The fully m-sorted array is `B = [1, 4, 2, 5, 3]`, so `B[0] = 1`
    whereas the claim asserts `B[0] = x_m = 2`.
  * DIAGNOSIS CONFIRMED.  `B[0] = 1 = x_4 = x_{2m} = min{3, 2, 1}`, the minimum of the whole
    gap-`m` chain -- exactly the failure mode named in the record.

The record's smallest (degenerate, `m = 1`) witness `N = 3`, `A = [3, 2, 1]` is certified too
(`degenerate_witness_m_eq_1`): `x_1 = 2 < 3 = x_0` so they swap on the first step, yet
`B = [1, 2, 3]` and `B[0] = 1 = x_2 != x_1 = 2`.

## What is certified by kernel `decide` in this file

  (1) `msort_of_witness` / `two_implementations_agree_on_witness`: `B = [1,4,2,5,3]`, computed
      by BOTH implementations the record used -- the gap-`m` insertion pass (`msortIns`) and
      independent per-residue-chain sorting (`msortChain`) -- which agree.
  (2) `first_step_really_exchanges`: the hypothesis is verified by executing exactly one
      insertion step and observing the exchange of positions 0 and `m`.
  (3) `hypothesis_holds_conclusion_fails` / `claim_false_on_witness`: hypothesis true,
      conclusion false, on the same instance.
  (4) `witness_diagnosis`: `B[0]` equals the chain minimum and equals `x_{2m}`.
  (5) `gap_sort_first_entry_claim_is_false` / `stated_implication_fails`: the universally
      quantified claim is false, by instantiation at the witness.
  (6) Exhaustive sweeps (all 120 permutations of `[1..5]`; all 24 permutations of `[1..4]`;
      all 243 length-5 arrays over `{1,2,3}`, i.e. WITH ties) reproducing, at kernel scale,
      the record's "0 exceptions out of 36243 counterexamples" control.

## Modelling judgments (a reviewer should check each)

  1. ARRAYS are `List Nat`, indexed by `nth` (out-of-range reads return `0`) and updated by
     `setAt` (out-of-range writes are no-ops).  Every index used in every theorem is in
     range, so these conventions are never load-bearing.
  2. VALUES are `Nat`, so "<" is exact integer comparison; no floats, no sentinels.
  3. `msortIns m a` is the textbook gap-`m` insertion pass, transcribed literally:
     `for i in m..N-1: key := a[i]; j := i; while j >= m and a[j-m] > key: a[j] := a[j-m];
     j := j-m; a[j] := key`.  The comparison is STRICT (`a[j-m] > key`), i.e. the pass is
     stable -- the standard convention, and the one under which the source's "they exchange
     places" is a real exchange rather than a tie-break.
  4. Both loops are made structurally recursive by an explicit FUEL argument (Lean core has no
     `while`).  The fuel supplied is provably generous: the outer loop gets `N` (it runs
     `N - m` times) and each inner shift gets `i + 1` (`j` strictly decreases by `m >= 1` per
     iteration, starting from `j = i`).  Running out of fuel would only ever TRUNCATE the
     computation; that it does not is witnessed independently by (1) -- the fuel-driven
     implementation agrees with the fuel-independent chain-sorting implementation on the
     witness and on every array of all three exhaustive sweeps.
  5. `msortChain m a` is the SECOND, independent implementation: for each residue
     `r = m-1, ..., 0` it gathers the values at indices `r, r+m, r+2m, ...`, sorts them with a
     plain insertion sort, and scatters them back.  It shares no code with `msortIns` beyond
     `nth`/`setAt`.  This mirrors the record's own two-implementation cross-check.
  6. The HYPOTHESIS is modelled in the strong, literal form `hypExchangeB`: run one insertion
     step and demand that positions 0 and `m` have genuinely exchanged distinct values.  The
     source's own paraphrase `x_m < x_0` is modelled separately (`hypLessB`) and the two are
     certified EQUIVALENT across every sweep (`nc_hypothesis_paraphrase_is_faithful`), so the
     refutation cannot be blamed on reading the hypothesis too weakly.
  7. The CONCLUSION is modelled as literally as possible: `B[0] = x_m`, where `x_m` is the
     value at index `m` of the ORIGINAL array `A` (not of `B`).
  8. `m = 0` is degenerate (`msortIns 0` is the identity); it is excluded from every sweep,
     and the witness uses `m = 2 >= 2`, a genuine gap, so nothing here depends on the
     degenerate case.  The record's `m = 1` witness (plain insertion sort) is included only as
     a secondary confirmation.
  9. HUMAN-ADJUDICATION STEP that Lean cannot discharge: Lean certifies the crisp proposition
     "there is an array and a gap at which the first insertion step exchanges positions 0 and
     m yet the m-sorted array does not begin with x_m".  That this is what the source sentence
     asserts -- rather than, say, loose shorthand for "B[0] is the smaller of x_0 and x_m at
     that moment" -- is a reading of English, recorded in `caveats`, not a kernel fact.

## Negative controls (each would FAIL to compile if the modelling were vacuous or rigged)

  * `nc_claim_is_not_always_false`: on `[2,3,1,4,5]` with `m = 2` the hypothesis HOLDS and the
    claim's conclusion HOLDS (`B[0] = 1 = x_2`).  The encoding therefore does not make the
    conclusion unsatisfiable; the witness is a genuine, localised failure.
  * `nc_hypothesis_discriminates`: the hypothesis is neither constantly true nor constantly
    false -- it fails on the already-2-sorted `[1,4,2,5,3]` and holds on the witness; over the
    120 permutations of `[1..5]` it holds for some and fails for others.
  * `nc_msort_is_not_degenerate`: `msortIns 2` is neither the identity nor a full sort on the
    witness, and `msortIns 0` IS the identity (so the degenerate gap is visibly excluded).
  * `nc_msort_permutes_its_input`: over all 120 permutations, the multiset of entries is
    preserved -- the model does not lose or invent values.
  * `nc_msort_really_m_sorts`: over all 120 permutations, every residue chain of the output is
    sorted (so the pass does what "m-sort" means), while the output is NOT fully sorted for
    some input (so it is not secretly a plain sort).
  * `nc_two_implementations_agree_*`: the fuelled insertion pass and the chain sorter agree on
    all 120 permutations of `[1..5]` (`m = 2`), on all 24 permutations of `[1..4]` for every
    `m` in `{1,2,3}`, and on all 243 length-5 arrays over `{1,2,3}` (ties included).
  * `nc_repaired_*`: the REPAIRED statement `B[0] = min(chain through 0)` holds with ZERO
    exceptions on all 120 permutations for every `m` in `{1,2,3,4}`, and on all 243 arrays
    with ties -- reproducing the record's 0-exceptions diagnosis control at kernel scale.
  * `nc_claim_fails_and_holds_within_one_sweep`: within the SAME sweep the flagged claim has
    genuine violations AND genuine satisfied instances, so neither sweep above is true merely
    because its hypotheses are never met.

Everything is `Bool`-valued and structurally recursive over lists of length <= 5; kernel
evaluation is a few hundred thousand `Nat`/list steps.
-/

set_option maxRecDepth 20000
set_option maxHeartbeats 4000000

namespace QEDCert.SE_cs_81391__q

/-! ## 0. Tiny hand-rolled list plumbing (no `List` API is relied on) -/

def lapp {α : Type} : List α → List α → List α
  | [],      ys => ys
  | x :: xs, ys => x :: lapp xs ys

def lmap {α β : Type} : List α → (α → β) → List β
  | [],      _ => []
  | x :: xs, f => f x :: lmap xs f

def joinLL {α : Type} : List (List α) → List α
  | []      => []
  | l :: ls => lapp l (joinLL ls)

def lall {α : Type} : List α → (α → Bool) → Bool
  | [],      _ => true
  | x :: xs, p => p x && lall xs p

def lany {α : Type} : List α → (α → Bool) → Bool
  | [],      _ => false
  | x :: xs, p => p x || lany xs p

def llen {α : Type} : List α → Nat
  | []      => 0
  | _ :: xs => Nat.succ (llen xs)

/-- `[0, 1, ..., k-1]`. -/
def upto : Nat → List Nat
  | 0     => []
  | k + 1 => lapp (upto k) [k]

/-- Array read; out-of-range reads return `0` (never exercised below). -/
def nth : List Nat → Nat → Nat
  | [],      _     => 0
  | x :: _,  0     => x
  | _ :: xs, k + 1 => nth xs k

/-- Array write; out-of-range writes are no-ops (never exercised below). -/
def setAt : List Nat → Nat → Nat → List Nat
  | [],      _,     _ => []
  | _ :: xs, 0,     v => v :: xs
  | x :: xs, k + 1, v => x :: setAt xs k v

/-- Structural equality of `Nat` arrays. -/
def eqL : List Nat → List Nat → Bool
  | [],      []      => true
  | x :: xs, y :: ys => Nat.beq x y && eqL xs ys
  | _,       _       => false

/-- Is the list nondecreasing? -/
def isSortedB : List Nat → Bool
  | []           => true
  | [_]          => true
  | x :: y :: r  => Nat.ble x y && isSortedB (y :: r)

/-! ## 1. Plain insertion sort (used only by the CHAIN implementation and by the controls) -/

def insSorted (x : Nat) : List Nat → List Nat
  | []      => [x]
  | a :: as =>
      match Nat.ble x a with
      | true  => x :: a :: as
      | false => a :: insSorted x as

def sortNat : List Nat → List Nat
  | []      => []
  | a :: as => insSorted a (sortNat as)

/-! ## 2. Implementation A -- the gap-`m` insertion pass, transcribed literally

    for i := m to N-1:
        key := a[i]; j := i
        while j >= m and a[j-m] > key:  a[j] := a[j-m];  j := j - m
        a[j] := key
-/

/-- The inner `while` loop: shift chain elements right while they exceed `key`, then drop
`key` into the hole.  `fuel` bounds the number of shifts (`j` decreases by `m` each time). -/
def shiftIns (m key : Nat) : List Nat → Nat → Nat → List Nat
  | a, j, 0          => setAt a j key
  | a, j, Nat.succ f =>
      match Nat.ble m j && Nat.blt key (nth a (j - m)) with
      | true  => shiftIns m key (setAt a j (nth a (j - m))) (j - m) f
      | false => setAt a j key

/-- The outer `for` loop over `i = m, m+1, ...`, bounded by `fuel` iterations. -/
def msLoop (m n : Nat) : List Nat → Nat → Nat → List Nat
  | a, _, 0          => a
  | a, i, Nat.succ f =>
      match Nat.blt i n with
      | false => a
      | true  => msLoop m n (shiftIns m (nth a i) a i (Nat.succ i)) (Nat.succ i) f

/-- **m-sort, implementation A**: the full gap-`m` insertion pass. -/
def msortIns (m : Nat) (a : List Nat) : List Nat :=
  msLoop m (llen a) a m (llen a)

/-- The array after exactly the FIRST insertion step (`i = m`) -- used to exhibit the
claim's hypothesis by execution. -/
def msortFirstStep (m : Nat) (a : List Nat) : List Nat :=
  msLoop m (llen a) a m 1

/-! ## 3. Implementation B -- sort each residue chain in place (independent of A) -/

/-- Indices of the gap-`m` chain through `r`: `r, r+m, r+2m, ...` below `n`. -/
def chainIdx (n m : Nat) : Nat → Nat → List Nat
  | _, 0          => []
  | r, Nat.succ f =>
      match Nat.blt r n with
      | false => []
      | true  => r :: chainIdx n m (r + m) f

def gather (a : List Nat) : List Nat → List Nat
  | []      => []
  | i :: is => nth a i :: gather a is

def scatter : List Nat → List Nat → List Nat → List Nat
  | a, [],      _       => a
  | a, _ :: _,  []      => a
  | a, i :: is, v :: vs => scatter (setAt a i v) is vs

/-- Sort the single residue chain through `r`. -/
def sortChain (m n : Nat) (a : List Nat) (r : Nat) : List Nat :=
  scatter a (chainIdx n m r n) (sortNat (gather a (chainIdx n m r n)))

/-- Sort chains `r = k-1, k-2, ..., 0`. -/
def chainLoop (m n : Nat) : List Nat → Nat → List Nat
  | a, 0          => a
  | a, Nat.succ r => chainLoop m n (sortChain m n a r) r

/-- **m-sort, implementation B**: sort every gap-`m` residue chain in place. -/
def msortChain (m : Nat) (a : List Nat) : List Nat :=
  chainLoop m (llen a) a m

/-- Every residue chain of `a` is sorted. -/
def allChainsSortedB (m : Nat) (a : List Nat) : Bool :=
  lall (upto m) (fun r => isSortedB (gather a (chainIdx (llen a) m r (llen a))))

/-! ## 4. The claim, as decidable predicates -/

/-- **The claim's hypothesis, literal form**: at the first insertion step, positions `0` and
`m` genuinely exchange (distinct) values.  Verified by running the step. -/
def hypExchangeB (m : Nat) (a : List Nat) : Bool :=
  Nat.blt m (llen a)
    && Nat.beq (nth (msortFirstStep m a) 0) (nth a m)
    && Nat.beq (nth (msortFirstStep m a) m) (nth a 0)
    && !(Nat.beq (nth a 0) (nth a m))

/-- **The source's own paraphrase of the hypothesis**: `x_m < x_0`. -/
def hypLessB (m : Nat) (a : List Nat) : Bool :=
  Nat.blt m (llen a) && Nat.blt (nth a m) (nth a 0)

/-- **The claim's conclusion**: the m-sorted array begins with `x_m`. -/
def conclB (m : Nat) (a : List Nat) : Bool :=
  Nat.beq (nth (msortIns m a) 0) (nth a m)

/-- **The claim at one instance**: hypothesis implies conclusion. -/
def claimAt (m : Nat) (a : List Nat) : Bool :=
  match hypExchangeB m a with
  | false => true
  | true  => conclB m a

/-- The minimum of the gap-`m` chain through position `0`. -/
def chainMin (m : Nat) (a : List Nat) : Nat :=
  nth (sortNat (gather a (chainIdx (llen a) m 0 (llen a)))) 0

/-- **The REPAIRED statement** (the record's diagnosis): `B[0] = min{x_0, x_m, x_{2m}, ...}`.
Note it is unconditional -- no hypothesis needed. -/
def repairedAt (m : Nat) (a : List Nat) : Bool :=
  Nat.beq (nth (msortIns m a) 0) (chainMin m a)

/-! ## 5. The witness -/

/-- `A = [3, 4, 2, 5, 1]`, `N = 5`. -/
def A : List Nat := [3, 4, 2, 5, 1]

/-- The gap `m = 2` -- a genuine gap (`m >= 2`), not the degenerate insertion-sort case. -/
def mW : Nat := 2

/-- `B = m-sort(A)`. -/
def B : List Nat := msortIns mW A

/-! ## 6. The refutation -/

/-- `B = [1, 4, 2, 5, 3]`. -/
theorem msort_of_witness : eqL B [1, 4, 2, 5, 3] = true := by decide

/-- The two independent implementations agree on the witness (the record's cross-check). -/
theorem two_implementations_agree_on_witness :
    eqL (msortIns mW A) (msortChain mW A) = true := by decide

/-- **Hypothesis, by execution.**  After exactly one insertion step the array is
`[2, 4, 3, 5, 1]`: position `0` holds `x_m = 2` and position `m` holds `x_0 = 3`, so `x_0` and
`x_m` really did "switch place during the first pass"; the source's paraphrase `x_m < x_0`
holds as well. -/
theorem first_step_really_exchanges :
    (eqL (msortFirstStep mW A) [2, 4, 3, 5, 1]
      && hypExchangeB mW A
      && hypLessB mW A) = true := by decide

/-- **MAIN (instance form).**  The hypothesis holds and the conclusion fails: `B[0] = 1`,
whereas the claim asserts `B[0] = x_m = 2`. -/
theorem hypothesis_holds_conclusion_fails :
    (hypExchangeB mW A
      && !(conclB mW A)
      && Nat.beq (nth B 0) 1
      && Nat.beq (nth A mW) 2) = true := by decide

/-- The same, as the claim evaluating to `false` on the witness. -/
theorem claim_false_on_witness : claimAt mW A = false := by decide

/-- **The record's diagnosis, confirmed.**  `B[0]` is the minimum of the WHOLE gap-`m` chain
through position `0` (`{x_0, x_2, x_4} = {3, 2, 1}`), and here that minimum is `x_{2m} = x_4 =
1`, not `x_m`. -/
theorem witness_diagnosis :
    (Nat.beq (nth B 0) (chainMin mW A)
      && Nat.beq (chainMin mW A) 1
      && Nat.beq (nth A 4) 1
      && eqL (gather A (chainIdx (llen A) mW 0 (llen A))) [3, 2, 1]) = true := by decide

/-- **MAIN (universal form).**  The claim, universally quantified over gaps and arrays, is
false. -/
theorem gap_sort_first_entry_claim_is_false :
    ¬ ∀ (m : Nat) (a : List Nat), claimAt m a = true := by
  intro h
  exact absurd (h mW A) (by decide)

/-- **MAIN (implication form).**  Stated the way the source states it: "if `x_0` and `x_m`
exchange on the first step then `B[0] = x_m`". -/
theorem stated_implication_fails :
    ¬ ∀ (m : Nat) (a : List Nat),
        hypExchangeB m a = true → Nat.beq (nth (msortIns m a) 0) (nth a m) = true := by
  intro h
  exact absurd (h mW A (by decide)) (by decide)

/-- The record's smallest, degenerate witness (`m = 1`, plain insertion sort): `A' = [3,2,1]`,
the first step swaps `x_0` and `x_1`, yet `B' = [1,2,3]` and `B'[0] = 1 = x_2 != 2 = x_1`. -/
theorem degenerate_witness_m_eq_1 :
    (hypExchangeB 1 [3, 2, 1]
      && eqL (msortIns 1 [3, 2, 1]) [1, 2, 3]
      && eqL (msortChain 1 [3, 2, 1]) [1, 2, 3]
      && !(conclB 1 [3, 2, 1])
      && claimAt 1 [3, 2, 1] == false) = true := by decide

/-! ## 7. Exhaustive sweeps -/

/-- All insertions of `x` into `l`. -/
def insertsOf (x : Nat) : List Nat → List (List Nat)
  | []      => [[x]]
  | a :: as => (x :: a :: as) :: lmap (insertsOf x as) (fun t => a :: t)

/-- All permutations of a list. -/
def permsOf : List Nat → List (List Nat)
  | []      => [[]]
  | a :: as => joinLL (lmap (permsOf as) (fun p => insertsOf a p))

/-- All 120 permutations of `[1,2,3,4,5]`. -/
def perms5 : List (List Nat) := permsOf [1, 2, 3, 4, 5]

/-- All 24 permutations of `[1,2,3,4]`. -/
def perms4 : List (List Nat) := permsOf [1, 2, 3, 4]

/-- All length-`k` tuples over the alphabet `vals` (arrays WITH ties). -/
def tuples (vals : List Nat) : Nat → List (List Nat)
  | 0     => [[]]
  | k + 1 => joinLL (lmap (tuples vals k) (fun t => lmap vals (fun v => v :: t)))

/-- All 243 length-5 arrays over `{1,2,3}`. -/
def ties5 : List (List Nat) := tuples [1, 2, 3] 5

/-- A counterexample WITH repeated keys, used to show `ties5` is populated by relevant
arrays: `[3,1,2,1,1]` at `m = 2` m-sorts to `[1,1,2,1,3]`, so `B[0] = 1 != 2 = x_m`. -/
def Aties : List Nat := [3, 1, 2, 1, 1]

theorem nc_sweeps_are_populated :
    (Nat.beq (llen perms5) 120
      && Nat.beq (llen perms4) 24
      && Nat.beq (llen ties5) 243
      && lany perms5 (fun a => eqL a A)
      && lany ties5 (fun a => eqL a Aties)
      && claimAt mW Aties == false) = true := by decide

/-! ## 8. Negative controls -/

/-- **NEGATIVE CONTROL 1 (the headline control).**  The claim's conclusion is NOT always
false under this encoding: on `[2,3,1,4,5]` with `m = 2` the hypothesis holds (`1 < 2`) AND
the conclusion holds (`B = [1,3,2,4,5]`, `B[0] = 1 = x_2`).  If the modelling were rigged --
e.g. if `conclB` were secretly the negation of something -- this theorem would not compile,
and the witness would be an artefact rather than a genuine localised failure. -/
theorem nc_claim_is_not_always_false :
    (hypExchangeB 2 [2, 3, 1, 4, 5]
      && conclB 2 [2, 3, 1, 4, 5]
      && claimAt 2 [2, 3, 1, 4, 5]
      && eqL (msortIns 2 [2, 3, 1, 4, 5]) [1, 3, 2, 4, 5]) = true := by decide

/-- **NEGATIVE CONTROL 2.**  The hypothesis discriminates: it fails on the already-2-sorted
`[1,4,2,5,3]` (there `x_2 = 2 > 1 = x_0`, no exchange) and holds on the witness; and both
polarities occur across the 120-permutation sweep. -/
theorem nc_hypothesis_discriminates :
    (hypExchangeB mW [1, 4, 2, 5, 3] == false
      && hypExchangeB mW A
      && lany perms5 (fun a => hypExchangeB mW a)
      && lany perms5 (fun a => !(hypExchangeB mW a))) = true := by decide

/-- **NEGATIVE CONTROL 3.**  The literal hypothesis and the source's paraphrase `x_m < x_0`
agree on every one of the 120 permutations, so the refutation does not turn on reading
"switches place with" too weakly or too strongly. -/
theorem nc_hypothesis_paraphrase_is_faithful :
    lall perms5 (fun a => hypExchangeB mW a == hypLessB mW a) = true := by decide

/-- **NEGATIVE CONTROL 4.**  `msortIns 2` is neither the identity nor a full sort on the
witness -- it is a genuine partial (gap-2) sort; and `msortIns 0` IS the identity, which is
why the degenerate gap is excluded from every sweep. -/
theorem nc_msort_is_not_degenerate :
    (eqL (msortIns mW A) A == false
      && isSortedB (msortIns mW A) == false
      && isSortedB A == false
      && eqL (msortIns 0 A) A) = true := by decide

/-- **NEGATIVE CONTROL 5.**  The pass really m-sorts: over all 120 permutations every residue
chain of the output is sorted... -/
theorem nc_msort_really_m_sorts :
    lall perms5 (fun a => allChainsSortedB mW (msortIns mW a)) = true := by decide

/-- ...while the output is NOT fully sorted for some input, so `msortIns` is not secretly an
ordinary sort (which would make `B[0]` the global minimum for trivial reasons). -/
theorem nc_msort_is_not_a_full_sort :
    lany perms5 (fun a => !(isSortedB (msortIns mW a))) = true := by decide

/-- **NEGATIVE CONTROL 6.**  The pass loses and invents nothing: over all 120 permutations the
sorted output equals the sorted input. -/
theorem nc_msort_permutes_its_input :
    lall perms5 (fun a => eqL (sortNat (msortIns mW a)) (sortNat a)) = true := by decide

/-- **NEGATIVE CONTROL 7a.**  Implementations A and B agree on all 120 permutations
(`m = 2`) -- so the fuel bounds in A never truncate and the transcription is faithful. -/
theorem nc_two_implementations_agree_perms5 :
    lall perms5 (fun a => eqL (msortIns mW a) (msortChain mW a)) = true := by decide

/-- **NEGATIVE CONTROL 7b.**  ...and on all 24 permutations of `[1..4]` for every gap
`m` in `{1,2,3}`. -/
theorem nc_two_implementations_agree_perms4_all_gaps :
    lall perms4 (fun a =>
        lall ([1, 2, 3] : List Nat) (fun m => eqL (msortIns m a) (msortChain m a)))
      = true := by decide

/-- **NEGATIVE CONTROL 7c.**  ...and on all 243 length-5 arrays over `{1,2,3}`, i.e. WITH
repeated keys, where stability could have separated the two implementations. -/
theorem nc_two_implementations_agree_with_ties :
    lall ties5 (fun a => eqL (msortIns mW a) (msortChain mW a)) = true := by decide

/-- **NEGATIVE CONTROL 8a (the record's diagnosis control).**  The REPAIRED statement
`B[0] = min(gap-m chain through 0)` holds with ZERO exceptions on all 120 permutations of
`[1..5]`, for each gap `m` in `{1,2,3,4}` (split into one theorem per gap purely to keep each
kernel `decide` small).  This is the kernel-scale reproduction of the record's
"0 exceptions over 36243 counterexamples" check, and it pins the failure on the claim's
identification of `B[0]` with `x_m` rather than on a broken model of m-sorting. -/
theorem nc_repaired_holds_on_perms5_gap1 :
    lall perms5 (fun a => repairedAt 1 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap2 :
    lall perms5 (fun a => repairedAt 2 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap3 :
    lall perms5 (fun a => repairedAt 3 a) = true := by decide

theorem nc_repaired_holds_on_perms5_gap4 :
    lall perms5 (fun a => repairedAt 4 a) = true := by decide

/-- **NEGATIVE CONTROL 8b.**  The same with ties: zero exceptions on all 243 length-5 arrays
over `{1,2,3}`. -/
theorem nc_repaired_holds_with_ties :
    lall ties5 (fun a => repairedAt mW a) = true := by decide

/-- **NEGATIVE CONTROL 9.**  Within the SAME sweep the flagged claim genuinely FAILS on some
arrays and genuinely HOLDS (with its hypothesis satisfied) on others.  Without this, the
sweeps above could be true merely because the hypothesis is never met, or the refutation could
be an artefact of a hypothesis that is met everywhere. -/
theorem nc_claim_fails_and_holds_within_one_sweep :
    (lany perms5 (fun a => !(claimAt mW a))
      && lany perms5 (fun a => hypExchangeB mW a && conclB mW a)
      && lany ties5 (fun a => !(claimAt mW a))) = true := by decide

/-! ## 9. Bundled certificate -/

/-- **Bundled certificate.**  On `A = [3,4,2,5,1]` with `m = 2`: one insertion step exchanges
`x_0 = 3` and `x_m = 2` (so the claim's hypothesis holds); the fully m-sorted array is
`B = [1,4,2,5,3]`, computed identically by two independent implementations; `B[0] = 1 != 2 =
x_m`, so the claim's conclusion fails; and `B[0]` is the minimum `1 = x_{2m}` of the whole
gap-`m` chain `{3,2,1}`, exactly as the record diagnoses. -/
theorem certificate :
    eqL (msortFirstStep mW A) [2, 4, 3, 5, 1] = true
      ∧ hypExchangeB mW A = true
      ∧ hypLessB mW A = true
      ∧ eqL B [1, 4, 2, 5, 3] = true
      ∧ eqL (msortIns mW A) (msortChain mW A) = true
      ∧ conclB mW A = false
      ∧ claimAt mW A = false
      ∧ Nat.beq (nth B 0) (chainMin mW A) = true :=
  ⟨by decide, by decide, by decide, by decide, by decide, by decide, by decide, by decide⟩

end QEDCert.SE_cs_81391__q
