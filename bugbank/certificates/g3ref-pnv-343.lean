import Mathlib
open Filter Set
open scoped Topology
/-! Original a_n=-n for positive indices; Lean n=0 corresponds to source n=1. -/
namespace G3refPnv343
noncomputable def witnessA (n : ℕ) : ℝ := -(n + 1 : ℝ)
lemma tends_negative : Tendsto witnessA atTop atBot := by
  apply tendsto_neg_atTop_atBot.comp
  change Tendsto (fun n : ℕ => (n : ℝ) + 1) atTop atTop
  exact tendsto_atTop_mono (fun n => by linarith) tendsto_natCast_atTop_atTop
 theorem refutes_bounded_above_implies_finite_limsup :
    (∀ n, witnessA n ≤ -1) ∧
    Filter.limsup (fun n => (witnessA n : EReal)) atTop = ⊥ ∧
    ¬ ∃ r : ℝ, Filter.limsup (fun n => (witnessA n : EReal)) atTop = (r : EReal) := by
  have h : Filter.limsup (fun n => (witnessA n : EReal)) atTop = ⊥ :=
    (EReal.tendsto_coe_atBot.comp tends_negative).limsup_eq
  refine ⟨?_, h, ?_⟩
  · intro n
    dsimp [witnessA]
    have hn : (0 : ℝ) ≤ n := Nat.cast_nonneg n
    linarith
  · simp [h]
end G3refPnv343
