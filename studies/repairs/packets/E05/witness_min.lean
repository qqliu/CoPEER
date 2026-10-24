import defs_only
/- Record SE_cs_1957__a2388 (E05): Lemma A fails at b = a = 2, k = 1, n = 4 (L = 2):
the driving sum is 12, the asserted value 16. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_cs_1957_a2388_Census

/-- The source's h at b = a = 2, k = 1. -/
noncomputable def sourceH (x : ℝ) : ℝ := x ^ (Real.logb 2 2) * Real.logb 2 x

theorem nat_values : drivingSum 2 (2 ^ 1) 1 1 2 = 12 ∧ claimedRHS 2 1 1 2 = 16 := by decide

theorem local_claim_nat_false : ¬ LocalClaimNat := by
  intro hall
  have h1 := hall 2 1 1 2 (by omega)
  have h2 := nat_values.1
  have h3 := nat_values.2
  omega

theorem real_values :
    (∑ j ∈ Finset.range 2, (2 : ℝ)^j * sourceH (4 / 2^j)) = 12 ∧
    (4 : ℝ)^(Real.logb 2 2) * (Real.logb 2 4)^2 = 16 ∧ (12 : ℝ) ≠ 16 := by
 have hlog : Real.logb 2 (4 : ℝ) = 2 := by
   have h : (4 : ℝ) = 2 ^ 2 := by norm_num
   rw [h, Real.logb_pow]
   norm_num
 norm_num [sourceH, Finset.sum_range_succ, hlog]

theorem local_claim_real_false : ¬ LocalClaimReal := by
  intro hall
  have h1 := hall 2 2 1 2 (by norm_num) (by norm_num)
  have hlog : Real.logb 2 (4 : ℝ) = 2 := by
    have h : (4 : ℝ) = 2 ^ 2 := by norm_num
    rw [h, Real.logb_pow]
    norm_num
  norm_num [sourceHgen, Finset.sum_range_succ, hlog] at h1

end SE_cs_1957_a2388_Census

#print axioms SE_cs_1957_a2388_Census.nat_values
#print axioms SE_cs_1957_a2388_Census.local_claim_nat_false
#print axioms SE_cs_1957_a2388_Census.real_values
#print axioms SE_cs_1957_a2388_Census.local_claim_real_false
