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
def step (n b : Nat) : Nat := if n + 1 < (b + 1) * (b + 1) then b else b + 1

/-- The corrected program: `progC 0 = 0` and `progC (n + 1) = step n (progC n)` (recursion shape fixed). -/
def progC : Nat → Nat
  | 0 => 0
  | n + 1 => step n (progC n)

/-- The corrected correctness statement (shape fixed): the specification `R`, unchanged, on every input. -/
def CorrectedCorrectness : Prop := ∀ x : Nat, R x (progC x)
-- ===== END FIXED PART =====

theorem sq_lt_succ_sq (c : Nat) : c * c < (c + 1) * (c + 1) := by
  have h : (c + 1) * (c + 1) = c * c + c + c + 1 := by
    simp [Nat.add_mul, Nat.mul_add, Nat.mul_one, Nat.one_mul]
    omega
  omega

theorem step_correct (n b : Nat) (h : R n b) : R (n + 1) (step n b) := by
  unfold step
  obtain ⟨hb1, hb2⟩ := h
  split
  · rename_i hlt
    exact ⟨by omega, hlt⟩
  · rename_i hge
    have heq : n + 1 = (b + 1) * (b + 1) := by omega
    refine ⟨by omega, ?_⟩
    have := sq_lt_succ_sq (b + 1)
    omega

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro x
  induction x with
  | zero => exact ⟨Nat.le_refl 0, by decide⟩
  | succ n ih =>
      show R (n + 1) (step n (progC n))
      exact step_correct n (progC n) ih

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x := by
  refine ⟨1, ?_⟩
  decide

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := repair_statement

end SqrtFailureBoundary
