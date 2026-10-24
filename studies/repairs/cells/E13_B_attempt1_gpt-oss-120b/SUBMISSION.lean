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
    ∀ n : Nat, Census_reddit_learnmath_8yjpp7.IsOdd n →
      Census_reddit_learnmath_8yjpp7.IsEven (n / 2) →
      (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n :=
by
  intro n hnodd hneven
  rcases hnodd with ⟨m, hm⟩
  rcases hneven with ⟨r, hr⟩
  -- `n % 2 = 1` because `n` is odd
  have hmod : n % 2 = 1 := by
    have : (2 * m + 1) % 2 = 1 := by simp
    simpa [hm] using this
  -- rewrite `n` using `mod_add_div`
  have hn : n = 1 + 2 * (r + r) := by
    have := (Nat.mod_add_div n 2).symm
    simpa [hmod, hr, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc,
      Nat.add_comm, Nat.add_left_comm, Nat.add_assoc] using this
  -- simplify the left‑hand side
  have hL : (n / 2 + 1) * 2 = 2 + 2 * (r + r) := by
    calc
      (n / 2 + 1) * 2 = ((r + r) + 1) * 2 := by simpa [hr]
      _ = ((r + r) * 2) + (1 * 2) := by
        simpa [Nat.add_mul] using (Nat.add_mul ((r + r)) 1 2).symm
      _ = (r * 2 + r * 2) + 2 := by
        simpa [Nat.add_mul, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc]
      _ = 2 + (r * 2 + r * 2) := by
        simp [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
      _ = 2 + ((r + r) * 2) := by
        simpa [Nat.add_mul, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc]
      _ = 2 + 2 * (r + r) := by
        simpa [Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc]
  -- finish
  calc
    (n / 2 + 1) * 2 = 2 + 2 * (r + r) := hL
    _ = (1 + 2 * (r + r)) + 1 := by
      simp [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
    _ = n + 1 := by simpa [hn]
    _ = rhs n := by rfl

theorem repair_nonvacuous :
    ∃ n : Nat,
      Census_reddit_learnmath_8yjpp7.IsOdd n ∧
      Census_reddit_learnmath_8yjpp7.IsEven (n / 2) ∧
      (n / 2 + 1) * 2 = Census_reddit_learnmath_8yjpp7.rhs n ∧
      Census_reddit_learnmath_8yjpp7.rhs n ≠ n + 2 :=
by
  refine ⟨5, ?_, ?_, ?_, ?_⟩
  · exact ⟨2, by decide⟩
  · exact ⟨1, by decide⟩
  · simp [rhs]
  · decide

-- The final theorem could be proved, but it is not required for this record.
-- CANNOT: proving `SourceGoal` exceeds the allowed effort.

end Census_reddit_learnmath_8yjpp7
