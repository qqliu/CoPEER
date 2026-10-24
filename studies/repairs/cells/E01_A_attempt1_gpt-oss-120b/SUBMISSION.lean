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

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
by
  intro x
  induction x with
  | zero =>
      simp [progC, R]
  | succ n ih =>
      set b := progC n with hb
      have hleft : b * b ≤ n := by
        have := ih.left
        simpa [hb] using this
      have hright : n < (b + 1) * (b + 1) := by
        have := ih.right
        simpa [hb] using this
      dsimp [progC] at *
      have : R (n + 1) (step n b) := by
        by_cases h : (b + 1) * (b + 1) ≤ n + 1
        · -- true branch, result is b+1
          have h_eq : n + 1 = (b + 1) * (b + 1) := by
            apply Nat.le_antisymm
            · exact h
            · exact Nat.succ_le_of_lt hright
          have left : (b + 1) * (b + 1) ≤ n + 1 := by
            simpa [h_eq]
          have right : n + 1 < (b + 2) * (b + 2) := by
            have hle1 : (b + 1) * (b + 1) ≤ (b + 1) * (b + 2) :=
              Nat.mul_le_mul_left (b + 1) (Nat.le_succ _)
            have hlt2 : (b + 1) * (b + 2) < (b + 2) * (b + 2) :=
              Nat.mul_lt_mul_of_pos_left (Nat.lt_succ_self (b + 1)) (Nat.succ_pos _)
            have hlt : (b + 1) * (b + 1) < (b + 2) * (b + 2) :=
              Nat.lt_of_le_of_lt hle1 hlt2
            simpa [h_eq] using hlt
          exact And.intro left right
        · -- false branch, result is b
          have h_lt : n + 1 < (b + 1) * (b + 1) := Nat.lt_of_not_ge h
          have left : b * b ≤ n + 1 := Nat.le_succ_of_le hleft
          have right : n + 1 < (b + 1) * (b + 1) := h_lt
          exact And.intro left right
      simpa [hb, step] using this

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x :=
by
  refine ⟨1, ?_⟩
  simp [progC, prog, step]

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
