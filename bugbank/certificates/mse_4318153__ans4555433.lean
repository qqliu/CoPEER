import Mathlib.Algebra.LinearRecurrence
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Topology.Order.LiminfLimsup
import Mathlib.Tactic

/-! The constant sequence 1 satisfies a(n+2)=-a(n+1)+2a(n).
Its actual real nth-root sequence has limit and limsup 1, while the
Mathlib characteristic polynomial has the root -2. Thus growth does
not bound every root of an arbitrary, possibly nonminimal recurrence.
This does not refute the statement for a minimal recurrence. -/
namespace MSE_4318153_ans4555433

noncomputable def recurrence : LinearRecurrence ℝ :=
  ⟨2, ![2, -1]⟩
def sequence (_ : ℕ) : ℝ := 1
noncomputable def rootSequence (n : ℕ) : ℝ := |sequence n| ^ (1 / (n : ℝ))

theorem satisfies_recurrence : recurrence.IsSolution sequence := by
  intro n
  change (1 : ℝ) = ∑ i : Fin 2, (![2, -1] i) * 1
  norm_num [Fin.sum_univ_two]

theorem root_is_neg_two : recurrence.charPoly.IsRoot (-2 : ℝ) := by
  change Polynomial.eval (-2) ((Polynomial.monomial 2) (1 : ℝ) -
    ∑ i : Fin 2, (Polynomial.monomial i.val) (![2, -1] i)) = 0
  norm_num [Fin.sum_univ_two]

theorem actual_root_limit : Filter.Tendsto rootSequence Filter.atTop (nhds (1 : ℝ)) := by
  have he : rootSequence = (fun _ : ℕ => (1 : ℝ)) := by
    funext n
    simp [rootSequence, sequence]
  rw [he]
  exact tendsto_const_nhds

theorem mse_4318153__ans4555433_refutation :
    recurrence.IsSolution sequence ∧
    Filter.Tendsto rootSequence Filter.atTop (nhds (1 : ℝ)) ∧
    Filter.limsup rootSequence Filter.atTop = 1 ∧
    recurrence.charPoly.IsRoot (-2 : ℝ) ∧
    ¬ |(-2 : ℝ)| ≤ 1 := by
  exact ⟨satisfies_recurrence, actual_root_limit, actual_root_limit.limsup_eq,
    root_is_neg_two, by norm_num⟩
end MSE_4318153_ans4555433
