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

/-- Universal: the corrected equation holds for every `n` satisfying the source's hypotheses. -/
theorem repair_statement : ∀ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n → Census_reddit_learnmath_8yjpp7.IsEven (n / 2) → (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n := by
  intro n hodd heven
  have hmod : n % 2 = 1 := by
    rcases hodd with ⟨m, hm⟩
    simpa [hm, Nat.add_mod, Nat.mul_mod, Nat.mod_self, Nat.mod_one]
  have h_eq : (n / 2 + 1) * 2 = n + 1 := by
    calc
      (n / 2 + 1) * 2
          = (n / 2) * 2 + 2 := by
            simpa [Nat.add_mul, Nat.mul_one] using (Nat.add_mul (n / 2) 1 2).symm
      _ = 2 * (n / 2) + 2 := by simp [Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc]
      _ = 2 * (n / 2) + (n % 2 + 1) := by
            simpa [hmod, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
      _ = (n % 2 + 2 * (n / 2)) + 1 := by
            simp [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
      _ = n + 1 := by
            simpa [Nat.mod_add_div, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
  simpa [rhs] using h_eq

/-- Non-vacuity: there exists an `n` satisfying the hypotheses, the corrected equation holds, and the RHS differs from `n+2`. -/
theorem repair_nonvacuous : ∃ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n ∧ Census_reddit_learnmath_8yjpp7.IsEven (n / 2) ∧ (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n ∧ Census_reddit_learnmath_8yjpp7.rhs n ≠ n + 2 := by
  refine ⟨1, ?odd, ?even, ?eq, ?neq⟩
  · exact ⟨0, by simp⟩
  · have : IsEven (0) := ⟨0, by simp⟩
    simpa using this
  · simp [rhs]
  · simp [rhs]

-- CANNOT: proof of SourceGoal not found

end Census_reddit_learnmath_8yjpp7
