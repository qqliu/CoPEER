import defs_only
/- EVALUATOR-ONLY reference correction for E06 (original package: repair, line 96). -/
namespace SE_cstheory_2312_a2318_Census.Ref

/-- Reference corrected total: `T + a - 2 (n - 2) d`. -/
def total (T a : Int) (n : Nat) (d : Int) : Int := T + a - 2 * ((n : Int) - 2) * d

end SE_cstheory_2312_a2318_Census.Ref
