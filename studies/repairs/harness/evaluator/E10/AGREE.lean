import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E10: the submitted criterion must have a zero entry exactly where the
reference (I + A)^(n-1) has one, on the listed (graph, i, j); that is, exactly at unreachable pairs. -/

/-- Test graphs (evaluator-only). -/
def path3 : SimpleGraph (Fin 3) where
  Adj i j := i ≠ j ∧ (i = 1 ∨ j = 1)
  symm := fun i j h => ⟨h.1.symm, h.2.symm⟩
  loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel path3.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
def edgePlusIsolated : SimpleGraph (Fin 3) where
  Adj i j := i ≠ j ∧ ((i.val, j.val) = (0, 1) ∨ (j.val, i.val) = (0, 1))
  symm := fun i j h => ⟨h.1.symm, h.2.symm⟩
  loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel edgePlusIsolated.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

theorem agree_path3_01 : (SE_math_994847_q.criterion path3 0 1 = 0 ↔ SE_math_994847_q.Ref.criterion path3 0 1 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_path3_02 : (SE_math_994847_q.criterion path3 0 2 = 0 ↔ SE_math_994847_q.Ref.criterion path3 0 2 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_path3_11 : (SE_math_994847_q.criterion path3 1 1 = 0 ↔ SE_math_994847_q.Ref.criterion path3 1 1 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_bot2_01 : (SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 ↔ SE_math_994847_q.Ref.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_bot2_00 : (SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 = 0 ↔ SE_math_994847_q.Ref.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_top3_02 : (SE_math_994847_q.criterion (⊤ : SimpleGraph (Fin 3)) 0 2 = 0 ↔ SE_math_994847_q.Ref.criterion (⊤ : SimpleGraph (Fin 3)) 0 2 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_epi_02 : (SE_math_994847_q.criterion edgePlusIsolated 0 2 = 0 ↔ SE_math_994847_q.Ref.criterion edgePlusIsolated 0 2 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_epi_01 : (SE_math_994847_q.criterion edgePlusIsolated 0 1 = 0 ↔ SE_math_994847_q.Ref.criterion edgePlusIsolated 0 1 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_bot1_00 : (SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 1)) 0 0 = 0 ↔ SE_math_994847_q.Ref.criterion (⊥ : SimpleGraph (Fin 1)) 0 0 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
theorem agree_top4_03 : (SE_math_994847_q.criterion (⊤ : SimpleGraph (Fin 4)) 0 3 = 0 ↔ SE_math_994847_q.Ref.criterion (⊤ : SimpleGraph (Fin 4)) 0 3 = 0) := by
  first
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; decide +kernel)
  | (simp only [SE_math_994847_q.criterion, SE_math_994847_q.Ref.criterion]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; simp only [Fintype.card_fin]; decide +kernel)
  | (unfold SE_math_994847_q.criterion SE_math_994847_q.Ref.criterion; norm_num [Fintype.card_fin]; decide +kernel)
#print axioms agree_path3_01
#print axioms agree_path3_02
#print axioms agree_path3_11
#print axioms agree_bot2_01
#print axioms agree_bot2_00
#print axioms agree_top3_02
#print axioms agree_epi_02
#print axioms agree_epi_01
#print axioms agree_bot1_00
#print axioms agree_top4_03
