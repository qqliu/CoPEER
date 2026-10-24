import Mathlib.Algebra.Group.Pointwise.Finset.Basic
import Mathlib.Data.Int.Interval
import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-! Original witness A={0,2,4,5,6}, k=5. Check all four k≥5 source
families, including both allowed c values in the first family. The k=4
families cannot apply. Mathlib finite sets, integer intervals, pointwise
sumsets, cardinalities and affine images replace bespoke list mathematics.
The two erroneous displayed bullets are local transcription errors in the
source summary, not a refutation of Freiman's theorem. -/
namespace MSE3739826
open scoped Pointwise

def A : Finset ℤ := {0,2,4,5,6}
def listed : Fin 5 → Finset ℤ :=
  ![Finset.Icc 0 1 ∪ Finset.Icc 3 5,
    Finset.Icc 0 2 ∪ Finset.Icc 4 5,
    {0} ∪ Finset.Icc 2 6,
    {0,2} ∪ Finset.Icc 4 12,
    {0} ∪ Finset.Icc 2 4 ∪ {6}]
def endpoint : Fin 5 → ℤ := ![5,5,6,12,6]

theorem source_hypotheses : A.card = 5 ∧ (A+A).card = 11 := by decide

theorem source_parameter_range (c : ℤ) (hc : 2 ≤ c ∧ c ≤ 5-2) :
    c=2 ∨ c=3 := by omega

theorem bounds {z : ℤ} (hz : z ∈ A) : 0 ≤ z ∧ z ≤ 6 := by
  simp only [A, Finset.mem_insert, Finset.mem_singleton] at hz
  omega

theorem source_entries : ∀ i, 0 ∈ listed i ∧ endpoint i ∈ listed i ∧ 5 ≤ endpoint i := by decide

/-- No unbounded nonconstant integer affine image of any listed entry is A. -/
theorem no_affine_image (i : Fin 5) (p q : ℤ) (hp : p ≠ 0) :
    (listed i).image (fun x => p*x+q) ≠ A := by
  intro he
  have h0 : q ∈ A := by
    rw [← he]
    exact Finset.mem_image.mpr ⟨0, (source_entries i).1, by ring⟩
  have hept : p * endpoint i + q ∈ A := by
    rw [← he]
    exact Finset.mem_image.mpr ⟨endpoint i,(source_entries i).2.1,rfl⟩
  obtain ⟨hqlo,hqhi⟩ := bounds h0
  have hb := bounds hept
  fin_cases i <;> norm_num [endpoint] at hb <;>
    have hpm : p = -1 ∨ p = 1 := by omega
  all_goals rcases hpm with rfl | rfl
  all_goals interval_cases q <;> revert he <;> decide

/-- The theorem selected for the record includes the hypothesis and every case. -/
theorem certificate :
    A.card = 5 ∧ (A+A).card = 2*5+1 ∧
    ∀ (i : Fin 5) (p q : ℤ), p ≠ 0 → (listed i).image (fun x => p*x+q) ≠ A :=
  ⟨source_hypotheses.1, source_hypotheses.2, no_affine_image⟩
end MSE3739826
