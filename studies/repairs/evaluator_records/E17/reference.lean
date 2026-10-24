import defs_only
/- EVALUATOR-ONLY reference correction for E17 (released certificate: corrected_identity, line 16). -/
namespace G3refPnv102.Ref

/-- Reference corrected right-hand side: `(2 * a ^ 2 - 1) ^ 2 + 3`. -/
def rhsC (a : ℤ) : ℤ := (2 * a ^ 2 - 1) ^ 2 + 3

theorem identity (a : ℤ) : lhs a = rhsC a := by
  unfold lhs rhsC
  ring

end G3refPnv102.Ref
