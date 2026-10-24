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

-- ===== Helper lemmas =====

theorem setI_getI_self (l : Store) (i : Nat) : setI l i (getI l i) = l := by
  induction l generalizing i with
  | nil => simp [setI, getI]
  | cons a l ih =>
    cases i with
    | zero => simp [setI, getI]
    | succ n => simpa [setI, getI] using ih n

theorem getI_setI_ne (l : Store) (i j : Nat) (v : Int) (h : i ≠ j) :
    getI (setI l i v) j = getI l j := by
  induction l generalizing i j with
  | nil => simp [setI, getI]
  | cons a l ih =>
    cases i with
    | zero =>
      cases j with
      | zero => omega
      | succ m => simp [setI, getI]
    | succ n =>
      cases j with
      | zero => simp [setI, getI]
      | succ m => simpa [setI, getI] using ih n m (by omega)

theorem getI_setI_eq (l : Store) (i : Nat) (v : Int) (h : i < l.length) :
    getI (setI l i v) i = v := by
  induction l generalizing i with
  | nil => simp at h
  | cons a l ih =>
    cases i with
    | zero => simp [setI, getI]
    | succ n =>
      have hn : n < l.length := by simpa using h
      simpa [setI, getI] using ih n hn

theorem length_setI (l : Store) (i : Nat) (v : Int) : (setI l i v).length = l.length := by
  simp [setI]

/-- Under `pre s`, `stepR1 s` succeeds and produces exactly `setI s 1 2`. -/
theorem stepR1_eq_of_pre (s : Store) (h : pre s = true) :
    stepR1 s = some (setI s 1 2) := by
  unfold pre at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hlen, h0⟩, h1⟩ := h
  unfold stepR1 writeAt
  rw [h0]
  have e1 : (2:Int) - 1 = 1 := by decide
  rw [e1]
  have hbridge : Int.ofNat s.length = (s.length : Int) := rfl
  have hcond : (decide (0 ≤ (1:Int)) && decide ((1:Int) < Int.ofNat s.length)) = true := by
    simp only [Bool.and_eq_true, decide_eq_true_eq]
    rw [hbridge]
    constructor
    · omega
    · omega
  rw [if_pos hcond]
  rfl

/-- Under `pre s`, the command result satisfies `postC`. -/
theorem holds_postC_of_pre (s : Store) (h : pre s = true) :
    holds postC (stepR1 s) = true := by
  have heq := stepR1_eq_of_pre s h
  unfold pre at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hlen, h0⟩, h1⟩ := h
  rw [heq]
  have hl : (setI s 1 2).length = s.length := length_setI s 1 2
  have hg0 : getI (setI s 1 2) 0 = getI s 0 := getI_setI_ne s 1 0 2 (by omega)
  have hg1 : getI (setI s 1 2) 1 = 2 := getI_setI_eq s 1 2 (by omega)
  simp [holds, postC, hl, hg0, hg1, h0, hlen]

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true :=
  holds_postC_of_pre

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  constructor
  · exact ⟨[2, 3], by decide, by decide⟩
  · exact ⟨[0, 0], by decide⟩

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro ht
    unfold postC at ht
    simp only [Bool.and_eq_true, decide_eq_true_eq] at ht
    obtain ⟨⟨hlen, h0⟩, h1⟩ := ht
    have hg0 : getI (setI t 1 3) 0 = getI t 0 := getI_setI_ne t 1 0 3 (by omega)
    have hg1 : getI (setI t 1 3) 1 = 3 := getI_setI_eq t 1 3 (by omega)
    have hl : (setI t 1 3).length = t.length := length_setI t 1 3
    have hpre : pre (setI t 1 3) = true := by
      unfold pre
      simp only [Bool.and_eq_true, decide_eq_true_eq]
      refine ⟨⟨by omega, ?_⟩, hg1⟩
      rw [hg0, h0]
    refine ⟨setI t 1 3, hpre, ?_⟩
    have heq := stepR1_eq_of_pre (setI t 1 3) hpre
    rw [heq]
    have hset : setI (setI t 1 3) 1 2 = setI t 1 2 := by simp [setI]
    rw [hset]
    have hself := setI_getI_self t 1
    rw [h1] at hself
    exact congrArg some hself
  · rintro ⟨s, hs, hstep⟩
    have heq := stepR1_eq_of_pre s hs
    rw [heq] at hstep
    have ht : t = setI s 1 2 := (Option.some.inj hstep).symm
    unfold pre at hs
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hs
    obtain ⟨⟨hlen, h0⟩, h1⟩ := hs
    have hg0 : getI (setI s 1 2) 0 = getI s 0 := getI_setI_ne s 1 0 2 (by omega)
    have hg1 : getI (setI s 1 2) 1 = 2 := getI_setI_eq s 1 2 (by omega)
    have hl : (setI s 1 2).length = s.length := length_setI s 1 2
    unfold postC
    simp only [Bool.and_eq_true, decide_eq_true_eq]
    rw [ht]
    refine ⟨⟨by omega, ?_⟩, hg1⟩
    rw [hg0, h0]

end SE_cs_1200_a1206_Census
