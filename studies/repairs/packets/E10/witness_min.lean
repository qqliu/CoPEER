import defs_only
/- Record SE_math_994847__q (E10): both readings of the located claim fail at the path
0 - 1 - 2 on three vertices, whose adjacency matrix A has (A^2)_{0,1} = 0 although the
graph is connected. -/
namespace SE_math_994847_q
open Matrix

def A : Matrix (Fin 3) (Fin 3) ℕ := !![0,1,0; 1,0,1; 0,1,0]

def sourceGraph : SimpleGraph (Fin 3) where
 Adj i j := i ≠ j ∧ (i = 1 ∨ j = 1)
 symm := fun i j h => ⟨h.1.symm, h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance : DecidableRel sourceGraph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

theorem sourceGraph_connected : sourceGraph.Connected := by decide

theorem sourceGraph_adjMatrix : sourceGraph.adjMatrix ℕ = A := by
  funext i j
  fin_cases i <;> fin_cases j <;> decide

theorem square_entry_zero :
    (sourceGraph.adjMatrix ℕ ^ (Fintype.card (Fin 3) - 1)) 0 1 = 0 := by
  rw [Fintype.card_fin]
  decide +kernel

theorem sourceGraph_has_zero_entry : HasZeroEntry sourceGraph := ⟨0, 1, square_entry_zero⟩

theorem local_claim_fails : ¬ LocalClaim sourceGraph :=
  fun h => h sourceGraph_has_zero_entry sourceGraph_connected

theorem entrywise_claim_fails : ¬ LocalClaimEntrywise sourceGraph :=
  fun h => h 0 1 square_entry_zero (sourceGraph_connected.preconnected 0 1)

theorem universal_local_claim_false : ¬ UniversalLocalClaim :=
  fun h => local_claim_fails (h (Fin 3) sourceGraph)

theorem universal_entrywise_claim_false : ¬ UniversalLocalClaimEntrywise :=
  fun h => entrywise_claim_fails (h (Fin 3) sourceGraph)

end SE_math_994847_q

#print axioms SE_math_994847_q.square_entry_zero
#print axioms SE_math_994847_q.universal_local_claim_false
#print axioms SE_math_994847_q.universal_entrywise_claim_false
