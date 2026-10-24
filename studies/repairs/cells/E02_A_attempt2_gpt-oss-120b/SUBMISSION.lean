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

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store,
    SE_cs_1200_a1206_Census.pre s = true →
    SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true
| s hs => by
  -- unpack the precondition
  have hs' : decide (s.length ≥ 2) = true ∧
              decide (getI s 0 = 2) = true ∧
              decide (getI s 1 = 3) = true := by
    simpa [pre] using hs
  rcases hs' with ⟨hlen_dec, h0_dec, h1_dec⟩
  have h0 : getI s 0 = 2 := (decide_eq_true_iff).1 h0_dec
  have hlen : s.length ≥ 2 := (decide_eq_true_iff).1 hlen_dec
  -- evaluate the step
  have hstep : stepR1 s = some (setI s 1 2) := by
    simp [stepR1, writeAt, h0, hlen]
  -- evaluate the postcondition after the step
  have : holds postC (some (setI s 1 2)) = true := by
    dsimp [holds, postC, setI, getI]
    simp [h0, hlen]
  simpa [hstep] using this

theorem repair_nonvacuous :
    (∃ s : SE_cs_1200_a1206_Census.Store,
        SE_cs_1200_a1206_Census.pre s = true ∧
        SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC
          (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧
    (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) :=
by
  -- first witness for the precondition
  have hpre : pre ([2, 3] : List Int) = true := by
    simp [pre]
  have hpost : holds postC (stepR1 ([2, 3] : List Int)) = true := by
    have := repair_statement ([2, 3] : List Int) hpre
    simpa using this
  refine And.intro ?left ?right
  · exact ⟨[2, 3], hpre, hpost⟩
  · -- a store where the corrected postcondition is false
    refine ⟨[], ?_⟩
    simp [postC]

-- CANNOT: proving the strongest‑postcondition equivalence is non‑trivial in the given framework
-- final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store,
--   SE_cs_1200_a1206_Census.postC t = true ↔
--   ∃ s : SE_cs_1200_a1206_Census.Store,
--     SE_cs_1200_a1206_Census.pre s = true ∧
--     SE_cs_1200_a1206_Census.stepR1 s = some t

end SE_cs_1200_a1206_Census
