import defs_only
/-!
Record E08: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Census_SE_math_1868681__q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected greatest number of edges of a bipartite simple graph on `p` labelled vertices, as a
natural-number expression in `p` (the source prints `p^2/4`, read in ℚ). The hole must be a closed
expression in `p`: no reference to `BipCounts`, `edges`, `IsGreatest`, `sSup`, `Set`, `Finset`, `SimpleGraph`;
no `if`/`match`. -/
def max_edges (p : ℕ) : ℕ := «HOLE»

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: for every `p`, `max_edges p` is attained by a bipartite graph on `Fin p` and bounds every
bipartite edge count on `Fin p`. -/
theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := sorry

/-- Non-vacuity: the corrected value differs from the printed `p^2/4` (in ℚ) for some `p`. -/
theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := sorry

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := sorry
-- ===== END OBLIGATIONS =====
end Census_SE_math_1868681__q
