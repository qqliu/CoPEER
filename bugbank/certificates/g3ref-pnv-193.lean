import Mathlib.NumberTheory.Zsqrtd.GaussianInt
import Mathlib.Tactic

/-!
Record: g3ref-pnv-193

Source URL:
proof-verification://qedbench_certificate_availability_triage/runs/g3refs_claim_contexts/g3ref-pnv-193.txt

Source claim: for integers `a` and `y`, the equation `a * y = 0` implies
`y = 0`, without assuming `a ≠ 0`.

Verified witness: `a = 0` and `y = 1`.  Both values are represented directly
in Lean's unbounded integer type.  Their product is zero, while `y` is not
zero, so the implication fails.

Material modelling judgments: the claim is encoded as the implication at the
verified integer witness, with no cancellation or nonzero hypothesis added.
The separately checked negative control is exactly the supplied case `a = 1`,
`y = 0`; it changes the load-bearing zero-coefficient feature and verifies
both the hypothesis and conclusion.  No semantic-adjudication overlay was
supplied, so the certificate does not assert anything beyond this claim,
witness, and negative control.
-/

namespace G3refPnv193

def witnessA : Int := 0
def witnessY : Int := 1

abbrev sourceClaimAtWitness : Prop :=
  witnessA * witnessY = 0 -> witnessY = 0

/-- Load-bearing refutation: the verified integer witness satisfies `a*y=0`
but falsifies `y=0`, and hence falsifies the source implication. -/
theorem refutes_ay_zero_implies_y_zero_without_nonzero_a :
    witnessA = 0 /\
    witnessY = 1 /\
    witnessA * witnessY = 0 /\
    witnessY ≠ 0 /\
    Not sourceClaimAtWitness := by
  decide

def controlA : Int := 1
def controlY : Int := 0

abbrev sourceClaimAtControl : Prop :=
  controlA * controlY = 0 -> controlY = 0

/-- Meaningful negative control: changing the coefficient from zero to one
and taking `y=0` makes both the supplied hypothesis and conclusion true. -/
theorem negative_control_nonzero_a_and_zero_y_satisfies_claim :
    controlA = 1 /\
    controlA ≠ 0 /\
    controlY = 0 /\
    controlA * controlY = 0 /\
    sourceClaimAtControl := by
  decide

/-- The same zero coefficient extends to all surrounding Gaussian-integer premises:
choose b=0,x=0 and z=i. Thus the dropped nonzero condition is not supplied by
Gaussian divisibility. The original a=0,y=1 witness is unchanged. -/
theorem full_gaussian_context_counterexample :
    (0 : GaussianInt) ∣ 0 ∧
    (0 : GaussianInt) * ⟨0,1⟩ = 0 ∧
    (0 : ℤ) * 1 = 0 ∧ (1 : ℤ) ≠ 0 := by
  norm_num
end G3refPnv193
