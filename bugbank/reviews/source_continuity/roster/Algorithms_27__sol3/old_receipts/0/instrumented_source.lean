import HumanReviewAxiomAudit
/-
================================================================================
  RECORD:  Algorithms_27__sol3   (Domain: Algorithms — QEDBench templated proof)
  SOURCE:  QEDBench bank, record Algorithms_27, solution 3 (no public URL)
  ROUTE:   SELF_CONTAINED_LEAN   (no imports, no axioms, no `sorry`, no
                                  `native_decide`; every theorem is closed by
                                  kernel-checked `decide` on 6-element instances
                                  with 24 labelled copies)
           The V2 DSL was checked first: QEDTemplateV2 has NO constructor for
           multiset partition / 3-Partition / block-sum claims (its only
           "partition" claims concern max-cut vertex partitions), so the claim
           is not representable there and this certificate is self-contained.
================================================================================

CLAIM BEING REFUTED (Lemma 3 of the 3-Partition -> 12Partition reduction):

    "In any valid 12Partition of S, each subset of 12 elements must contain
     exactly all four copies s^(1)_i .. s^(4)_i for exactly three distinct
     indices i."

Here A = (a_1, ..., a_3m) is a legitimate 3-Partition instance
(sum(A) = mB and B/4 < a_i < B/2 for every i), S consists of FOUR labelled
copies of each a_i (|S| = 12m, sum(S) = 4mB), and a valid 12Partition of S
is a partition of the 12m labelled copies into m subsets of exactly 12
elements, each of sum 4B.  Lemma 3 is what makes the claimed reduction
sound ("12Partition YES => 3-Partition YES"); both the lemma and the
soundness direction are universally quantified over finite integer
instances, hence finitely refutable by a single explicit instance.

WITNESS (primary; verified independently by
partB_feasibility/counterexample_search_qb_opus/verify_Algorithms_27__sol3.py):

    A = (5, 5, 5, 5, 6, 8), m = 2, B = 17.
    Legitimacy: sum(A) = 34 = 2*17, and the window holds exactly:
    4*a_i > 17 (20, 20, 20, 20, 24, 32) and 2*a_i < 17 (10, 10, 10, 10, 12, 16).
    A is a NO instance of 3-Partition: the available triple sums are
    5+5+5 = 15, 5+5+6 = 16, 5+5+8 = 18, 5+6+8 = 19 — never 17
    (decided below by a complete anchored backtracking search).

    Yet S = { s^(c)_i : 1 <= i <= 6, 1 <= c <= 4 } HAS a valid 12Partition
    (0-based below: element (i, c) is copy c of index i, value A[i]):

      block1 = (0,0); (2,0),(2,1),(2,2); (3,0),(3,1),(3,2),(3,3);
               (4,0),(4,1); (5,0),(5,1)
               values [5,5,5,5,5,5,5,5,6,6,8,8], size 12, sum 68 = 4B
      block2 = (0,1),(0,2),(0,3); (1,0),(1,1),(1,2),(1,3); (2,3);
               (4,2),(4,3); (5,2),(5,3)
               values [5,5,5,5,5,5,5,5,6,6,8,8], size 12, sum 68 = 4B

    The blocks are disjoint and cover all 24 labelled copies exactly once.
    Per-index copy multiplicities: block1 uses (1, 0, 3, 4, 2, 2) and
    block2 uses (3, 4, 1, 0, 2, 2) — block1 contains all four copies only
    of index 3 and PARTIAL copy sets of indices 0, 2, 4, 5, so it is not
    "all four copies for exactly three distinct indices"; same for block2.
    Lemma 3 is false, and the reduction maps a NO instance of 3-Partition
    to a YES instance of 12Partition, so it is unsound.

SECONDARY WITNESS (smallest found): A = (4, 4, 4, 4, 4, 6), m = 2, B = 13
(triple sums only 12 and 14, so NO), yet S splits into two valid blocks of
ten 4's + two 6's = 52 = 4B each.

ROOT CAUSE:  In 3-Partition the window B/4 < a_i < B/2 forces exactly three
elements per group of sum B.  After quadrupling, a 12-element block must sum
to T = 4B while each element lies in (T/16, T/8) — a window WIDER than the
(T/24, T/12) needed to force the "4 copies of 3 indices" structure, so T is
reachable by mixed multiplicity patterns with copy counts strictly between
0 and 4.  The lemma silently assumes the size window transfers under
quadrupling; it does not.

MODELLING JUDGMENTS (each pinned by a control theorem below):

 1. VALUES AND LABELS.  An instance is a `List Nat` of values (0-based
    index i carries value `nthVal vals i`); a labelled copy is a pair
    `(i, c) : Nat × Nat` with `c < 4`.  `labelled n` enumerates the full
    labelled set S; its size (24) and duplicate-freeness are pinned by
    `Algorithms_27__sol3_checker_discriminates`.  Nat values suffice: the
    witness values are positive integers, and a refutation for positive
    integers refutes the general claim a fortiori.

 2. LEGITIMACY.  `legit vals m B` checks |A| = 3m, sum(A) = mB, and the
    window EXACTLY as integers: `B < 4*a` and `2*a < B` (no division, no
    floats) — precisely the reduction's stated precondition.

 3. 3-PARTITION DECIDED, NOT ASSUMED.  `hasTP B fuel l` is a COMPLETE
    anchored backtracking search: the first remaining element anchors a
    triple, all (ordered) pairs of the rest complete it, recursion on the
    remainder with fuel = number of triples.  Any partition into triples of
    sum B can be reordered to put its first triple's members first, so
    anchoring loses nothing; ordered pairs only duplicate work.  Fuel m
    suffices (each level removes one triple from 3m elements).  Control:
    `hasTP` returns `true` on the legitimate YES instance (5,5,7,5,6,6)
    (5+5+7 = 17, 5+6+6 = 17), so the `false` verdict on the witness is the
    output of a genuinely complete decision procedure, not a stub.

 4. VALID 12PARTITION.  `validPartition vals B m blocks` demands: exactly m
    blocks; each block has exactly 12 labelled copies summing to 4B; the
    concatenation of the blocks is duplicate-free and equals the labelled
    set S as a set (mutual containment; both sides duplicate-free).  This
    is exactly the definition quoted in the claim.  Controls show it
    rejects a duplicated block list and a wrong block count.

 5. LEMMA 3 SHAPE.  `lemmaShape n b` holds iff every index contributes 0 or
    4 copies to b and exactly three indices contribute 4.  (For a 12-element
    block this is exactly "contains all four copies of exactly three
    distinct indices".)  Control: it ACCEPTS the intended all-copies blocks
    of the YES instance, so its rejection of block1/block2 is not vacuous.

 6. THE CLAIM AS AN INSTANCE.  `lemma3At vals B m blocks` is the exact
    instance "blocks form a valid 12Partition => every block has the lemma
    shape"; `soundnessAt vals B m blocks` is the exact instance
    "(legitimate A) and (blocks form a valid 12Partition of S) => A is a
    3-Partition YES instance".  Both are `false` on the witness and `true`
    on the intended partition of the YES control instance.

 7. This mirrors the exhaustive search and independent re-verification in
    partB_feasibility/counterexample_search_qb_opus/Algorithms_27__sol3.py
    and verify_Algorithms_27__sol3.py (exact integer arithmetic throughout).
================================================================================
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Algorithms27sol3

/-! ### Generic machinery -/

/-- Sum of a `Nat` list. -/
def sumL : List Nat → Nat
  | [] => 0
  | x :: xs => x + sumL xs

/-- `i`-th value of the instance (0 out of range — never load-bearing: every
label used below is in range, pinned by the set-equality with `labelled`). -/
def nthVal : List Nat → Nat → Nat
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, i + 1 => nthVal xs i

/-- Flatten a list of lists. -/
def joinL {α : Type} : List (List α) → List α
  | [] => []
  | l :: ls => l ++ joinL ls

/-- Equality of labelled copies. -/
def pairEq (p q : Nat × Nat) : Bool := p.1 == q.1 && p.2 == q.2

/-- Membership of a labelled copy in a list. -/
def memP (l : List (Nat × Nat)) (p : Nat × Nat) : Bool := l.any (pairEq p)

/-- No labelled copy listed twice. -/
def noDupP : List (Nat × Nat) → Bool
  | [] => true
  | p :: ps => !(memP ps p) && noDupP ps

/-! ### Legitimacy of a 3-Partition instance -/

/-- `vals` is a legitimate 3-Partition instance for `(m, B)`:
`|A| = 3m`, `sum(A) = mB`, and the exact integer window
`B < 4*a` and `2*a < B` (i.e. `B/4 < a < B/2` over ℚ) for every element. -/
def legit (vals : List Nat) (m B : Nat) : Bool :=
  (vals.length == 3 * m) && (sumL vals == m * B)
  && vals.all (fun a => decide (B < 4 * a) && decide (2 * a < B))

/-! ### Complete 3-Partition decision (anchored backtracking) -/

/-- All ways to pick one element of a list, with the remaining list. -/
def oneWithRest : List Nat → List (Nat × List Nat)
  | [] => []
  | x :: xs => (x, xs) :: (oneWithRest xs).map (fun yr => (yr.1, x :: yr.2))

/-- All ways to pick an (ordered) pair of elements, with the remaining list. -/
def pairsWithRest (l : List Nat) : List (Nat × Nat × List Nat) :=
  joinL ((oneWithRest l).map (fun ar =>
    (oneWithRest ar.2).map (fun br => (ar.1, br.1, br.2))))

/-- `hasTP B fuel l`: `l` can be partitioned into triples each of sum `B`
(complete search: the head anchors a triple, every pair of the rest is tried,
recursion on the remainder; `fuel` = number of triples = structural measure). -/
def hasTP (B : Nat) : Nat → List Nat → Bool
  | _, [] => true
  | 0, _ :: _ => false
  | fuel + 1, x :: xs =>
      (pairsWithRest xs).any (fun t =>
        (x + t.1 + t.2.1 == B) && hasTP B fuel t.2.2)

/-! ### Labelled copies and valid 12Partitions -/

/-- The labelled set S: four copies `(i, 0), ..., (i, 3)` of every index
`i < n` (for the witness, n = 6: 24 labelled copies). -/
def labelled (n : Nat) : List (Nat × Nat) :=
  joinL ((List.range n).map (fun i => (List.range 4).map (fun c => (i, c))))

/-- Value carried by a block of labelled copies. -/
def blockSum (vals : List Nat) (b : List (Nat × Nat)) : Nat :=
  sumL (b.map (fun p => nthVal vals p.1))

/-- `blocks` is a VALID 12PARTITION of S: exactly `m` blocks, each of exactly
12 labelled copies summing to `4B`, jointly duplicate-free and equal AS A SET
to the labelled set S (mutual containment; both sides duplicate-free). -/
def validPartition (vals : List Nat) (B m : Nat)
    (blocks : List (List (Nat × Nat))) : Bool :=
  let S := labelled vals.length
  let allC := joinL blocks
  (blocks.length == m)
  && blocks.all (fun b => (b.length == 12) && (blockSum vals b == 4 * B))
  && noDupP allC
  && allC.all (fun p => memP S p)
  && S.all (fun p => memP allC p)

/-- Number of copies of index `i` inside block `b`. -/
def copiesOf (b : List (Nat × Nat)) (i : Nat) : Nat :=
  (b.filter (fun p => p.1 == i)).length

/-- Lemma 3's shape: `b` contains all four copies of exactly three distinct
indices (every index contributes 0 or 4 copies; exactly three contribute 4). -/
def lemmaShape (n : Nat) (b : List (Nat × Nat)) : Bool :=
  (List.range n).all (fun i => (copiesOf b i == 0) || (copiesOf b i == 4))
  && (((List.range n).filter (fun i => copiesOf b i == 4)).length == 3)

/-- LEMMA 3, on one instance: if `blocks` is a valid 12Partition of S then
EVERY block has the lemma shape. -/
def lemma3At (vals : List Nat) (B m : Nat)
    (blocks : List (List (Nat × Nat))) : Bool :=
  !(validPartition vals B m blocks)
  || blocks.all (fun b => lemmaShape vals.length b)

/-- SOUNDNESS of the reduction, on one instance: if `vals` is legitimate and
`blocks` is a valid 12Partition of S, then `vals` is a 3-Partition YES
instance. -/
def soundnessAt (vals : List Nat) (B m : Nat)
    (blocks : List (List (Nat × Nat))) : Bool :=
  !(legit vals m B && validPartition vals B m blocks) || hasTP B m vals

/-! ### The witness -/

/-- A = (5, 5, 5, 5, 6, 8), m = 2, B = 17. -/
def Aw : List Nat := [5, 5, 5, 5, 6, 8]

/-- Block 1 of the exhibited 12Partition (labelled copies, 0-based). -/
def block1 : List (Nat × Nat) :=
  [(0, 0),
   (2, 0), (2, 1), (2, 2),
   (3, 0), (3, 1), (3, 2), (3, 3),
   (4, 0), (4, 1),
   (5, 0), (5, 1)]

/-- Block 2 of the exhibited 12Partition. -/
def block2 : List (Nat × Nat) :=
  [(0, 1), (0, 2), (0, 3),
   (1, 0), (1, 1), (1, 2), (1, 3),
   (2, 3),
   (4, 2), (4, 3),
   (5, 2), (5, 3)]

/-! ### Secondary witness (smallest found) -/

/-- A = (4, 4, 4, 4, 4, 6), m = 2, B = 13. -/
def A2w : List Nat := [4, 4, 4, 4, 4, 6]

def blockS1 : List (Nat × Nat) :=
  [(0, 0), (0, 1), (0, 2), (0, 3),
   (1, 0), (1, 1), (1, 2), (1, 3),
   (2, 0), (2, 1),
   (5, 0), (5, 1)]

def blockS2 : List (Nat × Nat) :=
  [(2, 2), (2, 3),
   (3, 0), (3, 1), (3, 2), (3, 3),
   (4, 0), (4, 1), (4, 2), (4, 3),
   (5, 2), (5, 3)]

/-! ### Control instance (legitimate YES instance, intended-shape partition) -/

/-- A = (5, 5, 7, 5, 6, 6), m = 2, B = 17: a legitimate YES instance
(5 + 5 + 7 = 17 and 5 + 6 + 6 = 17). -/
def Ayes : List Nat := [5, 5, 7, 5, 6, 6]

/-- The reduction's INTENDED block for the triple {0, 1, 2}: all copies. -/
def confBlock1 : List (Nat × Nat) :=
  [(0, 0), (0, 1), (0, 2), (0, 3),
   (1, 0), (1, 1), (1, 2), (1, 3),
   (2, 0), (2, 1), (2, 2), (2, 3)]

/-- The intended block for the triple {3, 4, 5}: all copies. -/
def confBlock2 : List (Nat × Nat) :=
  [(3, 0), (3, 1), (3, 2), (3, 3),
   (4, 0), (4, 1), (4, 2), (4, 3),
   (5, 0), (5, 1), (5, 2), (5, 3)]

/-! ================================================================
    MAIN REFUTATION
    ================================================================ -/

/-- **Refutation of Lemma 3 and of the reduction's soundness.**
A = (5,5,5,5,6,8), m = 2, B = 17 is a LEGITIMATE 3-Partition instance
(sum = mB, exact window B/4 < a < B/2) that is a NO instance (complete
backtracking finds no partition into triples of sum 17).  Yet
[block1, block2] is a VALID 12Partition of its labelled set S — 2 blocks
of 12 labelled copies each, each summing to 4B = 68, jointly covering all
24 copies exactly once — and NEITHER block has Lemma 3's shape: the pinned
per-index multiplicities are (1, 0, 3, 4, 2, 2) and (3, 4, 1, 0, 2, 2),
i.e. partial copy sets, not "all four copies of exactly three indices".
Hence `lemma3At = false` (Lemma 3 fails on a valid 12Partition) and
`soundnessAt = false` (a NO instance maps to a YES instance). -/
theorem Algorithms_27__sol3_refutation :
    legit Aw 2 17 = true
  ∧ hasTP 17 2 Aw = false
  ∧ validPartition Aw 17 2 [block1, block2] = true
  ∧ (List.range 6).map (copiesOf block1) = [1, 0, 3, 4, 2, 2]
  ∧ (List.range 6).map (copiesOf block2) = [3, 4, 1, 0, 2, 2]
  ∧ lemmaShape 6 block1 = false
  ∧ lemmaShape 6 block2 = false
  ∧ lemma3At Aw 17 2 [block1, block2] = false
  ∧ soundnessAt Aw 17 2 [block1, block2] = false := by
  decide

/-- **Secondary witness (smallest found).**  A = (4,4,4,4,4,6), m = 2,
B = 13: legitimate, a NO instance (triple sums are only 12 and 14), yet its
labelled set splits into two valid blocks of ten 4's + two 6's = 52 = 4B,
again with partial copy sets (multiplicities (4,4,2,0,0,2) / (0,0,2,4,4,2)).
The failure is therefore not special to the primary witness. -/
theorem Algorithms_27__sol3_secondary :
    legit A2w 2 13 = true
  ∧ hasTP 13 2 A2w = false
  ∧ validPartition A2w 13 2 [blockS1, blockS2] = true
  ∧ (List.range 6).map (copiesOf blockS1) = [4, 4, 2, 0, 0, 2]
  ∧ lemmaShape 6 blockS1 = false
  ∧ lemmaShape 6 blockS2 = false
  ∧ lemma3At A2w 13 2 [blockS1, blockS2] = false
  ∧ soundnessAt A2w 13 2 [blockS1, blockS2] = false := by
  decide

/-! ================================================================
    NEGATIVE CONTROLS
    ================================================================ -/

/-- **Negative control (anti-strawman): every checker can return the OTHER
verdict on honest data.**  On the legitimate YES instance A = (5,5,7,5,6,6),
B = 17: `hasTP` FINDS the triple partition (so its `false` on the witness is
the output of a complete search, not a stub); the intended all-copies blocks
form a valid 12Partition; `lemmaShape` ACCEPTS both of them (so its `false`
on block1/block2 is not the output of an unsatisfiable predicate); and both
`lemma3At` and `soundnessAt` are `true` here — the refuted statements are
exactly the ones that hold on conforming data.  If any modelling definition
were degenerate (constantly false shape test, vacuous validity test, stub
search), at least one conjunct below would fail to compile. -/
theorem Algorithms_27__sol3_negative_control :
    legit Ayes 2 17 = true
  ∧ hasTP 17 2 Ayes = true
  ∧ validPartition Ayes 17 2 [confBlock1, confBlock2] = true
  ∧ lemmaShape 6 confBlock1 = true
  ∧ lemmaShape 6 confBlock2 = true
  ∧ lemma3At Ayes 17 2 [confBlock1, confBlock2] = true
  ∧ soundnessAt Ayes 17 2 [confBlock1, confBlock2] = true := by
  decide

/-- **Negative control 2: the validity checker discriminates.**  The labelled
set really has 24 distinct copies; `validPartition` rejects a duplicated
block list (copies reused), a single block (wrong count), and swapping in a
wrong-sum block; `blockSum` genuinely reads the instance values (copy (5,0)
of Aw carries value 8, and the two witness blocks sum to 68 each); `legit`
rejects an instance violating the window (4*4 = 16 < 17 and 2*9 = 18 > 17).
So `validPartition Aw 17 2 [block1, block2] = true` above is a real check of
disjointness, coverage, sizes, and sums — not a constantly-true test. -/
theorem Algorithms_27__sol3_checker_discriminates :
    (labelled 6).length = 24
  ∧ noDupP (labelled 6) = true
  ∧ validPartition Aw 17 2 [block1, block1] = false
  ∧ validPartition Aw 17 2 [block1] = false
  ∧ validPartition Aw 17 2 [block1, confBlock2] = false
  ∧ blockSum Aw [(5, 0)] = 8
  ∧ blockSum Aw block1 = 68
  ∧ blockSum Aw block2 = 68
  ∧ legit [4, 5, 5, 5, 6, 9] 2 17 = false := by
  decide

end Algorithms27sol3

#human_review_axiom_audit
