import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Setoid.Partition
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Tactic
namespace Arxiv190506569Mathlib
abbrev I := Fin 2 × Fin 2
abbrev G := Multiplicative (ZMod 2)
def π : Setoid I := Setoid.ker Prod.fst
def σ : Setoid I := Setoid.ker Prod.snd
def a (i : I) : G := if i = (1,1) then Multiplicative.ofAdd 1 else 1
def b (_ : I) : G := 1

theorem meet_eq_bot : π ⊓ σ = ⊥ := by
  ext x y
  exact Prod.ext_iff.symm

theorem join_eq_top : π ⊔ σ = ⊤ := by
  apply top_unique
  intro x y _
  exact (π ⊔ σ).trans (Setoid.le_def.mp le_sup_left (show π x (x.1,y.2) from rfl))
    (Setoid.le_def.mp le_sup_right (show σ (x.1,y.2) y from rfl))

def BlockConstant (p : Setoid I) (f : I → G) : Prop :=
  ∀ i j, p i j → f i = f j

def Solution (uv : (I → G) × (I → G)) : Prop :=
  BlockConstant π uv.1 ∧ BlockConstant σ uv.2 ∧
  ∀ i, uv.1 i * uv.2 i = a i * (b i)⁻¹

theorem ratio_hypothesis :
    ∀ i j, (π ⊓ σ) i j → a i * (b i)⁻¹ = a j * (b j)⁻¹ := by
  rw [meet_eq_bot]
  intro i j h
  exact congrArg (fun x => a x * (b x)⁻¹) h

theorem no_solutions (uv : (I → G) × (I → G)) : ¬Solution uv := by
  rintro ⟨hu,hv,h⟩
  have u0 := hu (0,0) (0,1) rfl
  have u1 := hu (1,0) (1,1) rfl
  have v0 := hv (0,0) (1,0) rfl
  have v1 := hv (0,1) (1,1) rfl
  have h00 := h (0,0)
  have h01 := h (0,1)
  have h10 := h (1,0)
  have h11 := h (1,1)
  norm_num [a,b] at h00 h01 h10 h11
  rw [←u0] at h01
  have veq := mul_left_cancel (h00.trans h01.symm)
  have veq' : uv.2 (1,0) = uv.2 (1,1) := v0.symm.trans (veq.trans v1)
  rw [u1,veq',h11] at h10
  exact (by decide : (Multiplicative.ofAdd (1 : ZMod 2) : G) ≠ 1) h10

theorem solution_count_zero : Nat.card {uv // Solution uv} = 0 := by
  letI : IsEmpty {uv // Solution uv} := ⟨fun uv => no_solutions uv.val uv.property⟩
  simp

theorem asserted_count_two : Nat.card G ^ Nat.card (Quotient (π ⊔ σ)) = 2 := by
  rw [join_eq_top]
  norm_num [Nat.card_eq_fintype_card]

theorem original_witness_refutes :
    Nat.card I = 4 ∧ (∀ i j, (π ⊓ σ) i j → a i * (b i)⁻¹ = a j * (b j)⁻¹) ∧
    Nat.card {uv // Solution uv} = 0 ∧
    Nat.card G ^ Nat.card (Quotient (π ⊔ σ)) = 2 := by
  exact ⟨by simp [Nat.card_eq_fintype_card], ratio_hypothesis, solution_count_zero, asserted_count_two⟩
end Arxiv190506569Mathlib
#print axioms Arxiv190506569Mathlib.original_witness_refutes
