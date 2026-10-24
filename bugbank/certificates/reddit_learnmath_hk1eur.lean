import Mathlib.Data.Set.Prod
import Mathlib.Data.Set.Lattice
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Retains A={1,2},C={2},x=1 and supplies source context B={0},D={1},y=0 already present in the original Lean. Product disjointness holds while A∩C contains2. Uses Set.prod/Disjoint.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_hk1eur
def A : Set ℕ := {1,2}
def B : Set ℕ := {0}
def C : Set ℕ := {2}
def D : Set ℕ := {1}
theorem certificate : Disjoint (A.prod B) (C.prod D) ∧
    (1,0) ∈ A.prod B ∧ (1 : ℕ) ∉ C ∧ ¬ Disjoint A C := by
  refine ⟨Set.disjoint_left.mpr ?_, ⟨by simp [A], by simp [B]⟩, by simp [C], ?_⟩
  · intro z hz hz'
    have h0 : z.2 = 0 := hz.2
    have h1 : z.2 = 1 := hz'.2
    omega
  · intro h
    exact Set.disjoint_left.mp h (by simp [A] : 2 ∈ A) (by simp [C] : 2 ∈ C)
end Audit_reddit_learnmath_hk1eur
