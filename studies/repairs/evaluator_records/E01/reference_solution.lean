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

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected program meets `R` on every natural input. -/
theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro x
  induction x with
  | zero => exact ⟨Nat.le_refl 0, Nat.zero_lt_one⟩
  | succ n ih =>
    obtain ⟨h1, h2⟩ := ih
    show R (n + 1) (step n (progC n))
    unfold step
    by_cases hlt : n + 1 < (progC n + 1) * (progC n + 1)
    · simp only [hlt, ite_true]
      exact ⟨Nat.le_succ_of_le h1, hlt⟩
    · simp only [hlt, ite_false]
      have hge : (progC n + 1) * (progC n + 1) ≤ n + 1 := Nat.le_of_not_lt hlt
      refine ⟨hge, ?_⟩
      have st : n + 1 ≤ (progC n + 1) * (progC n + 1) := Nat.succ_le_of_lt h2
      have grow : (progC n + 1) * (progC n + 1) < (progC n + 1 + 1) * (progC n + 1 + 1) :=
        Nat.mul_self_lt_mul_self (Nat.lt_succ_self _)
      exact Nat.lt_of_le_of_lt st grow

/-- Non-vacuity: the program was actually changed (some input on which `progC` and `prog` differ). -/
theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x := ⟨1, by decide⟩

/-- The endpoint of this record is the corrected universal statement itself (a corrected program with a
universal correctness proof against the unchanged specification); restate it here, e.g. `:= repair_statement`.
If you cannot, replace this declaration (this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := repair_statement
-- ===== END OBLIGATIONS =====
end SqrtFailureBoundary
