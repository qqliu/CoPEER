import defs_only
/-!
Record E17: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace G3refPnv102

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected right-hand side of the identity of stored line 0004. The hole must have the frozen form
`(α * a ^ e + β) ^ 2 + γ` with integer literals `α ≠ 0`, `e ≥ 1`, `β`, `γ` (a square of a binomial in `a` plus a
constant; e.g. `(3 * a ^ 5 - 7) ^ 2 + 11`): no `lhs`/`rhs`, no other shape. -/
def rhsC (a : ℤ) : ℤ := (2 * a ^ 2 - 1) ^ 2 + 3

/-- The corrected located identity (shape fixed): for every integer `a`. -/
def CorrectedIdentity : Prop := ∀ a : ℤ, lhs a = rhsC a
-- ===== END FIXED PART =====

theorem repair_statement : ∀ a : ℤ, G3refPnv102.lhs a = G3refPnv102.rhsC a := by
  intro a
  unfold lhs rhsC
  ring

theorem repair_nonvacuous : ∃ a : ℤ, G3refPnv102.rhsC a ≠ G3refPnv102.rhs a := by
  refine ⟨2, ?_⟩
  unfold rhsC G3refPnv102.rhs
  norm_num

theorem final_theorem : ∀ (a : ℤ) (p : ℕ), Nat.Prime p → (p : ℤ) ∣ a ^ 4 - a ^ 2 + 1 → (p : ℤ) ∣ G3refPnv102.rhsC a := by
  intro a p hp hdiv
  have hlhs : (p : ℤ) ∣ G3refPnv102.lhs a := by
    have h_eq : G3refPnv102.lhs a = 4 * (a ^ 4 - a ^ 2 + 1) := by
      unfold G3refPnv102.lhs
      ring
    have : (p : ℤ) ∣ (a ^ 4 - a ^ 2 + 1) * 4 := by
      exact dvd_mul_of_dvd_left hdiv 4
    have : (p : ℤ) ∣ 4 * (a ^ 4 - a ^ 2 + 1) := by
      simpa [mul_comm] using this
    simpa [h_eq] using this
  simpa [repair_statement a] using hlhs

end G3refPnv102
