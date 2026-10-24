import defs_only
/-!
Record E12: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace RedditAskmath1bq1jtcCensus

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The inner linear form of the corrected factorisation `6*q+2 = 2*(factor q)`.
The hole must be a linear expression `a*q + b` (or `a*q - b`) with integer literals `a`, `b`:
only the two literals of the source's `3*q+2` may change. -/
def factor (q : Int) : Int := 3*q+1

/-- The corrected located line, read for every integer quotient `q` (shape fixed). -/
def CorrectedClaim : Prop := ∀ q : Int, 6*q+2 = 2*(factor q)
-- ===== END FIXED PART =====

theorem repair_statement : ∀ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) := by
  intro q
  unfold RedditAskmath1bq1jtcCensus.factor
  omega

theorem repair_nonvacuous : ∃ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) ∧ RedditAskmath1bq1jtcCensus.factor q ≠ 3*q+2 := by
  refine ⟨0, ?_, ?_⟩
  · unfold RedditAskmath1bq1jtcCensus.factor; omega
  · unfold RedditAskmath1bq1jtcCensus.factor; decide

theorem final_theorem : RedditAskmath1bq1jtcCensus.SourceGoal := by
  intro p hp hp2 hp3
  obtain ⟨hp2le, hdvd⟩ := hp
  have hmod : 6 * (p / 6) + p % 6 = p := Nat.div_add_mod p 6
  have hr : p % 6 < 6 := by
    have h6 : (0:Nat) < 6 := by decide
    exact Nat.mod_lt p h6
  generalize hqdef : p / 6 = q at hmod
  generalize hrdef : p % 6 = r at hmod hr
  have hcases : r = 0 ∨ r = 1 ∨ r = 2 ∨ r = 3 ∨ r = 4 ∨ r = 5 := by omega
  rcases hcases with h0 | h1 | h2 | h3 | h4 | h5
  · -- r = 0
    exfalso
    have hpeq : p = 2 * (3 * q) := by omega
    have h2dvd : (2 : Nat) ∣ p := ⟨3 * q, hpeq⟩
    rcases hdvd 2 h2dvd with hh1 | hh2
    · exact absurd hh1 (by decide)
    · exact hp2 hh2.symm
  · -- r = 1
    exact Or.inl ⟨q, by omega⟩
  · -- r = 2
    exfalso
    have hpeq : p = 2 * (3 * q + 1) := by omega
    have h2dvd : (2 : Nat) ∣ p := ⟨3 * q + 1, hpeq⟩
    rcases hdvd 2 h2dvd with hh1 | hh2
    · exact absurd hh1 (by decide)
    · exact hp2 hh2.symm
  · -- r = 3
    exfalso
    have hpeq : p = 3 * (2 * q + 1) := by omega
    have h3dvd : (3 : Nat) ∣ p := ⟨2 * q + 1, hpeq⟩
    rcases hdvd 3 h3dvd with hh1 | hh2
    · exact absurd hh1 (by decide)
    · exact hp3 hh2.symm
  · -- r = 4
    exfalso
    have hpeq : p = 2 * (3 * q + 2) := by omega
    have h2dvd : (2 : Nat) ∣ p := ⟨3 * q + 2, hpeq⟩
    rcases hdvd 2 h2dvd with hh1 | hh2
    · exact absurd hh1 (by decide)
    · exact hp2 hh2.symm
  · -- r = 5
    exact Or.inr ⟨q, by omega⟩

end RedditAskmath1bq1jtcCensus
