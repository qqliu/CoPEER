import defs_only
/-!
Record E16: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace ProofWiki120506CodexExpansion

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
def onImageLine (q : ℝ × ℝ) : Prop := q.1 = q.2

def imageLine : Set (ℝ × ℝ) := {q | onImageLine q}

def CorrectedImage : Prop := L '' XAxis = imageLine
-- ===== END FIXED PART =====

theorem repair_statement : ProofWiki120506CodexExpansion.L '' ProofWiki120506CodexExpansion.XAxis = ProofWiki120506CodexExpansion.imageLine :=
by
  exact Set.Subset.antisymm
    (fun q hq =>
      by
        rcases hq with ⟨p, hp, rfl⟩
        dsimp [imageLine, onImageLine, L] at *
        simpa [hp])
    (fun q hq =>
      by
        rcases q with ⟨x, y⟩
        have hxy : x = y := hq
        refine ⟨(x, 0), ?_, ?_⟩
        · dsimp [XAxis]; simp
        · dsimp [L]; simpa [hxy])

theorem repair_nonvacuous : ∃ q : ℝ × ℝ, q ∈ ProofWiki120506CodexExpansion.imageLine ∧ q ∉ ProofWiki120506CodexExpansion.Claimed :=
by
  refine ⟨(1, 1), ?_, ?_⟩
  · dsimp [ProofWiki120506CodexExpansion.imageLine, ProofWiki120506CodexExpansion.onImageLine]
    simp
  · intro h
    have : (1 : ℝ) + 1 = 0 := by
      simpa [ProofWiki120506CodexExpansion.Claimed] using h
    linarith

-- CANNOT: final theorem proof not completed
