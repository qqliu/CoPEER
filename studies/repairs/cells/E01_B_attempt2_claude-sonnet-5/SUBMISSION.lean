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

/-- Ring identity for squares of successors, over `Nat`, proved without `ring` (core Lean only). -/
theorem sq_succ (b : Nat) : (b + 1) * (b + 1) = b * b + 2 * b + 1 := by
  simp [Nat.succ_mul, Nat.mul_succ]
  omega

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro x
  induction x with
  | zero =>
      constructor <;> simp [progC]
  | succ n ih =>
      show R (n + 1) (step n (progC n))
      obtain ⟨h1, h2⟩ := ih
      unfold step
      by_cases h : n + 1 < (progC n + 1) * (progC n + 1)
      · simp only [h, if_true]
        constructor
        · omega
        · exact h
      · simp only [h, if_false]
        have heq : n + 1 = (progC n + 1) * (progC n + 1) := by omega
        have hstep := sq_succ (progC n + 1)
        constructor
        · omega
        · omega

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x := by
  refine ⟨1, ?_⟩
  decide

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := repair_statement

end SqrtFailureBoundary
