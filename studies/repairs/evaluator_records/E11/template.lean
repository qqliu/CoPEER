import defs_only
/-!
Record E11: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace ProofWiki25056Census

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected scalar factor `s a` in `(C a * p).content = s a * p.content`, as an expression in the
integer `a` (the source has `a` itself). No reference to `content`; no `if`/`match`. -/
def scalar_factor (a : ℤ) : ℤ := «HOLE»

/-- The corrected pull-out identity for every integer scalar and every integer polynomial (shape fixed;
`Polynomial.content` is Mathlib's normalised gcd of the coefficients). -/
def CorrectedClaim : Prop :=
  ∀ (a : ℤ) (p : Polynomial ℤ), (Polynomial.C a * p).content = scalar_factor a * p.content
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected identity for every integer `a` and every `p ∈ ℤ[X]`. -/
theorem repair_statement : ∀ (a : ℤ) (p : Polynomial ℤ), (Polynomial.C a * p).content = ProofWiki25056Census.scalar_factor a * p.content := sorry

/-- Non-vacuity: the corrected factor differs from the source's `a` somewhere and is not identically zero. -/
theorem repair_nonvacuous : (∃ a : ℤ, ProofWiki25056Census.scalar_factor a ≠ a) ∧ (∃ a : ℤ, ProofWiki25056Census.scalar_factor a ≠ 0) := sorry

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ (a : ℤ) (p : Polynomial ℤ), (Polynomial.C a * p).content = ProofWiki25056Census.scalar_factor a * p.content := sorry
-- ===== END OBLIGATIONS =====
end ProofWiki25056Census
