import defs_only
/- EVALUATOR-ONLY reference correction for E14 (released certificate: every_fitting_value_has_at_most_170157_digits, line 262;
maximum_has_170157_digits, line 252; certificate, line 411). -/
namespace Audit_reddit_math_2s4u2m.Ref

/-- Reference corrected digit count: 170157 = ceil(565248 * log10 2) (565248 * log10 2 = 170156.60...). -/
def digitBound : Nat := 170157

end Audit_reddit_math_2s4u2m.Ref
