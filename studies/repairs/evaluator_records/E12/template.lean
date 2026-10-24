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
def factor (q : Int) : Int := «HOLE»

/-- The corrected located line, read for every integer quotient `q` (shape fixed). -/
def CorrectedClaim : Prop := ∀ q : Int, 6*q+2 = 2*(factor q)
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected line holds for every integer `q`. -/
theorem repair_statement : ∀ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) := sorry

/-- Non-vacuity: the corrected line has an instance, and the corrected factor is not the source's `3*q+2` there. -/
theorem repair_nonvacuous : ∃ q : Int, 6*q+2 = 2*(RedditAskmath1bq1jtcCensus.factor q) ∧ RedditAskmath1bq1jtcCensus.factor q ≠ 3*q+2 := sorry

/-- The target theorem of the source, unchanged (`SourceGoal` from defs_only:
`∀ p : Nat, IsPrime p → p ≠ 2 → p ≠ 3 → (∃ q, p = 6*q+1) ∨ (∃ q, p = 6*q+5)`).
If you cannot prove it, replace this declaration (this doc comment included) by the single line
`-- CANNOT: <reason>`. -/
theorem final_theorem : RedditAskmath1bq1jtcCensus.SourceGoal := sorry
-- ===== END OBLIGATIONS =====
end RedditAskmath1bq1jtcCensus
