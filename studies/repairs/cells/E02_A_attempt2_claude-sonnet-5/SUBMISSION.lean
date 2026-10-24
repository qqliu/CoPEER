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

-- ===== HELPER LEMMAS =====

private theorem getI_set_ne (s : Store) (i j : Nat) (v : Int) (h : i ≠ j) :
    getI (s.set i v) j = getI s j := by
  unfold getI
  rw [List.getD_eq_getElem?_getD, List.getElem?_set_ne h, ← List.getD_eq_getElem?_getD]

private theorem getI_set_self (s : Store) (i : Nat) (v : Int) (h : i < s.length) :
    getI (s.set i v) i = v := by
  unfold getI
  rw [List.getD_eq_getElem?_getD, List.getElem?_set_self h]
  rfl

private theorem length_set (s : Store) (i : Nat) (v : Int) : (s.set i v).length = s.length := by
  simp

private theorem set_set_of_lt (t : Store) (i : Nat) (a b : Int) (hi : i < t.length) :
    (t.set i a).set i b = t.set i b := by
  apply List.ext_getElem?
  intro j
  by_cases hj : j = i
  · subst hj
    rw [List.getElem?_set_self (by simpa using hi), List.getElem?_set_self hi]
  · rw [List.getElem?_set_ne (Ne.symm hj), List.getElem?_set_ne (Ne.symm hj),
      List.getElem?_set_ne (Ne.symm hj)]

private theorem set_self_of_getI (t : Store) (i : Nat) (v : Int) (hi : i < t.length)
    (h : getI t i = v) : t.set i v = t := by
  apply List.ext_getElem?
  intro j
  by_cases hj : j = i
  · subst hj
    rw [List.getElem?_set_self hi, List.getElem?_eq_getElem hi]
    unfold getI at h
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi] at h
    simp at h
    simp [h]
  · rw [List.getElem?_set_ne (Ne.symm hj)]

private theorem pre_iff (s : Store) :
    pre s = true ↔ s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 3 := by
  unfold pre
  simp only [Bool.and_eq_true, decide_eq_true_eq, and_assoc]

private theorem postC_iff (s : Store) :
    postC s = true ↔ s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 2 := by
  unfold postC
  simp only [Bool.and_eq_true, decide_eq_true_eq, and_assoc]

/-- Under `pre`, the command evaluates to `some (setI s 1 2)`. -/
private theorem stepR1_eq (s : Store) (hpre : pre s = true) :
    stepR1 s = some (setI s 1 2) := by
  obtain ⟨hlen, h0, _h1⟩ := (pre_iff s).mp hpre
  unfold stepR1
  rw [h0]
  unfold writeAt
  have hcast : Int.ofNat s.length = (s.length : Int) := rfl
  have hcond : (decide (0 ≤ (2 : Int) - 1) && decide ((2 : Int) - 1 < Int.ofNat s.length)) = true := by
    simp only [decide_eq_true_eq, Bool.and_eq_true, hcast]
    omega
  rw [hcond]
  norm_num [setI]

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s hpre
  obtain ⟨hlen, h0, _h1⟩ := (pre_iff s).mp hpre
  rw [stepR1_eq s hpre]
  unfold holds
  rw [postC_iff]
  unfold setI
  have hlt : (1 : Nat) < s.length := by omega
  refine ⟨by simpa [length_set], ?_, ?_⟩
  · rw [getI_set_ne s 1 0 2 (by decide)]
    exact h0
  · exact getI_set_self s 1 2 hlt

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  constructor
  · refine ⟨[2, 3], ?_, ?_⟩
    · decide
    · decide
  · refine ⟨[], ?_⟩
    decide

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro ht
    obtain ⟨hlen, h0, h1⟩ := (postC_iff t).mp ht
    have hlt : (1 : Nat) < t.length := by omega
    have hpre' : pre (setI t 1 3) = true := by
      rw [pre_iff]
      unfold setI
      refine ⟨by simpa [length_set], ?_, ?_⟩
      · rw [getI_set_ne t 1 0 3 (by decide)]
        exact h0
      · exact getI_set_self t 1 3 hlt
    refine ⟨setI t 1 3, hpre', ?_⟩
    rw [stepR1_eq (setI t 1 3) hpre']
    unfold setI
    have hlt' : (1 : Nat) < (t.set 1 3).length := by simpa [length_set]
    rw [set_set_of_lt t 1 3 2 hlt]
    exact set_self_of_getI t 1 2 hlt h1
  · rintro ⟨s, hpre, hstep⟩
    have h := repair_statement s hpre
    rw [hstep] at h
    unfold holds at h
    exact h

end SE_cs_1200_a1206_Census
