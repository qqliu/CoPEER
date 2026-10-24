import Mathlib.SetTheory.ZFC.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: The original hereditarily finite sets now live in Mathlib ZFSet. Union X={∅} is a subset of K, A={{∅}} belongs to K, yet unionX and A are incomparable. No custom finite universe is substituted.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_87dz19
open scoped ZFSet
noncomputable def e : ZFSet.{0} := ∅
noncomputable def s : ZFSet.{0} := {e}
noncomputable def a : ZFSet.{0} := {s}
noncomputable def k : ZFSet.{0} := {e,s,a,{e,s}}
theorem certificate_core : ZFSet.sUnion ({s} : ZFSet.{0}) = s ∧ s ⊆ k ∧ a ∈ k ∧
    ¬ s ⊆ a ∧ ¬ a ⊆ s := by
  have es : e ≠ s := by
    intro h
    have hh : e ∈ s := by simp [s]
    rw [← h] at hh
    simpa [e] using hh
  refine ⟨ZFSet.sUnion_singleton, ?_, ?_, ?_, ?_⟩
  · intro x hx; simp only [s, ZFSet.mem_singleton] at hx; subst x; simp [k]
  · simp [k]
  · intro h; have := h (show e ∈ s by simp [s]); exact es (by simpa [a] using this)
  · intro h; have := h (show s ∈ a by simp [a]); exact es.symm (by simpa only [s, ZFSet.mem_singleton] using this)
theorem certificate : ZFSet.sUnion ({s} : ZFSet.{0}) = s ∧ s ⊆ k ∧ s ≠ k ∧ a ∈ k ∧
    ¬ s ⊆ a ∧ ¬ a ⊆ s := by
  rcases certificate_core with ⟨hu,hs,ha,hn1,hn2⟩
  refine ⟨hu,hs,?_,ha,hn1,hn2⟩
  intro h
  have hmem : s ∈ k := by simp [k]
  rw [← h] at hmem
  exact ZFSet.mem_irrefl s hmem
end Audit_reddit_learnmath_87dz19
