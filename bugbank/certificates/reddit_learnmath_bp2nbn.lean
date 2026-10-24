import Mathlib.Algebra.Polynomial.Degree.Units
import Mathlib.Algebra.Polynomial.Degree.Operations
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: f=2x²−2 is a genuine rational quadratic with displayed nonconstant factors. Any monic factorization has quadratic coefficient1, contradicting2. Uses Polynomial rather than coefficient records.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_bp2nbn
open Polynomial
noncomputable def f : Polynomial ℚ := C 2*X^2-C 2
theorem certificate_core : f.natDegree = 2 ∧
    f = (C 2*X-C 2)*(X+C 1) ∧
    ¬ ∃ a b : ℚ, f = (X-C a)*(X-C b) := by
  refine ⟨by norm_num [f], by simp [f]; ring, ?_⟩
  rintro ⟨a,b,h⟩
  have h2 := congrArg (fun p : Polynomial ℚ => p.coeff 2) h
  norm_num [f, sub_mul, mul_sub, Polynomial.coeff_sub, Polynomial.coeff_mul_X, Polynomial.coeff_X_mul, Polynomial.coeff_C_mul] at h2
theorem certificate : f.natDegree = 2 ∧
    f = (C 2*X-C 2)*(X+C 1) ∧
    ¬ IsUnit (C 2*X-C 2 : Polynomial ℚ) ∧ ¬ IsUnit (X+C 1 : Polynomial ℚ) ∧
    ¬ ∃ a b : ℚ, f = (X-C a)*(X-C b) := by
  rcases certificate_core with ⟨hd,hfac,hfail⟩
  refine ⟨hd,hfac,?_,?_,hfail⟩
  · apply Polynomial.not_isUnit_of_natDegree_pos
    rw [Polynomial.natDegree_sub_C, Polynomial.natDegree_C_mul_X 2 (by norm_num)]
    norm_num
  · apply Polynomial.not_isUnit_of_natDegree_pos
    rw [Polynomial.natDegree_X_add_C]
    norm_num
end Audit_reddit_learnmath_bp2nbn
