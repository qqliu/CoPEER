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
def onImageLine (q : ℝ × ℝ) : Prop := q.2 = q.1

/-- The corrected image line (shape fixed). -/
def imageLine : Set (ℝ × ℝ) := {q | onImageLine q}

/-- The corrected located statement (shape fixed): the image of the x-axis under the source's map `L` is
exactly the line `imageLine` (both inclusions). -/
def CorrectedImage : Prop := L '' XAxis = imageLine
-- ===== END FIXED PART =====

theorem repair_statement : ProofWiki120506CodexExpansion.L '' ProofWiki120506CodexExpansion.XAxis = ProofWiki120506CodexExpansion.imageLine := by
  ext q
  constructor
  · rintro ⟨p, hp, rfl⟩
    have hp' : p.2 = 0 := hp
    show p.1 + p.2 = p.1
    rw [hp', add_zero]
  · intro h
    have h' : q.2 = q.1 := h
    refine ⟨(q.1, 0), (rfl : ((q.1, (0:ℝ)) : ℝ × ℝ).2 = 0), ?_⟩
    show ((q.1, q.1 + 0) : ℝ × ℝ) = q
    ext
    · rfl
    · simp [h']

theorem repair_nonvacuous : ∃ q : ℝ × ℝ, q ∈ ProofWiki120506CodexExpansion.imageLine ∧ q ∉ ProofWiki120506CodexExpansion.Claimed := by
  refine ⟨(1, 1), (rfl : ((1, 1) : ℝ × ℝ).2 = ((1, 1) : ℝ × ℝ).1), ?_⟩
  intro h
  have h' : (1 : ℝ) + 1 = 0 := h
  norm_num at h'

theorem final_theorem : ProofWiki120506CodexExpansion.L '' ProofWiki120506CodexExpansion.XAxis = ProofWiki120506CodexExpansion.imageLine :=
  repair_statement

end ProofWiki120506CodexExpansion
