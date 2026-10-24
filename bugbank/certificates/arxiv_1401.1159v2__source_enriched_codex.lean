import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Tactic
namespace Arxiv14011159v2SourceEnrichedCodex
open Polynomial
noncomputable def P : Polynomial ℤ := 1+X+C 3*X^2
def unimodal (p : Polynomial ℤ) : Prop := ∃ m : ℕ,
  (∀ i j, i ≤ j → j ≤ m → p.coeff i ≤ p.coeff j) ∧
  (∀ i j, m ≤ i → i ≤ j → p.coeff j ≤ p.coeff i)
lemma coeff_P (n : ℕ) : P.coeff n = if n=0 then 1 else if n=1 then 1 else if n=2 then 3 else 0 := by
  simp [P,coeff_add,coeff_C_mul,coeff_X_pow,coeff_X,coeff_one]
  split_ifs <;> omega
lemma P_unimodal : unimodal P := by
  refine ⟨2,?_,?_⟩
  · intro i j hij hj
    simp only [coeff_P]
    split_ifs <;> omega
  · intro i j hi hij
    simp only [coeff_P]
    split_ifs <;> omega
lemma coeff_product :
    (P*P).coeff 2 = 7 ∧ (P*P).coeff 3 = 6 ∧ (P*P).coeff 4 = 9 := by
  norm_num [coeff_mul,coeff_P,Finset.Nat.antidiagonal_succ,Finset.Nat.antidiagonal_zero]
theorem refutes_unimodal_product : unimodal P ∧ ¬ unimodal (P*P) := by
  refine ⟨P_unimodal,?_⟩
  obtain ⟨h2,h3,h4⟩ := coeff_product
  rintro ⟨m,hin,hout⟩
  by_cases hm : 3 ≤ m
  · have h := hin 2 3 (by omega) hm
    omega
  · have h := hout 3 4 (by omega) (by omega)
    omega
end Arxiv14011159v2SourceEnrichedCodex
