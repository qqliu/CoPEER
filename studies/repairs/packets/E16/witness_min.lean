import defs_only
/- Record proofwiki_120506__codex_expansion (E16): the point (1, 0) lies on the x-axis, its image under L is
(1, 1), which is not on the line x + y = 0; so the image of the x-axis is not contained in that line. -/
namespace ProofWiki120506CodexExpansion

theorem unit_point_on_axis : ((1 : ℝ), (0 : ℝ)) ∈ XAxis := rfl

theorem image_of_unit_point : L ((1 : ℝ), (0 : ℝ)) = ((1 : ℝ), (1 : ℝ)) := by
  simp [L]

theorem image_point_off_claimed_line : L ((1 : ℝ), (0 : ℝ)) ∉ Claimed := by
  rw [image_of_unit_point]
  simp [Claimed]

theorem image_not_subset_claimed : ¬ (L '' XAxis ⊆ Claimed) := by
  intro h
  apply image_point_off_claimed_line
  apply h
  exact ⟨((1 : ℝ), (0 : ℝ)), unit_point_on_axis, rfl⟩

theorem source_image_claim_false : ¬ SourceImageClaim := by
  intro h
  apply image_not_subset_claimed
  rw [SourceImageClaim] at h
  rw [h]

end ProofWiki120506CodexExpansion

#print axioms ProofWiki120506CodexExpansion.image_not_subset_claimed
#print axioms ProofWiki120506CodexExpansion.source_image_claim_false
