/-
Explanation census, record reddit_askmath_1bq1jtc.  Core Lean only: no imports, no Mathlib.

Released certificate (not modified, not imported):
  partB_feasibility/reddit_certificates/reddit_askmath_1bq1jtc.lean
  sha256 d2b5e94a6ac955318c3818136df963e5c79e613f27ee34a28735f2148f31af36
  selected declaration RedditAskmath1bq1jtc.audited_counterexample :
      (6*(0 : ℤ)+2) ≠ 2*(3*0+2)
The released file has no definitions; its one theorem is restated below as `claim_refuted`
(`ℤ` is Mathlib notation for core `Int`; the statement is otherwise character for character the same).

Source line (verbatim): "6q + 2 = 2(3q +2) so is even."
Dossier, family:  "The two expressions differ by 2 for every integer q."
Dossier, repair:  "Expanding the claimed right-hand side gives 2(3q + 2) = 6q + 4, not 6q + 2."
Model-written formalisation; no human review.
-/
namespace RedditAskmath1bq1jtcCensus

/-! ## (a) the refuted local claim -/

/-- The quoted equality at `q`, exactly as the source writes it. -/
def Claim (q : Int) : Prop := 6*q+2 = 2*(3*q+2)

/-- The released theorem, restated (released witness `q = 0`: `2 ≠ 4`). -/
theorem claim_refuted : (6*(0 : Int)+2) ≠ 2*(3*0+2) := by decide

/-- The same thing through `Claim`. -/
theorem claim_refuted' : ¬ Claim 0 := by unfold Claim; decide

/-- The source asserts the equality for the arbitrary quotient `q`; that universal claim is false. -/
theorem universal_claim_refuted : ¬ (∀ q : Int, Claim q) := fun h => claim_refuted' (h 0)

/-! ## (b) the documented family: the claim fails at EVERY integer -/

/-- "The two expressions differ by 2 for every integer q." -/
theorem family_gap : ∀ q : Int, 2*(3*q+2) - (6*q+2) = 2 := by
  intro q; omega

/-- Family (universal): the quoted equality fails at every integer `q`. -/
theorem family : ∀ q : Int, 6*q+2 ≠ 2*(3*q+2) := by
  intro q; omega

/-- Family over the natural numbers (the quotient of a prime by 6 is a natural number). -/
theorem family_nat : ∀ q : Nat, 6*q+2 ≠ 2*(3*q+2) := by
  intro q; omega

/-- The released witness is the member `q = 0` of the family. -/
theorem claim_refuted_from_family : (6*(0 : Int)+2) ≠ 2*(3*0+2) := family 0

/-! ## (c) the documented repair -/

/-- Repair exactly as the dossier words it: the right-hand side expands to `6q + 4`. -/
theorem repair_dossier : ∀ q : Int, 2*(3*q+2) = 6*q+4 := by
  intro q; omega

/-- "... not 6q + 2": the dossier's expansion and the source's left-hand side never agree. -/
theorem repair_dossier_not : ∀ q : Int, 6*q+4 ≠ 6*q+2 := by
  intro q; omega

/-- The dossier's repair, read as an equation with the right-hand side kept, is the source's own
    NEXT line ("6q + 4 = 2(3q + 2) so is even"), which was never in doubt. -/
theorem source_next_line : ∀ q : Int, 6*q+4 = 2*(3*q+2) := by
  intro q; omega

/-- Repair the source's step needs (NOT stated in the dossier's explanation field nor in the roster's
    repair string; a checker's note in the source packet does state it): the factorisation of `6q+2`. -/
theorem repair : ∀ q : Int, 6*q+2 = 2*(3*q+1) := by
  intro q; omega

/-- With it the source's inference "so is even" goes through for every `q`. -/
theorem repair_even : ∀ q : Int, (2 : Int) ∣ 6*q+2 := by
  intro q; exact ⟨3*q+1, repair q⟩

/-- Natural-number forms. -/
theorem repair_nat : ∀ q : Nat, 6*q+2 = 2*(3*q+1) := by
  intro q; omega

/-! ## (d) exactness -/

/-- Exact failure set: the quoted equality holds at no integer. -/
theorem exact : ∀ q : Int, (6*q+2 = 2*(3*q+2)) ↔ False := by
  intro q; constructor
  · intro h; exact family q h
  · intro h; exact h.elim

/-- Exact repair constant: `6q + 2 = 2(3q + c)` holds iff `c = 1`, for every `q`. -/
theorem exact_constant : ∀ q c : Int, (6*q+2 = 2*(3*q+c)) ↔ c = 1 := by
  intro q c; constructor <;> intro h <;> omega

/-- Exact repair among all factorisations `2(aq + b)`: only `a = 3`, `b = 1`. -/
theorem exact_linear : ∀ a b : Int, (∀ q : Int, 6*q+2 = 2*(a*q+b)) ↔ (a = 3 ∧ b = 1) := by
  intro a b; constructor
  · intro h
    have h0 := h 0
    have h1 := h 1
    simp only [Int.mul_zero, Int.mul_one] at h0 h1
    omega
  · rintro ⟨rfl, rfl⟩ q
    omega

/-- Exact modulus: the quoted equality holds modulo `m` iff `m ∣ 2`
    (so it is true in `Z/2`, which is all that "so is even" uses, and false in every `Z/m`, `m > 2`, and in `Z`). -/
theorem exact_modulus : ∀ m q : Int, m ∣ (2*(3*q+2) - (6*q+2)) ↔ m ∣ 2 := by
  intro m q; rw [family_gap q]

/-- The same in remainder form (Lean's `x % 0 = x`, `0 ∣ 2` false: the case `m = 0` is the integers). -/
theorem exact_modulus_emod : ∀ m q : Int, (6*q+2) % m = (2*(3*q+2)) % m ↔ m ∣ 2 := by
  intro m q
  have hgap : (6*q+2) - 2*(3*q+2) = -2 := by omega
  rw [Int.emod_eq_emod_iff_emod_sub_eq_zero, hgap, ← Int.dvd_iff_emod_eq_zero, Int.dvd_neg]

/-- Instance: modulo 2 the quoted equality is true at every `q`. -/
theorem holds_mod_two : ∀ q : Int, (6*q+2) % 2 = (2*(3*q+2)) % 2 :=
  fun q => (exact_modulus_emod 2 q).mpr ⟨1, by decide⟩

/-- Instance: modulo 3 it is false at every `q`. -/
theorem fails_mod_three : ∀ q : Int, (6*q+2) % 3 ≠ (2*(3*q+2)) % 3 := by
  intro q; omega

/-! ## The conclusion the dossier calls true ("not a refutation of the true prime>3 conclusion") -/

/-- Primality on `Nat`, stated from scratch (no Mathlib). -/
def IsPrime (p : Nat) : Prop := 2 ≤ p ∧ ∀ d : Nat, d ∣ p → d = 1 ∨ d = p

/-- The source's theorem: every prime other than 2 and 3 is `6q + 1` or `6q + 5`. -/
theorem source_conclusion (p : Nat) (hp : IsPrime p) (h2 : p ≠ 2) (h3 : p ≠ 3) :
    (∃ q : Nat, p = 6*q+1) ∨ (∃ q : Nat, p = 6*q+5) := by
  obtain ⟨hp2, hd⟩ := hp
  have a2 := hd 2
  have a3 := hd 3
  have h : p % 6 = 1 ∨ p % 6 = 5 := by omega
  rcases h with h | h
  · left; exact ⟨p / 6, by omega⟩
  · right; exact ⟨p / 6, by omega⟩

/-- In the four residue classes the source discards, the only primes are 2 and 3. -/
theorem discarded_classes (p : Nat) (hp : IsPrime p)
    (hr : p % 6 = 0 ∨ p % 6 = 2 ∨ p % 6 = 3 ∨ p % 6 = 4) : p = 2 ∨ p = 3 := by
  obtain ⟨hp2, hd⟩ := hp
  have a2 := hd 2
  have a3 := hd 3
  omega

theorem isPrime_two : IsPrime 2 := by
  refine ⟨by decide, ?_⟩
  intro d h
  have hle := Nat.le_of_dvd (by decide) h
  obtain ⟨k, hk⟩ := h
  have : d = 0 ∨ d = 1 ∨ d = 2 := by omega
  rcases this with rfl | rfl | rfl <;> omega

theorem isPrime_three : IsPrime 3 := by
  refine ⟨by decide, ?_⟩
  intro d h
  have hle := Nat.le_of_dvd (by decide) h
  obtain ⟨k, hk⟩ := h
  have : d = 0 ∨ d = 1 ∨ d = 2 ∨ d = 3 := by omega
  rcases this with rfl | rfl | rfl | rfl <;> omega

theorem isPrime_five : IsPrime 5 := by
  refine ⟨by decide, ?_⟩
  intro d h
  have hle := Nat.le_of_dvd (by decide) h
  obtain ⟨k, hk⟩ := h
  have : d = 0 ∨ d = 1 ∨ d = 2 ∨ d = 3 ∨ d = 4 ∨ d = 5 := by omega
  rcases this with rfl | rfl | rfl | rfl | rfl | rfl <;> omega

theorem isPrime_seven : IsPrime 7 := by
  refine ⟨by decide, ?_⟩
  intro d h
  have hle := Nat.le_of_dvd (by decide) h
  obtain ⟨k, hk⟩ := h
  have : d = 0 ∨ d = 1 ∨ d = 2 ∨ d = 3 ∨ d = 4 ∨ d = 5 ∨ d = 6 ∨ d = 7 := by omega
  rcases this with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> omega

/-- The form is necessary, not sufficient: `25 = 6*4 + 1` is not prime. -/
theorem form_not_sufficient : (∃ q : Nat, 25 = 6*q+1) ∧ ¬ IsPrime 25 := by
  refine ⟨⟨4, by decide⟩, ?_⟩
  rintro ⟨_, h⟩
  have := h 5 ⟨5, by decide⟩
  omega

end RedditAskmath1bq1jtcCensus

#print axioms RedditAskmath1bq1jtcCensus.claim_refuted
#print axioms RedditAskmath1bq1jtcCensus.claim_refuted'
#print axioms RedditAskmath1bq1jtcCensus.universal_claim_refuted
#print axioms RedditAskmath1bq1jtcCensus.family_gap
#print axioms RedditAskmath1bq1jtcCensus.family
#print axioms RedditAskmath1bq1jtcCensus.family_nat
#print axioms RedditAskmath1bq1jtcCensus.claim_refuted_from_family
#print axioms RedditAskmath1bq1jtcCensus.repair_dossier
#print axioms RedditAskmath1bq1jtcCensus.repair_dossier_not
#print axioms RedditAskmath1bq1jtcCensus.source_next_line
#print axioms RedditAskmath1bq1jtcCensus.repair
#print axioms RedditAskmath1bq1jtcCensus.repair_even
#print axioms RedditAskmath1bq1jtcCensus.repair_nat
#print axioms RedditAskmath1bq1jtcCensus.exact
#print axioms RedditAskmath1bq1jtcCensus.exact_constant
#print axioms RedditAskmath1bq1jtcCensus.exact_linear
#print axioms RedditAskmath1bq1jtcCensus.exact_modulus
#print axioms RedditAskmath1bq1jtcCensus.exact_modulus_emod
#print axioms RedditAskmath1bq1jtcCensus.holds_mod_two
#print axioms RedditAskmath1bq1jtcCensus.fails_mod_three
#print axioms RedditAskmath1bq1jtcCensus.source_conclusion
#print axioms RedditAskmath1bq1jtcCensus.discarded_classes
#print axioms RedditAskmath1bq1jtcCensus.isPrime_two
#print axioms RedditAskmath1bq1jtcCensus.isPrime_three
#print axioms RedditAskmath1bq1jtcCensus.isPrime_five
#print axioms RedditAskmath1bq1jtcCensus.isPrime_seven
#print axioms RedditAskmath1bq1jtcCensus.form_not_sufficient
