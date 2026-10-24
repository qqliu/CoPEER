/- Review overlay for SE_cs_97637__a97647.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

set_option maxRecDepth 10000

namespace SE_cs_97637_a97647

abbrev R (x y : Nat) : Prop := y * y ≤ x ∧ x < (y + 1) * (y + 1)

def prog : Nat → Nat
  | 0 => 0
  | n + 1 =>
      let b := prog n
      if n + 1 ≤ (b + 1) * (b + 1) then b else b + 1

theorem prog_one : prog 1 = 0 := by decide

theorem witness_fails : ¬ R 1 (prog 1) := by decide

theorem refutation : ¬ (∀ x : Nat, R x (prog x)) :=
  fun h => absurd (h 1) witness_fails

theorem perfect_squares_fail :
    ¬ R 4 (prog 4) ∧ ¬ R 9 (prog 9) ∧ ¬ R 16 (prog 16) ∧ ¬ R 25 (prog 25) := by
  decide

theorem neg_control_spec_satisfiable : R 2 (prog 2) ∧ R 3 (prog 3) ∧ R 99 (prog 99) := by
  decide

theorem neg_control_prog_nontrivial :
    prog 0 = 0 ∧ prog 2 = 1 ∧ prog 3 = 1 ∧ prog 8 = 2 ∧ prog 99 = 9 ∧ prog 100 = 9 := by
  decide

theorem neg_control_lower_bound_holds : prog 1 * prog 1 ≤ 1 := by decide

def progStrict : Nat → Nat
  | 0 => 0
  | n + 1 =>
      let b := progStrict n
      if n + 1 < (b + 1) * (b + 1) then b else b + 1

theorem neg_control_strict_guard_fixes_it :
    R 1 (progStrict 1) ∧ R 4 (progStrict 4) ∧ R 9 (progStrict 9) ∧ R 16 (progStrict 16)
      ∧ progStrict 1 = 1 ∧ progStrict 4 = 2 ∧ progStrict 9 = 3 ∧ progStrict 100 = 10 := by
  decide

end SE_cs_97637_a97647
