/-!
Explanation census, record reddit_learnmath_8yjpp7.  Core Lean, no imports.

Released certificate (not modified, not imported):
  partB_feasibility/reddit_certificates/reddit_learnmath_8yjpp7.lean
  theorem Audit_reddit_learnmath_8yjpp7.certificate :
    Odd (5 : ℕ) ∧ Even (5 / 2 : ℕ) ∧ ((5 / 2 : ℕ)+1)*2 = 6 ∧ ((5 / 2 : ℕ)+1)*2 ≠ 5+2
The released file has no definitions of its own; `Odd` and `Even` are Mathlib's.
Mathlib unfolds them on Nat to `∃ m, n = 2 * m + 1` and `∃ r, n = r + r`.  This core
file states them in that unfolded form (`IsOdd`, `IsEven`) and proves the link to the
remainder form.  The companion file reddit_learnmath_8yjpp7_explanation_mathlib.lean
restates the headline theorems over Mathlib's own `Odd` and `Even`, with the released
theorem restated verbatim.

Source claim (the odd branch of an induction about the pseudocode `Increment`):
  "If floor(n / 2) is even then we have the aforementioned case 1) in the recursive
   call and thus we have (floor(n / 2)+ 1) * 2 = n + 2."
Documented explanation:
  "Generally, the hypotheses imply n=4k+1. Then floor(n/2)=2k, so
   (floor(n/2)+1)*2=4k+2=n+1, not n+2."
-/

namespace Census_reddit_learnmath_8yjpp7

/-- Mathlib's `Odd` on Nat, unfolded. -/
def IsOdd (n : Nat) : Prop := ∃ m, n = 2 * m + 1
/-- Mathlib's `Even` on Nat, unfolded. -/
def IsEven (n : Nat) : Prop := ∃ r, n = r + r

theorem isOdd_iff (n : Nat) : IsOdd n ↔ n % 2 = 1 := by
  constructor
  · intro h
    cases h with
    | intro m hm => omega
  · intro h
    exact ⟨n / 2, by omega⟩

theorem isEven_iff (n : Nat) : IsEven n ↔ n % 2 = 0 := by
  constructor
  · intro h
    cases h with
    | intro r hr => omega
  · intro h
    exact ⟨n / 2, by omega⟩

/-- The source's local claim, both hypotheses retained (oddness comes from the
enclosing "2) n is odd" branch, the floor-even hypothesis from the quoted sentence). -/
def SourceClaim : Prop :=
  ∀ n : Nat, IsOdd n → IsEven (n / 2) → (n / 2 + 1) * 2 = n + 2

/-- The quoted sentence read alone: only the floor-even hypothesis. -/
def SourceClaimQuoteOnly : Prop :=
  ∀ n : Nat, IsEven (n / 2) → (n / 2 + 1) * 2 = n + 2

/-- The released witness, in the released theorem's shape. -/
theorem claim_refuted_witness :
    IsOdd 5 ∧ IsEven (5 / 2) ∧ (5 / 2 + 1) * 2 = 6 ∧ (5 / 2 + 1) * 2 ≠ 5 + 2 :=
  ⟨⟨2, rfl⟩, ⟨1, rfl⟩, rfl, by decide⟩

theorem claim_refuted : ¬ SourceClaim := by
  intro h
  have h5 := h 5 ⟨2, rfl⟩ ⟨1, rfl⟩
  exact absurd h5 (by decide)

theorem claim_refuted_quote_only : ¬ SourceClaimQuoteOnly := by
  intro h
  have h5 := h 5 ⟨1, rfl⟩
  exact absurd h5 (by decide)

/-! ### The documented family: "the hypotheses imply n=4k+1" -/

/-- "the hypotheses imply n=4k+1", and conversely: the hypothesis set IS the family. -/
theorem hypotheses_iff_family (n : Nat) :
    (IsOdd n ∧ IsEven (n / 2)) ↔ ∃ k, n = 4 * k + 1 := by
  rw [isOdd_iff, isEven_iff]
  constructor
  · intro h
    exact ⟨n / 4, by omega⟩
  · intro h
    cases h with
    | intro k hk => omega

/-- "Then floor(n/2)=2k, so (floor(n/2)+1)*2=4k+2=n+1, not n+2", for every k. -/
theorem family (k : Nat) :
    IsOdd (4 * k + 1) ∧ IsEven ((4 * k + 1) / 2) ∧
    (4 * k + 1) / 2 = 2 * k ∧
    ((4 * k + 1) / 2 + 1) * 2 = 4 * k + 2 ∧
    4 * k + 2 = (4 * k + 1) + 1 ∧
    ((4 * k + 1) / 2 + 1) * 2 ≠ (4 * k + 1) + 2 := by
  refine ⟨⟨2 * k, by omega⟩, ⟨k, by omega⟩, by omega, by omega, by omega, by omega⟩

/-- The claim fails at EVERY n satisfying its hypotheses (not only at some). -/
theorem family_all (n : Nat) (h1 : IsOdd n) (_h2 : IsEven (n / 2)) :
    (n / 2 + 1) * 2 ≠ n + 2 := by
  rw [isOdd_iff] at h1
  omega

/-- The family is unbounded and its members are distinct. -/
theorem family_unbounded (N : Nat) :
    ∃ n, N < n ∧ IsOdd n ∧ IsEven (n / 2) ∧ (n / 2 + 1) * 2 ≠ n + 2 := by
  refine ⟨4 * N + 1, by omega, ⟨2 * N, by omega⟩, ⟨N, by omega⟩, by omega⟩

/-- Exact failure set of the source claim: hypotheses hold and the conclusion fails
iff n = 4k+1. -/
theorem exact_failure_set (n : Nat) :
    (IsOdd n ∧ IsEven (n / 2) ∧ (n / 2 + 1) * 2 ≠ n + 2) ↔ ∃ k, n = 4 * k + 1 := by
  rw [isOdd_iff, isEven_iff]
  constructor
  · intro h
    exact ⟨n / 4, by omega⟩
  · intro h
    cases h with
    | intro k hk => omega

/-! ### The documented repair: the expression equals n+1 -/

/-- The repair under the documented hypotheses. -/
theorem repair (n : Nat) (h1 : IsOdd n) (_h2 : IsEven (n / 2)) :
    (n / 2 + 1) * 2 = n + 1 := by
  rw [isOdd_iff] at h1
  omega

/-- The repair does not need the floor-even hypothesis: every odd n. -/
theorem repair_all_odd (n : Nat) (h1 : IsOdd n) : (n / 2 + 1) * 2 = n + 1 := by
  rw [isOdd_iff] at h1
  omega

/-- Slack: n = 3 is outside the documented family (floor(3/2) = 1 is not even,
3 is not of the form 4k+1) and the repaired identity holds there all the same. -/
theorem slack :
    IsOdd 3 ∧ ¬ IsEven (3 / 2) ∧ (¬ ∃ k, 3 = 4 * k + 1) ∧ (3 / 2 + 1) * 2 = 3 + 1 := by
  refine ⟨⟨1, rfl⟩, ?_, ?_, rfl⟩
  · rw [isEven_iff]; decide
  · intro h
    cases h with
    | intro k hk => omega

/-- Exactness of the repair: the expression equals n+1 iff n is odd. -/
theorem exact (n : Nat) : (n / 2 + 1) * 2 = n + 1 ↔ IsOdd n := by
  rw [isOdd_iff]
  omega

/-- Exactness of the source's equation: the expression equals n+2 iff n is even.
So the source's equation is the even-branch identity used in the odd branch. -/
theorem exact_claimed_equation (n : Nat) : (n / 2 + 1) * 2 = n + 2 ↔ IsEven n := by
  rw [isEven_iff]
  omega

/-- The two candidate values cover every n and never coincide. -/
theorem dichotomy (n : Nat) :
    ((n / 2 + 1) * 2 = n + 1 ∨ (n / 2 + 1) * 2 = n + 2) ∧
    ¬ ((n / 2 + 1) * 2 = n + 1 ∧ (n / 2 + 1) * 2 = n + 2) := by
  omega

/-! ### The quote-only reading (ambiguity in "the hypotheses") -/

/-- If oddness is not counted among "the hypotheses", the dossier sentence
"the hypotheses imply n=4k+1" is false: n = 4 has floor(4/2) = 2 even. -/
theorem quote_only_hypothesis_does_not_imply_family :
    ¬ (∀ n : Nat, IsEven (n / 2) → ∃ k, n = 4 * k + 1) := by
  intro h
  cases h 4 ⟨1, rfl⟩ with
  | intro k hk => omega

/-- Under the quote-only reading the claim holds exactly on the multiples of 4 and
fails exactly on the documented family. -/
theorem quote_only_exact (n : Nat) (h : IsEven (n / 2)) :
    ((n / 2 + 1) * 2 = n + 2 ↔ ∃ k, n = 4 * k) ∧
    ((n / 2 + 1) * 2 ≠ n + 2 ↔ ∃ k, n = 4 * k + 1) := by
  rw [isEven_iff] at h
  refine ⟨⟨fun h' => ⟨n / 4, by omega⟩, fun h' => ?_⟩, ⟨fun h' => ⟨n / 4, by omega⟩, fun h' => ?_⟩⟩
  · cases h' with
    | intro k hk => omega
  · cases h' with
    | intro k hk => omega

/-! ### The algorithm of the source, and what the repair buys -/

/-- The source's pseudocode:
    Increment(y): if y = 0 then return(1) else
                    if (y mod 2) = 1 then return(2 · Increment(y/2)) else return(y + 1) -/
def Increment (y : Nat) : Nat :=
  if h0 : y = 0 then 1
  else if y % 2 = 1 then 2 * Increment (y / 2)
  else y + 1
termination_by y
decreasing_by omega

/-- The statement the source's induction is after.  Its odd step is exactly
`repair_all_odd`; with the source's `n + 2` the step would not close. -/
theorem increment_correct (n : Nat) : Increment n = n + 1 := by
  induction n using Nat.strongRecOn with
  | ind n ih =>
    unfold Increment
    split
    · omega
    · split
      · have hlt : n / 2 < n := by omega
        rw [ih (n / 2) hlt]
        omega
      · rfl

/-- The source's "thus we have" expression is what the function returns on the
family, and that value is n+1, never n+2. -/
theorem increment_on_family (n : Nat) (h1 : IsOdd n) (h2 : IsEven (n / 2)) :
    Increment n = (n / 2 + 1) * 2 ∧ Increment n = n + 1 ∧ Increment n ≠ n + 2 := by
  have hr := repair n h1 h2
  have hc := increment_correct n
  omega

/-! ### Integers with floor division (the range searched in the dossier appendix) -/

/-- On Int, `/` by the positive literal 2 is floor division.  Same exact failure set. -/
theorem int_exact_failure_set (n : Int) :
    ((n / 2) % 2 = 0 ∧ (n / 2 + 1) * 2 ≠ n + 2) ↔ n % 4 = 1 := by
  omega

theorem int_repair_all_odd (n : Int) (h : n % 2 = 1) : (n / 2 + 1) * 2 = n + 1 := by
  omega

theorem int_exact (n : Int) : (n / 2 + 1) * 2 = n + 1 ↔ n % 2 = 1 := by
  omega

end Census_reddit_learnmath_8yjpp7

#print axioms Census_reddit_learnmath_8yjpp7.claim_refuted_witness
#print axioms Census_reddit_learnmath_8yjpp7.claim_refuted
#print axioms Census_reddit_learnmath_8yjpp7.claim_refuted_quote_only
#print axioms Census_reddit_learnmath_8yjpp7.isOdd_iff
#print axioms Census_reddit_learnmath_8yjpp7.isEven_iff
#print axioms Census_reddit_learnmath_8yjpp7.hypotheses_iff_family
#print axioms Census_reddit_learnmath_8yjpp7.family
#print axioms Census_reddit_learnmath_8yjpp7.family_all
#print axioms Census_reddit_learnmath_8yjpp7.family_unbounded
#print axioms Census_reddit_learnmath_8yjpp7.exact_failure_set
#print axioms Census_reddit_learnmath_8yjpp7.repair
#print axioms Census_reddit_learnmath_8yjpp7.repair_all_odd
#print axioms Census_reddit_learnmath_8yjpp7.slack
#print axioms Census_reddit_learnmath_8yjpp7.exact
#print axioms Census_reddit_learnmath_8yjpp7.exact_claimed_equation
#print axioms Census_reddit_learnmath_8yjpp7.dichotomy
#print axioms Census_reddit_learnmath_8yjpp7.quote_only_hypothesis_does_not_imply_family
#print axioms Census_reddit_learnmath_8yjpp7.quote_only_exact
#print axioms Census_reddit_learnmath_8yjpp7.increment_correct
#print axioms Census_reddit_learnmath_8yjpp7.increment_on_family
#print axioms Census_reddit_learnmath_8yjpp7.int_exact_failure_set
#print axioms Census_reddit_learnmath_8yjpp7.int_repair_all_odd
#print axioms Census_reddit_learnmath_8yjpp7.int_exact
