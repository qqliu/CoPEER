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

-- helper: decompose pre
theorem pre_decomp {s : Store} (h : pre s = true) :
    s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 3 := by
  unfold pre at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

theorem stepR1_eq {s : Store} (h : s.length ≥ 2) (h0 : getI s 0 = 2) :
    stepR1 s = some (setI s 1 2) := by
  unfold stepR1 writeAt
  rw [h0]
  have e1 : (2 : Int) - 1 = 1 := by decide
  rw [e1]
  have c1 : decide ((0:Int) ≤ 1) = true := by decide
  have c2 : decide ((1:Int) < Int.ofNat s.length) = true := by
    simp only [decide_eq_true_eq]
    show (1:Int) < (s.length : Int)
    omega
  rw [c1, c2]
  simp

theorem getI_setI_ne {s : Store} {i j : Nat} {v : Int} (hij : i ≠ j) :
    getI (setI s i v) j = getI s j := by
  unfold getI setI
  rw [List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD]
  rw [List.getElem?_set_ne hij]

theorem getI_setI_eq {s : Store} {i : Nat} {v : Int} (h : i < s.length) :
    getI (setI s i v) i = v := by
  unfold getI setI
  rw [List.getD_eq_getElem?_getD]
  rw [List.getElem?_set_self]
  · rfl
  · exact h

theorem len_setI {s : Store} {i : Nat} {v : Int} : (setI s i v).length = s.length := by
  unfold setI
  simp

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s h
  obtain ⟨hlen, h0, h1⟩ := pre_decomp h
  rw [stepR1_eq hlen h0]
  unfold holds postC
  have hlen' : (setI s 1 2).length = s.length := len_setI
  have e0 : getI (setI s 1 2) 0 = 2 := by rw [getI_setI_ne (by decide)]; exact h0
  have e1 : getI (setI s 1 2) 1 = 2 := getI_setI_eq (by omega)
  simp [hlen', e0, e1, hlen]

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  constructor
  · exact ⟨[2,3], by decide, by decide⟩
  · exact ⟨[], by decide⟩

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro ht
    unfold postC at ht
    simp only [Bool.and_eq_true, decide_eq_true_eq] at ht
    obtain ⟨⟨hlen, h0⟩, h1⟩ := ht
    refine ⟨setI t 1 3, ?_, ?_⟩
    · unfold pre
      have hlen' : (setI t 1 3).length = t.length := len_setI
      have e0 : getI (setI t 1 3) 0 = 2 := by rw [getI_setI_ne (by decide)]; exact h0
      have e1 : getI (setI t 1 3) 1 = 3 := getI_setI_eq (by omega)
      simp [hlen', e0, e1, hlen]
    · have hlen' : (setI t 1 3).length = t.length := len_setI
      have e0 : getI (setI t 1 3) 0 = 2 := by rw [getI_setI_ne (by decide)]; exact h0
      rw [stepR1_eq (by omega) e0]
      have hset : setI (setI t 1 3) 1 2 = setI t 1 2 := by
        unfold setI; rw [List.set_set]
      have hself : setI t 1 2 = t := by
        unfold setI
        apply List.ext_getElem
        · simp
        · intro n hn1 hn2
          by_cases hne : n = 1
          · subst hne
            rw [List.getElem_set_self]
            have e1' : getI t 1 = 2 := h1
            unfold getI at e1'
            rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (by omega)] at e1'
            simpa using e1'.symm
          · rw [List.getElem_set_ne (Ne.symm hne)]
      rw [hset, hself]
  · rintro ⟨s, hs, heq⟩
    have h := repair_statement s hs
    rw [heq] at h
    exact h

end SE_cs_1200_a1206_Census
