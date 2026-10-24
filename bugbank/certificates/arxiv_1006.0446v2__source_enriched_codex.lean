import Mathlib.GroupTheory.FreeGroup.Basic
import Mathlib.Tactic
namespace Arxiv10060446v2SourceEnrichedCodex
abbrev F := FreeGroup (Fin 2)
def a : F := FreeGroup.of 0
def b : F := FreeGroup.of 1
def S : F →* F := FreeGroup.lift fun i => if i=0 then b else a⁻¹*b⁻¹
def T : F →* F := FreeGroup.lift fun i => if i=0 then a⁻¹ else b⁻¹
-- A concrete permutation image witnesses inequality in the actual free group.
def image : F →* Equiv.Perm (Fin 3) :=
  FreeGroup.lift fun i => if i=0 then Equiv.swap 0 1 else Equiv.swap 1 2
lemma ba_ne_ab : b*a ≠ a*b := by
  intro h
  have h' := congrArg (fun w => image w 0) h
  norm_num [image,a,b] at h'
  exact (by decide : (2:Fin 3) ≠ (Equiv.swap 0 1) ((Equiv.swap 1 2) 0)) h'
theorem refutes_displayed_direct_product_action :
    S a = b ∧ S b = a⁻¹*b⁻¹ ∧ T a = a⁻¹ ∧ T b = b⁻¹ ∧
    S (T b) = b*a ∧ T (S b) = a*b ∧ S.comp T ≠ T.comp S := by
  have sa : S a = b := by simp [S,a]
  have sb : S b = a⁻¹*b⁻¹ := by simp [S,b]
  have ta : T a = a⁻¹ := by simp [T,a]
  have tb : T b = b⁻¹ := by simp [T,b]
  have st : S (T b) = b*a := by rw [tb,map_inv,sb,mul_inv_rev,inv_inv,inv_inv]
  have ts : T (S b) = a*b := by rw [sb,map_mul,map_inv,map_inv,ta,tb,inv_inv,inv_inv]
  refine ⟨sa,sb,ta,tb,st,ts,?_⟩
  intro h
  have he := DFunLike.congr_fun h b
  exact ba_ne_ab (st.symm.trans (he.trans ts))
end Arxiv10060446v2SourceEnrichedCodex
