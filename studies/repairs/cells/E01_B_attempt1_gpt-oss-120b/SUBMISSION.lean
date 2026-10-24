import defs_only
/-!
Record E01: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SqrtFailureBoundary

def step (n b : Nat) : Nat := if n + 1 < (b + 1) * (b + 1) then b else b + 1

def progC : Nat → Nat
  | 0 => 0
  | n + 1 => step n (progC n)

def CorrectedCorrectness : Prop := ∀ x : Nat, R x (progC x)

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
by
  intro x
  induction x with
  | zero =>
      simp [progC, R]
  | succ n ih =>
      rcases ih with ⟨hleft, hright⟩
      set b := progC n with hbdef
      have hleft' : b * b ≤ n := by
        simpa [hbdef] using hleft
      have hright' : n < (b + 1) * (b + 1) := by
        simpa [hbdef] using hright
      by_cases h : n + 1 < (b + 1) * (b + 1)
      ·
        have h1 : b * b ≤ n + 1 := le_trans hleft' (Nat.le_succ _)
        simpa [progC, step, hbdef, h] using And.intro h1 h
      ·
        have hle : (b + 1) * (b + 1) ≤ n + 1 := Nat.le_of_not_gt h
        have h_eq : n + 1 = (b + 1) * (b + 1) :=
          Nat.le_antisymm hle (Nat.succ_le_of_lt hright')
        have hlt : n + 1 < (b + 2) * (b + 2) := by
          have : (b + 1) * (b + 1) < (b + 2) * (b + 2) := by
            have hpos : 0 < (b + 1) + (b + 2) := Nat.succ_pos _
            have := Nat.lt_add_of_pos_right ((b + 1) * (b + 1)) hpos
            simpa [Nat.mul_succ, Nat.succ_mul, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc] using this
          simpa [h_eq]
        simpa [progC, step, hbdef, h] using And.intro hle hlt

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x :=
by
  refine ⟨1, ?_⟩
  simpa using (by decide : progC 1 ≠ prog 1)

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
