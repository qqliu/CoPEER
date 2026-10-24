import Mathlib
/-! The source shear is a genuine real linear map, hence an affine map. -/
namespace ProofWiki120506CodexExpansion

def L : (ℝ × ℝ) →ₗ[ℝ] (ℝ × ℝ) where
  toFun p := (p.1, p.1 + p.2)
  map_add' p q := by ext <;> dsimp <;> ring
  map_smul' c p := by ext <;> dsimp <;> ring

def XAxis : Set (ℝ × ℝ) := {p | p.2 = 0}
def Claimed : Set (ℝ × ℝ) := {q | q.1 + q.2 = 0}

theorem refutes_published_x_axis_image :
    (1, 0) ∈ XAxis ∧ L (1, 0) = (1, 1) ∧
    L (1, 0) ∉ Claimed ∧ ¬ (L '' XAxis ⊆ Claimed) := by
  have hn : L (1, 0) ∉ Claimed := by norm_num [L, Claimed]
  refine ⟨rfl, by norm_num [L], hn, ?_⟩
  intro h
  exact hn (h ⟨(1, 0), rfl, rfl⟩)

theorem corrected_whole_image : L '' XAxis = {q | q.2 = q.1} := by
  ext q
  constructor
  · rintro ⟨p, hp, rfl⟩
    simpa [L, XAxis] using hp
  · intro hq
    refine ⟨(q.1, 0), rfl, ?_⟩
    ext <;> simp_all [L]
end ProofWiki120506CodexExpansion
