/- Review overlay for SE_math_4031678__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

import Mathlib

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_math_4031678_q

def lhs : Nat := Nat.choose 100 50

def rhs : Nat := 100 * Nat.choose 99 49

abbrev printedImplication : Prop := lhs ≤ rhs → 51 ≤ 50

theorem SE_math_4031678__q_refuted : ¬ printedImplication := by
  unfold printedImplication
  norm_num [lhs, rhs, Nat.choose_eq_factorial_div_factorial]

theorem exact_values :
    lhs ≤ rhs
    ∧ rhs - lhs = 4943675882732645473405812365544 := by norm_num [lhs, rhs, Nat.choose_eq_factorial_div_factorial]

theorem negative_control_absorption : rhs = 50 * lhs := by norm_num [lhs, rhs, Nat.choose_eq_factorial_div_factorial]

end SE_math_4031678_q
