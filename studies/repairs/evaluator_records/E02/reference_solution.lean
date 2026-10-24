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

theorem shape (c d : Int) (s : Store) :
    (decide (s.length ≥ 2) && decide (getI s 0 = c) && decide (getI s 1 = d)) = true
      ↔ ∃ rest, s = c :: d :: rest := by
  constructor
  · intro h
    match s, h with
    | [], h => simp at h
    | [a], h => simp [getI] at h
    | a :: b :: rest, h =>
      simp [getI] at h
      exact ⟨rest, by rw [h.1, h.2]⟩
  · rintro ⟨rest, rfl⟩
    simp [getI]

theorem pre_iff (s : Store) : pre s = true ↔ ∃ rest, s = 2 :: 3 :: rest := shape 2 3 s

theorem writeAt_one (a b v : Int) (rest : List Int) :
    writeAt (a :: b :: rest) 1 v = some (a :: v :: rest) := by
  simp [writeAt, setI] <;> omega

theorem stepR1_family (rest : List Int) : stepR1 (2 :: 3 :: rest) = some (2 :: 2 :: rest) := by
  show writeAt (2 :: 3 :: rest) (2 - 1) 2 = _
  exact writeAt_one 2 3 2 rest

theorem postC_iff (s : Store) : postC s = true ↔ ∃ rest, s = 2 :: 2 :: rest := shape 2 2 s

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: from every store satisfying the precondition the command succeeds and the corrected
postcondition holds afterwards. -/
theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s h
  obtain ⟨rest, rfl⟩ := (pre_iff s).1 h
  rw [stepR1_family]
  exact (postC_iff _).2 ⟨rest, rfl⟩

/-- Non-vacuity: the corrected postcondition is reached from some store satisfying the precondition, and it
is not the constant `true` predicate. -/
theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := ⟨⟨[2, 3], by decide, by decide⟩, ⟨[1, 1], by decide⟩⟩

/-- The corrected specification statement (the endpoint for this record): the corrected postcondition is
the strongest postcondition of the command under the precondition, i.e. it holds of a store exactly when
that store is reachable by the command from a store satisfying `pre`. If you cannot prove it, replace this
declaration (this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro h
    obtain ⟨rest, rfl⟩ := (postC_iff t).1 h
    exact ⟨2 :: 3 :: rest, (pre_iff _).2 ⟨rest, rfl⟩, stepR1_family rest⟩
  · rintro ⟨s, hs, hst⟩
    obtain ⟨rest, rfl⟩ := (pre_iff s).1 hs
    rw [stepR1_family rest] at hst
    injection hst with hst
    subst hst
    exact (postC_iff _).2 ⟨rest, rfl⟩
-- ===== END OBLIGATIONS =====
end SE_cs_1200_a1206_Census
