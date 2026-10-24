import defs_only
/- EVALUATOR-ONLY reference correction for E09 (original package: repair, line 87, with G.Preconnected). -/
namespace SE_math_782216_q_Census.Ref

/-- Reference added hypothesis: `G` is preconnected (any two vertices are joined by a walk). -/
def guard {V : Type} [Fintype V] (G : SimpleGraph V) : Prop := G.Preconnected

theorem universal : ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], guard G → BaseClaim G := by
  intro V _ G _ hc he
  have hb : G = ⊥ := by rwa [Finset.card_eq_zero, SimpleGraph.edgeFinset_eq_empty] at he
  unfold guard at hc
  rw [hb] at hc
  have := SimpleGraph.preconnected_bot_iff_subsingleton.mp hc
  exact Fintype.card_le_one_iff_subsingleton.mpr this

end SE_math_782216_q_Census.Ref
