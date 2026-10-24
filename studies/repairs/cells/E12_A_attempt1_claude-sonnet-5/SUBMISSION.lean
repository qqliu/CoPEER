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
  unfold RedditAskmath1bq1jtcCensus.SourceGoal
  intro p hp hp2 hp3
  have h2 : ¬ (2 ∣ p) := by
    intro hd
    have := hp.2 2 hd
    rcases this with h | h
    · omega
    · exact hp2 h.symm
  have h3 : ¬ (3 ∣ p) := by
    intro hd
    have := hp.2 3 hd
    rcases this with h | h
    · omega
    · exact hp3 h.symm
  have hdm : p = 6 * (p / 6) + p % 6 := (Nat.div_add_mod p 6).symm
  have hlt : p % 6 < 6 := Nat.mod_lt p (by omega)
  have h2' : ∀ k : Nat, p ≠ 2 * k := by
    intro k hk
    apply h2
    exact ⟨k, hk⟩
  have h3' : ∀ k : Nat, p ≠ 3 * k := by
    intro k hk
    apply h3
    exact ⟨k, hk⟩
  generalize hq : p / 6 = q at hdm
  have hr : p % 6 = 0 ∨ p % 6 = 1 ∨ p % 6 = 2 ∨ p % 6 = 3 ∨ p % 6 = 4 ∨ p % 6 = 5 := by omega
  rcases hr with hr | hr | hr | hr | hr | hr
  · exact absurd (by omega : p = 2 * (3 * q)) (h2' (3*q))
  · left; exact ⟨q, by omega⟩
  · exact absurd (by omega : p = 2 * (3 * q + 1)) (h2' (3*q+1))
  · exact absurd (by omega : p = 3 * (2 * q + 1)) (h3' (2*q+1))
  · exact absurd (by omega : p = 2 * (3 * q + 2)) (h2' (3*q+2))
  · right; exact ⟨q, by omega⟩

end RedditAskmath1bq1jtcCensus
