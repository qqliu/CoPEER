/-!
# `mse_605342__ans609345` — coprimality does not force the claimed norm descent

Route: `SELF_CONTAINED_LEAN`; no V2 constructor models quadratic rings or their norms.
No imports are used.

We instantiate the sentence in the Gaussian integers with `alpha=i`, `a=-1`, `b=-1`.
The explicit Bézout identity `0*a + (-1)*b = 1` certifies coprimality.  Nevertheless
`a-alpha*b = -1+i`, whose norm is 2, while `N(b)=1`.  Thus the asserted strict decrease
would read `2<1`.

The negative control keeps the same unit `b` but takes `a=alpha*b`; then the difference
is zero and strict descent really holds.  This prevents a constant norm or broken
subtraction from vacuously certifying the counterexample.
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace MSE_605342_ans609345

/-- Gaussian integer `(re,im)`, denoting `re + im*i`. -/
abbrev GI := Int × Int

def add (z w : GI) : GI := (z.1 + w.1, z.2 + w.2)
def neg (z : GI) : GI := (-z.1, -z.2)
def sub (z w : GI) : GI := add z (neg w)
def mul (z w : GI) : GI := (z.1*w.1 - z.2*w.2, z.1*w.2 + z.2*w.1)
def norm (z : GI) : Int := z.1*z.1 + z.2*z.2

def zero : GI := (0,0)
def one : GI := (1,0)
def alpha : GI := (0,1)
def a : GI := (-1,0)
def b : GI := (-1,0)
def bezoutU : GI := zero
def bezoutV : GI := (-1,0)

def bezoutCert (x y u v : GI) : Bool := add (mul u x) (mul v y) == one

/-- The explicit coprime pair makes the alleged norm inequality false. -/
theorem mse_605342__ans609345_refutation :
    bezoutCert a b bezoutU bezoutV = true
      ∧ mul alpha b = (0,-1)
      ∧ sub a (mul alpha b) = (-1,1)
      ∧ norm (sub a (mul alpha b)) = 2
      ∧ norm b = 1
      ∧ ¬ (norm (sub a (mul alpha b)) < norm b) := by
  decide

/-! ### NEGATIVE CONTROL

At the unique value `a=alpha*b` the difference is zero and the descent succeeds.  The
same unit still supplies a Bézout certificate, so this is a non-vacuous positive instance
of exactly the modelled implication.
-/
def aGood : GI := mul alpha b

theorem mse_605342__ans609345_negative_control :
    bezoutCert aGood b bezoutU bezoutV = true
      ∧ sub aGood (mul alpha b) = zero
      ∧ norm (sub aGood (mul alpha b)) = 0
      ∧ norm (sub aGood (mul alpha b)) < norm b := by
  decide

end MSE_605342_ans609345


#print axioms MSE_605342_ans609345.mse_605342__ans609345_refutation
#print axioms MSE_605342_ans609345.mse_605342__ans609345_negative_control
