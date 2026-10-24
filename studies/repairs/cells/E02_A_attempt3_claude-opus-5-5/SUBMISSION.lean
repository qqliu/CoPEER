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

theorem pre_iff (s : Store) : pre s = true ↔ ∃ r : List Int, s = 2 :: 3 :: r := by
  match s with
  | [] => simp [pre]
  | [a] => simp [pre]
  | a :: b :: r =>
    simp [pre, getI]

theorem postC_iff (s : Store) : postC s = true ↔ ∃ r : List Int, s = 2 :: 2 :: r := by
  match s with
  | [] => simp [postC]
  | [a] => simp [postC]
  | a :: b :: r =>
    simp [postC, getI]

theorem step_eq (r : List Int) : stepR1 (2 :: 3 :: r) = some (2 :: 2 :: r) := by
  simp [stepR1, writeAt, getI, setI]
  omega

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s h
  obtain ⟨r, rfl⟩ := (pre_iff s).1 h
  rw [step_eq]
  exact (postC_iff _).2 ⟨r, rfl⟩

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  refine ⟨⟨[2, 3], ?_, ?_⟩, ⟨[], ?_⟩⟩
  · exact (pre_iff _).2 ⟨[], rfl⟩
  · exact repair_statement _ ((pre_iff _).2 ⟨[], rfl⟩)
  · rfl

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  rw [postC_iff]
  constructor
  · rintro ⟨r, rfl⟩
    exact ⟨2 :: 3 :: r, (pre_iff _).2 ⟨r, rfl⟩, step_eq r⟩
  · rintro ⟨s, hs, hst⟩
    obtain ⟨r, rfl⟩ := (pre_iff s).1 hs
    rw [step_eq] at hst
    exact ⟨r, (Option.some.inj hst).symm⟩

end SE_cs_1200_a1206_Census
