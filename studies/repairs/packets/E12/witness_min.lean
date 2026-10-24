import defs_only
/- Record reddit_askmath_1bq1jtc (E12): the located line fails at the integer q = 0. -/
namespace RedditAskmath1bq1jtcCensus

/-- At `q = 0` the quoted equality reads `2 = 4`. -/
theorem claim_fails_at_zero : ¬ Claim 0 := by
  unfold Claim
  decide

/-- Hence the located line, read universally over the quotient `q`, is false. -/
theorem universal_claim_false : ¬ UniversalClaim := fun h => claim_fails_at_zero (h 0)

end RedditAskmath1bq1jtcCensus

#print axioms RedditAskmath1bq1jtcCensus.claim_fails_at_zero
#print axioms RedditAskmath1bq1jtcCensus.universal_claim_false
