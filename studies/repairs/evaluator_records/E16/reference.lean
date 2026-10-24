import defs_only
/- EVALUATOR-ONLY reference correction for E16 (released certificate: corrected_whole_image, line 21). -/
namespace ProofWiki120506CodexExpansion.Ref

/-- Reference defining condition of the image line: `y = x`. -/
def onImageLine (q : ℝ × ℝ) : Prop := q.2 = q.1

def imageLine : Set (ℝ × ℝ) := {q | onImageLine q}

theorem whole_image : L '' XAxis = imageLine := by
  ext q
  constructor
  · rintro ⟨p, hp, rfl⟩
    simp only [XAxis, Set.mem_setOf_eq] at hp
    simp [L, imageLine, onImageLine, hp]
  · intro hq
    simp only [imageLine, onImageLine, Set.mem_setOf_eq] at hq
    refine ⟨(q.1, 0), rfl, ?_⟩
    ext <;> simp [L, hq]

end ProofWiki120506CodexExpansion.Ref
