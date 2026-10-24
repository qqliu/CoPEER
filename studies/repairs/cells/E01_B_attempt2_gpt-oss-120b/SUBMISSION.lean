import defs_only
namespace SqrtFailureBoundary

def step (n b : Nat) : Nat := if n + 1 < (b + 1) * (b + 1) then b else b + 1

def progC : Nat → Nat
  | 0 => 0
  | n + 1 => step n (progC n)

def CorrectedCorrectness : Prop := ∀ x : Nat, R x (progC x)

theorem repair_statement : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) := by
  intro x
  induction x with
  | zero =>
      simp [progC, step, R]
  | succ n ih =>
      set b := progC n with hb
      have ihR : R n b := by
        simpa [hb] using ih
      dsimp [progC, step] at *
      by_cases h : n + 1 < (b + 1) * (b + 1)
      ·
        have left : b * b ≤ n + 1 := by
          have : b * b ≤ n := ihR.1
          exact le_trans this (Nat.le_succ n)
        have right : n + 1 < (b + 1) * (b + 1) := h
        have : b * b ≤ n + 1 ∧ n + 1 < (b + 1) * (b + 1) := And.intro left right
        simpa [h] using this
      ·
        have hle : (b + 1) * (b + 1) ≤ n + 1 := Nat.le_of_not_lt h
        have left : (b + 1) * (b + 1) ≤ n + 1 := hle
        have right : n + 1 < (b + 2) * (b + 2) := by
          have le1 : n + 1 ≤ (b + 1) * (b + 1) := Nat.succ_le_of_lt ihR.2
          have lt_sq : (b + 1) * (b + 1) < (b + 2) * (b + 2) := by
            have h1 : (b + 1) * (b + 1) < (b + 2) * (b + 1) := by
              have hlt : b + 1 < b + 2 := Nat.lt_succ_self (b + 1)
              have pos : 0 < b + 1 := Nat.succ_pos _
              exact Nat.mul_lt_mul_of_pos_right hlt pos
            have h2 : (b + 2) * (b + 1) < (b + 2) * (b + 2) := by
              have hlt : b + 1 < b + 2 := Nat.lt_succ_self (b + 1)
              have pos : 0 < b + 2 := Nat.succ_pos _
              exact Nat.mul_lt_mul_of_pos_left hlt pos
            exact lt_trans h1 h2
          exact Nat.lt_of_le_of_lt le1 lt_sq
        have : (b + 1) * (b + 1) ≤ n + 1 ∧ n + 1 < (b + 2) * (b + 2) := And.intro left right
        simpa [h] using this

theorem repair_nonvacuous : ∃ x : Nat, SqrtFailureBoundary.progC x ≠ SqrtFailureBoundary.prog x := by
  refine ⟨1, ?_⟩
  have hC : progC 1 = 1 := by
    simp [progC, step]
  have hP : prog 1 = 0 := by
    simp [prog]
  intro h_eq
  have : (1 : Nat) = 0 := by
    simpa [hC, hP] using h_eq
  exact (Nat.succ_ne_self 0) this

theorem final_theorem : ∀ x : Nat, SqrtFailureBoundary.R x (SqrtFailureBoundary.progC x) :=
  repair_statement

end SqrtFailureBoundary
