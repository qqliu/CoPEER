import defs_only
/-!
Record E01: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SqrtFailureBoundary

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected recursive step: the value of the program at input `n + 1` computed from `n` and the
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

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
by
  intro x
  induction x with
  | zero =>
      simp [progC, R]
  | succ n ih =>
      rcases ih with ⟨hbl, hbu⟩
      by_cases hcond : (progC n + 1) * (progC n + 1) ≤ n + 1
      · -- then branch returns progC n + 1
        have h1 : (progC n + 1) * (progC n + 1) ≤ n + 1 := hcond
        have hle : n + 1 ≤ (progC n + 1) * (progC n + 1) := Nat.succ_le_of_lt hbu
        have hlt_sq : (progC n + 1) * (progC n + 1) < (progC n + 2) * (progC n + 2) := by
          have hlt1 : (progC n + 1) * (progC n + 1) < (progC n + 1) * (progC n + 2) := by
            have pos : 0 < progC n + 1 := Nat.succ_pos _
            have : (progC n + 1) < (progC n + 2) := Nat.lt_succ_self (progC n + 1)
            exact Nat.mul_lt_mul_of_pos_left this pos
          have hle2 : (progC n + 1) * (progC n + 2) ≤ (progC n + 2) * (progC n + 2) := by
            have : (progC n + 1) ≤ (progC n + 2) := Nat.le_succ _
            simpa [Nat.mul_comm] using Nat.mul_le_mul_left (progC n + 2) this
          exact Nat.lt_of_lt_of_le hlt1 hle2
        have h2 : n + 1 < (progC n + 2) * (progC n + 2) := Nat.lt_of_le_of_lt hle hlt_sq
        have : R (n + 1) (progC n + 1) := ⟨h1, h2⟩
        simpa [progC, step, hcond]
      · -- else branch returns progC n
        have hlt : n + 1 < (progC n + 1) * (progC n + 1) := Nat.lt_of_not_ge hcond
        have h1 : progC n * progC n ≤ n + 1 := Nat.le_trans hbl (Nat.le_succ _)
        have : R (n + 1) (progC n) := ⟨h1, hlt⟩
        simpa [progC, step, hcond]

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x :=
by
  refine ⟨1, ?_⟩
  simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.prog, step]

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
