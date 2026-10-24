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
def factor (q : Int) : Int := 3*q + 1

/-- The corrected located line, read for every integer quotient `q` (shape fixed). -/
def CorrectedClaim : Prop := ∀ q : Int, 6*q+2 = 2*(factor q)
-- ===== END FIXED PART =====

theorem repair_statement : ∀ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) := by
  intro q
  unfold factor
  omega

theorem repair_nonvacuous : ∃ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) ∧ RedditAskmath1bq1jtcCensus.factor q ≠ 3*q+2 := by
  refine ⟨0, ?_, ?_⟩ <;> unfold factor <;> omega

theorem final_theorem : RedditAskmath1bq1jtcCensus.SourceGoal := by
  intro p hp h2 h3
  obtain ⟨hp2, hd⟩ := hp
  have k2 : ¬ 2 ∣ p := fun h => by rcases hd 2 h with h | h <;> omega
  have k3 : ¬ 3 ∣ p := fun h => by rcases hd 3 h with h | h <;> omega
  have : p % 6 = 1 ∨ p % 6 = 5 := by omega
  rcases this with h | h
  · exact Or.inl ⟨p / 6, by omega⟩
  · exact Or.inr ⟨p / 6, by omega⟩

end RedditAskmath1bq1jtcCensus
