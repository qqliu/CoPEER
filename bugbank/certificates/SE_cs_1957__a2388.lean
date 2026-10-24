import Mathlib
/- Review overlay for SE_cs_1957__a2388.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

import Mathlib.Data.Nat.Log
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Finset.Range

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_cs_1957_a2388

def lgbAux (b : Nat) (_fuel : Nat) (x : Nat) : Nat := Nat.log b x

def lgb (b x : Nat) : Nat := Nat.log b x

def h (b p k x : Nat) : Nat := x ^ p * (lgb b x) ^ k

def drivingSumAux (b a p k L m : Nat) : Nat := ∑ j ∈ Finset.range m, a ^ j * h b p k (b ^ (L-j))

def drivingSum (b a p k L : Nat) : Nat := drivingSumAux b a p k L L

def geoSumAux (r m : Nat) : Nat := ∑ j ∈ Finset.range m, r ^ j

def middleTerm (b a p k L : Nat) : Nat :=
  (b ^ L) ^ p * L ^ k * geoSumAux (a / b ^ p) L

def claimedRHS (b p k L : Nat) : Nat := (b ^ L) ^ p * L ^ (k + 1)

def powerSumAux (k m : Nat) : Nat := ∑ j ∈ Finset.range m, (j+1) ^ k

def trueRHS (b p k L : Nat) : Nat := (b ^ L) ^ p * powerSumAux k L

def lemmaAFailsAt (b a p k L : Nat) : Bool :=
  ! (drivingSum b a p k L == claimedRHS b p k L)

theorem lemmaA_false_primary :
    drivingSum 2 2 1 1 2 = 12
    ∧ claimedRHS 2 1 1 2 = 16
    ∧ drivingSum 2 2 1 1 2 ≠ claimedRHS 2 1 1 2 := by decide

theorem lemmaA_false_secondary :
    drivingSum 2 1 0 1 2 = 3
    ∧ claimedRHS 2 0 1 2 = 4
    ∧ drivingSum 2 1 0 1 2 ≠ claimedRHS 2 0 1 2 := by decide

theorem lemmaA_false_more :
    lemmaAFailsAt 2 2 1 1 3 = true    -- n = 8, k = 1:  48 ≠ 72
    ∧ lemmaAFailsAt 2 2 1 2 2 = true  -- n = 4, k = 2:  20 ≠ 32
    ∧ lemmaAFailsAt 2 2 1 2 3 = true  -- n = 8, k = 2: 112 ≠ 216
    ∧ lemmaAFailsAt 3 9 2 1 2 = true  -- b = 3, a = 9, n = 9: 243 ≠ 324
    := by decide

theorem second_equality_of_the_chain_is_fine :
    middleTerm 2 2 1 1 2 = claimedRHS 2 1 1 2
    ∧ middleTerm 2 1 0 1 2 = claimedRHS 2 0 1 2
    ∧ middleTerm 2 2 1 2 3 = claimedRHS 2 1 2 3
    ∧ drivingSum 2 2 1 1 2 ≠ middleTerm 2 2 1 1 2 := by decide

theorem drivingSum_eq_trueRHS :
    drivingSum 2 2 1 1 2 = trueRHS 2 1 1 2
    ∧ drivingSum 2 1 0 1 2 = trueRHS 2 0 1 2
    ∧ drivingSum 2 2 1 1 3 = trueRHS 2 1 1 3
    ∧ drivingSum 2 2 1 2 3 = trueRHS 2 1 2 3
    ∧ drivingSum 3 9 2 1 2 = trueRHS 3 2 1 2 := by decide

theorem neg_control_lgb_nontrivial :
    lgb 2 1 = 0 ∧ lgb 2 2 = 1 ∧ lgb 2 4 = 2 ∧ lgb 2 8 = 3 ∧ lgb 2 16 = 4
    ∧ lgb 3 1 = 0 ∧ lgb 3 3 = 1 ∧ lgb 3 9 = 2 ∧ lgb 3 27 = 3
    ∧ lgb 2 8 ≠ 0 ∧ lgb 2 8 ≠ lgb 2 2 := by decide

theorem neg_control_lemmaA_holds_where_it_should :
    drivingSum 2 2 1 0 2 = claimedRHS 2 1 0 2    -- k = 0, n = 4  (both 8)
    ∧ drivingSum 2 2 1 0 3 = claimedRHS 2 1 0 3  -- k = 0, n = 8
    ∧ drivingSum 3 9 2 0 3 = claimedRHS 3 2 0 3  -- k = 0, b = 3, n = 27
    ∧ drivingSum 2 2 1 1 1 = claimedRHS 2 1 1 1  -- L = 1
    ∧ drivingSum 2 2 1 3 1 = claimedRHS 2 1 3 1  -- L = 1, k = 3
    ∧ lemmaAFailsAt 2 2 1 0 2 = false
    ∧ lemmaAFailsAt 2 2 1 1 1 = false := by decide

theorem neg_control_sum_is_nondegenerate :
    drivingSum 2 2 1 1 2 ≠ 0
    ∧ drivingSumAux 2 2 1 1 2 1 = 8            -- j = 0 term alone
    ∧ drivingSum 2 2 1 1 2 ≠ drivingSumAux 2 2 1 1 2 1
    ∧ h 2 1 1 4 = 8 ∧ h 2 1 1 2 = 2 ∧ h 2 1 1 1 = 0 := by decide

theorem neg_control_ratio_is_exact :
    (2 : Nat) = 2 ^ 1 ∧ (1 : Nat) = 2 ^ 0 ∧ (9 : Nat) = 3 ^ 2
    ∧ 2 / 2 ^ 1 = 1 ∧ 1 / 2 ^ 0 = 1 ∧ 9 / 3 ^ 2 = 1
    ∧ geoSumAux 1 2 = 2 ∧ geoSumAux 1 3 = 3 := by decide

theorem neg_control_power_sums :
    powerSumAux 1 2 = 3 ∧ powerSumAux 1 3 = 6 ∧ powerSumAux 2 3 = 14
    ∧ powerSumAux 0 2 = 2 ∧ powerSumAux 0 3 = 3
    ∧ powerSumAux 1 1 = 1
    ∧ powerSumAux 0 3 = 3 ^ (0 + 1)              -- k = 0: agrees
    ∧ powerSumAux 1 1 = 1 ^ (1 + 1)              -- L = 1: agrees
    ∧ powerSumAux 1 3 ≠ 3 ^ (1 + 1)              -- k, L ≥ 2: strictly smaller
    ∧ powerSumAux 1 3 < 3 ^ (1 + 1) := by decide

noncomputable def sourceH (x : ℝ) : ℝ := x ^ (Real.logb 2 2) * Real.logb 2 x

theorem real_log_source_counterexample :
    (∑ j ∈ Finset.range 2, (2 : ℝ)^j * sourceH (4 / 2^j)) = 12 ∧
    (4 : ℝ)^(Real.logb 2 2) * (Real.logb 2 4)^2 = 16 ∧ (12 : ℝ) ≠ 16 := by
 have hlog : Real.logb 2 (4 : ℝ) = 2 := by
   have h : (4 : ℝ) = 2 ^ 2 := by norm_num
   rw [h, Real.logb_pow]
   norm_num
 norm_num [sourceH, Finset.sum_range_succ, hlog]

end SE_cs_1957_a2388
