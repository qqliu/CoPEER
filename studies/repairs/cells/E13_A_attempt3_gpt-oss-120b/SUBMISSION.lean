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

/-! ### Obligations -/

theorem repair_statement :
    ∀ n : Nat,
      Census_reddit_learnmath_8yjpp7.IsOdd n →
      Census_reddit_learnmath_8yjpp7.IsEven (n / 2) →
      (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n :=
by
  intro n hodd _
  -- unfold rhs
  dsimp [rhs]
  rcases hodd with ⟨m, hm⟩
  -- compute n % 2 = 1
  have hmod : n % 2 = 1 := by
    have : (2 * m + 1) % 2 = 1 := by
      calc
        (2 * m + 1) % 2
            = ((2 * m) % 2 + 1 % 2) % 2 := by
              simpa [Nat.add_mod] using (Nat.add_mod (2 * m) 1 2)
        _ = (0 + 1) % 2 := by
              simp [Nat.mul_mod_left]
        _ = 1 % 2 := by simp
        _ = 1 := by decide
    simpa [hm] using this
  -- rewrite n using the standard division identity
  have h_eq : n = 1 + 2 * (n / 2) := by
    simpa [hmod, Nat.add_comm, Nat.mul_comm] using (Nat.mod_add_div n 2).symm
  -- now finish the calculation
  calc
    (n / 2 + 1) * 2
        = (n / 2) * 2 + 2 := by
          simpa [Nat.add_mul, Nat.one_mul, Nat.mul_one] using
            (Nat.add_mul (n / 2) 1 2).symm
    _ = 2 * (n / 2) + 2 := by
          simpa [Nat.mul_comm, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
    _ = (1 + 2 * (n / 2)) + 1 := by
          have : 2 * (n / 2) + 2 = (1 + 2 * (n / 2)) + 1 := by
            calc
              2 * (n / 2) + 2
                  = 2 * (n / 2) + (1 + 1) := by simp
              _ = (2 * (n / 2) + 1) + 1 := by
                    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
              _ = (1 + 2 * (n / 2)) + 1 := by
                    simpa [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
          simpa [this]
    _ = n + 1 := by
          simpa [h_eq, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]

theorem repair_nonvacuous :
    ∃ n : Nat,
      Census_reddit_learnmath_8yjpp7.IsOdd n ∧
      Census_reddit_learnmath_8yjpp7.IsEven (n / 2) ∧
      (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n ∧
      Census_reddit_learnmath_8yjpp7.rhs n ≠ n + 2 :=
by
  refine ⟨1, ?_, ?_, ?_, ?_⟩
  · -- 1 is odd
    exact ⟨0, by simp⟩
  · -- (1 / 2) = 0, which is even
    have : Census_reddit_learnmath_8yjpp7.IsEven (0 : Nat) := ⟨0, by simp⟩
    simpa using this
  · -- the equation holds
    simp [rhs]
  · -- rhs 1 = 2 ≠ 3
    decide

-- CANNOT: unable to prove Increment correctness within the given constraints
-- theorem final_theorem : Census_reddit_learnmath_8yjpp7.SourceGoal := ...

end Census_reddit_learnmath_8yjpp7
