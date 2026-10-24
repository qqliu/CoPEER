import defs_only
/- Record g3ref-pnv-102 (E17): the identity of stored line 0004 fails at a = 2 (52 vs 12), inside the
source's own context (p = 13 is prime and divides 2^4 - 2^2 + 1 = 13). -/
namespace G3refPnv102

theorem lhs_at_two : lhs 2 = 52 := by norm_num [lhs]
theorem rhs_at_two : rhs 2 = 12 := by norm_num [rhs]
theorem identity_fails_at_two : lhs 2 ≠ rhs 2 := by norm_num [lhs, rhs]
theorem thirteen_prime : Nat.Prime 13 := by norm_num
theorem thirteen_divides_context_at_two : ((13 : ℕ) : ℤ) ∣ (2 : ℤ) ^ 4 - 2 ^ 2 + 1 := by norm_num

theorem source_identity_false : ¬ SourceIdentity := fun h => identity_fails_at_two (h 2)

theorem source_identity_in_context_false : ¬ SourceIdentityInContext :=
  fun h => identity_fails_at_two (h 2 13 thirteen_prime thirteen_divides_context_at_two)

end G3refPnv102

#print axioms G3refPnv102.identity_fails_at_two
#print axioms G3refPnv102.source_identity_false
#print axioms G3refPnv102.source_identity_in_context_false
