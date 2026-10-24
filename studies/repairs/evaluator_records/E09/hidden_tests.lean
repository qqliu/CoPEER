import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E09: the submitted hypothesis `guard` must be equivalent to the reference
(preconnectedness) on every listed finite graph; the listed graphs are chosen so that both admissible hypotheses of the
grammar (G.Preconnected, G.Connected) agree on them (no empty vertex type). -/

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

theorem agree_bot1 : (SE_math_782216_q_Census.guard (⊥ : SimpleGraph (Fin 1)) ↔ SE_math_782216_q_Census.Ref.guard (⊥ : SimpleGraph (Fin 1))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_bot2 : (SE_math_782216_q_Census.guard (⊥ : SimpleGraph (Fin 2)) ↔ SE_math_782216_q_Census.Ref.guard (⊥ : SimpleGraph (Fin 2))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_bot3 : (SE_math_782216_q_Census.guard (⊥ : SimpleGraph (Fin 3)) ↔ SE_math_782216_q_Census.Ref.guard (⊥ : SimpleGraph (Fin 3))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_top3 : (SE_math_782216_q_Census.guard (⊤ : SimpleGraph (Fin 3)) ↔ SE_math_782216_q_Census.Ref.guard (⊤ : SimpleGraph (Fin 3))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_top2 : (SE_math_782216_q_Census.guard (⊤ : SimpleGraph (Fin 2)) ↔ SE_math_782216_q_Census.Ref.guard (⊤ : SimpleGraph (Fin 2))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_top1 : (SE_math_782216_q_Census.guard (⊤ : SimpleGraph (Fin 1)) ↔ SE_math_782216_q_Census.Ref.guard (⊤ : SimpleGraph (Fin 1))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_path3 : (SE_math_782216_q_Census.guard path3 ↔ SE_math_782216_q_Census.Ref.guard path3) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_edgePlusIsolated : (SE_math_782216_q_Census.guard edgePlusIsolated ↔ SE_math_782216_q_Census.Ref.guard edgePlusIsolated) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
theorem agree_top4 : (SE_math_782216_q_Census.guard (⊤ : SimpleGraph (Fin 4)) ↔ SE_math_782216_q_Census.Ref.guard (⊤ : SimpleGraph (Fin 4))) := by
  first
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; decide)
  | (simp only [SE_math_782216_q_Census.guard, SE_math_782216_q_Census.Ref.guard]; decide)
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; simp [SimpleGraph.connected_iff])
  | (unfold SE_math_782216_q_Census.guard SE_math_782216_q_Census.Ref.guard; constructor <;> intro h <;> first | decide | exact h.preconnected | exact ⟨h⟩ | simp_all)
#print axioms agree_bot1
#print axioms agree_bot2
#print axioms agree_bot3
#print axioms agree_top3
#print axioms agree_top2
#print axioms agree_top1
#print axioms agree_path3
#print axioms agree_edgePlusIsolated
#print axioms agree_top4
