import defs_only
/- Record SE_cs_156543__q (E04): the located step fails at the pair (sigmaInfinite, 0)
with the extension sigmaPrimeInfinite. -/
namespace SEcs156543q

/-- `{P1E,P2E} {}^omega`: both request at position 0, nobody ever commits. -/
def sigmaInfinite (n : Nat) : Letter := if n = 0 then eeL else emptyL

/-- `{P1E,P2E} {P1C}^omega`: the same first letter, then P1 commits forever. -/
def sigmaPrimeInfinite (n : Nat) : Letter := if n = 0 then eeL else c1L

theorem sigma_violates_at_zero : ¬PhiInfinite sigmaInfinite 0 := by
  intro h
  obtain ⟨j, _, hj⟩ := h ⟨rfl, rfl⟩
  by_cases h0 : j = 0 <;>
    simp [sigmaInfinite, h0, eeL, emptyL] at hj

theorem same_prefix_of_length_one : AgreeUpTo 1 sigmaPrimeInfinite sigmaInfinite := by
  intro k hk
  have hk0 : k = 0 := by omega
  subst hk0
  rfl

theorem sigmaPrime_satisfies_at_zero : PhiInfinite sigmaPrimeInfinite 0 :=
  fun _ => ⟨1, by decide, Or.inl rfl⟩

theorem local_claim_false : ¬LocalClaim :=
  fun h => h sigmaInfinite 0 sigma_violates_at_zero sigmaPrimeInfinite
    same_prefix_of_length_one sigmaPrime_satisfies_at_zero

end SEcs156543q

#print axioms SEcs156543q.sigma_violates_at_zero
#print axioms SEcs156543q.local_claim_false
