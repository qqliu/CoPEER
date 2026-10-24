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

/-- Every store of length ≥ 2 can be split into its first two elements and a tail. -/
theorem exists_cons_cons (s : Store) (h : s.length ≥ 2) :
    ∃ a b rest, s = a :: b :: rest := by
  match s, h with
  | a :: b :: rest, _ => exact ⟨a, b, rest, rfl⟩

/-- Unfold `pre` into its three components. -/
theorem pre_iff (s : Store) :
    pre s = true ↔ s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 3 := by
  unfold pre
  simp only [Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · intro h
    exact ⟨h.1.1, h.1.2, h.2⟩
  · intro h
    exact ⟨⟨h.1, h.2.1⟩, h.2.2⟩

/-- Unfold `postC` into its three components. -/
theorem postC_iff (s : Store) :
    postC s = true ↔ s.length ≥ 2 ∧ getI s 0 = 2 ∧ getI s 1 = 2 := by
  unfold postC
  simp only [Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · intro h
    exact ⟨h.1.1, h.1.2, h.2⟩
  · intro h
    exact ⟨⟨h.1, h.2.1⟩, h.2.2⟩

/-- The core computation: from a store satisfying `pre`, `stepR1` succeeds and produces
`a :: 2 :: rest` where `a = 2`. -/
theorem stepR1_eq (a b : Int) (rest : Store) (h0 : a = 2) (h1 : b = 3) :
    stepR1 (a :: b :: rest) = some (a :: (2 : Int) :: rest) := by
  subst h0; subst h1
  unfold stepR1 writeAt
  have hg : getI ((2:Int) :: (3:Int) :: rest) 0 = 2 := rfl
  rw [hg]
  have hcond : (decide (0 ≤ (2:Int) - 1) && decide ((2:Int) - 1 < Int.ofNat (List.length ((2:Int) :: (3:Int) :: rest)))) = true := by
    simp only [List.length_cons, Int.ofNat_eq_natCast, Bool.and_eq_true, decide_eq_true_eq]
    constructor
    · omega
    · omega
  rw [if_pos hcond]
  have ht : ((2:Int) - 1).toNat = 1 := by decide
  rw [ht]
  rfl

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true → SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true := by
  intro s hs
  rw [pre_iff] at hs
  obtain ⟨hlen, h0, h1⟩ := hs
  obtain ⟨a, b, rest, rfl⟩ := exists_cons_cons s hlen
  have h0' : a = 2 := h0
  have h1' : b = 3 := h1
  rw [stepR1_eq a b rest h0' h1', h0']
  show postC ((2:Int) :: (2:Int) :: rest) = true
  rw [postC_iff]
  refine ⟨?_, rfl, rfl⟩
  simp only [List.length_cons]
  omega

theorem repair_nonvacuous : (∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.holds SE_cs_1200_a1206_Census.postC (SE_cs_1200_a1206_Census.stepR1 s) = true) ∧ (∃ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = false) := by
  refine ⟨⟨[2, 3], by decide, by decide⟩, ⟨[0, 0], by decide⟩⟩

theorem final_theorem : ∀ t : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.postC t = true ↔ ∃ s : SE_cs_1200_a1206_Census.Store, SE_cs_1200_a1206_Census.pre s = true ∧ SE_cs_1200_a1206_Census.stepR1 s = some t := by
  intro t
  constructor
  · intro ht
    rw [postC_iff] at ht
    obtain ⟨hlen, h0, h1⟩ := ht
    obtain ⟨a, b, rest, rfl⟩ := exists_cons_cons t hlen
    have h0' : a = 2 := h0
    have h1' : b = 2 := h1
    subst h0'; subst h1'
    refine ⟨(2:Int) :: (3 : Int) :: rest, ?_, ?_⟩
    · rw [pre_iff]
      refine ⟨?_, rfl, rfl⟩
      simp only [List.length_cons]
      omega
    · exact stepR1_eq 2 3 rest rfl rfl
  · intro hex
    obtain ⟨s, hs, hstep⟩ := hex
    rw [pre_iff] at hs
    obtain ⟨hlen, h0, h1⟩ := hs
    obtain ⟨a, b, rest, rfl⟩ := exists_cons_cons s hlen
    have h0' : a = 2 := h0
    have h1' : b = 3 := h1
    rw [stepR1_eq a b rest h0' h1'] at hstep
    have ht : t = a :: (2:Int) :: rest := by
      injection hstep with hstep'
      exact hstep'.symm
    rw [ht, h0']
    show postC ((2:Int) :: (2:Int) :: rest) = true
    rw [postC_iff]
    refine ⟨?_, rfl, rfl⟩
    simp only [List.length_cons]
    omega

end SE_cs_1200_a1206_Census
