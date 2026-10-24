import Mathlib

/- Review overlay for SE_math_4537650__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_math_4537650_q

def interval (lo hi : Nat) : List Nat := (Finset.Icc lo hi).sort (· ≤ ·)

def isMultiple (n k : Nat) : Bool := decide (n > 0 ∧ k % n = 0)

def countMultiples (n lo hi : Nat) : Nat :=
  ((Finset.Icc lo hi).filter (fun k => n > 0 ∧ k % n = 0)).card

def leftCount (m n : Nat) : Nat := countMultiples n 2 m
def rightCount (m n : Nat) : Nat := countMultiples n (m + 2) (2 * m)

theorem SE_math_4537650__q_refuted :
    leftCount 6 4 = 1
    ∧ rightCount 6 4 = 2
    ∧ ¬ (leftCount 6 4 ≥ rightCount 6 4) := by decide

theorem negative_control_counting :
    countMultiples 4 2 12 = 3
    ∧ rightCount 6 4 ≥ leftCount 6 4 := by decide

theorem primary_counterexample : leftCount 2 4 = 0 ∧ rightCount 2 4 = 1 ∧
 ¬leftCount 2 4 ≥ rightCount 2 4 := by decide
end SE_math_4537650_q
