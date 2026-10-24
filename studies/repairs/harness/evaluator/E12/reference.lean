import defs_only
/- EVALUATOR-ONLY reference correction for E12 (from the original package: repair, line 67). Never copied into a sandbox. -/
namespace RedditAskmath1bq1jtcCensus.Ref

/-- Reference inner linear form: `6*q+2 = 2*(3*q+1)`. -/
def factor (q : Int) : Int := 3*q+1

theorem universal : ∀ q : Int, 6*q+2 = 2*(factor q) := by
  intro q; unfold factor; omega

end RedditAskmath1bq1jtcCensus.Ref
