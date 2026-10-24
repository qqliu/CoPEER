import defs_only
/-!
Record E13: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Census_reddit_learnmath_8yjpp7

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected right-hand side of the odd-branch equation `(n / 2 + 1) * 2 = rhs n`.
The hole must be a closed arithmetic expression in `n`: no division or remainder, no `if`/`match`,
no reference to `Increment`. -/
def rhs (n : Nat) : Nat := «HOLE»

/-- The corrected located claim under the source's two hypotheses (shape fixed). -/
def CorrectedClaim : Prop := ∀ n : Nat, IsOdd n → IsEven (n / 2) → (n / 2 + 1) * 2 = rhs n
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected equation holds for every `n` satisfying the source's hypotheses. -/
theorem repair_statement : ∀ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n → Census_reddit_learnmath_8yjpp7.IsEven (n / 2) → (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n := sorry

/-- Non-vacuity: the hypotheses are jointly satisfiable, the corrected equation holds there, and the corrected
right-hand side is not the source's `n + 2` there. -/
theorem repair_nonvacuous : ∃ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n ∧ Census_reddit_learnmath_8yjpp7.IsEven (n / 2) ∧ (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n ∧ Census_reddit_learnmath_8yjpp7.rhs n ≠ n + 2 := sorry

/-- The statement the source's induction is after, unchanged (`SourceGoal` from defs_only:
`∀ n : Nat, Increment n = n + 1`). If you cannot prove it, replace this declaration (this doc comment
included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : Census_reddit_learnmath_8yjpp7.SourceGoal := sorry
-- ===== END OBLIGATIONS =====
end Census_reddit_learnmath_8yjpp7
