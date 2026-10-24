import defs_only
/- Record SE_math_1868681__q (E08): the source sentence fails at p = 3, where 3^2/4 = 9/4 is
not a natural number and so cannot be an attained edge count. -/
namespace Census_SE_math_1868681__q

theorem no_nat_equals_nine_quarters : ∀ m : ℕ, (m : ℚ) ≠ (3 : ℚ) ^ 2 / 4 := by
  intro m hm
  have h : (m : ℚ) * 4 = 9 := by linarith
  have hnat : m * 4 = 9 := by exact_mod_cast h
  omega

theorem source_claim_false_at_three : ¬ SourceClaim 3 := by
  rintro ⟨⟨m, _, hm⟩, _⟩
  apply no_nat_equals_nine_quarters m
  simpa using hm

theorem universal_source_claim_false : ¬ UniversalSourceClaim :=
  fun h => source_claim_false_at_three (h 3)

end Census_SE_math_1868681__q

#print axioms Census_SE_math_1868681__q.source_claim_false_at_three
#print axioms Census_SE_math_1868681__q.universal_source_claim_false
