import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Tactic
namespace Arxiv250804726v3SourceEnrichedCodex
open Polynomial
-- The source explicitly allows multisets: the six occurrences remain distinct.
noncomputable def P : Polynomial ℤ := (1+X)^6
theorem refutes_coefficient_nt_bound :
    (0:ℕ)<6 ∧ (0:ℕ)<2 ∧ P.coeff 2 = 15 ∧ P.coeff 2 > (6:ℤ)*2 := by
  norm_num [P,Polynomial.coeff_one_add_X_pow,show Nat.choose 6 2 = 15 from by decide]
end Arxiv250804726v3SourceEnrichedCodex
