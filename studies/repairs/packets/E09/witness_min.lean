import defs_only
/- Record SE_math_782216__q (E09): the base-case sentence fails at the edgeless graph on two
vertices (0 edges, 2 vertices). -/
namespace SE_math_782216_q_Census

theorem bot_two_no_edges : (⊥ : SimpleGraph (Fin 2)).edgeFinset.card = 0 := by simp

theorem two_vertices : ¬ Fintype.card (Fin 2) ≤ 1 := by decide

theorem base_claim_fails_on_bot_two : ¬ BaseClaim (⊥ : SimpleGraph (Fin 2)) :=
  fun h => two_vertices (h bot_two_no_edges)

theorem universal_base_claim_false : ¬ UniversalBaseClaim :=
  fun h => base_claim_fails_on_bot_two (h (Fin 2) ⊥)

end SE_math_782216_q_Census

#print axioms SE_math_782216_q_Census.base_claim_fails_on_bot_two
#print axioms SE_math_782216_q_Census.universal_base_claim_false
