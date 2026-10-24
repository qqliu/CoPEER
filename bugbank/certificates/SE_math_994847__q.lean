/- Review overlay for SE_math_994847__q.
The original record and human decisions remain frozen. Audit and witness disposition:
../audits/stackexchange_final.json. Historical auxiliary computations are not broader
source-fidelity or universal-quantifier proofs. The audit selects the release theorem.
-/

import Mathlib

namespace SE_math_994847_q
open Matrix

def A : Matrix (Fin 3) (Fin 3) ℕ := !![0,1,0; 1,0,1; 0,1,0]

theorem matrix_square_counterexample :
    (∀ i j : Fin 3, i = j ∨ A i j = 1 ∨ ∃ k : Fin 3, A i k = 1 ∧ A k j = 1) ∧
    A 0 1 = 1 ∧ (A^2) 0 1 = 0 := by
  constructor
  · decide
  · norm_num [A, pow_two, Matrix.mul_apply, Fin.sum_univ_succ] <;> decide

theorem length_two_control : (A^2) 0 2 = 1 := by
  norm_num [A, pow_two, Matrix.mul_apply, Fin.sum_univ_succ] <;> decide

def sourceGraph : SimpleGraph (Fin 3) where
 Adj i j := i ≠ j ∧ (i = 1 ∨ j = 1)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel sourceGraph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
theorem source_graph_counterexample : sourceGraph.Connected ∧
    sourceGraph.adjMatrix ℕ = A ∧ (A^2) 0 1 = 0 := by
 refine ⟨by decide, ?_, matrix_square_counterexample.2.2⟩
 funext i j
 fin_cases i <;> fin_cases j <;> decide

end SE_math_994847_q
