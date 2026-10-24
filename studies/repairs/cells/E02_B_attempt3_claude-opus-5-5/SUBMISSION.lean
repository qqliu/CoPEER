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

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s h
  match s with
  | [] => simp [pre] at h
  | [_] => simp [pre] at h
  | a :: b :: rest =>
    simp [pre, getI] at h
    obtain ⟨rfl, rfl⟩ := h
    simp [stepR1, writeAt, getI, setI, holds, postC]
    have h1 : (1 : Int) < ↑rest.length + 1 + 1 := by omega
    rw [if_pos h1]
    simp

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) :=
  ⟨⟨[2, 3], by decide, by decide⟩, ⟨[], by decide⟩⟩

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro h
    match t with
    | [] => simp [postC] at h
    | [_] => simp [postC] at h
    | a :: b :: rest =>
      simp [postC, getI] at h
      obtain ⟨rfl, rfl⟩ := h
      refine ⟨2 :: 3 :: rest, ?_, ?_⟩
      · simp [pre, getI]
      · simp [stepR1, writeAt, getI, setI]
        omega
  · rintro ⟨s, hs, hst⟩
    have := repair_statement s hs
    rw [hst] at this
    simpa [holds] using this

end SE_cs_1200_a1206_Census
