/-!
# Finite kernel of the C_9[K_2] objection (clique blowup of the nine-cycle)

Scope. This file certifies ONLY the finite, local part of the archived refutation of
the clique-blowup recolourability conjecture of Belavadi, Cameron and Sintiari:

* the 18-vertex graph `C_9[K_2]`, with the adjacency rule of the archived checker
  `BugBank/certificates/discoveries_20260910/prime_blowup_check.py`
  (sha256 `ab767b7d42450ad0d647ddf24191989e8ffc60a95c41d8c0d636b74e7bf49fba`):
  vertices `0..17`, clique index `v / 2`, and `u ~ v` iff `u ≠ v` and either the clique
  indices agree or they differ by `1` or `8` modulo `9`;
* the archived six-colouring `six = (1,2,3,4,5,6) * 3`, i.e. periodic palettes
  `{1,2}, {3,4}, {5,6}` around the cycle;
* the archived five-colouring `five`.

It proves that `six` is a proper colouring using all six colours in which every vertex
sees all five other colours on its neighbours, hence no single-vertex recolouring of
`six` is proper and no proper six-colouring differs from `six` at exactly one vertex
(`six` is an isolated vertex of the reconfiguration graph `R_6`). It also proves that a
proper colouring with at most five colours exists, so six colours is at least
`chi + 1`, and that a second proper six-colouring exists, so `R_6` has an isolated
vertex and at least two vertices.

NOT certified here: that `C_9` is prime, that every induced subgraph of `C_9` is
recolourable (the antecedent of the conjecture), the value `chi = 5` (only `chi ≤ 5`
is shown), the general statement for `C_n[K_2]`, or the count `90 * 2^n`. Those remain
ordinary mathematical arguments in the archive. This artifact is outside the frozen
285-record release. Core Lean only; no Mathlib.
-/

namespace C9K2

/-- Adjacency in `C_9[K_2]`; verbatim translation of the archived checker's edge rule
`u // 2 == v // 2 or (u // 2 - v // 2) % 9 in (1, 8)` for `u ≠ v`. -/
def adj (u v : Fin 18) : Bool :=
  decide (u ≠ v) &&
    (decide (u.val / 2 = v.val / 2) ||
     decide ((u.val / 2 + 9 - v.val / 2) % 9 = 1) ||
     decide ((u.val / 2 + 9 - v.val / 2) % 9 = 8))

/-- The archived six-colouring `(1,2,3,4,5,6) * 3`. -/
def six (v : Fin 18) : Nat := v.val % 6 + 1

/-- The archived five-colouring. -/
def fiveList : List Nat := [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 1, 5, 2, 3, 4, 5]

def five (v : Fin 18) : Nat := fiveList.getD v.val 0

/-- A colouring is proper when adjacent vertices receive different colours. -/
abbrev Proper (f : Fin 18 → Nat) : Prop := ∀ u v : Fin 18, adj u v = true → f u ≠ f v

/-- Recolour the single vertex `v` with colour `c`. -/
def recolour (f : Fin 18 → Nat) (v : Fin 18) (c : Nat) : Fin 18 → Nat :=
  fun w => if w = v then c else f w

/-! ## The graph -/

theorem adj_irrefl : ∀ v : Fin 18, adj v v = false := by decide

theorem adj_symm : ∀ u v : Fin 18, adj u v = adj v u := by decide

/-- Every vertex has exactly five neighbours (so the graph has 45 edges). -/
theorem five_regular :
    ∀ v : Fin 18, ((List.finRange 18).filter (fun u => adj u v)).length = 5 := by decide

/-! ## The six-colouring -/

theorem six_proper : Proper six := by decide

theorem six_range : ∀ v : Fin 18, 1 ≤ six v ∧ six v ≤ 6 := by decide

theorem six_uses_all : ∀ c : Fin 6, ∃ v : Fin 18, six v = c.val + 1 := by decide

/-- Saturation: every vertex sees each of the five other colours on a neighbour. -/
theorem six_saturated :
    ∀ (v : Fin 18) (c : Fin 6), c.val + 1 ≠ six v →
      ∃ u : Fin 18, adj u v = true ∧ six u = c.val + 1 := by decide

/-- Frozen: no single-vertex recolouring of `six` within the six colours is proper. -/
theorem six_frozen (v : Fin 18) (c : Nat) (h1 : 1 ≤ c) (h6 : c ≤ 6) (hne : c ≠ six v) :
    ¬ Proper (recolour six v c) := by
  intro hP
  have hc : (⟨c - 1, by omega⟩ : Fin 6).val + 1 = c := by
    show c - 1 + 1 = c
    omega
  obtain ⟨u, hadj, hu⟩ := six_saturated v ⟨c - 1, by omega⟩ (by rw [hc]; exact hne)
  have huv : u ≠ v := by
    intro h
    rw [h, adj_irrefl] at hadj
    exact Bool.noConfusion hadj
  have h := hP u v hadj
  apply h
  show (if u = v then c else six u) = (if v = v then c else six v)
  simp [huv, hu, hc]

/-- Isolation in the reconfiguration graph `R_6`: a proper colouring with colours in
`1..6` that agrees with `six` off a single vertex agrees with it everywhere. -/
theorem six_isolated (g : Fin 18 → Nat) (hP : Proper g)
    (hr : ∀ w : Fin 18, 1 ≤ g w ∧ g w ≤ 6) (v : Fin 18)
    (hagree : ∀ w : Fin 18, w ≠ v → g w = six w) : g v = six v := by
  apply Decidable.byContradiction
  intro hne
  have hg : g = recolour six v (g v) := by
    funext w
    show g w = if w = v then g v else six w
    by_cases hw : w = v
    · simp [hw]
    · simp [hw]; exact hagree w hw
  have hfrozen := six_frozen v (g v) (hr v).1 (hr v).2 hne
  rw [← hg] at hfrozen
  exact hfrozen hP

/-! ## Six colours is at least `chi + 1`, and `R_6` has a second vertex -/

theorem five_proper : Proper five := by decide

theorem five_range : ∀ v : Fin 18, 1 ≤ five v ∧ five v ≤ 5 := by decide

theorem five_ne_six : ∃ v : Fin 18, five v ≠ six v := by decide

/-- The finite kernel in one statement. -/
theorem frozen_six_colouring_certificate :
    Proper six ∧ (∀ c : Fin 6, ∃ v : Fin 18, six v = c.val + 1) ∧
    (∀ (g : Fin 18 → Nat), Proper g → (∀ w, 1 ≤ g w ∧ g w ≤ 6) →
      ∀ v : Fin 18, (∀ w, w ≠ v → g w = six w) → g v = six v) ∧
    (∃ f : Fin 18 → Nat, Proper f ∧ (∀ w, 1 ≤ f w ∧ f w ≤ 5)) ∧
    (∃ f : Fin 18 → Nat, Proper f ∧ (∀ w, 1 ≤ f w ∧ f w ≤ 6) ∧ ∃ v, f v ≠ six v) :=
  ⟨six_proper, six_uses_all, six_isolated,
   ⟨five, five_proper, five_range⟩,
   ⟨five, five_proper, fun w => ⟨(five_range w).1, Nat.le_succ_of_le (five_range w).2⟩,
    five_ne_six⟩⟩

end C9K2

#print axioms C9K2.six_proper
#print axioms C9K2.six_saturated
#print axioms C9K2.six_frozen
#print axioms C9K2.six_isolated
#print axioms C9K2.five_proper
#print axioms C9K2.frozen_six_colouring_certificate
