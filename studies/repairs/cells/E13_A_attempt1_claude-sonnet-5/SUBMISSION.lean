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
def rhs (n : Nat) : Nat := n + 1

/-- The corrected located claim under the source's two hypotheses (shape fixed). -/
def CorrectedClaim : Prop := ∀ n : Nat, IsOdd n → IsEven (n / 2) → (n / 2 + 1) * 2 = rhs n
-- ===== END FIXED PART =====

theorem repair_statement : ∀ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n → Census_reddit_learnmath_8yjpp7.IsEven (n / 2) → (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n := by
  rintro n ⟨m, rfl⟩ _
  simp [rhs]
  omega

theorem repair_nonvacuous : ∃ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n ∧ Census_reddit_learnmath_8yjpp7.IsEven (n / 2) ∧ (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n ∧ Census_reddit_learnmath_8yjpp7.rhs n ≠ n + 2 := by
  refine ⟨1, ⟨0, rfl⟩, ⟨0, rfl⟩, ?_, ?_⟩ <;> simp [rhs]

theorem final_theorem : Census_reddit_learnmath_8yjpp7.SourceGoal := by
  unfold SourceGoal
  intro n
  induction n using Nat.strongRecOn with
  | _ n ih =>
    unfold Increment
    split
    · next h0 => omega
    · next h0 =>
      split
      · next hodd =>
        have hlt : n / 2 < n := by omega
        rw [ih (n / 2) hlt]
        omega
      · next hnodd => omega

end Census_reddit_learnmath_8yjpp7
