import Mathlib
/- Review overlay for SE_math_3804372__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_math_3804372_q

def admissible (d : Nat) : Bool := decide (d > 1)

def claimedBound (d : Nat) : Bool := decide (6 < 2 ^ (2 ^ (d - 1)))

theorem SE_math_3804372__q_refuted :
    admissible 2 = true
    ∧ 2 ^ (2 ^ (2 - 1)) = 4
    ∧ claimedBound 2 = false := by decide

theorem negative_control_d3 :
    admissible 3 = true ∧ claimedBound 3 = true := by decide


theorem rational_source_counterexample :
    (2 : ℕ) > 1 ∧ (6 : ℚ) / 2^(2^((2 : ℕ)-1)) = 3/2 ∧
    ¬ (6 : ℚ) / 2^(2^((2 : ℕ)-1)) < 1 := by norm_num

end SE_math_3804372_q
