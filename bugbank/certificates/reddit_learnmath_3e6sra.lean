import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: The same three vertices with only edge{1,2} form an actual acyclic SimpleGraph with no walk from1 to3. Mathlib acyclicity/reachability replaces enumeration of path codes.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_3e6sra
def G : SimpleGraph (Fin 3) := SimpleGraph.edge 0 1
theorem certificate : G.IsAcyclic ∧ ¬ G.Reachable 0 2 := by
  constructor
  · simpa [G] using (SimpleGraph.isAcyclic_bot (V := Fin 3)).sup_edge_of_not_reachable
      (u := 0) (v := 1) (by simp)
  · apply SimpleGraph.not_reachable_of_neighborSet_right_eq_empty (by decide)
    ext x
    fin_cases x <;> simp [G, SimpleGraph.neighborSet, SimpleGraph.edge_adj]
end Audit_reddit_learnmath_3e6sra
