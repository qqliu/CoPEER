import Mathlib.Combinatorics.SimpleGraph.Paths
import Mathlib.Tactic.NormNum
set_option autoImplicit false
namespace ProofCerts.Alg29
namespace Sol5
/-- The original isolated vertex 0 and 17 new isolated vertices. -/
def G : SimpleGraph (Fin 18) := ⊥
def added : Finset (Fin 18) := Finset.univ.erase 0
def path : G.Walk 1 1 := .nil
theorem sol5_n_path_can_hit_added_vertex :
    added.card = 17 ∧ Fintype.card (Fin 18) - 17 = 1 ∧
    path.IsPath ∧ path.support.length = 1 ∧
    (1 : Fin 18) ∈ path.support ∧ (1 : Fin 18) ∈ added ∧
    (0 : Fin 18) ∉ path.support := by
  norm_num [added,path,SimpleGraph.Walk.isPath_def]
end Sol5
end ProofCerts.Alg29
#print axioms ProofCerts.Alg29.Sol5.sol5_n_path_can_hit_added_vertex
