import Mathlib
/-! The displayed formula is evaluated over actual complex numbers. A complex
square root does not give a real norm, and even its zero test fails. -/
noncomputable section
namespace ProofWiki12198CodexExpansion

def formula (v : ℂ × ℂ) : ℂ := Complex.sqrt (v.1 ^ 2 + v.2 ^ 2)
def witnessX : ℂ × ℂ := (1, Complex.I)

theorem refutes_published_positive_definiteness :
    formula witnessX = 0 ∧ witnessX ≠ 0 ∧
    ¬ (∀ v : ℂ × ℂ, formula v = 0 ↔ v = 0) := by
  have hf : formula witnessX = 0 := by simp [formula, witnessX]
  have hn : witnessX ≠ 0 := by simp [witnessX]
  exact ⟨hf, hn, fun h => hn ((h witnessX).mp hf)⟩

theorem negative_control_no_cancellation : formula (1, 0) = 1 := by
  simp [formula]
end ProofWiki12198CodexExpansion
