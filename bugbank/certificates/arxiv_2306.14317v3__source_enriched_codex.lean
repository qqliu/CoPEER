import Mathlib.LinearAlgebra.QuadraticForm.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Tactic
namespace Arxiv230614317v3SourceEnrichedCodex
abbrev K := ZMod 3
abbrev V := Fin 2 → K
def q : QuadraticForm K V := QuadraticMap.proj 0 0 + QuadraticMap.proj 1 1
lemma q_formula (v : V) : q v = v 0 * v 0 + v 1 * v 1 := rfl
lemma polar_formula (v w : V) :
    q.polarBilin v w = 2*v 0*w 0 + 2*v 1*w 1 := by
  simp [QuadraticMap.polarBilin_apply_apply, QuadraticMap.polar,q_formula]
  ring
lemma anisotropic : ∀ v : V, q v = 0 → v = 0 := by
  simp only [q_formula]
  decide
lemma polar_nondegenerate : ∀ v : V, (∀ w : V, q.polarBilin v w = 0) → v = 0 := by
  simp only [polar_formula]
  decide
theorem refutes_universal_hyperbolic_decomposition :
    Module.finrank K V = 2 ∧
    (∀ v : V, (∀ w : V, q.polarBilin v w = 0) → v = 0) ∧
    ¬ ∃ e f : V, q e = 0 ∧ q f = 0 ∧ q.polarBilin e f = 1 := by
  refine ⟨by simp [V],polar_nondegenerate,?_⟩
  rintro ⟨e,f,he,hf,hpair⟩
  have he0 := anisotropic e he
  subst e
  simpa using hpair
end Arxiv230614317v3SourceEnrichedCodex
