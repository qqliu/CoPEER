import Mathlib

open scoped BigOperators

set_option linter.style.nameCheck false

namespace QEDReview27sol3

/- Source-exact positional construction in Algorithms 27 solution 3. -/
def vals : Fin 6 → ℕ := ![9, 10, 11, 12, 13, 15]

def transformed (p : Fin 6 × Fin 4) : ℕ :=
  vals p.1 + (p.2.val + 1) * 71 * 4 ^ (6 - p.1.val)

def blockA : Finset (Fin 6 × Fin 4) :=
  Finset.univ.filter (fun p => p.2.val = 0 ∨ p.2.val = 3)

def blockB : Finset (Fin 6 × Fin 4) :=
  Finset.univ.filter (fun p => p.2.val = 1 ∨ p.2.val = 2)

theorem Algorithms_27__sol3_refuted :
    (∑ i : Fin 6, vals i) = 2 * 35 ∧
    (∀ i, 35 < 4 * vals i ∧ 2 * vals i < 35) ∧
    Function.Injective transformed ∧
    (∀ p, 0 < transformed p) ∧
    blockA.card = 12 ∧ blockB.card = 12 ∧
    Disjoint blockA blockB ∧ blockA ∪ blockB = Finset.univ ∧
    (∑ p ∈ blockA, transformed p) = 1938440 ∧
    (∑ p ∈ blockB, transformed p) = 1938440 ∧
    (∀ i : Fin 6, (blockA.filter (fun p => p.1 = i)).card = 2 ∧
      (blockB.filter (fun p => p.1 = i)).card = 2) := by
  decide


end QEDReview27sol3
