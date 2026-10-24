/- Review overlay for SE_math_4219732__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

import Mathlib

namespace SE_math_4219732_q
open Filter Asymptotics

theorem cubic_exceeds_every_linear_bound (C : ℝ) (N : ℕ) :
    ∃ n : ℕ, N ≤ n ∧ C * (n : ℝ) < (n : ℝ)^3 := by
  obtain ⟨m, hm⟩ := exists_nat_gt C
  let n := max N m + 2
  have hNm : N ≤ n := by dsimp [n]; omega
  have hmn : m ≤ n := by dsimp [n]; omega
  have hn : (2 : ℝ) ≤ n := by exact_mod_cast (show 2 ≤ n by dsimp [n]; omega)
  have hm' : (m : ℝ) ≤ n := by exact_mod_cast hmn
  have hCn : C < (n : ℝ) := lt_of_lt_of_le hm hm'
  have hCsq : C < (n : ℝ)^2 := by nlinarith
  refine ⟨n, hNm, ?_⟩
  have hh := mul_lt_mul_of_pos_right hCsq (show (0 : ℝ) < n by linarith)
  nlinarith [hh]

theorem source_asymptotic_refutation :
    ¬IsBigO atTop (fun n : ℕ => (n : ℝ)^3) (fun n : ℕ => (n : ℝ)) := by
  intro h
  obtain ⟨C, hc⟩ := h.bound
  obtain ⟨N, hN⟩ := eventually_atTop.1 hc
  obtain ⟨n, hn, hbad⟩ := cubic_exceeds_every_linear_bound C N
  have hb := hN n hn
  have hb' : (n : ℝ)^3 ≤ C * n := by
    simpa only [Real.norm_eq_abs, abs_of_nonneg (show (0 : ℝ) ≤ n by positivity),
      abs_of_nonneg (show (0 : ℝ) ≤ (n : ℝ)^3 by positivity)] using hb
  exact not_le_of_gt hbad hb'

theorem valid_constant_factor_control :
    IsBigO atTop (fun n : ℕ => (2 : ℝ) * n) (fun n : ℕ => (n : ℝ)) := by
  apply isBigO_iff.2
  refine ⟨2, Filter.Eventually.of_forall ?_⟩
  intro n
  simp [norm_mul]
end SE_math_4219732_q
