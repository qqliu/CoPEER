/-!
# SE_cs_1200__a1206: the documented family and repair, formalised (explanation census)

Source (cs.stackexchange answer 1206 to question 1200), quoted local claim:
"consider the assignment `A[A[0]-1] := A[0]` under the precondition `A[0] = 2 ∧ A[1] = 3`:
you cannot make a simple substitution to obtain the correct postcondition `A[0] = 1 ∧ A[1] = 1`".
The refuted content is the Hoare triple `{A[0]=2 ∧ A[1]=3}  A[A[0]-1] := A[0]  {A[0]=1 ∧ A[1]=1}`.

Documented family: "The same holds for any longer array with A[0]=2, A[1]=3 ...; the trailing
cells are irrelevant."  Documented repair: "The strongest postcondition of this assignment under
the given precondition is A[0] = 2 AND A[1] = 2".

`Store`, `getI`, `setI`, `writeAt`, `pre`, `post`, `postActual`, `stepR1`, `stepR2`, `stepR3`,
`holds`, `resultIs` are restated verbatim from the released certificate
`qedbench_certificate_availability_triage/validation/human_review_20260915/lean/SE_cs_1200__a1206.lean`
(sha256 0649d69dfbea7e1532fcb6121fa38c7ede59ff558f8fee465cddfadb8e4f705e); only the namespace is
changed, to keep the two files distinct.  `stepAlt` is NOT in the released file: it models the
alternative command `A[A[0]-1] := A[0]-1` that the dossier's explanation offers as "a plausible
intended example".  Core Lean only, no imports.
-/

namespace SE_cs_1200_a1206_Census

/-! ## Released definitions, verbatim -/

abbrev Store := List Int

def getI (s : Store) (i : Nat) : Int := s.getD i 0

def setI (s : Store) (i : Nat) (v : Int) : Store := s.set i v

def writeAt (s : Store) (i : Int) (v : Int) : Option Store :=
  if decide (0 ≤ i) && decide (i < Int.ofNat s.length) then some (setI s i.toNat v) else none

def pre (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 3)

def post (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 1) && decide (getI s 1 = 1)

def postActual (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 2)

def stepR1 (s : Store) : Option Store :=
  writeAt s (getI s 0 - 1) (getI s 0)

def stepR2 (s : Store) : Option Store :=
  match writeAt s (getI s 0 - 1) (getI s 0) with
  | none   => none
  | some t => writeAt t (getI s 0 - 1) (getI t 0)

def stepR3 (s : Store) : Option Store :=
  let v := getI s 0
  writeAt s (getI s 0 - 1) v

def holds (p : Store → Bool) : Option Store → Bool
  | none   => false
  | some t => p t

def resultIs : Option Store → Store → Bool
  | none,   _ => false
  | some t, u => decide (t = u)

/-! ## New definition (not released): the dossier's "plausible intended example" -/

/-- `A[A[0]-1] := A[0]-1`, index and right-hand side evaluated in the pre-state. -/
def stepAlt (s : Store) : Option Store :=
  writeAt s (getI s 0 - 1) (getI s 0 - 1)

/-! ## Shape of the three state predicates -/

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

/-- The precondition holds exactly on the stores `2 :: 3 :: rest`: this IS the documented family
("any longer array with A[0]=2, A[1]=3"), `rest` being the irrelevant trailing cells. -/
theorem pre_iff (s : Store) : pre s = true ↔ ∃ rest, s = 2 :: 3 :: rest := shape 2 3 s

theorem post_iff (s : Store) : post s = true ↔ ∃ rest, s = 1 :: 1 :: rest := shape 1 1 s

theorem postActual_iff (s : Store) : postActual s = true ↔ ∃ rest, s = 2 :: 2 :: rest :=
  shape 2 2 s

/-- The `length ≥ 2` clause of the released `pre` is redundant (the default read value is `0`),
so `pre` is literally the source's `A[0] = 2 ∧ A[1] = 3`. -/
theorem pre_iff_source (s : Store) : pre s = true ↔ (getI s 0 = 2 ∧ getI s 1 = 3) := by
  constructor
  · intro h
    obtain ⟨rest, rfl⟩ := (pre_iff s).1 h
    simp [getI]
  · intro h
    match s, h with
    | [], h => simp [getI] at h
    | [a], h => simp [getI] at h
    | a :: b :: rest, h =>
      simp [getI] at h
      exact (pre_iff _).2 ⟨rest, by rw [h.1, h.2]⟩

/-! ## One write -/

theorem writeAt_zero (a v : Int) (rest : List Int) :
    writeAt (a :: rest) 0 v = some (v :: rest) := by
  simp [writeAt, setI] <;> omega

theorem writeAt_one (a b v : Int) (rest : List Int) :
    writeAt (a :: b :: rest) 1 v = some (a :: v :: rest) := by
  simp [writeAt, setI] <;> omega

theorem stepR1_family (rest : List Int) : stepR1 (2 :: 3 :: rest) = some (2 :: 2 :: rest) := by
  show writeAt (2 :: 3 :: rest) (2 - 1) 2 = _
  exact writeAt_one 2 3 2 rest

/-! ## The three operational readings agree on EVERY store, not only on the family -/

theorem stepR3_eq_stepR1 (s : Store) : stepR3 s = stepR1 s := rfl

/-- The command never changes `A[0]`, from any store. -/
theorem A0_invariant (s t : Store) (h : stepR1 s = some t) : getI t 0 = getI s 0 := by
  match s, h with
  | [], h => simp [stepR1, writeAt, getI] at h
  | a :: rest, h =>
    simp only [stepR1, writeAt, getI, List.getD_cons_zero] at h
    split at h
    · injection h with h
      subst h
      cases hn : (a - 1).toNat with
      | zero => simp [setI, getI]
      | succ m => simp [setI, getI]
    · cases h

theorem writeAt_idem (s t : Store) (i v : Int) (h : writeAt s i v = some t) :
    writeAt t i v = some t := by
  unfold writeAt at h
  split at h
  · injection h with h
    subst h
    rename_i hc
    simp [writeAt, setI] at hc ⊢
    exact hc
  · cases h

theorem stepR2_eq_stepR1 (s : Store) : stepR2 s = stepR1 s := by
  unfold stepR2
  cases h : writeAt s (getI s 0 - 1) (getI s 0) with
  | none => simp [stepR1, h]
  | some t =>
    have h0 : getI t 0 = getI s 0 := A0_invariant s t h
    show writeAt t (getI s 0 - 1) (getI t 0) = stepR1 s
    rw [h0, writeAt_idem s t _ _ h]
    exact h.symm

/-! ## (a) The refuted local claim -/

/-- The released witness, restated: `[2,3]` satisfies the precondition, every reading yields
`[2,2]`, and the asserted postcondition is false there. -/
theorem claim_refuted_witness :
    (pre [2, 3] = true)
  ∧ (resultIs (stepR1 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR2 [2, 3]) [2, 2] = true)
  ∧ (resultIs (stepR3 [2, 3]) [2, 2] = true)
  ∧ (post [2, 2] = false)
  ∧ (postActual [2, 2] = true) := by decide

/-- The source's Hoare triple `{pre} A[A[0]-1] := A[0] {post}` is not valid. -/
theorem claim_refuted : ¬ (∀ s : Store, pre s = true → holds post (stepR1 s) = true) := by
  intro h
  have h1 := h [2, 3] (by decide)
  revert h1
  decide

/-! ## (b) The documented family -/

theorem post_false_family (rest : List Int) : post (2 :: 2 :: rest) = false := by
  simp [post, getI]

/-- FAMILY, indexed by the trailing cells: for every `rest`, the store `2 :: 3 :: rest` satisfies
the precondition, all three readings produce `2 :: 2 :: rest` (trailing cells untouched), and the
asserted postcondition is false there. -/
theorem family (rest : List Int) :
    pre (2 :: 3 :: rest) = true
  ∧ stepR1 (2 :: 3 :: rest) = some (2 :: 2 :: rest)
  ∧ stepR2 (2 :: 3 :: rest) = some (2 :: 2 :: rest)
  ∧ stepR3 (2 :: 3 :: rest) = some (2 :: 2 :: rest)
  ∧ post (2 :: 2 :: rest) = false := by
  refine ⟨(pre_iff _).2 ⟨rest, rfl⟩, stepR1_family rest, ?_, ?_, post_false_family rest⟩
  · rw [stepR2_eq_stepR1]; exact stepR1_family rest
  · rw [stepR3_eq_stepR1]; exact stepR1_family rest

/-- FAMILY, stated over the released predicate: the claim fails at EVERY store satisfying the
precondition, under every reading (the dossier's "failure rate is 100%"). -/
theorem family_all (s : Store) (h : pre s = true) :
    holds post (stepR1 s) = false ∧ holds post (stepR2 s) = false
      ∧ holds post (stepR3 s) = false := by
  obtain ⟨rest, rfl⟩ := (pre_iff s).1 h
  have f := family rest
  rw [f.2.1, f.2.2.1, f.2.2.2.1]
  exact ⟨f.2.2.2.2, f.2.2.2.2, f.2.2.2.2⟩

/-- The family is infinite: it has a member of every length `n + 2`. -/
theorem family_unbounded (n : Nat) : ∃ s : Store, s.length = n + 2 ∧ pre s = true :=
  ⟨2 :: 3 :: List.replicate n 0, by simp, (pre_iff _).2 ⟨_, rfl⟩⟩

/-- "writes to exactly one cell ... the only cell modified is A[1], and it receives the value 2;
A[0] is not written at all": frame statement on every member of the family. -/
theorem frame (s : Store) (h : pre s = true) :
    ∃ t, stepR1 s = some t ∧ t.length = s.length ∧ getI t 0 = 2 ∧ getI t 1 = 2
      ∧ ∀ i, i ≠ 1 → getI t i = getI s i := by
  obtain ⟨rest, rfl⟩ := (pre_iff s).1 h
  refine ⟨2 :: 2 :: rest, stepR1_family rest, by simp, by simp [getI], by simp [getI], ?_⟩
  intro i hi
  match i, hi with
  | 0, _ => simp [getI]
  | 1, hi => exact absurd rfl hi
  | k + 2, _ => simp [getI]

/-! ## (c) The documented repair -/

/-- REPAIR (soundness): from every store satisfying the precondition the command terminates
without an out-of-bounds error and `A[0] = 2 ∧ A[1] = 2` holds afterwards, under every reading. -/
theorem repair (s : Store) (h : pre s = true) :
    holds postActual (stepR1 s) = true ∧ holds postActual (stepR2 s) = true
      ∧ holds postActual (stepR3 s) = true := by
  obtain ⟨rest, rfl⟩ := (pre_iff s).1 h
  have f := family rest
  rw [f.2.1, f.2.2.1, f.2.2.2.1]
  have hp : postActual (2 :: 2 :: rest) = true := (postActual_iff _).2 ⟨rest, rfl⟩
  exact ⟨hp, hp, hp⟩

/-- EXACT (the repair is the STRONGEST postcondition, as a set of states): a store satisfies
`A[0] = 2 ∧ A[1] = 2` iff it is reachable by the command from a store satisfying the
precondition. -/
theorem exact (t : Store) :
    postActual t = true ↔ ∃ s, pre s = true ∧ stepR1 s = some t := by
  constructor
  · intro h
    obtain ⟨rest, rfl⟩ := (postActual_iff t).1 h
    exact ⟨2 :: 3 :: rest, (pre_iff _).2 ⟨rest, rfl⟩, stepR1_family rest⟩
  · rintro ⟨s, hs, hst⟩
    obtain ⟨rest, rfl⟩ := (pre_iff s).1 hs
    rw [stepR1_family rest] at hst
    injection hst with hst
    subst hst
    exact (postActual_iff _).2 ⟨rest, rfl⟩

/-- EXACT, in Hoare-logic form: a postcondition `Q` is valid for `{pre} cmd {Q}` (total
correctness) iff `A[0] = 2 ∧ A[1] = 2` implies `Q`. -/
theorem repair_is_strongest (Q : Store → Prop) :
    (∀ s, pre s = true → ∃ t, stepR1 s = some t ∧ Q t) ↔ (∀ t, postActual t = true → Q t) := by
  constructor
  · intro h t ht
    obtain ⟨s, hs, hst⟩ := (exact t).1 ht
    obtain ⟨t', ht', hQ⟩ := h s hs
    rw [hst] at ht'
    injection ht' with ht'
    subst ht'
    exact hQ
  · intro h s hs
    obtain ⟨rest, rfl⟩ := (pre_iff s).1 hs
    exact ⟨2 :: 2 :: rest, stepR1_family rest, h _ ((postActual_iff _).2 ⟨rest, rfl⟩)⟩

/-- The repaired and the asserted postconditions are incompatible. -/
theorem postActual_post_disjoint (t : Store) : ¬ (postActual t = true ∧ post t = true) := by
  rintro ⟨h1, h2⟩
  obtain ⟨r1, rfl⟩ := (postActual_iff t).1 h1
  obtain ⟨r2, h⟩ := (post_iff _).1 h2
  injection h with h _
  revert h; decide

/-! ## (d) Exactness on the claim side: the weakest precondition of the asserted postcondition -/

/-- EXACT (claim side): the asserted postcondition `A[0] = 1 ∧ A[1] = 1` holds after the command
iff it already held before it. -/
theorem exact_wp (s : Store) : holds post (stepR1 s) = true ↔ post s = true := by
  constructor
  · intro h
    cases hs : stepR1 s with
    | none => rw [hs] at h; cases h
    | some t =>
      rw [hs] at h
      have ht : post t = true := h
      obtain ⟨r, rfl⟩ := (post_iff t).1 ht
      have h0 : getI s 0 = 1 := by
        have := A0_invariant s _ hs
        simpa [getI] using this.symm
      match s, h0, hs with
      | [], h0, _ => simp [getI] at h0
      | a :: rest, h0, hs =>
        have ha : a = 1 := by simpa [getI] using h0
        subst ha
        have : stepR1 (1 :: rest) = some (1 :: rest) := by
          show writeAt (1 :: rest) (1 - 1) 1 = _
          exact writeAt_zero 1 1 rest
        rw [this] at hs
        injection hs with hs
        rw [hs]; exact ht
  · intro h
    obtain ⟨r, rfl⟩ := (post_iff s).1 h
    have : stepR1 (1 :: 1 :: r) = some (1 :: 1 :: r) := by
      show writeAt (1 :: 1 :: r) (1 - 1) 1 = _
      exact writeAt_zero 1 1 (1 :: r)
    rw [this]; exact h

/-- The asserted postcondition fails after the command from EVERY store that does not already
satisfy it; the documented family `2 :: 3 :: rest` is only the part of this failure set singled
out by the source's precondition. -/
theorem post_fails_wide (s : Store) (h : post s = false) : holds post (stepR1 s) = false := by
  cases hb : holds post (stepR1 s) with
  | false => rfl
  | true => rw [(exact_wp s).1 hb] at h; cases h

/-- Certified instance outside the documented family: `A[1] = 3` plays no role in the failure. -/
theorem post_fails_outside_family :
    pre [2, 7] = false ∧ resultIs (stepR1 [2, 7]) [2, 2] = true
      ∧ holds post (stepR1 [2, 7]) = false
      ∧ pre [5, 5, 5, 5, 5] = false ∧ holds post (stepR1 [5, 5, 5, 5, 5]) = false := by decide

/-- Consequence: for ANY precondition `P`, the triple `{P} cmd {A[0]=1 ∧ A[1]=1}` is valid iff
`P` already implies `A[0]=1 ∧ A[1]=1`. -/
theorem triple_valid_iff (P : Store → Prop) :
    (∀ s, P s → holds post (stepR1 s) = true) ↔ (∀ s, P s → post s = true) :=
  ⟨fun h s hs => (exact_wp s).1 (h s hs), fun h s hs => (exact_wp s).2 (h s hs)⟩

/-- The failure set of the source's triple is exactly the precondition set (the family). -/
theorem exact_failure_set (s : Store) :
    (pre s = true ∧ holds post (stepR1 s) = false) ↔ pre s = true :=
  ⟨fun h => h.1, fun h => ⟨h, (family_all s h).1⟩⟩

/-! ## The dossier's aside ("a plausible intended example would have been something like
`A[A[0]-1] := A[0]-1`") does NOT rescue the asserted postcondition -/

theorem stepAlt_family (rest : List Int) : stepAlt (2 :: 3 :: rest) = some (2 :: 1 :: rest) := by
  show writeAt (2 :: 3 :: rest) (2 - 1) (2 - 1) = _
  exact writeAt_one 2 3 (2 - 1) rest

theorem post_head (x : Int) (r : List Int) (h : post (x :: r) = true) : x = 1 := by
  obtain ⟨r', h'⟩ := (post_iff _).1 h
  injection h' with h' _

/-- With the alternative command the asserted postcondition is unreachable from EVERY store,
not merely from the family. -/
theorem aside_alt_never_reaches_post (s : Store) : holds post (stepAlt s) = false := by
  cases hb : holds post (stepAlt s) with
  | false => rfl
  | true =>
    exfalso
    cases hs : stepAlt s with
    | none => rw [hs] at hb; cases hb
    | some t =>
      rw [hs] at hb
      have ht : post t = true := hb
      match s, hs with
      | [], hs => simp [stepAlt, writeAt, getI] at hs
      | a :: rest, hs =>
        simp only [stepAlt, writeAt, getI, List.getD_cons_zero] at hs
        split at hs
        · rename_i hc
          injection hs with hs
          subst hs
          simp at hc
          cases hn : (a - 1).toNat with
          | zero =>
            rw [hn] at ht
            have := post_head _ _ (by simpa [setI] using ht)
            omega
          | succ m =>
            rw [hn] at ht
            have := post_head _ _ (by simpa [setI] using ht)
            omega
        · cases hs

/-- Stronger: with the printed constants NO single-cell write `A[i] := v` whatsoever reaches the
asserted postcondition from a member of the family (both cells 0 and 1 would have to change). -/
theorem no_single_write_reaches_post (rest : List Int) (i v : Int) (t : Store)
    (h : writeAt (2 :: 3 :: rest) i v = some t) : post t = false := by
  unfold writeAt at h
  split at h
  · injection h with h
    subst h
    cases hn : i.toNat with
    | zero => simp [setI, post, getI]
    | succ m =>
      cases m with
      | zero => simp [setI, post, getI]
      | succ k => simp [setI, post, getI]
  · cases h

/-- Non-vacuity of the hypothesis of `no_single_write_reaches_post`: in-bounds writes exist and
each changes at most one of the two constrained cells. -/
theorem single_write_examples (rest : List Int) :
    writeAt (2 :: 3 :: rest) 0 1 = some (1 :: 3 :: rest)
  ∧ writeAt (2 :: 3 :: rest) 1 1 = some (2 :: 1 :: rest) :=
  ⟨writeAt_zero 2 1 (3 :: rest), writeAt_one 2 3 1 rest⟩

/-- The negative control of the released file, restated: the asserted postcondition is reachable
by this very command, but only from a store that already satisfies it. -/
theorem negative_control :
    post [1, 1] = true ∧ resultIs (stepR1 [1, 1]) [1, 1] = true ∧ pre [1, 1] = false := by decide

end SE_cs_1200_a1206_Census

#print axioms SE_cs_1200_a1206_Census.claim_refuted_witness
#print axioms SE_cs_1200_a1206_Census.claim_refuted
#print axioms SE_cs_1200_a1206_Census.pre_iff
#print axioms SE_cs_1200_a1206_Census.pre_iff_source
#print axioms SE_cs_1200_a1206_Census.family
#print axioms SE_cs_1200_a1206_Census.family_all
#print axioms SE_cs_1200_a1206_Census.family_unbounded
#print axioms SE_cs_1200_a1206_Census.frame
#print axioms SE_cs_1200_a1206_Census.repair
#print axioms SE_cs_1200_a1206_Census.exact
#print axioms SE_cs_1200_a1206_Census.repair_is_strongest
#print axioms SE_cs_1200_a1206_Census.postActual_post_disjoint
#print axioms SE_cs_1200_a1206_Census.exact_wp
#print axioms SE_cs_1200_a1206_Census.triple_valid_iff
#print axioms SE_cs_1200_a1206_Census.post_fails_wide
#print axioms SE_cs_1200_a1206_Census.post_fails_outside_family
#print axioms SE_cs_1200_a1206_Census.exact_failure_set
#print axioms SE_cs_1200_a1206_Census.A0_invariant
#print axioms SE_cs_1200_a1206_Census.stepR2_eq_stepR1
#print axioms SE_cs_1200_a1206_Census.stepR3_eq_stepR1
#print axioms SE_cs_1200_a1206_Census.stepAlt_family
#print axioms SE_cs_1200_a1206_Census.aside_alt_never_reaches_post
#print axioms SE_cs_1200_a1206_Census.no_single_write_reaches_post
#print axioms SE_cs_1200_a1206_Census.single_write_examples
#print axioms SE_cs_1200_a1206_Census.negative_control
