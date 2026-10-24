import defs_only
/- EVALUATOR-ONLY reference correction for E02 (original package: postActual, line 41; repair, line 231; exact, line 243). -/
namespace SE_cs_1200_a1206_Census.Ref

/-- Reference corrected postcondition: `A[0] = 2 ∧ A[1] = 2`. -/
def postC (s : Store) : Bool :=
  decide (s.length ≥ 2) && decide (getI s 0 = 2) && decide (getI s 1 = 2)

end SE_cs_1200_a1206_Census.Ref
