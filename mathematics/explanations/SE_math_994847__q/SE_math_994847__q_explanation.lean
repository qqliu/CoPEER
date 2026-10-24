/-
Explanation census, record SE_math_994847__q.

Formalises the documented explanation (family and repair) of the retained record, over the
released definitions restated verbatim from
qedbench_certificate_availability_triage/validation/human_review_20260915/lean/SE_math_994847__q.lean
(sha256 9cc9e902c3480dce43d46d8ed83ccdbf053268320f992b5050aa76da1ed8bb2b).

The released file is a Mathlib file (SimpleGraph, adjMatrix, Connected), so this file uses
Mathlib too, through the existing project (toolchain leanprover/lean4:v4.30.0), read-only.

Headline theorems: claim_refuted, family, family_refutes_claim, family_needs_two_vertices,
repair_entry_exact, repair, repair_sum, repair_empty_edge_case, slack and family_not_exact (the
family condition "bipartite" is sufficient for failure but not necessary: the paw graph).
-/

import Mathlib

namespace SE_math_994847_q
open Matrix

/-! ## Released definitions and theorems, restated verbatim -/

def A : Matrix (Fin 3) (Fin 3) ℕ := !![0,1,0; 1,0,1; 0,1,0]

theorem matrix_square_counterexample :
    (∀ i j : Fin 3, i = j ∨ A i j = 1 ∨ ∃ k : Fin 3, A i k = 1 ∧ A k j = 1) ∧
    A 0 1 = 1 ∧ (A^2) 0 1 = 0 := by
  constructor
  · decide
  · norm_num [A, pow_two, Matrix.mul_apply, Fin.sum_univ_succ] <;> decide

def sourceGraph : SimpleGraph (Fin 3) where
 Adj i j := i ≠ j ∧ (i = 1 ∨ j = 1)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel sourceGraph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
theorem source_graph_counterexample : sourceGraph.Connected ∧
    sourceGraph.adjMatrix ℕ = A ∧ (A^2) 0 1 = 0 := by
 refine ⟨by decide, ?_, matrix_square_counterexample.2.2⟩
 funext i j
 fin_cases i <;> fin_cases j <;> decide

/-! ## The refuted local claim as a predicate on an arbitrary finite simple graph -/

section General

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- `A^(n-1)` has a zero entry, where `n` is the number of vertices. -/
def HasZeroEntry : Prop :=
  ∃ i j : V, (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i j = 0

/-- The source's local claim, entrywise reading: "If any `A^{n-1}_{i,j}` would be 0, that would
mean that there would not be any path connecting those vertices." -/
def LocalClaimEntrywise : Prop :=
  ∀ i j : V, (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i j = 0 → ¬ G.Reachable i j

/-- The source's local claim, graph-level conclusion: "Thus, the graph would be disconnected." -/
def LocalClaim : Prop := HasZeroEntry G → ¬ G.Connected

/-- The entrywise reading implies the graph-level one, so refuting the graph-level claim refutes
both. -/
theorem entrywise_implies_local (h : LocalClaimEntrywise G) : LocalClaim G := by
  rintro ⟨i, j, hij⟩ hc
  exact h i j hij (hc i j)

/-! ## Parity lemmas for bipartite graphs -/

/-- If no walk from `u` to `v` has length exactly `k`, the `(u,v)` entry of `A^k` is zero. -/
theorem pow_entry_zero_of_no_walk (k : ℕ) (u v : V)
    (h : ∀ p : G.Walk u v, p.length ≠ k) : (G.adjMatrix ℕ ^ k) u v = 0 := by
  rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk, Nat.cast_id, Fintype.card_eq_zero_iff]
  exact ⟨fun ⟨p, hp⟩ => h p hp⟩

/-- "odd walk length cannot return to its initial part": in a bipartite graph every diagonal
entry of an odd power of `A` is zero. -/
theorem bipartite_diag_zero (c : G.Coloring Bool) {k : ℕ} (hk : Odd k) (i : V) :
    (G.adjMatrix ℕ ^ k) i i = 0 := by
  apply pow_entry_zero_of_no_walk
  intro p hp
  have he : Even p.length := (c.even_length_iff_congr p).mpr Iff.rfl
  rw [hp] at he
  exact (Nat.not_even_iff_odd.mpr hk) he

/-- "even walk length cannot switch parts": in a bipartite graph the entry of an even power of
`A` at the endpoints of any edge is zero. -/
theorem bipartite_edge_zero (c : G.Coloring Bool) {k : ℕ} (hk : Even k) {i j : V}
    (hij : G.Adj i j) : (G.adjMatrix ℕ ^ k) i j = 0 := by
  apply pow_entry_zero_of_no_walk
  intro p hp
  have ho : Odd p.length := by
    rw [c.odd_length_iff_not_congr p, ← not_iff, ← Bool.eq_iff_iff]
    exact c.valid hij
  rw [hp] at ho
  exact (Nat.not_odd_iff_even.mpr hk) ho

/-! ## The documented family -/

/-- FAMILY. Every connected bipartite graph with at least two vertices has a zero entry in
`A^(n-1)`. -/
theorem family (hconn : G.Connected) (hbip : G.Colorable 2) (hn : 2 ≤ Fintype.card V) :
    HasZeroEntry G := by
  obtain ⟨c0⟩ := hbip
  let c : G.Coloring Bool := G.recolorOfEquiv finTwoEquiv c0
  rcases Nat.even_or_odd (Fintype.card V - 1) with hk | hk
  · -- n odd: use the endpoints of an edge
    obtain ⟨u, v, huv⟩ := Fintype.one_lt_card_iff.mp (show 1 < Fintype.card V by omega)
    obtain ⟨p⟩ := hconn u v
    cases p with
    | nil => exact absurd rfl huv
    | cons h q => exact ⟨_, _, bipartite_edge_zero G c hk h⟩
  · -- n even: use a diagonal entry
    obtain ⟨i⟩ := hconn.nonempty
    exact ⟨i, i, bipartite_diag_zero G c hk i⟩

/-- The family restated with Mathlib's `IsBipartite` (an abbreviation of `Colorable 2`). -/
theorem family_isBipartite (hconn : G.Connected) (hbip : G.IsBipartite)
    (hn : 2 ≤ Fintype.card V) : HasZeroEntry G := family G hconn hbip hn

/-- The source's local claim fails, in both readings, at every member of the family. -/
theorem family_refutes_claim (hconn : G.Connected) (hbip : G.Colorable 2)
    (hn : 2 ≤ Fintype.card V) : ¬ LocalClaim G ∧ ¬ LocalClaimEntrywise G := by
  have h1 : ¬ LocalClaim G := fun h => h (family G hconn hbip hn) hconn
  exact ⟨h1, fun h => h1 (entrywise_implies_local G h)⟩

/-- The two sub-cases exactly as the dossier words them. Connectivity is not needed for them. -/
theorem family_even_n (hbip : G.Colorable 2) (hn : Even (Fintype.card V)) (i : V) :
    (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i i = 0 := by
  obtain ⟨c0⟩ := hbip
  have hpos : 0 < Fintype.card V := Fintype.card_pos_iff.mpr ⟨i⟩
  have hk : Odd (Fintype.card V - 1) := by
    obtain ⟨m, hm⟩ := hn
    exact ⟨m - 1, by omega⟩
  exact bipartite_diag_zero G (G.recolorOfEquiv finTwoEquiv c0) hk i

theorem family_odd_n (hbip : G.Colorable 2) (hn : Odd (Fintype.card V)) {i j : V}
    (hij : G.Adj i j) : (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i j = 0 := by
  obtain ⟨c0⟩ := hbip
  have hk : Even (Fintype.card V - 1) := by
    obtain ⟨m, hm⟩ := hn
    exact ⟨m, by omega⟩
  exact bipartite_edge_zero G (G.recolorOfEquiv finTwoEquiv c0) hk hij

/-! ## The documented repair -/

/-- Entries of `(I+A)^k` detect walks of length at most `k` ("the identity allows padding by
stationary steps"). -/
theorem one_add_pow_entry_ne_zero_iff (k : ℕ) (i j : V) :
    ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length ≤ k := by
  induction k generalizing i j with
  | zero =>
    rw [pow_zero]
    constructor
    · intro h
      by_cases hij : i = j
      · subst hij; exact ⟨SimpleGraph.Walk.nil, Nat.le_refl _⟩
      · exact absurd (Matrix.one_apply_ne hij) h
    · rintro ⟨p, hp⟩
      have hij : i = j := SimpleGraph.Walk.eq_of_length_eq_zero (Nat.le_zero.mp hp)
      subst hij
      rw [Matrix.one_apply_eq]
      exact one_ne_zero
  | succ k ih =>
    rw [pow_succ', Matrix.mul_apply]
    constructor
    · intro h
      have hex : ∃ l, (1 + G.adjMatrix ℕ) i l * ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := by
        by_contra hcon
        exact h (Finset.sum_eq_zero (fun l _ => by
          by_contra hne
          exact hcon ⟨l, hne⟩))
      obtain ⟨l, hl⟩ := hex
      have h1 : (1 + G.adjMatrix ℕ) i l ≠ 0 := left_ne_zero_of_mul hl
      have h2 : ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := right_ne_zero_of_mul hl
      obtain ⟨p, hp⟩ := (ih l j).mp h2
      by_cases hil : i = l
      · subst hil; exact ⟨p, Nat.le_succ_of_le hp⟩
      · have hadj : G.Adj i l := by
          by_contra hna
          apply h1
          rw [Matrix.add_apply, Matrix.one_apply_ne hil, SimpleGraph.adjMatrix_apply, if_neg hna]
          omega
        exact ⟨SimpleGraph.Walk.cons hadj p, by rw [SimpleGraph.Walk.length_cons]; omega⟩
    · rintro ⟨p, hp⟩
      have hex : ∃ l, (1 + G.adjMatrix ℕ) i l ≠ 0 ∧ ∃ q : G.Walk l j, q.length ≤ k := by
        cases p with
        | nil =>
          refine ⟨_, ?_, SimpleGraph.Walk.nil, Nat.zero_le _⟩
          rw [Matrix.add_apply, Matrix.one_apply_eq]; omega
        | cons h q =>
          refine ⟨_, ?_, q, ?_⟩
          · rw [Matrix.add_apply, SimpleGraph.adjMatrix_apply, if_pos h]; omega
          · rw [SimpleGraph.Walk.length_cons] at hp; omega
      obtain ⟨l, hl1, q, hq⟩ := hex
      have hl2 : ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := (ih l j).mpr ⟨q, hq⟩
      intro hsum
      exact (mul_ne_zero hl1 hl2) ((Finset.sum_eq_zero_iff.mp hsum) l (Finset.mem_univ l))

/-- REPAIR, entrywise and exact: the `(i,j)` entry of `(I+A)^(n-1)` is nonzero if and only if
`i` and `j` are joined by a walk. No hypothesis on the graph at all. -/
theorem repair_entry_exact (i j : V) :
    ((1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1)) i j ≠ 0 ↔ G.Reachable i j := by
  rw [one_add_pow_entry_ne_zero_iff]
  constructor
  · rintro ⟨p, _⟩; exact ⟨p⟩
  · intro hr
    obtain ⟨p, hp⟩ := hr.exists_isPath
    exact ⟨p, Nat.le_sub_one_of_lt hp.length_lt⟩

/-- REPAIR (the source theorem itself): on a nonempty vertex set, `G` is connected if and only if
`(I+A)^(n-1)` has no zero entry. -/
theorem repair [Nonempty V] :
    G.Connected ↔ ∀ i j : V, ((1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1)) i j ≠ 0 := by
  rw [SimpleGraph.connected_iff]
  constructor
  · intro h i j
    exact (repair_entry_exact G i j).mpr (h.1 i j)
  · intro h
    exact ⟨fun i j => (repair_entry_exact G i j).mp (h i j), inferInstance⟩

/-- Entries of `A^0 + A^1 + ... + A^(m-1)` detect walks of length less than `m`. -/
theorem sum_pow_entry_ne_zero_iff (m : ℕ) (i j : V) :
    (∑ k ∈ Finset.range m, G.adjMatrix ℕ ^ k) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length < m := by
  rw [Matrix.sum_apply, Ne, Finset.sum_eq_zero_iff]
  constructor
  · intro h
    by_contra hcon
    apply h
    intro k hk
    apply pow_entry_zero_of_no_walk
    intro p hp
    exact hcon ⟨p, by rw [hp]; exact Finset.mem_range.mp hk⟩
  · rintro ⟨p, hp⟩ h
    have h0 := h p.length (Finset.mem_range.mpr hp)
    rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk, Nat.cast_id, Fintype.card_eq_zero_iff] at h0
    exact h0.false ⟨p, rfl⟩

/-- REPAIR, second documented form: "the sum of powers from 0 through n-1". -/
theorem repair_sum [Nonempty V] :
    G.Connected ↔
      ∀ i j : V, (∑ k ∈ Finset.range (Fintype.card V), G.adjMatrix ℕ ^ k) i j ≠ 0 := by
  rw [SimpleGraph.connected_iff]
  constructor
  · intro h i j
    obtain ⟨p, hp⟩ := (h.1 i j).exists_isPath
    exact (sum_pow_entry_ne_zero_iff G _ i j).mpr ⟨p, hp.length_lt⟩
  · intro h
    refine ⟨fun i j => ?_, inferInstance⟩
    obtain ⟨p, _⟩ := (sum_pow_entry_ne_zero_iff G _ i j).mp (h i j)
    exact ⟨p⟩

end General

/-! ## The refuted claim at the released witness -/

/-- CLAIM REFUTED at the released witness `P_3`: both readings of the local claim fail. -/
theorem claim_refuted : ¬ LocalClaim sourceGraph ∧ ¬ LocalClaimEntrywise sourceGraph := by
  have hz : HasZeroEntry sourceGraph := by
    refine ⟨0, 1, ?_⟩
    rw [source_graph_counterexample.2.1, Fintype.card_fin]
    exact source_graph_counterexample.2.2
  have h1 : ¬ LocalClaim sourceGraph := fun h => h hz source_graph_counterexample.1
  exact ⟨h1, fun h => h1 (entrywise_implies_local sourceGraph h)⟩

/-- The released witness is a member of the documented family. -/
theorem sourceGraph_in_family :
    sourceGraph.Connected ∧ sourceGraph.Colorable 2 ∧ 2 ≤ Fintype.card (Fin 3) := by
  refine ⟨source_graph_counterexample.1, ⟨SimpleGraph.Coloring.mk (fun i => if i = 1 then 1 else 0) ?_⟩, by simp⟩
  intro v w h
  revert h
  revert v w
  decide

/-! ## The family hypothesis "at least two vertices" is needed -/

/-- The one-vertex graph is connected and bipartite, and `A^(n-1) = A^0 = I` has no zero entry,
so the dossier's hypothesis "at least two vertices" cannot be dropped. -/
theorem family_needs_two_vertices :
    (⊥ : SimpleGraph (Fin 1)).Connected ∧ (⊥ : SimpleGraph (Fin 1)).Colorable 2 ∧
      ¬ HasZeroEntry (⊥ : SimpleGraph (Fin 1)) := by
  refine ⟨by decide, ⟨SimpleGraph.Coloring.mk (fun _ => 0) ?_⟩, ?_⟩
  · intro v w h
    exact absurd h (by simp)
  · rintro ⟨i, j, h⟩
    have hij : i = j := Subsingleton.elim i j
    subst hij
    rw [Fintype.card_fin, Nat.sub_self, pow_zero, Matrix.one_apply_eq] at h
    exact one_ne_zero h

/-! ## Edge case of the repair: the empty vertex set -/

/-- Without `Nonempty V` the repair is false under Mathlib's convention that the graph on no
vertices is not connected: the matrix condition is vacuously true on `Fin 0`. -/
theorem repair_empty_edge_case :
    ¬ ((⊥ : SimpleGraph (Fin 0)).Connected ↔
        ∀ i j : Fin 0,
          ((1 + (⊥ : SimpleGraph (Fin 0)).adjMatrix ℕ) ^ (Fintype.card (Fin 0) - 1)) i j ≠ 0) := by
  intro h
  have hc := h.mpr (fun i => i.elim0)
  exact hc.nonempty.elim (fun i => i.elim0)

/-! ## Slack: the family condition is not necessary for failure -/

/-- The paw graph: triangle `0,1,2` with a pendant vertex `3` attached to `0`. -/
def pawGraph : SimpleGraph (Fin 4) where
 Adj i j := i ≠ j ∧ (i = 0 ∨ j = 0 ∨ (i = 1 ∧ j = 2) ∨ (i = 2 ∧ j = 1))
 symm := by intro i j h; exact ⟨h.1.symm, by tauto⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel pawGraph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

theorem paw_connected : pawGraph.Connected := by decide

theorem paw_not_bipartite : ¬ pawGraph.Colorable 2 := by
  rintro ⟨c⟩
  have h01 : c 0 ≠ c 1 := c.valid (by decide)
  have h02 : c 0 ≠ c 2 := c.valid (by decide)
  have h12 : c 1 ≠ c 2 := c.valid (by decide)
  have key : ∀ a b d : Fin 2, a ≠ b → a ≠ d → b ≠ d → False := by decide
  exact key _ _ _ h01 h02 h12

theorem paw_zero_entry : (pawGraph.adjMatrix ℕ ^ (Fintype.card (Fin 4) - 1)) 3 3 = 0 := by
  rw [Fintype.card_fin]
  decide +kernel

/-- SLACK. The natural converse of the family ("a connected graph on at least two vertices with a
zero entry in `A^(n-1)` is bipartite") is false: the paw graph is connected, not bipartite, has
four vertices, and the local claim fails at it. -/
theorem slack :
    pawGraph.Connected ∧ ¬ pawGraph.Colorable 2 ∧ 2 ≤ Fintype.card (Fin 4) ∧
      HasZeroEntry pawGraph ∧ ¬ LocalClaim pawGraph := by
  have hz : HasZeroEntry pawGraph := ⟨3, 3, paw_zero_entry⟩
  exact ⟨paw_connected, paw_not_bipartite, by simp, hz, fun h => h hz paw_connected⟩

/-- Hence "bipartite" does not characterise failure of the local claim among connected graphs on
at least two vertices. -/
theorem family_not_exact :
    ¬ ∀ (G : SimpleGraph (Fin 4)) [DecidableRel G.Adj], G.Connected →
        (HasZeroEntry G ↔ G.Colorable 2) := by
  intro h
  exact paw_not_bipartite ((h pawGraph paw_connected).mp slack.2.2.2.1)

end SE_math_994847_q

#print axioms SE_math_994847_q.claim_refuted
#print axioms SE_math_994847_q.family
#print axioms SE_math_994847_q.family_isBipartite
#print axioms SE_math_994847_q.family_refutes_claim
#print axioms SE_math_994847_q.family_needs_two_vertices
#print axioms SE_math_994847_q.family_even_n
#print axioms SE_math_994847_q.family_odd_n
#print axioms SE_math_994847_q.repair_entry_exact
#print axioms SE_math_994847_q.repair
#print axioms SE_math_994847_q.repair_sum
#print axioms SE_math_994847_q.repair_empty_edge_case
#print axioms SE_math_994847_q.sourceGraph_in_family
#print axioms SE_math_994847_q.slack
#print axioms SE_math_994847_q.family_not_exact
