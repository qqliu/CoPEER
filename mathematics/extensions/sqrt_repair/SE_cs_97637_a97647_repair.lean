/- Universal repair certificate for SE_cs_97637__a97647 (2026-09-18).
The released certificate (validation/human_review_20260915/lean/SE_cs_97637__a97647.lean) refutes the
all-input specification of `prog` via x = 1 and checks the strict-guard variant `progStrict` only at
finitely many instances. This file restates the SAME definitions verbatim and proves the universal
statement: `progStrict` meets the specification R for EVERY input. Core Lean only; no Mathlib, no
`decide` over the universal claim, no additional axioms. The released certificate is not modified. -/

set_option maxRecDepth 10000

namespace SE_cs_97637_a97647_repair

abbrev R (x y : Nat) : Prop := y * y ≤ x ∧ x < (y + 1) * (y + 1)

def prog : Nat → Nat
  | 0 => 0
  | n + 1 =>
      let b := prog n
      if n + 1 ≤ (b + 1) * (b + 1) then b else b + 1

def progStrict : Nat → Nat
  | 0 => 0
  | n + 1 =>
      let b := progStrict n
      if n + 1 < (b + 1) * (b + 1) then b else b + 1

/-- The original program fails the specification (same witness as the released certificate). -/
theorem prog_refutation : ¬ (∀ x : Nat, R x (prog x)) :=
  fun h => absurd (h 1) (by decide)

/-- Every input: the strict-guard program returns the integer square root. -/
theorem strict_guard_correct : ∀ x : Nat, R x (progStrict x) := by
  intro x
  induction x with
  | zero => exact ⟨Nat.le_refl 0, Nat.zero_lt_one⟩
  | succ n ih =>
    obtain ⟨h1, h2⟩ := ih
    show R (n + 1) (let b := progStrict n; if n + 1 < (b + 1) * (b + 1) then b else b + 1)
    by_cases hlt : n + 1 < (progStrict n + 1) * (progStrict n + 1)
    · simp only [hlt, ite_true]
      exact ⟨Nat.le_succ_of_le h1, hlt⟩
    · simp only [hlt, ite_false]
      have hge : (progStrict n + 1) * (progStrict n + 1) ≤ n + 1 := Nat.le_of_not_lt hlt
      refine ⟨hge, ?_⟩
      have step : n + 1 ≤ (progStrict n + 1) * (progStrict n + 1) := Nat.succ_le_of_lt h2
      have grow : (progStrict n + 1) * (progStrict n + 1) < (progStrict n + 1 + 1) * (progStrict n + 1 + 1) :=
        Nat.mul_self_lt_mul_self (Nat.lt_succ_self _)
      exact Nat.lt_of_le_of_lt step grow

/-- The two facts side by side: the original fails at 1, the repair is correct everywhere. -/
theorem error_and_repair : (¬ R 1 (prog 1)) ∧ (∀ x : Nat, R x (progStrict x)) :=
  ⟨by decide, strict_guard_correct⟩

end SE_cs_97637_a97647_repair

#print axioms SE_cs_97637_a97647_repair.strict_guard_correct
#print axioms SE_cs_97637_a97647_repair.error_and_repair
#print axioms SE_cs_97637_a97647_repair.prog_refutation
