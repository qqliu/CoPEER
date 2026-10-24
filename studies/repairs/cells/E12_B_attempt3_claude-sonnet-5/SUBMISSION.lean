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
  · unfold RedditAskmath1bq1jtcCensus.factor; omega

theorem final_theorem : RedditAskmath1bq1jtcCensus.SourceGoal := by
  intro p hp hp2 hp3
  obtain ⟨_, hdvd⟩ := hp
  have hdm : 6 * (p / 6) + p % 6 = p := Nat.div_add_mod p 6
  have hrlt : p % 6 < 6 := Nat.mod_lt p (by omega)
  generalize hq : p / 6 = q at hdm
  generalize hr : p % 6 = r at hdm hrlt
  have hcases : r = 0 ∨ r = 1 ∨ r = 2 ∨ r = 3 ∨ r = 4 ∨ r = 5 := by omega
  rcases hcases with h0 | h1 | h2c | h3 | h4 | h5
  · exfalso
    have h2 : 2 ∣ p := ⟨3*q, by omega⟩
    rcases hdvd 2 h2 with h | h
    · exact absurd h (by decide)
    · exact hp2 h.symm
  · left
    exact ⟨q, by omega⟩
  · exfalso
    have h2 : 2 ∣ p := ⟨3*q+1, by omega⟩
    rcases hdvd 2 h2 with h | h
    · exact absurd h (by decide)
    · exact hp2 h.symm
  · exfalso
    have h3' : 3 ∣ p := ⟨2*q+1, by omega⟩
    rcases hdvd 3 h3' with h | h
    · exact absurd h (by decide)
    · exact hp3 h.symm
  · exfalso
    have h2 : 2 ∣ p := ⟨3*q+2, by omega⟩
    rcases hdvd 2 h2 with h | h
    · exact absurd h (by decide)
    · exact hp2 h.symm
  · right
    exact ⟨q, by omega⟩

end RedditAskmath1bq1jtcCensus
