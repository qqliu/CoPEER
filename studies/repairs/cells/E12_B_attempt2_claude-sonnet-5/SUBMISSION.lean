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
  · unfold RedditAskmath1bq1jtcCensus.factor
    omega
  · unfold RedditAskmath1bq1jtcCensus.factor
    omega

theorem final_theorem : RedditAskmath1bq1jtcCensus.SourceGoal := by
  intro p hp hp2 hp3
  obtain ⟨hp_ge, hdvd⟩ := hp
  have h6 : 6*(p/6) + p%6 = p := Nat.div_add_mod p 6
  have hr6 : p % 6 < 6 := Nat.mod_lt p (by omega)
  have hcase : p % 6 = 0 ∨ p % 6 = 1 ∨ p % 6 = 2 ∨ p % 6 = 3 ∨ p % 6 = 4 ∨ p % 6 = 5 := by omega
  rcases hcase with h | h | h | h | h | h
  · exfalso
    have hd2 : (2:Nat) ∣ p := ⟨3*(p/6), by omega⟩
    rcases hdvd 2 hd2 with h1 | h1
    · omega
    · exact hp2 h1.symm
  · left
    exact ⟨p/6, by omega⟩
  · exfalso
    have hd2 : (2:Nat) ∣ p := ⟨3*(p/6)+1, by omega⟩
    rcases hdvd 2 hd2 with h1 | h1
    · omega
    · exact hp2 h1.symm
  · exfalso
    have hd3 : (3:Nat) ∣ p := ⟨2*(p/6)+1, by omega⟩
    rcases hdvd 3 hd3 with h1 | h1
    · omega
    · exact hp3 h1.symm
  · exfalso
    have hd2 : (2:Nat) ∣ p := ⟨3*(p/6)+2, by omega⟩
    rcases hdvd 2 hd2 with h1 | h1
    · omega
    · exact hp2 h1.symm
  · right
    exact ⟨p/6, by omega⟩

end RedditAskmath1bq1jtcCensus
