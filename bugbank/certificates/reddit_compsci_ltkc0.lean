import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The source is explicitly a joke (linked troll image). For the literal schedule of one elementary iteration each 18 months, a trace of 2^n iterations takes 18·2^n months. Mathlib asymptotics proves this is not O(n); no P-versus-NP claim is made.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditCompsciLtkc0

open Filter Asymptotics

def runtime (n : ℕ) : ℝ := 18 * 2^n

theorem audited_counterexample :
    runtime 4 = 288 ∧ runtime 5 = 576 ∧
    ¬ (runtime =O[atTop] fun n : ℕ => (n : ℝ)) := by
  refine ⟨by norm_num [runtime], by norm_num [runtime], ?_⟩
  have h : (fun n : ℕ => (n : ℝ)) =o[atTop] fun n : ℕ => (2 : ℝ)^n :=
    isLittleO_coe_const_pow_of_one_lt (by norm_num)
  have hf : ∃ᶠ n : ℕ in atTop, (n : ℝ) ≠ 0 := by
    apply Filter.Eventually.frequently
    filter_upwards [eventually_ge_atTop 1] with n hn
    exact_mod_cast (show n ≠ 0 by omega)
  intro hb
  apply h.not_isBigO hf
  have := hb.const_mul_left (1/18 : ℝ)
  simpa [runtime, mul_assoc] using this

end RedditCompsciLtkc0
