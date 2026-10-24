import Mathlib
/-! Mathlib's endomorphism ring of the actual additive group ZMod 2. -/
namespace ProofWiki52087CodexExpansion
abbrev A := ZMod 2
abbrev End := AddMonoid.End A

def publishedLHS (f g h : End) : End := f * (g + h)
def publishedRHS (f g h : End) : End := (f + g) * (f + h)

theorem refutes_published_distributivity_identity :
    publishedLHS 0 1 1 = 0 ∧ publishedRHS 0 1 1 = 1 ∧
    publishedLHS 0 1 1 ≠ publishedRHS 0 1 1 ∧
    ¬ (∀ f g h : End, publishedLHS f g h = publishedRHS f g h) := by
  have hl : publishedLHS 0 1 1 = 0 := by simp [publishedLHS]
  have hr : publishedRHS 0 1 1 = 1 := by simp [publishedRHS]
  have hn : publishedLHS 0 1 1 ≠ publishedRHS 0 1 1 := by
    rw [hl, hr]
    intro h
    have := congrArg (fun f : End => f (1 : A)) h
    norm_num at this
  exact ⟨hl, hr, hn, fun h => hn (h 0 1 1)⟩

theorem corrected_distributivity (f g h : End) :
    f * (g + h) = f * g + f * h := mul_add f g h

theorem negative_control_h_zero_restores_equality :
    publishedLHS 0 1 0 = publishedRHS 0 1 0 := by
  simp [publishedLHS, publishedRHS]
end ProofWiki52087CodexExpansion
