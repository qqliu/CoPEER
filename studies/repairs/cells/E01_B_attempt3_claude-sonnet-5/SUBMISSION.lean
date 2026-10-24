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

theorem sq_succ (k : Nat) : (k + 1) * (k + 1) = k * k + 2 * k + 1 := by
  simp [Nat.succ_mul, Nat.mul_succ, Nat.mul_comm]
  omega

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro x
  induction x with
  | zero => simp [progC, R]
  | succ n ih =>
    obtain ⟨h1, h2⟩ := ih
    have e1 := sq_succ (progC n)
    have e2 := sq_succ (progC n + 1)
    show R (n + 1) (step n (progC n))
    unfold step
    by_cases h : (progC n + 1) * (progC n + 1) ≤ n + 1
    · simp only [h, if_true]
      refine ⟨h, ?_⟩
      omega
    · simp only [h, if_false]
      refine ⟨?_, ?_⟩
      · omega
      · omega

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x :=
  ⟨1, by decide⟩

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
