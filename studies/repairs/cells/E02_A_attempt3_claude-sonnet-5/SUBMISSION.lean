import defs_only
/-!
Record E02: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_cs_1200_a1206_Census

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected postcondition of the triple `{pre} A[A[0]-1] := A[0] {postC}`. The hole must be a `Bool`
predicate on the store; the canonical form is `decide (s.length ≥ 2) && decide (getI s 0 = c) && decide (getI s 1 = d)`
with integer literals `c`, `d` (the source's are 1 and 1). It may not refer to the command (`stepR1`, `writeAt`, ...). -/
def postC (s : Store) : Bool := decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 2)

/-- The corrected triple: total correctness under the operational reading `stepR1` (form fixed). -/
def CorrectedTriple : Prop := ∀ s : Store, pre s = true → holds postC (stepR1 s) = true
-- ===== END FIXED PART =====

theorem length_ge_two_cons {s : Store} (h : s.length ≥ 2) :
    ∃ a b rest, s = a :: b :: rest := by
  match s, h with
  | (a :: b :: rest), h => exact ⟨a, b, rest, rfl⟩

theorem pre_unfold {s : Store} (h : pre s = true) :
    s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 3 := by
  unfold pre at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

theorem step_eq {s : Store} (h : pre s = true) :
    stepR1 s = some (setI s 1 2) := by
  obtain ⟨hlen, h0, h1⟩ := pre_unfold h
  unfold stepR1 writeAt
  rw [h0]
  simp
  omega

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s h
  obtain ⟨hlen, h0, h1⟩ := pre_unfold h
  obtain ⟨a, b, rest, hs⟩ := length_ge_two_cons hlen
  subst hs
  unfold getI at h0 h1
  simp [List.getD] at h0 h1
  rw [step_eq h]
  unfold holds postC setI getI
  simp [List.set, List.getD, h0]

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  constructor
  · refine ⟨[2, 3], ?_, ?_⟩
    · unfold pre getI
      simp
    · apply repair_statement
      unfold pre getI
      simp
  · refine ⟨[0, 0], ?_⟩
    unfold postC getI
    simp

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro ht
    unfold postC at ht
    simp only [Bool.and_eq_true, decide_eq_true_eq] at ht
    obtain ⟨⟨hlen, h0⟩, h1⟩ := ht
    obtain ⟨a, b, rest, hs⟩ := length_ge_two_cons hlen
    subst hs
    unfold getI at h0 h1
    simp [List.getD] at h0 h1
    subst h0
    refine ⟨(2 : Int) :: 3 :: rest, ?_, ?_⟩
    · unfold pre getI
      simp
    · rw [step_eq (by unfold pre getI; simp)]
      unfold setI
      simp [List.set, h1]
  · rintro ⟨s, hpre, hstep⟩
    obtain ⟨hlen, h0, h1⟩ := pre_unfold hpre
    rw [step_eq hpre] at hstep
    obtain ⟨a, b, rest, hs⟩ := length_ge_two_cons hlen
    subst hs
    unfold getI at h0 h1
    simp [List.getD] at h0 h1
    subst h0
    have ht : t = setI (2 :: b :: rest) 1 2 := by
      cases hstep
      rfl
    subst ht
    unfold postC setI getI
    simp [List.set, List.getD]

end SE_cs_1200_a1206_Census
