import Mathlib
/-! Original p=x1²+x2² over F2, with actual Mathlib multivariate
polynomials and symmetry. For two variables, degree reverse lexicographic
comparison is total degree followed by reversed exponent of x2. -/
set_option maxHeartbeats 1600000
noncomputable section
namespace ProofWiki10516CodexExpansion
open MvPolynomial
abbrev E := Fin 2 →₀ ℕ
abbrev K := ZMod 2
def a : E := Finsupp.single 0 2
def b : E := Finsupp.single 1 2
noncomputable def p : MvPolynomial (Fin 2) K :=
  ∑ i : Fin 2, monomial (Finsupp.single i 2) 1
def Greater (u v : E) : Prop :=
  u 0 + u 1 > v 0 + v 1 ∨ (u 0 + u 1 = v 0 + v 1 ∧ u 1 < v 1)

theorem symmetric : p.IsSymmetric := by
  intro e
  simp only [p, map_sum, rename_monomial, Finsupp.mapDomain_single]
  exact Equiv.sum_comp e (fun i : Fin 2 => (monomial (Finsupp.single i 2) 1 : MvPolynomial (Fin 2) K))

theorem coeff_formula (d : E) : coeff d p =
    (if a = d then 1 else 0) + (if b = d then 1 else 0) := by
  classical
  simp only [p, Fin.sum_univ_two, coeff_add, coeff_monomial, a, b]
  split_ifs <;> norm_num

theorem leading : coeff a p ≠ 0 ∧ ∀ d : E, coeff d p ≠ 0 → ¬ Greater d a := by
  have hab : a ≠ b := by
    intro h
    have hh := congrArg (fun z : E => z 0) h
    norm_num [a,b] at hh
  constructor
  · rw [coeff_formula]
    simp [hab, Ne.symm hab]
  · intro d hd
    by_cases ha : a = d
    · subst d
      simp [Greater]
    · by_cases hb : b = d
      · subst d
        norm_num [Greater,a,b]
      · rw [coeff_formula] at hd
        simp [ha,hb] at hd

theorem refutes_reversed_exponent_comparison :
    p.IsSymmetric ∧ coeff a p ≠ 0 ∧ coeff b p ≠ 0 ∧
    (∀ d : E, coeff d p ≠ 0 → ¬ Greater d a) ∧
    a 0 > a 1 ∧ Greater a b ∧ ¬ Greater b a := by
  refine ⟨symmetric, leading.1, ?_, leading.2, ?_, ?_, ?_⟩
  · rw [coeff_formula]
    have hab : a ≠ b := by
      intro h
      have hh := congrArg (fun z : E => z 0) h
      norm_num [a,b] at hh
    simp [hab]
  all_goals norm_num [Greater,a,b]
end ProofWiki10516CodexExpansion
