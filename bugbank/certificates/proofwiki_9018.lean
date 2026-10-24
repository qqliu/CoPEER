import Mathlib
/-! An actual nonunital ring with zero multiplication, and the full
untruncated sequence Cauchy product. Only Mathlib's standard finite sum is
needed to define the source's coefficient formula. -/
namespace ProofWiki9018

def R := ZMod 2
instance : AddCommGroup R := inferInstanceAs (AddCommGroup (ZMod 2))
instance : NonUnitalCommRing R where
  __ := (inferInstance : AddCommGroup R)
  mul _ _ := 0
  mul_assoc _ _ _ := rfl
  mul_comm _ _ := rfl
  left_distrib _ _ _ := (zero_add 0).symm
  right_distrib _ _ _ := (zero_add 0).symm
  zero_mul _ := rfl
  mul_zero _ := rfl

abbrev Seq := ℕ → R

def cauchy (f g : Seq) (n : ℕ) : R :=
  ∑ i ∈ Finset.range (n + 1), f i * g (n - i)

def nonzeroSequence : Seq := fun _ => (1 : ZMod 2)

theorem cauchy_zero (f g : Seq) : cauchy f g = 0 := by
  funext n
  simp [cauchy, show ∀ x y : R, x * y = 0 from fun _ _ => rfl]

theorem sequence_nonzero : nonzeroSequence ≠ 0 := by
  intro h
  have hh := congrFun h 0
  exact (by decide : (1 : ZMod 2) ≠ 0) hh

theorem refutes_unchanged_construction_for_nonunital_ring :
    (∀ f g : Seq, cauchy f g = 0) ∧
    ¬ (∃ u : Seq, ∀ f : Seq, cauchy u f = f) ∧
    ¬ (∃ f : Seq, cauchy f f ≠ 0) := by
  refine ⟨cauchy_zero, ?_, ?_⟩
  · rintro ⟨u, hu⟩
    exact sequence_nonzero ((hu nonzeroSequence).symm.trans (cauchy_zero _ _))
  · rintro ⟨f, hf⟩
    exact hf (cauchy_zero _ _)
end ProofWiki9018
