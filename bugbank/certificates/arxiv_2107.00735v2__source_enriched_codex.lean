import Mathlib.GroupTheory.SpecificGroups.Dihedral
import Mathlib.GroupTheory.Subgroup.Center
import Mathlib.GroupTheory.PGroup
import Mathlib.GroupTheory.SpecificGroups.Cyclic.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Push
/-!
Original witness retained: Mathlib's `DihedralGroup 4` is D₈, with the central
order-two subgroup N={1,r²} and reflection subgroup H={1,s}. The certificate
checks the source's p-group and unique minimal normal subgroup branch, and
shows H is nonnormal despite H∩N=1 and |H|=2. The conclusion concerns the
prerequisite for using G/H as a quotient group; it does not refute the paper's
codegree inequality. No custom multiplication or subgroup tables are used.
-/
namespace Arxiv210700735v2SourceEnrichedCodex
abbrev G := DihedralGroup 4
open DihedralGroup
def N : Subgroup G where
  carrier := {x | x = 1 ∨ x = r 2}
  one_mem' := Or.inl rfl
  mul_mem' := by decide
  inv_mem' := by decide
def H : Subgroup G where
  carrier := {x | x = 1 ∨ x = sr 0}
  one_mem' := Or.inl rfl
  mul_mem' := by decide
  inv_mem' := by decide
instance : DecidablePred (· ∈ N) := fun _ => inferInstanceAs (Decidable (_ = (1:G) ∨ _ = r 2))
instance : DecidablePred (· ∈ H) := fun _ => inferInstanceAs (Decidable (_ = (1:G) ∨ _ = sr 0))
lemma N_normal : N.Normal := ⟨by decide⟩
lemma H_not_normal : ¬ H.Normal := by
 intro h
 have hh := h.conj_mem (sr 0) (by decide : sr 0 ∈ H) (r 1)
 exact (by decide : (r 1:G) * sr 0 * (r 1)⁻¹ ∉ H) hh
lemma contains_N (K : Subgroup G) (hK : K.Normal) (hne : K ≠ ⊥) : N ≤ K := by
 have hex : ∃ x : G, x ∈ K ∧ x ≠ 1 := by
  by_contra! h
  apply hne
  apply le_antisymm
  · intro x hx
    exact Subgroup.mem_bot.mpr (h x hx)
  · exact bot_le
 obtain ⟨x,hx,hx1⟩ := hex
 have h2 : (r 2:G) ∈ K := by
  rcases x with i | i
  · fin_cases i
    · exact False.elim (hx1 rfl)
    · have hh := K.mul_mem hx hx; convert hh using 1
    · exact hx
    · have hh := K.mul_mem hx hx; convert hh using 1
  · have hh := K.mul_mem (hK.conj_mem _ hx (r 1)) hx
    fin_cases i <;> convert hh using 1
 intro y hy
 rcases hy with rfl | rfl
 · exact K.one_mem
 · exact h2
lemma N_nontrivial : N ≠ ⊥ := by
  intro h
  have hh : (r 2:G) ∈ N := by decide
  rw [h] at hh
  exact (by decide : (r 2:G) ≠ 1) (Subgroup.mem_bot.mp hh)

/-- The source's uniqueness branch uses the order-theoretic minimality of actual
normal subgroups. A stronger statement, `contains_N`, was proved above. -/
lemma unique_minimal_normal :
    ∃! K : Subgroup G, Minimal (fun K => K.Normal ∧ K ≠ ⊥) K := by
  refine ⟨N,⟨⟨N_normal,N_nontrivial⟩,?_⟩,?_⟩
  · intro K hK _
    exact contains_N K hK.1 hK.2
  · intro K hK
    apply le_antisymm
    · exact hK.2 ⟨N_normal,N_nontrivial⟩ (contains_N K hK.1.1 hK.1.2)
    · exact contains_N K hK.1.1 hK.1.2

lemma not_cyclic : ¬ IsCyclic G := by
  intro h
  letI : IsCyclic G := h
  exact (by decide : (r 1:G) * sr 0 ≠ sr 0 * r 1) (mul_comm' _ _)

/-- A quotient projection with kernel H cannot be a group homomorphism.
Mathlib's normal-kernel theorem supplies the requisite general fact. -/
lemma no_homomorphism_has_kernel_H {Q : Type*} [Group Q] (f : G →* Q) :
    f.ker ≠ H := by
  intro h
  have hn := f.normal_ker
  rw [h] at hn
  exact H_not_normal hn

theorem refutes_quotient_without_normality :
 Fintype.card G = 2^3 ∧ Nat.Prime 2 ∧ IsPGroup 2 G ∧
 Fintype.card N = 2 ∧ Fintype.card H = 2 ∧
 N.Normal ∧ N ≤ Subgroup.center G ∧ N ≠ ⊥ ∧
 (∀ K : Subgroup G, K.Normal → K ≠ ⊥ → N ≤ K) ∧
 (∃! K : Subgroup G, Minimal (fun K => K.Normal ∧ K ≠ ⊥) K) ∧
 ¬ IsCyclic G ∧
 (r 2 : G) ≠ 1 ∧ (sr 0 : G) ≠ 1 ∧ (r 2 : G) ≠ sr 0 ∧
 (r 2 : G)^2 = 1 ∧ (sr 0 : G)^2 = 1 ∧
 H ⊓ N = ⊥ ∧ H ≠ N ∧ ¬ H.Normal := by
 refine ⟨by decide,by decide,IsPGroup.of_card (n := 3) (by rw [Nat.card_eq_fintype_card]; decide),by decide,by decide,N_normal,?_,N_nontrivial,
   contains_N,unique_minimal_normal,not_cyclic,by decide,by decide,by decide,
   by decide,by decide,?_,?_,H_not_normal⟩
 · intro x hx; exact Subgroup.mem_center_iff.mpr (by revert x; decide)
 · apply le_antisymm
   · intro x hx
     apply Subgroup.mem_bot.mpr
     have h : ∀ x:G, x ∈ H → x ∈ N → x=1 := by decide
     exact h x hx.1 hx.2
   · exact bot_le
 · intro h
   exact H_not_normal (h ▸ N_normal)
end Arxiv210700735v2SourceEnrichedCodex
