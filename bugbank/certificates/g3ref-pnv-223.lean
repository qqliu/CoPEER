import Mathlib
/-! Original cyclic C4 witness in additive notation. Includes maximality, generator order, and gcd hypotheses. -/
namespace G3refPnv223
abbrev G := ZMod 4
def H : AddSubgroup G := AddSubgroup.zmultiples 2
lemma two_mem : (2:G) ∈ H := AddSubgroup.mem_zmultiples 2
lemma proper : H ≠ ⊤ := by
  intro h
  have hm : (1:G) ∈ H := by rw [h]; trivial
  rcases (AddSubgroup.mem_zmultiples_iff).mp hm with ⟨k,hk⟩
  have : (2:G) * (1:G) = 0 := by
    calc
      (2:G) * (1:G) = 2 * (k • (2:G)) := by rw [hk]
      _ = 0 := by simp [zsmul_eq_mul, mul_left_comm, show (2:G)*2=0 by decide]
  exact (by decide : (2:G) ≠ 0) this
lemma maximal : IsCoatom H := by
  refine ⟨proper, ?_⟩
  intro K hK
  obtain ⟨x,hx,hnot⟩ := SetLike.not_le_iff_exists.mp (not_le_of_gt hK)
  have htwo : (2:G) ∈ K := hK.le two_mem
  have hone : (1:G) ∈ K := by
    fin_cases x
    · exact False.elim (hnot H.zero_mem)
    · exact hx
    · exact False.elim (hnot two_mem)
    · have hn := K.neg_mem hx
      convert hn using 1
  apply top_unique
  intro y hy
  fin_cases y
  · exact K.zero_mem
  · exact hone
  · exact htwo
  · convert K.add_mem hone htwo using 1
lemma generates : AddSubgroup.zmultiples (1:G) = ⊤ := by
  apply top_unique
  intro y hy
  fin_cases y
  · exact (AddSubgroup.zmultiples (1:G)).zero_mem
  · exact AddSubgroup.mem_zmultiples 1
  · exact ⟨2, by decide⟩
  · exact ⟨3, by decide⟩
theorem refutes_strict_subgroup_containment :
    Nat.card G = 4 ∧ addOrderOf (1:G) = 4 ∧
    AddSubgroup.zmultiples (1:G) = ⊤ ∧ IsCoatom H ∧
    Nat.gcd 4 6 = 2 ∧ Nat.Prime 2 ∧ (2:ℕ) ∣ 6 ∧ (2:ℕ) < 6 ∧
    AddSubgroup.zmultiples (6:G) = H ∧ ¬ AddSubgroup.zmultiples (6:G) < H := by
  have heq : (6:G) = 2 := by decide
  refine ⟨?_, ?_, generates, maximal, by decide, by decide, by decide, by decide, ?_, ?_⟩
  · simp [G]
  · exact ZMod.addOrderOf_one 4
  · rw [heq]; rfl
  · rw [heq]; exact lt_irrefl H
end G3refPnv223
