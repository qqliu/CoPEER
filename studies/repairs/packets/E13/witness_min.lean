import defs_only
/- Record reddit_learnmath_8yjpp7 (E13): the located claim fails at n = 5. -/
namespace Census_reddit_learnmath_8yjpp7

/-- `n = 5` is odd, `5 / 2 = 2` is even, and `(5 / 2 + 1) * 2 = 6 ≠ 5 + 2`. -/
theorem claim_fails_at_five :
    IsOdd 5 ∧ IsEven (5 / 2) ∧ (5 / 2 + 1) * 2 = 6 ∧ (5 / 2 + 1) * 2 ≠ 5 + 2 :=
  ⟨⟨2, rfl⟩, ⟨1, rfl⟩, rfl, by decide⟩

theorem source_claim_false : ¬ SourceClaim :=
  fun h => absurd (h 5 ⟨2, rfl⟩ ⟨1, rfl⟩) (by decide)

theorem source_claim_quote_only_false : ¬ SourceClaimQuoteOnly :=
  fun h => absurd (h 5 ⟨1, rfl⟩) (by decide)

end Census_reddit_learnmath_8yjpp7

#print axioms Census_reddit_learnmath_8yjpp7.claim_fails_at_five
#print axioms Census_reddit_learnmath_8yjpp7.source_claim_false
#print axioms Census_reddit_learnmath_8yjpp7.source_claim_quote_only_false
