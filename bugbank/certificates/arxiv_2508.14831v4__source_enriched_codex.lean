import Mathlib.Analysis.SpecialFunctions.Log.Base
import Mathlib.Analysis.Asymptotics.Defs
import Mathlib.Tactic

open scoped BigOperators
namespace Arxiv2508_14831v4SourceEnrichedCodex
/-! The source's retained midpoint ancestors have lengths 2^k,...,1.
The finite sum below is their exact ceiling/logarithm potential using Mathlib
Real.logb, Nat.ceil, and Finset.sum. The final theorem refutes eventual big-O
with arbitrary real constants, so a finite-size exception cannot explain it. -/
noncomputable def potential (k : ℕ) : ℕ :=
  ∑ m ∈ Finset.range (k + 1), ⌈Real.logb 2 (1 + (2:ℝ)^m)⌉₊

theorem ceil_log (m : ℕ) : ⌈Real.logb 2 (1 + (2:ℝ)^m)⌉₊ = m+1 := by
  have h : (1 + (2:ℝ)^m) = ((1+2^m:ℕ):ℝ) := by norm_cast
  rw [h]
  rw [show (2:ℝ) = ((2:ℕ):ℝ) from rfl, Real.natCeil_logb_natCast]
  apply Nat.le_antisymm
  · apply Nat.clog_le_of_le_pow
    rw [pow_succ]
    have hp : 1 ≤ (2:ℕ)^m := Nat.one_le_pow m 2 (by omega)
    omega
  · have := (Nat.lt_clog_iff_pow_lt (b:=2) (by omega)).mpr (show 2^m < 1+2^m by omega)
    omega

theorem potential_eq (k : ℕ) : 2 * potential k = (k+1)*(k+2) := by
  simp only [potential, ceil_log]
  induction k with
  | zero => norm_num
  | succ k ih =>
    rw [Finset.sum_range_succ]
    nlinarith

theorem unbounded (C N : ℕ) : ∃ k ≥ N, C*k < potential k := by
  refine ⟨2*C+N+1, by omega, ?_⟩
  have h := potential_eq (2*C+N+1)
  nlinarith
theorem not_bigO : ¬ Asymptotics.IsBigO Filter.atTop
    (fun k : ℕ => (potential k : ℝ))
    (fun k : ℕ => Real.logb 2 ((2:ℝ)^k)) := by
  intro h
  obtain ⟨c, hc, hb⟩ := h.exists_nonneg
  obtain ⟨N, hN⟩ := Filter.eventually_atTop.1 hb.bound
  obtain ⟨C, hC⟩ := exists_nat_gt c
  obtain ⟨k, hk, hlarge⟩ := unbounded C N
  have hbound := hN k hk
  have hlog : Real.logb 2 ((2:ℝ)^k) = k := by
    simp [Real.logb,Real.log_ne_zero_of_pos_of_ne_one (by norm_num : (0:ℝ)<2) (by norm_num : (2:ℝ) ≠ 1)]
  rw [hlog] at hbound
  simp only [Real.norm_eq_abs, Nat.abs_cast] at hbound
  have hcap : c * (k:ℝ) ≤ (C:ℝ) * k := mul_le_mul_of_nonneg_right (le_of_lt hC) (Nat.cast_nonneg _)
  have hstrict : (C:ℝ) * k < (potential k:ℝ) := by exact_mod_cast hlarge
  linarith
theorem refutes_per_path_potential_is_O_logT :
    (∀ m : ℕ, ⌈Real.logb 2 (1 + (2:ℝ)^m)⌉₊ = m+1) ∧
    (∀ k : ℕ, 2 * potential k = (k+1)*(k+2)) ∧
    ¬ Asymptotics.IsBigO Filter.atTop
      (fun k : ℕ => (potential k : ℝ))
      (fun k : ℕ => Real.logb 2 ((2:ℝ)^k)) :=
  ⟨ceil_log, potential_eq, not_bigO⟩
end Arxiv2508_14831v4SourceEnrichedCodex
