/-
Explanation census, record SE_cs_156543__q (Stack Exchange cs 156543, question arm).

Core Lean 4 only (no Mathlib, no imports).  The released certificate
  qedbench_certificate_availability_triage/validation/human_review_20260915/lean/SE_cs_156543__q.lean
  (sha256 18997c7006d7c7492c04f833bf6db5029b87a161ba27769a45baf8d98afac1be)
selects `SEcs156543q.infinite_word_refutation`.  Section 1 restates, verbatim, every released
definition that declaration depends on (`Letter`, `emptyL`, `eeL`, `c1L`, `PhiInfinite`,
`sigmaInfinite`, `sigmaPrimeInfinite`), the released helper `nthLetter`, and the released
theorem `infinite_word_refutation` itself (statement and proof script byte-identical; the
released file imports Mathlib, but this script also elaborates in core Lean).  The released
lasso evaluator (`Lasso`, `satF`, `satPos`, ...) is not restated: the selected declaration
does not depend on it.  Everything after Section 1 is new and is NOT part of the release,
with one exception: Section 9 restates, verbatim, the released enumerator (`bindL`,
`allLetters`, `wordsOfLen`) in order to kernel-check the dossier's counts.

Provenance: Sections 1-7 were written by a first agent whose session was interrupted before a
receipt existed; Sections 8-9 were added by a second agent that resumed the work, after
re-reading and recompiling Sections 1-7 unchanged.

Source step (line 0016 of the question): with phi = (P1E & P2E) -> F (P1C | P2C),
  if sigma, i |/= phi and sigma_hat = sigma[..i], then EVERY infinite word sigma' that has
  sigma_hat as a prefix satisfies sigma', i |/= phi.
Documented family: a commit placed at ANY later position repairs the violation, so the step
  fails at every admissible (sigma, i).
Documented repair (corrected classification): every finite prefix extends to a word of
  G phi (appending {P1C}^omega always works), so G phi has no bad prefix: it is a liveness
  property and not a safety property, and no other position or longer prefix saves the step.
-/

namespace SEcs156543q

/-! ## 1. Released definitions, restated verbatim -/

structure Letter where
  p1e : Bool
  p2e : Bool
  p1c : Bool
  p2c : Bool

def emptyL : Letter := ⟨false, false, false, false⟩

def eeL    : Letter := ⟨true,  true,  false, false⟩

def c1L    : Letter := ⟨false, false, true,  false⟩

def nthLetter : List Letter → Nat → Letter → Letter
  | [],      _,     d => d
  | a :: _,  0,     _ => a
  | _ :: as, k + 1, d => nthLetter as k d

def PhiInfinite (w : Nat → Letter) (i : Nat) : Prop :=
  ((w i).p1e = true ∧ (w i).p2e = true) →
    ∃ j : Nat, i ≤ j ∧ ((w j).p1c = true ∨ (w j).p2c = true)

def sigmaInfinite (n : Nat) : Letter := if n = 0 then eeL else emptyL
def sigmaPrimeInfinite (n : Nat) : Letter := if n = 0 then eeL else c1L

/-- Released theorem, statement and proof verbatim. -/
theorem infinite_word_refutation :
    ¬PhiInfinite sigmaInfinite 0 ∧
    sigmaInfinite 0 = sigmaPrimeInfinite 0 ∧
    (∀ i : Nat, PhiInfinite sigmaPrimeInfinite i) := by
  constructor
  · intro h
    obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
    by_cases h0 : j = 0 <;>
      simp [sigmaInfinite, h0, eeL, emptyL] at hj
  constructor
  · rfl
  · intro i hi
    by_cases h0 : i = 0
    · subst i
      exact ⟨1, by decide, Or.inl rfl⟩
    · simp [sigmaPrimeInfinite, h0, c1L] at hi

/-! ## 2. New vocabulary (not released) -/

/-- Version-stable replacements for the core `if_pos` / `if_neg` lemmas. -/
theorem ite_pos' {α : Type} {c : Prop} [Decidable c] (h : c) {a b : α} :
    (if c then a else b) = a := by
  split
  · rfl
  · contradiction

theorem ite_neg' {α : Type} {c : Prop} [Decidable c] (h : ¬c) {a b : α} :
    (if c then a else b) = b := by
  split
  · contradiction
  · rfl

/-- Both processes request entry. -/
def Request (a : Letter) : Prop := a.p1e = true ∧ a.p2e = true

/-- Some process is in its critical section (a "commit"). -/
def Commit (a : Letter) : Prop := a.p1c = true ∨ a.p2c = true

instance (a : Letter) : Decidable (Request a) := by unfold Request; exact inferInstance
instance (a : Letter) : Decidable (Commit a) := by unfold Commit; exact inferInstance

/-- `PhiInfinite` is, definitionally, "request now implies commit now or later". -/
theorem phi_unfold (w : Nat → Letter) (i : Nat) :
    PhiInfinite w i ↔ (Request (w i) → ∃ j : Nat, i ≤ j ∧ Commit (w j)) := Iff.rfl

/-- `u` and `v` have the same finite prefix of length `n` (positions `0 .. n-1`). -/
def AgreeUpTo (n : Nat) (u v : Nat → Letter) : Prop := ∀ k : Nat, k < n → u k = v k

/-- The full property `G phi`. -/
def GPhi (w : Nat → Letter) : Prop := ∀ i : Nat, PhiInfinite w i

/-- The source's step at line 0016, with `sigma_hat = sigma[..i]` the prefix of length `i+1`. -/
def LocalClaim : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → ¬PhiInfinite σ' i

/-- One instance `(sigma, i, sigma')` of the step has true hypotheses and a false conclusion.
Infinite-word analogue of the released `stepInstance phi base i ext = false`. -/
def StepInstanceFails (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter) : Prop :=
  ¬PhiInfinite σ i ∧ AgreeUpTo (i + 1) σ' σ ∧ PhiInfinite σ' i

/-- The step is exactly the absence of failing instances (definition check, not a result). -/
theorem localClaim_iff_no_failing_instance :
    LocalClaim ↔ ∀ (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter), ¬StepInstanceFails σ i σ' := by
  constructor
  · intro h σ i σ' hf
    exact h σ i hf.1 σ' hf.2.1 hf.2.2
  · intro h σ i hadm σ' hag hphi
    exact h σ i σ' ⟨hadm, hag, hphi⟩

/-- Overwrite position `j` of `σ` with the letter `a`. -/
def placeAt (σ : Nat → Letter) (j : Nat) (a : Letter) : Nat → Letter :=
  fun k => if k = j then a else σ k

/-- Keep the first `n` letters of `σ`, then `{P1C}` forever: the dossier's `sigma_hat . {P1C}^omega`. -/
def appendC1 (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else c1L

/-- Keep the first `n` letters of `σ`, then `{}` forever: the dossier's `sigma_hat . {}^omega`. -/
def appendEmpty (σ : Nat → Letter) (n : Nat) : Nat → Letter :=
  fun k => if k < n then σ k else emptyL

/-- The infinite word `w . t^omega` for a finite word `w` given as a list. -/
def wordOf (w : List Letter) (t : Letter) : Nat → Letter := fun k => nthLetter w k t

/-- Source definition of a safety property (lines 0010-0012). -/
def IsSafety (P : (Nat → Letter) → Prop) : Prop :=
  ∀ σ : Nat → Letter, ¬P σ →
    ∃ n : Nat, ∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬P σ'

/-- Standard definition of a liveness property: every finite prefix extends into `P`. -/
def IsLiveness (P : (Nat → Letter) → Prop) : Prop :=
  ∀ (σ : Nat → Letter) (n : Nat), ∃ σ' : Nat → Letter, AgreeUpTo n σ' σ ∧ P σ'

/-! ## 3. The local claim is refuted (released witness) -/

theorem claim_refuted : ¬LocalClaim := by
  intro h
  have hw := infinite_word_refutation
  refine h sigmaInfinite 0 hw.1 sigmaPrimeInfinite ?_ (hw.2.2 0)
  intro k hk
  have hk0 : k = 0 := by omega
  subst hk0
  exact hw.2.1.symm

/-! ## 4. Family: a commit at any later position repairs the violation -/

theorem placeAt_self (σ : Nat → Letter) (j : Nat) (a : Letter) : placeAt σ j a j = a := by
  unfold placeAt; exact ite_pos' rfl

theorem placeAt_other (σ : Nat → Letter) (j k : Nat) (a : Letter) (h : k ≠ j) :
    placeAt σ j a k = σ k := by
  unfold placeAt; exact ite_neg' h

theorem placeAt_agrees (σ : Nat → Letter) (n j : Nat) (a : Letter) (h : n ≤ j) :
    AgreeUpTo n (placeAt σ j a) σ := by
  intro k hk
  exact placeAt_other σ j k a (by omega)

/-- Any word with a commit at some position `j ≥ i` satisfies `phi` at `i`. -/
theorem phi_of_commit (w : Nat → Letter) (i j : Nat) (hij : i ≤ j) (hc : Commit (w j)) :
    PhiInfinite w i := fun _ => ⟨j, hij, hc⟩

/-- FAMILY.  For EVERY admissible pair `(σ, i)` (σ violates phi at i), EVERY later position
`j > i` and EVERY commit letter `a` (P1C, P2C or both, with anything else), the extension of
`sigma_hat = σ[..i]` obtained by placing `a` at position `j` is a failing instance of the step:
it has `sigma_hat` as a prefix and satisfies phi at `i`. -/
theorem family (σ : Nat → Letter) (i : Nat) (hadm : ¬PhiInfinite σ i)
    (j : Nat) (hij : i < j) (a : Letter) (ha : Commit a) :
    StepInstanceFails σ i (placeAt σ j a) := by
  refine ⟨hadm, placeAt_agrees σ (i + 1) j a (by omega), ?_⟩
  apply phi_of_commit _ i j (by omega)
  rw [placeAt_self]; exact ha

/-- The step fails at every admissible pair: it never holds non-vacuously. -/
theorem family_every_admissible_pair_fails (σ : Nat → Letter) (i : Nat)
    (hadm : ¬PhiInfinite σ i) : ∃ σ' : Nat → Letter, StepInstanceFails σ i σ' :=
  ⟨placeAt σ (i + 1) c1L, family σ i hadm (i + 1) (by omega) c1L (Or.inl rfl)⟩

/-- In an admissible word there is no commit at or after position `i`. -/
theorem no_commit_of_admissible (σ : Nat → Letter) (i : Nat) (hadm : ¬PhiInfinite σ i)
    (j : Nat) (hij : i ≤ j) : ¬Commit (σ j) :=
  fun hc => hadm (phi_of_commit σ i j hij hc)

/-- In an admissible word both processes request at position `i`. -/
theorem request_of_admissible (σ : Nat → Letter) (i : Nat) (hadm : ¬PhiInfinite σ i) :
    Request (σ i) := by
  by_cases hr : Request (σ i)
  · exact hr
  · exact absurd (fun h => absurd h hr) hadm

/-- The family is genuinely infinite: for a fixed admissible pair, distinct later positions
give distinct repairing extensions. -/
theorem family_injective (σ : Nat → Letter) (i : Nat) (hadm : ¬PhiInfinite σ i)
    (j j' : Nat) (hij : i < j) (a : Letter) (ha : Commit a)
    (heq : placeAt σ j a = placeAt σ j' a) : j = j' := by
  by_cases h : j = j'
  · exact h
  · have h1 : placeAt σ j a j = placeAt σ j' a j := congrFun heq j
    rw [placeAt_self, placeAt_other σ j' j a h] at h1
    exact absurd (h1 ▸ ha) (no_commit_of_admissible σ i hadm j (by omega))

/-- Admissible pairs exist at every position: the word "request forever, never commit". -/
def allReq : Nat → Letter := fun _ => eeL

theorem allReq_admissible (i : Nat) : ¬PhiInfinite allReq i := by
  intro h
  obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
  cases hj with
  | inl h1 =>
    have h1' : eeL.p1c = true := h1
    exact absurd h1' (by decide)
  | inr h2 =>
    have h2' : eeL.p2c = true := h2
    exact absurd h2' (by decide)

/-- The step fails at every position `i` and with the commit at every later position `j`. -/
theorem family_every_position (i j : Nat) (hij : i < j) :
    StepInstanceFails allReq i (placeAt allReq j c1L) :=
  family allReq i (allReq_admissible i) j hij c1L (Or.inl rfl)

/-! ## 5. Exactness: which extensions repair, and where the step fails -/

/-- EXACT.  For an admissible pair `(σ, i)` and ANY infinite word `σ'` with prefix
`sigma_hat = σ[..i]`:  σ' satisfies phi at i  iff  σ' has a commit at some position `j > i`.
So "place a commit at a later position" is not only sufficient but the only way to repair. -/
theorem exact (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter)
    (hadm : ¬PhiInfinite σ i) (hag : AgreeUpTo (i + 1) σ' σ) :
    PhiInfinite σ' i ↔ ∃ j : Nat, i < j ∧ Commit (σ' j) := by
  have hi : σ' i = σ i := hag i (by omega)
  constructor
  · intro hphi
    have hreq : Request (σ' i) := by rw [hi]; exact request_of_admissible σ i hadm
    obtain ⟨j, hij, hc⟩ := hphi hreq
    refine ⟨j, ?_, hc⟩
    by_cases hji : j = i
    · subst hji
      rw [hi] at hc
      exact absurd hc (no_commit_of_admissible σ j hadm j (Nat.le_refl j))
    · omega
  · intro ⟨j, hij, hc⟩
    exact phi_of_commit σ' i j (by omega) hc

/-- Exact description of the failing instances of the step. -/
theorem exact_failing_instances (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter) :
    StepInstanceFails σ i σ' ↔
      (¬PhiInfinite σ i ∧ AgreeUpTo (i + 1) σ' σ ∧ ∃ j : Nat, i < j ∧ Commit (σ' j)) := by
  constructor
  · intro ⟨hadm, hag, hphi⟩
    exact ⟨hadm, hag, (exact σ i σ' hadm hag).mp hphi⟩
  · intro ⟨hadm, hag, hex⟩
    exact ⟨hadm, hag, (exact σ i σ' hadm hag).mpr hex⟩

/-- Exact description of the pairs `(σ, i)` at which the step fails: all admissible ones. -/
theorem exact_failing_pairs (σ : Nat → Letter) (i : Nat) :
    (∃ σ' : Nat → Letter, StepInstanceFails σ i σ') ↔ ¬PhiInfinite σ i :=
  ⟨fun ⟨_, h⟩ => h.1, family_every_admissible_pair_fails σ i⟩

/-- FAMILY, longer prefix.  If the source had chosen any longer prefix `σ[..n)` with `n > i`,
a commit placed at any position `j ≥ n` still repairs the violation at `i`. -/
theorem family_longer_prefix (σ : Nat → Letter) (i n : Nat) (hadm : ¬PhiInfinite σ i)
    (hin : i < n) (j : Nat) (hnj : n ≤ j) (a : Letter) (ha : Commit a) :
    ¬PhiInfinite σ i ∧ AgreeUpTo n (placeAt σ j a) σ ∧ PhiInfinite (placeAt σ j a) i := by
  refine ⟨hadm, placeAt_agrees σ n j a hnj, ?_⟩
  apply phi_of_commit _ i j (by omega)
  rw [placeAt_self]; exact ha

/-- EXACT, longer prefix.  For an admissible pair `(σ, i)`, any prefix length `n > i` and any
word `σ'` with prefix `σ[..n)`:  σ' satisfies phi at i  iff  σ' has a commit at some `j ≥ n`. -/
theorem exact_longer_prefix (σ : Nat → Letter) (i n : Nat) (σ' : Nat → Letter)
    (hadm : ¬PhiInfinite σ i) (hin : i < n) (hag : AgreeUpTo n σ' σ) :
    PhiInfinite σ' i ↔ ∃ j : Nat, n ≤ j ∧ Commit (σ' j) := by
  constructor
  · intro hphi
    have hreq : Request (σ' i) := by rw [hag i hin]; exact request_of_admissible σ i hadm
    obtain ⟨j, hij, hc⟩ := hphi hreq
    refine ⟨j, ?_, hc⟩
    by_cases hjn : j < n
    · rw [hag j hjn] at hc
      exact absurd hc (no_commit_of_admissible σ i hadm j hij)
    · omega
  · intro ⟨j, hnj, hc⟩
    exact phi_of_commit σ' i j (by omega) hc

/-- Derived corrected step (NOT documented in the dossier; a corollary of `exact`): for an
admissible pair, every extension of `sigma_hat` that never commits after `i` violates phi at
`i`.  The added hypothesis is not a condition on a finite prefix, so this corrected step
cannot serve the source's safety argument. -/
theorem corrected_step (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter)
    (hadm : ¬PhiInfinite σ i) (hag : AgreeUpTo (i + 1) σ' σ)
    (hnc : ∀ j : Nat, i < j → ¬Commit (σ' j)) : ¬PhiInfinite σ' i := by
  intro hphi
  obtain ⟨j, hij, hc⟩ := (exact σ i σ' hadm hag).mp hphi
  exact hnc j hij hc

/-- The hypothesis added in `corrected_step` is necessary. -/
theorem corrected_step_condition_necessary (σ : Nat → Letter) (i : Nat) (σ' : Nat → Letter)
    (hadm : ¬PhiInfinite σ i) (hag : AgreeUpTo (i + 1) σ' σ)
    (hviol : ¬PhiInfinite σ' i) : ∀ j : Nat, i < j → ¬Commit (σ' j) :=
  fun j hij hc => hviol ((exact σ i σ' hadm hag).mpr ⟨j, hij, hc⟩)

/-- Negative control: overwriting a later position with a NON-commit letter never repairs. -/
theorem noncommit_does_not_repair (σ : Nat → Letter) (i : Nat) (hadm : ¬PhiInfinite σ i)
    (j : Nat) (hij : i < j) (a : Letter) (ha : ¬Commit a) :
    ¬PhiInfinite (placeAt σ j a) i := by
  intro hphi
  obtain ⟨k, hik, hc⟩ :=
    (exact σ i (placeAt σ j a) hadm (placeAt_agrees σ (i + 1) j a (by omega))).mp hphi
  by_cases hkj : k = j
  · subst hkj
    rw [placeAt_self] at hc
    exact ha hc
  · rw [placeAt_other σ j k a hkj] at hc
    exact no_commit_of_admissible σ i hadm k (by omega) hc

/-- The dossier's admissibility test is exact: a finite prefix `σ[..n)` and a position `i < n`
arise from SOME violating word iff `sigma_hat . {}^omega` violates phi at `i`. -/
theorem admissibility_test_exact (σ : Nat → Letter) (n i : Nat) (hin : i < n) :
    (∃ τ : Nat → Letter, AgreeUpTo n τ σ ∧ ¬PhiInfinite τ i) ↔
      ¬PhiInfinite (appendEmpty σ n) i := by
  constructor
  · intro ⟨τ, hag, hτ⟩ hphi
    apply hτ
    intro hreq
    have hτi : τ i = σ i := hag i hin
    have hei : appendEmpty σ n i = σ i := by unfold appendEmpty; exact ite_pos' hin
    have hreq' : Request (appendEmpty σ n i) := by rw [hei, ← hτi]; exact hreq
    obtain ⟨j, hij, hc⟩ := hphi hreq'
    by_cases hjn : j < n
    · have hej : appendEmpty σ n j = σ j := by unfold appendEmpty; exact ite_pos' hjn
      rw [hej, ← hag j hjn] at hc
      exact ⟨j, hij, hc⟩
    · have hej : appendEmpty σ n j = emptyL := by unfold appendEmpty; exact ite_neg' hjn
      rw [hej] at hc
      cases hc with
      | inl h1 => exact absurd h1 (by decide)
      | inr h2 => exact absurd h2 (by decide)
  · intro h
    refine ⟨appendEmpty σ n, ?_, h⟩
    intro k hk
    unfold appendEmpty; exact ite_pos' hk

/-! ## 6. Repair: `G phi` has no bad prefix; it is liveness, not safety -/

theorem appendC1_agrees (σ : Nat → Letter) (n : Nat) : AgreeUpTo n (appendC1 σ n) σ := by
  intro k hk
  unfold appendC1; exact ite_pos' hk

theorem appendC1_tail (σ : Nat → Letter) (n k : Nat) (h : ¬k < n) : appendC1 σ n k = c1L := by
  unfold appendC1; exact ite_neg' h

/-- REPAIR.  For EVERY word `σ` and EVERY prefix length `n` (not only `n ≤ 3`), the word
`σ[..n) . {P1C}^omega` has that prefix and satisfies the full formula `G phi`. -/
theorem repair (σ : Nat → Letter) (n : Nat) :
    AgreeUpTo n (appendC1 σ n) σ ∧ GPhi (appendC1 σ n) := by
  refine ⟨appendC1_agrees σ n, ?_⟩
  intro i hreq
  by_cases hin : i < n
  · refine ⟨n, by omega, Or.inl ?_⟩
    rw [appendC1_tail σ n n (by omega)]; rfl
  · rw [appendC1_tail σ n i hin] at hreq
    exact absurd hreq.1 (by decide)

theorem nthLetter_ge : ∀ (w : List Letter) (k : Nat) (d : Letter),
    w.length ≤ k → nthLetter w k d = d
  | [],      _,     _, _ => rfl
  | _ :: _,  0,     _, h => absurd h (by simp)
  | _ :: as, k + 1, d, h => by
      have h' : as.length ≤ k := by
        have : (as.length + 1) ≤ k + 1 := by simpa using h
        omega
      exact nthLetter_ge as k d h'

theorem nthLetter_lt : ∀ (w : List Letter) (k : Nat) (d d' : Letter),
    k < w.length → nthLetter w k d = nthLetter w k d'
  | [],      _,     _, _, h => absurd h (by simp)
  | _ :: _,  0,     _, _, _ => rfl
  | _ :: as, k + 1, d, d', h => by
      have h' : k < as.length := by
        have : k + 1 < as.length + 1 := by simpa using h
        omega
      exact nthLetter_lt as k d d' h'

/-- REPAIR, list form, literally the dossier's sentence "appending {P1C}^omega always works":
for every finite word `w` (any length, including the empty word), `w . {P1C}^omega` keeps
every letter of `w` and satisfies `G phi`. -/
theorem repair_list (w : List Letter) :
    (∀ (k : Nat) (d : Letter), k < w.length → wordOf w c1L k = nthLetter w k d) ∧
      GPhi (wordOf w c1L) := by
  refine ⟨fun k d hk => nthLetter_lt w k c1L d hk, ?_⟩
  intro i hreq
  by_cases hin : i < w.length
  · refine ⟨w.length, by omega, Or.inl ?_⟩
    show (nthLetter w w.length c1L).p1c = true
    rw [nthLetter_ge w w.length c1L (Nat.le_refl _)]; rfl
  · have hi : wordOf w c1L i = c1L := nthLetter_ge w i c1L (by omega)
    rw [hi] at hreq
    exact absurd hreq.1 (by decide)

/-- `G phi` has no bad prefix at all. -/
theorem repair_no_bad_prefix (σ : Nat → Letter) (n : Nat) :
    ¬(∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬GPhi σ') :=
  fun h => h (appendC1 σ n) (repair σ n).1 (repair σ n).2

/-- `G phi` is a liveness property. -/
theorem repair_liveness : IsLiveness GPhi :=
  fun σ n => ⟨appendC1 σ n, (repair σ n).1, (repair σ n).2⟩

/-- `G phi` is not everything: the released violating word is outside it. -/
theorem gphi_not_trivial : ¬GPhi sigmaInfinite :=
  fun h => infinite_word_refutation.1 (h 0)

/-- `G phi` is NOT a safety property, under the source's own definition. -/
theorem repair_not_safety : ¬IsSafety GPhi := by
  intro hs
  obtain ⟨n, hn⟩ := hs sigmaInfinite gphi_not_trivial
  exact repair_no_bad_prefix sigmaInfinite n hn

/-- "The argument cannot be repaired by choosing a different position i or a longer prefix":
for every word, every prefix length `n` and every position `i`, the conclusion of the step
(all extensions of `σ[..n)` violate phi at `i`) is false. -/
theorem repair_no_other_position_or_prefix (σ : Nat → Letter) (n i : Nat) :
    ¬(∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬PhiInfinite σ' i) :=
  fun h => h (appendC1 σ n) (repair σ n).1 ((repair σ n).2 i)

/-- Weaker reading of the source step.  In the source the position `i` is obtained from
"there exists i ≥ 0 such that σ, i |/= phi", so a charitable reader may require the step only
for SOME violating position of each word outside `G phi`. -/
def LocalClaimSomePosition : Prop :=
  ∀ σ : Nat → Letter, ¬GPhi σ →
    ∃ i : Nat, ¬PhiInfinite σ i ∧
      ∀ σ' : Nat → Letter, AgreeUpTo (i + 1) σ' σ → ¬PhiInfinite σ' i

/-- The weaker reading is refuted as well; this needs the family theorem, not only the
released witness, because every violating position of the word has to be excluded. -/
theorem claim_refuted_some_position : ¬LocalClaimSomePosition := by
  intro h
  obtain ⟨i, hadm, hall⟩ := h sigmaInfinite gphi_not_trivial
  obtain ⟨σ', hf⟩ := family_every_admissible_pair_fails sigmaInfinite i hadm
  exact hall σ' hf.2.1 hf.2.2

/-- Weakest reading: for each word outside `G phi` SOME position and SOME prefix length work. -/
def LocalClaimAnyChoice : Prop :=
  ∀ σ : Nat → Letter, ¬GPhi σ →
    ∃ i n : Nat, ∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬PhiInfinite σ' i

/-- Even the weakest reading is refuted: no choice of position or prefix rescues the step. -/
theorem claim_refuted_any_choice : ¬LocalClaimAnyChoice := by
  intro h
  obtain ⟨i, n, hall⟩ := h sigmaInfinite gphi_not_trivial
  exact repair_no_other_position_or_prefix sigmaInfinite n i hall

/-- Definition check: a property that is both safety and liveness has empty complement
(the fact quoted at line 0004 of the source), so the two definitions interlock as intended. -/
theorem safety_and_liveness_trivial (P : (Nat → Letter) → Prop)
    (hs : IsSafety P) (hl : IsLiveness P) (σ : Nat → Letter) : ¬¬P σ := by
  intro hn
  obtain ⟨n, hbad⟩ := hs σ hn
  obtain ⟨σ', hag, hp⟩ := hl σ n
  exact hbad σ' hag hp

/-! ## 7. Slack: the documented repairing construction is sufficient, not necessary -/

def c2L : Letter := ⟨false, false, false, true⟩

def sigmaSlack (n : Nat) : Letter := if n = 0 then eeL else c2L

/-- SLACK.  An extension of the released bad-prefix candidate `sigma_hat = {P1E,P2E}` that
satisfies `G phi` and never contains P1C: "append {P1C}^omega" is not the only repair, and a
P1C commit is not necessary. -/
theorem slack :
    AgreeUpTo 1 sigmaSlack sigmaInfinite ∧ GPhi sigmaSlack ∧
      (∀ k : Nat, (sigmaSlack k).p1c = false) ∧ sigmaSlack ≠ appendC1 sigmaInfinite 1 := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro k hk
    have hk0 : k = 0 := by omega
    subst hk0
    rfl
  · intro i hreq
    by_cases h0 : i = 0
    · subst h0
      exact ⟨1, by decide, Or.inr rfl⟩
    · have hi : sigmaSlack i = c2L := by unfold sigmaSlack; exact ite_neg' h0
      rw [hi] at hreq
      exact absurd hreq.1 (by decide)
  · intro k
    by_cases h0 : k = 0
    · subst h0; rfl
    · have hk : sigmaSlack k = c2L := by unfold sigmaSlack; exact ite_neg' h0
      rw [hk]; rfl
  · intro heq
    have h1 : sigmaSlack 1 = appendC1 sigmaInfinite 1 1 := congrFun heq 1
    have h2 : (sigmaSlack 1).p1c = (appendC1 sigmaInfinite 1 1).p1c := by rw [h1]
    exact absurd h2 (by decide)

/-! ## 8. Added on resume (second agent): the premise behind "not a safety property",
and the exclusive reading of `sigma[..i]` -/

/-- The property that contains every word. -/
def TopProp : (Nat → Letter) → Prop := fun _ => True

/-- "No bad prefix" ALONE does not give "not safety": the trivial property has no bad prefix,
is a liveness property and IS a safety property under the source's definition.  So the dossier's
inference "no bad prefixes at all ... not a safety property" uses one more premise, namely that
`G phi` is not everything (`gphi_not_trivial`), which the dossier supplies through its violating
word sigma. -/
theorem no_bad_prefix_alone_does_not_refute_safety :
    (∀ (σ : Nat → Letter) (n : Nat),
        ¬(∀ σ' : Nat → Letter, AgreeUpTo n σ' σ → ¬TopProp σ')) ∧
      IsLiveness TopProp ∧ IsSafety TopProp := by
  refine ⟨?_, ?_, ?_⟩
  · intro σ n h
    exact h σ (fun _ _ => rfl) True.intro
  · intro σ n
    exact ⟨σ, fun _ _ => rfl, True.intro⟩
  · intro σ hn
    exact absurd True.intro hn

/-- For a liveness property, safety holds exactly when the complement is empty (stated without
classical logic as `¬¬P σ` for every word).  This is the exact form of the dossier's inference. -/
theorem liveness_safety_iff (P : (Nat → Letter) → Prop) (hl : IsLiveness P) :
    IsSafety P ↔ ∀ σ : Nat → Letter, ¬¬P σ := by
  constructor
  · intro hs σ hn
    obtain ⟨n, hbad⟩ := hs σ hn
    obtain ⟨σ', hag, hp⟩ := hl σ n
    exact hbad σ' hag hp
  · intro h σ hn
    exact absurd hn (h σ)

/-- The source step under the EXCLUSIVE reading of `sigma[..i]` (prefix of length `i`, position
`i` itself not fixed). -/
def LocalClaimExclusive : Prop :=
  ∀ (σ : Nat → Letter) (i : Nat), ¬PhiInfinite σ i →
    ∀ σ' : Nat → Letter, AgreeUpTo i σ' σ → ¬PhiInfinite σ' i

/-- The exclusive reading is refuted by the same released witness. -/
theorem claim_refuted_exclusive : ¬LocalClaimExclusive := by
  intro h
  have hw := infinite_word_refutation
  refine h sigmaInfinite 0 hw.1 sigmaPrimeInfinite ?_ (hw.2.2 0)
  intro k hk
  exact absurd hk (Nat.not_lt_zero k)

/-! ## 9. Added on resume (second agent): the dossier's counts, kernel-checked

Released definitions restated verbatim for this section: `bindL`, `allLetters`, `wordsOfLen`.
Everything else in this section is new.  The counts are evaluated by the kernel
(`decide +kernel`: kernel reduction only, no compiled-code evaluation, no compiler trust). -/

def bindL {α β : Type} : List α → (α → List β) → List β
  | [],      _ => []
  | a :: as, f => f a ++ bindL as f

def allLetters : List Letter :=
  bindL [false, true] (fun a =>
    bindL [false, true] (fun b =>
      bindL [false, true] (fun c =>
        [false, true].map (fun d => (⟨a, b, c, d⟩ : Letter)))))

def wordsOfLen : Nat → List (List Letter)
  | 0     => [[]]
  | n + 1 => bindL (wordsOfLen n) (fun w => allLetters.map (fun a => w ++ [a]))

def reqB (a : Letter) : Bool := a.p1e && a.p2e

def comB (a : Letter) : Bool := a.p1c || a.p2c

theorem reqB_iff (a : Letter) : reqB a = true ↔ Request a := by
  cases a with
  | mk e1 e2 c1 c2 => cases e1 <;> cases e2 <;> simp [reqB, Request]

theorem comB_iff (a : Letter) : comB a = true ↔ Commit a := by
  cases a with
  | mk e1 e2 c1 c2 => cases c1 <;> cases c2 <;> simp [comB, Commit]

/-- No letter of the finite word contains a commit. -/
def noCom : List Letter → Bool
  | []      => true
  | a :: as => !comB a && noCom as

theorem noCom_iff : ∀ w : List Letter,
    noCom w = true ↔ ∀ j : Nat, ¬Commit (nthLetter w j emptyL)
  | [] => by
      constructor
      · intro _ j hc
        have hc' : Commit emptyL := hc
        cases hc' with
        | inl h => exact absurd h (by decide)
        | inr h => exact absurd h (by decide)
      · intro _; rfl
  | a :: as => by
      have ih := noCom_iff as
      constructor
      · intro h j
        have h' : (!comB a && noCom as) = true := h
        rw [Bool.and_eq_true] at h'
        cases j with
        | zero =>
          intro hc
          have hca : comB a = true := (comB_iff a).mpr hc
          rw [hca] at h'
          exact absurd h'.1 (by decide)
        | succ k => exact ih.mp h'.2 k
      · intro h
        show (!comB a && noCom as) = true
        rw [Bool.and_eq_true]
        constructor
        · cases hca : comB a with
          | false => rfl
          | true => exact absurd ((comB_iff a).mp hca) (h 0)
        · exact ih.mpr (fun k => h (k + 1))

/-- Boolean form of the dossier's admissibility test for a finite prefix `w` and a position
`i`: `i < |w|`, a request at `i`, and no commit in `w` from `i` on. -/
def admB : List Letter → Nat → Bool
  | [],      _     => false
  | a :: as, 0     => reqB a && noCom (a :: as)
  | _ :: as, i + 1 => admB as i

theorem phi_shift (a : Letter) (as : List Letter) (i : Nat) :
    PhiInfinite (wordOf (a :: as) emptyL) (i + 1) ↔ PhiInfinite (wordOf as emptyL) i := by
  constructor
  · intro h hreq
    obtain ⟨j, hij, hc⟩ := h hreq
    cases j with
    | zero => omega
    | succ k => exact ⟨k, by omega, hc⟩
  · intro h hreq
    obtain ⟨j, hij, hc⟩ := h hreq
    exact ⟨j + 1, by omega, hc⟩

/-- `admB` decides exactly the dossier's semantic test "`w . {}^omega` violates phi at `i`"
(for positions inside the prefix). -/
theorem admB_iff : ∀ (w : List Letter) (i : Nat),
    admB w i = true ↔ (i < w.length ∧ ¬PhiInfinite (wordOf w emptyL) i)
  | [], i => by
      constructor
      · intro h
        have h' : false = true := h
        exact absurd h' (by decide)
      · intro h
        exact absurd h.1 (Nat.not_lt_zero i)
  | a :: as, 0 => by
      constructor
      · intro h
        have h' : (reqB a && noCom (a :: as)) = true := h
        rw [Bool.and_eq_true] at h'
        refine ⟨Nat.succ_pos _, ?_⟩
        intro hphi
        obtain ⟨j, _, hc⟩ := hphi ((reqB_iff a).mp h'.1)
        exact (noCom_iff (a :: as)).mp h'.2 j hc
      · intro h
        show (reqB a && noCom (a :: as)) = true
        rw [Bool.and_eq_true]
        constructor
        · cases hr : reqB a with
          | true => rfl
          | false =>
            exfalso
            apply h.2
            intro hreq
            have hr' : reqB a = true := (reqB_iff a).mpr hreq
            rw [hr] at hr'
            exact absurd hr' (by decide)
        · apply (noCom_iff (a :: as)).mpr
          intro j hc
          exact h.2 (fun _ => ⟨j, Nat.zero_le j, hc⟩)
  | a :: as, i + 1 => by
      have ih := admB_iff as i
      have hlen : (a :: as).length = as.length + 1 := rfl
      show admB as i = true ↔ _
      rw [ih, phi_shift, hlen]
      constructor
      · intro h; exact ⟨by omega, h.2⟩
      · intro h; exact ⟨by omega, h.2⟩

/-- Every admissible (prefix, position) pair in the dossier's list form is repaired, whatever
the length of the prefix: put `{P1C}` right after the prefix.  (Instance of
`family_longer_prefix`; this is the universal statement behind the dossier's "357/357".) -/
theorem admissible_prefix_repaired (w : List Letter) (i : Nat) (h : admB w i = true) :
    AgreeUpTo w.length (placeAt (wordOf w emptyL) w.length c1L) (wordOf w emptyL) ∧
      PhiInfinite (placeAt (wordOf w emptyL) w.length c1L) i := by
  obtain ⟨hi, hadm⟩ := (admB_iff w i).mp h
  have hf := family_longer_prefix (wordOf w emptyL) i w.length hadm hi w.length
    (Nat.le_refl _) c1L (Or.inl rfl)
  exact ⟨hf.2.1, hf.2.2⟩

/-- Number of admissible positions of a prefix. -/
def countAdm (w : List Letter) : Nat := ((List.range w.length).filter (admB w)).length

/-- 1 if the prefix is admissible at its last position (the proof's exact configuration). -/
def lastAdm (w : List Letter) : Nat := if admB w (w.length - 1) then 1 else 0

def total (f : List Letter → Nat) (ws : List (List Letter)) : Nat :=
  ws.foldl (fun acc w => acc + f w) 0

/-- Base-16 code of a letter and of a word, used only to check the enumeration. -/
def codeL (a : Letter) : Nat :=
  (if a.p1e then 8 else 0) + (if a.p2e then 4 else 0) + (if a.p1c then 2 else 0)
    + (if a.p2c then 1 else 0)

def codeW (w : List Letter) : Nat := w.foldl (fun acc a => 16 * acc + codeL a) 0

/-- `ws` lists words of length `n` whose codes are `k, k+1, k+2, ...` in this order
(written with the recursive call in tail position so that the kernel can evaluate it on 4096
words without deep recursion). -/
def codesFrom (n : Nat) : List (List Letter) → Nat → Bool
  | [],      _ => true
  | w :: ws, k => if codeW w == k && w.length == n then codesFrom n ws (k + 1) else false

/-- What `codesFrom` certifies: the word at index `idx` has code `k + idx` and length `n`. -/
theorem codesFrom_get (n : Nat) : ∀ (ws : List (List Letter)) (k : Nat),
    codesFrom n ws k = true →
      ∀ (idx : Nat) (h : idx < ws.length), codeW (ws[idx]) = k + idx ∧ (ws[idx]).length = n
  | [], _, _, idx, h => absurd h (Nat.not_lt_zero idx)
  | w :: ws, k, hcf, idx, h => by
      have hcf' : (if (codeW w == k && w.length == n) = true
          then codesFrom n ws (k + 1) else false) = true := hcf
      by_cases hc : (codeW w == k && w.length == n) = true
      · rw [ite_pos' hc] at hcf'
        rw [Bool.and_eq_true] at hc
        have h1 : codeW w = k := by simpa using hc.1
        have h2 : w.length = n := by simpa using hc.2
        cases idx with
        | zero => exact ⟨h1, h2⟩
        | succ m =>
          have hm : m < ws.length := by
            have : m + 1 < ws.length + 1 := h
            omega
          have ih := codesFrom_get n ws (k + 1) hcf' m hm
          show codeW (ws[m]) = k + (m + 1) ∧ (ws[m]).length = n
          exact ⟨by omega, ih.2⟩
      · rw [ite_neg' hc] at hcf'
        exact absurd hcf' (by decide)

/-- A list passing `codesFrom` has no repeated word. -/
theorem codesFrom_no_repeats (n : Nat) (ws : List (List Letter)) (k : Nat)
    (hcf : codesFrom n ws k = true) (i j : Nat) (hi : i < ws.length) (hj : j < ws.length)
    (heq : ws[i] = ws[j]) : i = j := by
  have a := (codesFrom_get n ws k hcf i hi).1
  have b := (codesFrom_get n ws k hcf j hj).1
  rw [heq] at a
  omega

/-- The released enumerator lists, for n = 1, 2, 3, words of length n with codes
0, 1, 2, ... in order; with `codesFrom_no_repeats` this means no word is listed twice. -/
theorem enumeration_check :
    codesFrom 1 (wordsOfLen 1) 0 = true ∧ codesFrom 2 (wordsOfLen 2) 0 = true ∧
      codesFrom 3 (wordsOfLen 3) 0 = true := by
  decide +kernel

theorem mem_bindL {α β : Type} (f : α → List β) (b : β) :
    ∀ (l : List α) (a : α), a ∈ l → b ∈ f a → b ∈ bindL l f
  | [], _, ha, _ => nomatch ha
  | x :: xs, a, ha, hb => by
      show b ∈ f x ++ bindL xs f
      rw [List.mem_append]
      cases ha with
      | head => exact Or.inl hb
      | tail _ ha' => exact Or.inr (mem_bindL f b xs a ha' hb)

theorem mem_allLetters (a : Letter) : a ∈ allLetters := by
  cases a with
  | mk e1 e2 c1 c2 =>
    cases e1 <;> cases e2 <;> cases c1 <;> cases c2 <;> simp [allLetters, bindL]

theorem snoc_decomposition : ∀ (n : Nat) (w : List Letter), w.length = n + 1 →
    ∃ (w' : List Letter) (a : Letter), w = w' ++ [a] ∧ w'.length = n
  | _, [], h => nomatch h
  | 0, [x], _ => ⟨[], x, rfl, rfl⟩
  | 0, _ :: _ :: _, h => by
      have : False := by simp at h
      exact this.elim
  | n + 1, x :: xs, h => by
      have hxs : xs.length = n + 1 := by
        have : xs.length + 1 = n + 1 + 1 := h
        omega
      obtain ⟨w', a, hw, hl⟩ := snoc_decomposition n xs hxs
      refine ⟨x :: w', a, ?_, ?_⟩
      · rw [hw]; rfl
      · show w'.length + 1 = n + 1
        omega

/-- The released enumerator is complete at every length: each word of length `n` is listed. -/
theorem enumeration_complete : ∀ (n : Nat) (w : List Letter), w.length = n → w ∈ wordsOfLen n
  | 0, w, h => by
      cases w with
      | nil => exact List.Mem.head _
      | cons x xs => exact nomatch h
  | n + 1, w, h => by
      obtain ⟨w', a, hw, hl⟩ := snoc_decomposition n w h
      show w ∈ bindL (wordsOfLen n) (fun w => allLetters.map (fun a => w ++ [a]))
      apply mem_bindL _ w (wordsOfLen n) w' (enumeration_complete n w' hl)
      rw [hw]
      exact List.mem_map.mpr ⟨a, mem_allLetters a, rfl⟩

/-- Dossier: "all 4368 prefixes of length 1..3". -/
theorem dossier_count_prefixes :
    (wordsOfLen 1).length + (wordsOfLen 2).length + (wordsOfLen 3).length = 4368 := by
  decide +kernel

/-- Dossier: "357 admissible pairs". -/
theorem dossier_count_admissible :
    total countAdm (wordsOfLen 1) + total countAdm (wordsOfLen 2)
      + total countAdm (wordsOfLen 3) = 357 := by
  decide +kernel

/-- Dossier: "273 with i = |sigma_hat| - 1". -/
theorem dossier_count_admissible_last :
    total lastAdm (wordsOfLen 1) + total lastAdm (wordsOfLen 2)
      + total lastAdm (wordsOfLen 3) = 273 := by
  decide +kernel

/-- Dossier: "4624 extensions sigma_hat . u . v^omega with |u| <= 1 and 1 <= |v| <= 2". -/
theorem dossier_count_extensions :
    ((wordsOfLen 0).length + (wordsOfLen 1).length)
      * ((wordsOfLen 1).length + (wordsOfLen 2).length) = 4624 := by
  decide +kernel

/-- Consistency with the released sweep (lengths 1..2): 21 admissible pairs, 17 at the last
position, the numbers of the released `admissible_count` theorems, recomputed with `admB`. -/
theorem released_counts_recomputed :
    total countAdm (wordsOfLen 1) + total countAdm (wordsOfLen 2) = 21 ∧
    total lastAdm (wordsOfLen 1) + total lastAdm (wordsOfLen 2) = 17 := by
  decide +kernel

end SEcs156543q

#print axioms SEcs156543q.infinite_word_refutation
#print axioms SEcs156543q.localClaim_iff_no_failing_instance
#print axioms SEcs156543q.claim_refuted
#print axioms SEcs156543q.family
#print axioms SEcs156543q.family_every_admissible_pair_fails
#print axioms SEcs156543q.family_injective
#print axioms SEcs156543q.family_every_position
#print axioms SEcs156543q.exact
#print axioms SEcs156543q.exact_failing_instances
#print axioms SEcs156543q.exact_failing_pairs
#print axioms SEcs156543q.family_longer_prefix
#print axioms SEcs156543q.exact_longer_prefix
#print axioms SEcs156543q.corrected_step
#print axioms SEcs156543q.corrected_step_condition_necessary
#print axioms SEcs156543q.noncommit_does_not_repair
#print axioms SEcs156543q.admissibility_test_exact
#print axioms SEcs156543q.repair
#print axioms SEcs156543q.repair_list
#print axioms SEcs156543q.repair_no_bad_prefix
#print axioms SEcs156543q.repair_liveness
#print axioms SEcs156543q.repair_not_safety
#print axioms SEcs156543q.repair_no_other_position_or_prefix
#print axioms SEcs156543q.claim_refuted_some_position
#print axioms SEcs156543q.claim_refuted_any_choice
#print axioms SEcs156543q.safety_and_liveness_trivial
#print axioms SEcs156543q.slack
#print axioms SEcs156543q.no_bad_prefix_alone_does_not_refute_safety
#print axioms SEcs156543q.liveness_safety_iff
#print axioms SEcs156543q.claim_refuted_exclusive
#print axioms SEcs156543q.admB_iff
#print axioms SEcs156543q.admissible_prefix_repaired
#print axioms SEcs156543q.codesFrom_get
#print axioms SEcs156543q.codesFrom_no_repeats
#print axioms SEcs156543q.enumeration_check
#print axioms SEcs156543q.enumeration_complete
#print axioms SEcs156543q.dossier_count_prefixes
#print axioms SEcs156543q.dossier_count_admissible
#print axioms SEcs156543q.dossier_count_admissible_last
#print axioms SEcs156543q.dossier_count_extensions
#print axioms SEcs156543q.released_counts_recomputed
