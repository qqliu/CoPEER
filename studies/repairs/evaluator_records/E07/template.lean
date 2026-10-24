import defs_only
/-!
Record E07: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Census_SE_math_1291495__q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected edge count of the spanning tree `G'` on `k + 1` vertices, as an integer expression in
`k` (the source prints `k - 1`). Only this count may be changed; by the template `SentenceWith` the
companion count of `G` is `edge_count k + m`. The hole must be a closed expression in `k`. -/
def edge_count (k : ℕ) : ℤ := «HOLE»

/-- The corrected sentence for every `k ≥ 2`, the range on which the source's hypotheses can be met
(shape fixed). -/
def CorrectedSentence : Prop := ∀ k : ℕ, 2 ≤ k → SentenceWith k (edge_count k)
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected sentence holds for every `k ≥ 2`, every finite vertex type with `k + 1`
elements, every connected `G` with a cycle and every spanning tree `G'` of `G`. -/
theorem repair_statement : ∀ k : ℕ, 2 ≤ k → Census_SE_math_1291495__q.SentenceWith k (Census_SE_math_1291495__q.edge_count k) := sorry

/-- Non-vacuity: the corrected count differs from the printed `k - 1` for some admissible `k`, and the
hypotheses of the sentence are satisfiable for some `k ≥ 2`. -/
theorem repair_nonvacuous : (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧ (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := sorry

/-- The theorem the source sets out to prove, unchanged (`SourceTheorem` from defs_only: a connected
graph on `k + 1` vertices with `k` edges is a tree). If you cannot prove it, replace this declaration
(this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := sorry
-- ===== END OBLIGATIONS =====
end Census_SE_math_1291495__q
