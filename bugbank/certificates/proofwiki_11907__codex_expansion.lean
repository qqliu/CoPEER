import Mathlib
/-! Keep the original F4/F2 witness, realized by Mathlib's GaloisField2 2.
A root alpha of X²+X+1 is moved by Frobenius, which fixes the base field.
Choose L=F=F4 in the source's normal-intermediate-extension paragraph. -/
noncomputable section
namespace ProofWiki11907CodexExpansion
instance : Fact (Nat.Prime 2) := ⟨by decide⟩
abbrev K := ZMod 2
abbrev F := GaloisField 2 2
instance : Fintype F := Fintype.ofFinite F

def tau : F ≃ₐ[K] F where
  __ := frobeniusEquiv F 2
  commutes' c := by
    change (algebraMap K F c)^2 = algebraMap K F c
    rw [← map_pow]
    congr 1
    fin_cases c <;> decide

theorem card_four : Fintype.card F = 4 := by
  rw [← Nat.card_eq_fintype_card]
  exact GaloisField.card (p := 2) (n := 2) (by decide)

theorem nontrivial_root : ∃ a : F, a ≠ 0 ∧ a ≠ 1 := by
  by_contra hn
  push_neg at hn
  have hs : Function.Surjective (fun b : Bool => if b then (1 : F) else 0) := by
    intro z
    by_cases hz : z = 0
    · exact ⟨false, hz.symm⟩
    · exact ⟨true, (hn z hz).symm⟩
  have hc := Fintype.card_le_of_surjective _ hs
  rw [card_four] at hc
  norm_num at hc

theorem refutes_tau_fixes_intermediate_field :
    IsGalois K F ∧ ∃ a : F,
    a^2 + a + 1 = 0 ∧ tau a = a^2 ∧ tau a ≠ a ∧
    (∀ c : K, tau (algebraMap K F c) = algebraMap K F c) := by
  refine ⟨inferInstance, ?_⟩
  obtain ⟨a,ha0,ha1⟩ := nontrivial_root
  have hp : a^4 = a := by simpa [card_four] using FiniteField.pow_card a
  have hprod : a * (a-1) * (a^2+a+1) = 0 := by linear_combination hp
  have hroot : a^2+a+1 = 0 := (mul_eq_zero.mp hprod).resolve_left (mul_ne_zero ha0 (sub_ne_zero.mpr ha1))
  have ht : tau a = a^2 := rfl
  refine ⟨a,hroot,ht,?_,fun c => tau.commutes c⟩
  intro he
  rw [ht] at he
  have hmul : a * (a-1) = 0 := by linear_combination he
  exact mul_ne_zero ha0 (sub_ne_zero.mpr ha1) hmul
end ProofWiki11907CodexExpansion
