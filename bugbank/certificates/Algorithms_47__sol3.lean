import Mathlib.Analysis.Convex.Extreme
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
set_option autoImplicit false
namespace ProofCerts.Alg47
/-- The real polyhedron specified by the two rows (0,1) and (0,-1). -/
def P3 : Set (ℝ × ℝ) := {z | z.2 ≤ 0 ∧ -z.2 ≤ 0}
theorem P3_snd_eq_zero (z : ℝ × ℝ) (hz : z ∈ P3) : z.2 = 0 := by
  obtain ⟨h1,h2⟩ := hz
  linarith
theorem convex_P3 : Convex ℝ P3 := by
  intro x hx y hy a b ha hb hab
  change a*x.2 + b*y.2 ≤ 0 ∧ -(a*x.2 + b*y.2) ≤ 0
  simp [P3_snd_eq_zero x hx, P3_snd_eq_zero y hy]
/-- Every nonempty Mathlib extreme subset of this line is the whole line. -/
theorem extreme_eq_P3 {F : Set (ℝ × ℝ)} (hF : IsExtreme ℝ P3 F) (hne : F.Nonempty) : F = P3 := by
  letI : Invertible (2 : ℝ) := invertibleOfNonzero (by norm_num)
  apply Set.Subset.antisymm hF.subset
  obtain ⟨x,hx⟩ := hne
  intro y hy
  let z : ℝ × ℝ := (2*x.1-y.1, 0)
  have hz : z ∈ P3 := by simp [z,P3]
  have hmid : midpoint ℝ y z = x := by
    have hx0 := P3_snd_eq_zero x (hF.subset hx)
    have hy0 := P3_snd_eq_zero y hy
    ext <;> norm_num [midpoint, AffineMap.lineMap_apply, z] <;> linarith
  exact hF.left_mem_of_mem_openSegment hy hz hx (hmid ▸ midpoint_mem_openSegment y z)

/-- Literal specialization of the source's active-inequality face definition.
This is an input-specific matrix evaluation, not a replacement definition of
Mathlib convexity or extremality. -/
def activeFace (I : Finset (Fin 2)) : Set (ℝ × ℝ) :=
  {z | z ∈ P3 ∧ ∀ i ∈ I, if i = 0 then z.2 = 0 else -z.2 = 0}
theorem activeFace_eq (I : Finset (Fin 2)) : activeFace I = P3 := by
  ext z
  constructor
  · exact fun h => h.1
  · intro hz
    refine ⟨hz, ?_⟩
    intro i hi
    have h0 := P3_snd_eq_zero z hz
    split_ifs <;> simp [h0]

theorem sol3_minimal_face_singleton_fails :
    Convex ℝ P3 ∧ IsExtreme ℝ P3 P3 ∧ P3.Nonempty ∧
    (∀ F : Set (ℝ × ℝ), IsExtreme ℝ P3 F → F.Nonempty → F = P3) ∧
    (∀ I : Finset (Fin 2), activeFace I = P3) ∧
    ¬ ∃ x : ℝ × ℝ, P3 = {x} := by
  refine ⟨convex_P3, IsExtreme.rfl, ⟨(0,0), by simp [P3]⟩,
    fun F hF hn => extreme_eq_P3 hF hn, activeFace_eq, ?_⟩
  rintro ⟨x,hx⟩
  have h0 : (0,0) ∈ P3 := by simp [P3]
  have h1 : (1,0) ∈ P3 := by simp [P3]
  rw [hx, Set.mem_singleton_iff] at h0 h1
  have := congrArg Prod.fst (h0.trans h1.symm)
  norm_num at this
end ProofCerts.Alg47
#print axioms ProofCerts.Alg47.sol3_minimal_face_singleton_fails
