import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E03: the submitted closed form must agree with the reference
(c ^ n - c) / (c - 1) at the listed (c, n) in the source's domain (c ≠ 1, 1 ≤ n). -/
theorem agree_0 : SE_cs_13118_a13122_explanation_real.closed_form 2 3 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 2 3 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_1 : SE_cs_13118_a13122_explanation_real.closed_form 2 1 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 2 1 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_2 : SE_cs_13118_a13122_explanation_real.closed_form 2 2 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 2 2 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_3 : SE_cs_13118_a13122_explanation_real.closed_form 3 2 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 3 2 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_4 : SE_cs_13118_a13122_explanation_real.closed_form 3 3 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 3 3 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_5 : SE_cs_13118_a13122_explanation_real.closed_form 2 4 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 2 4 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_6 : SE_cs_13118_a13122_explanation_real.closed_form 2 5 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 2 5 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_7 : SE_cs_13118_a13122_explanation_real.closed_form (-1) 3 = SE_cs_13118_a13122_explanation_real.Ref.closed_form (-1) 3 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_8 : SE_cs_13118_a13122_explanation_real.closed_form (1/2) 3 = SE_cs_13118_a13122_explanation_real.Ref.closed_form (1/2) 3 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_9 : SE_cs_13118_a13122_explanation_real.closed_form 0 3 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 0 3 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
theorem agree_10 : SE_cs_13118_a13122_explanation_real.closed_form 5 2 = SE_cs_13118_a13122_explanation_real.Ref.closed_form 5 2 := by
  first
  | (norm_num [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form])
  | (simp only [SE_cs_13118_a13122_explanation_real.closed_form, SE_cs_13118_a13122_explanation_real.Ref.closed_form]; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; ring_nf; norm_num)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; field_simp; ring)
  | (unfold SE_cs_13118_a13122_explanation_real.closed_form SE_cs_13118_a13122_explanation_real.Ref.closed_form; simp [Finset.sum_Icc_succ_top]; norm_num)
#print axioms agree_0
#print axioms agree_1
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_6
#print axioms agree_7
#print axioms agree_8
#print axioms agree_9
#print axioms agree_10
