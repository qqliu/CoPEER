import defs_only
/- EVALUATOR-ONLY reference correction for E11 (original package: repair, line 42). -/
namespace ProofWiki25056Census.Ref

/-- Reference corrected scalar factor: `|a|`. -/
def scalar_factor (a : ℤ) : ℤ := |a|

theorem universal : ∀ (a : ℤ) (p : Polynomial ℤ), (Polynomial.C a * p).content = scalar_factor a * p.content := by
  intro a p
  unfold scalar_factor
  rw [Polynomial.content_C_mul, Int.abs_eq_normalize]

end ProofWiki25056Census.Ref
