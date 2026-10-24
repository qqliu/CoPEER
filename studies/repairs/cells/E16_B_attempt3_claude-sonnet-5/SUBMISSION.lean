import defs_only
/-!
Record E16: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace ProofWiki120506CodexExpansion

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The defining condition of the corrected image line, as a statement about a point `q : ℝ × ℝ` with
coordinates `q.1`, `q.2`. The hole must be ONE linear equation `<left> = <right>` whose sides are built from
`q.1`, `q.2`, integer literals, `+`, `-` and `*` by a literal (e.g. `3 * q.1 - 2 * q.2 = 5`); it must mention
`q.1` or `q.2`; no `∧`/`∨`/`¬`/quantifiers, no membership, no `L`, `XAxis` or `Claimed`. -/
def onImageLine (q : ℝ × ℝ) : Prop := q.1 = q.2

/-- The corrected image line (shape fixed). -/
def imageLine : Set (ℝ × ℝ) := {q | onImageLine q}

/-- The corrected located statement (shape fixed): the image of the x-axis under the source's map `L` is
exactly the line `imageLine` (both inclusions). -/
def CorrectedImage : Prop := L '' XAxis = imageLine
-- ===== END FIXED PART =====

theorem repair_statement : ProofWiki120506CodexExpansion.L '' ProofWiki120506CodexExpansion.XAxis = ProofWiki120506CodexExpansion.imageLine := by
  ext q
  simp only [Set.mem_image, XAxis, Set.mem_setOf_eq, imageLine, onImageLine]
  constructor
  · rintro ⟨p, hp, rfl⟩
    show p.1 = p.1 + p.2
    rw [hp]; ring
  · intro hq
    refine ⟨(q.1, 0), rfl, ?_⟩
    show (q.1, q.1 + (0:ℝ)) = q
    have : q.1 + (0:ℝ) = q.2 := by rw [hq]; ring
    rw [this]

theorem repair_nonvacuous : ∃ q : ℝ × ℝ, q ∈ ProofWiki120506CodexExpansion.imageLine ∧ q ∉ ProofWiki120506CodexExpansion.Claimed := by
  refine ⟨(1, 1), ?_, ?_⟩
  · show onImageLine (1, 1)
    rfl
  · show ¬ ((1:ℝ) + 1 = 0)
    norm_num

theorem final_theorem : ProofWiki120506CodexExpansion.L '' ProofWiki120506CodexExpansion.XAxis = ProofWiki120506CodexExpansion.imageLine := repair_statement

end ProofWiki120506CodexExpansion
