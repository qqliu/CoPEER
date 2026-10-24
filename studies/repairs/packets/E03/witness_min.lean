import defs_only
/- Record SE_cs_13118__a13122 (E03): the located line fails at c = 2, n = 3. -/
namespace SE_cs_13118_a13122_explanation_real

/-- `Sigma (2^·) 3 = 2 + 4 = 6`. -/
theorem sum_at_two_three : Sigma (fun k => (2 : ℝ) ^ k) 3 = 6 := by
  unfold Sigma
  rw [show Finset.Icc 1 (3 - 1) = ({1, 2} : Finset ℕ) from by decide]
  norm_num

/-- The asserted closed form at `c = 2`, `n = 3` is `7`. -/
theorem closed_form_at_two_three : ((2 : ℝ) ^ 3 - 1) / (2 - 1) = 7 := by norm_num

theorem local_claim_false : ¬ LocalClaim := by
  intro h
  have h3 := h 2 3 (by norm_num) (by norm_num)
  rw [sum_at_two_three, closed_form_at_two_three] at h3
  norm_num at h3

end SE_cs_13118_a13122_explanation_real

#print axioms SE_cs_13118_a13122_explanation_real.sum_at_two_three
#print axioms SE_cs_13118_a13122_explanation_real.local_claim_false
