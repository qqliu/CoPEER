import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E12: the submitted `factor` must agree with the reference
linear form on every listed integer. Core record: decide / rfl / simp / omega only. -/
theorem agree_0 : RedditAskmath1bq1jtcCensus.factor 0 = RedditAskmath1bq1jtcCensus.Ref.factor 0 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_1 : RedditAskmath1bq1jtcCensus.factor 1 = RedditAskmath1bq1jtcCensus.Ref.factor 1 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_m1 : RedditAskmath1bq1jtcCensus.factor (-1) = RedditAskmath1bq1jtcCensus.Ref.factor (-1) := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_2 : RedditAskmath1bq1jtcCensus.factor 2 = RedditAskmath1bq1jtcCensus.Ref.factor 2 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_m2 : RedditAskmath1bq1jtcCensus.factor (-2) = RedditAskmath1bq1jtcCensus.Ref.factor (-2) := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_5 : RedditAskmath1bq1jtcCensus.factor 5 = RedditAskmath1bq1jtcCensus.Ref.factor 5 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_m7 : RedditAskmath1bq1jtcCensus.factor (-7) = RedditAskmath1bq1jtcCensus.Ref.factor (-7) := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_10 : RedditAskmath1bq1jtcCensus.factor 10 = RedditAskmath1bq1jtcCensus.Ref.factor 10 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
theorem agree_100 : RedditAskmath1bq1jtcCensus.factor 100 = RedditAskmath1bq1jtcCensus.Ref.factor 100 := by
  first
  | decide
  | rfl
  | (simp [RedditAskmath1bq1jtcCensus.factor, RedditAskmath1bq1jtcCensus.Ref.factor])
  | (unfold RedditAskmath1bq1jtcCensus.factor RedditAskmath1bq1jtcCensus.Ref.factor; omega)
#print axioms agree_0
#print axioms agree_1
#print axioms agree_m1
#print axioms agree_2
#print axioms agree_m2
#print axioms agree_5
#print axioms agree_m7
#print axioms agree_10
#print axioms agree_100
