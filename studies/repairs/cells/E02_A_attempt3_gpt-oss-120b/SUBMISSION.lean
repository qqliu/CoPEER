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

theorem repair_statement :
  ∀ s : SE_cs_1200_a1206_Census.Store,
    SE_cs_1200_a1206_Census.pre s = true →
    SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true :=
by
  intro s hs
  -- extract the three conjuncts from the precondition
  have hpre : (decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 3)) = true := by
    simpa [pre] using hs
  have h_and12 := (Bool.and_eq_true).mp hpre
  have h_and01 := (Bool.and_eq_true).mp h_and12.1
  have hlen : s.length ≥ 2 := (decide_eq_true_eq).1 h_and01.1
  have h0 : getI s 0 = 2 := (decide_eq_true_eq).1 h_and01.2
  have h1 : getI s 1 = 3 := (decide_eq_true_eq).1 h_and12.2
  -- simplify the goal using these facts
  simpa [holds, stepR1, writeAt, postC, h0, hlen]

theorem repair_nonvacuous :
  (∃ s : SE_cs_1200_a1206_Census.Store,
      SE_cs_1200_a1206_Census.pre s = true ∧
      SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧
    (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) :=
by
  have hs : SE_cs_1200_a1206_Census.pre ([2, 3] : List Int) = true := by
    simp [pre]
  have hstep :
      SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC
        (SE_cs_1200_a1206_Census.stepR1 ([2, 3] : List Int)) = true :=
    repair_statement ([2, 3] : List Int) hs
  have hfalse : SE_cs_1200_a1206_Census.postC ([] : List Int) = false := by
    simp [postC]
  exact ⟨⟨[2, 3], hs, hstep⟩, ⟨[], hfalse⟩⟩

theorem final_theorem :
  ∀ t : SE_cs_1200_a1206_Census.Store,
    SE_cs_1200_a1206_Census.postC t = true ↔
      ∃ s : SE_cs_1200_a1206_Census.Store,
        SE_cs_1200_a1206_Census.pre s = true ∧
        SE_cs_1200_a1206_Census.stepR1 s = some t :=
by
  intro t
  constructor
  · intro ht
    -- extract facts from the postcondition
    have hpost :
        ((decide (t.length ≥ 2) && decide (getI t 0 = 2)) && decide (getI t 1 = 2)) = true := by
      simpa [postC] using ht
    have h_and12 := (Bool.and_eq_true).mp hpost
    have h_and01 := (Bool.and_eq_true).mp h_and12.1
    have hlen : t.length ≥ 2 := (decide_eq_true_eq).1 h_and01.1
    have h0 : getI t 0 = 2 := (decide_eq_true_eq).1 h_and01.2
    have h1 : getI t 1 = 2 := (decide_eq_true_eq).1 h_and12.2
    -- build a suitable pre‑state
    let s := setI t 1 3
    have hs_pre : SE_cs_1200_a1206_Census.pre s = true := by
      have h0s : getI s 0 = 2 := by
        simpa [s, getI, setI] using h0
      have h1s : getI s 1 = 3 := by
        simpa [s, getI, setI]
      simp [pre, hlen, h0s, h1s]
    have hstep : SE_cs_1200_a1206_Census.stepR1 s = some t := by
      unfold stepR1 writeAt
      have h0s : getI s 0 = 2 := by
        simpa [s, getI, setI] using h0
      have : s.length ≥ 2 := hlen
      simp [s, h0s, this]
    exact ⟨s, hs_pre, hstep⟩
  · rintro ⟨s, hs, hstep⟩
    have hholds := repair_statement s hs
    have : SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (some t) = true := by
      simpa [holds, hstep] using hholds
    simpa [holds] using this

end SE_cs_1200_a1206_Census
