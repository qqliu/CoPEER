import defs_only
/-!
Record E01: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SqrtFailureBoundary

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected recursive step: the value of the program at input `n + 1`, computed from `n` and the
previous value `b = progC n`. The hole must have the form `if <comparison in n and b> then <value> else <value>`
with exactly one `if` and values that are expressions in `n` and `b` (no `prog`, no `match`, no `let`). -/
def step (n b : Nat) : Nat := if (b + 1) * (b + 1) ≤ n + 1 then b + 1 else b

/-- The corrected program: `progC 0 = 0` and `progC (n + 1) = step n (progC n)` (recursion shape fixed). -/
def progC : Nat → Nat
  | 0 => 0
  | n + 1 => step n (progC n)

/-- The corrected correctness statement (shape fixed): the specification `R`, unchanged, on every input. -/
def CorrectedCorrectness : Prop := ∀ x : Nat, R x (progC x)
-- ===== END FIXED PART =====

private theorem sq_succ (b : Nat) : (b + 1) * (b + 1) = b * b + 2 * b + 1 := by
  simp [Nat.add_mul, Nat.mul_add, Nat.one_mul, Nat.mul_one]
  omega

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro n
  induction n with
  | zero => exact ⟨Nat.le_refl 0, by decide⟩
  | succ n ih =>
      obtain ⟨hle, hlt⟩ := ih
      show R (n + 1) (step n (progC n))
      generalize hb : progC n = b at hle hlt ⊢
      unfold step
      have e1 : (b + 1) * (b + 1) = b * b + 2 * b + 1 := sq_succ b
      have e2 : (b + 1 + 1) * (b + 1 + 1) = b * b + 4 * b + 4 := by
        have h := sq_succ (b + 1)
        rw [h, e1]
        omega
      by_cases hc : (b + 1) * (b + 1) ≤ n + 1
      · simp only [hc, if_true]
        constructor
        · exact hc
        · rw [e2]
          omega
      · simp only [hc, if_false]
        constructor
        · omega
        · omega

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x := by
  refine ⟨1, ?_⟩
  decide

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
