import Mathlib
/- Record SE_cs_1957__a2388 (E05, cs.stackexchange reply a2388, "Lemma A").

Source setting: a recurrence with a ≥ 1, b ≥ 2, p = log_b a, and driving function
h(x) = x^{log_b a} · (log_b x)^k for some k ≥ 0.  At n = b^L the source evaluates the
driving sum g(n) = Σ_{j=0}^{L-1} a^j · h(n / b^j) and asserts (Lemma A)
  g(n) = n^{log_b a} · (log_b n)^{k+1}
through a chain of two equalities whose middle term is `middleTerm`.
Nat model (Mathlib's `Nat.log`, `Finset.sum`): `drivingSum`, `claimedRHS`, `LocalClaimNat`.
Real model (`Real.logb`, rpow): `sourceHgen`, `LocalClaimReal`, for every real b > 1, a > 0. -/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_cs_1957_a2388_Census

def lgbAux (b : Nat) (_fuel : Nat) (x : Nat) : Nat := Nat.log b x

def lgb (b x : Nat) : Nat := Nat.log b x

def h (b p k x : Nat) : Nat := x ^ p * (lgb b x) ^ k

def drivingSumAux (b a p k L m : Nat) : Nat := ∑ j ∈ Finset.range m, a ^ j * h b p k (b ^ (L-j))

def drivingSum (b a p k L : Nat) : Nat := drivingSumAux b a p k L L

def geoSumAux (r m : Nat) : Nat := ∑ j ∈ Finset.range m, r ^ j

def middleTerm (b a p k L : Nat) : Nat :=
  (b ^ L) ^ p * L ^ k * geoSumAux (a / b ^ p) L

def claimedRHS (b p k L : Nat) : Nat := (b ^ L) ^ p * L ^ (k + 1)

def lemmaAFailsAt (b a p k L : Nat) : Bool :=
  ! (drivingSum b a p k L == claimedRHS b p k L)

/-- h(x) = x^{log_b a} * (log_b x)^k, the source's function, with Mathlib's Real.logb and rpow. -/
noncomputable def sourceHgen (b a : ℝ) (k : ℕ) (x : ℝ) : ℝ :=
  x ^ (Real.logb b a) * (Real.logb b x) ^ k

/-- The located claim in the Nat model (a = b^p, n = b^L, b ≥ 2). -/
def LocalClaimNat : Prop :=
  ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = claimedRHS b p k L

/-- The located claim over the reals (every real b > 1, a > 0, natural k, n = b^L). -/
def LocalClaimReal : Prop :=
  ∀ (b a : ℝ) (k L : ℕ), 1 < b → 0 < a →
    ∑ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
      = (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k+1)

end SE_cs_1957_a2388_Census
