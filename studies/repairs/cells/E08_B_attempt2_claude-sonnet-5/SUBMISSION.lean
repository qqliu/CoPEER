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
def max_edges (p : ℕ) : ℕ := p / 2 * (p - p / 2)

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

/-- A pure arithmetic fact: `p^2` is at most one more than four times the floor of `p^2/4`
(written via `p/2 * (p - p/2)`, natural-number division). -/
theorem aux_le (p : ℕ) : p ^ 2 ≤ 4 * (p / 2 * (p - p / 2)) + 1 := by
  rcases Nat.even_or_odd p with ⟨r, hr⟩ | ⟨r, hr⟩
  · subst hr
    have e1 : (r + r) / 2 = r := by omega
    have e2 : (r + r) - r = r := by omega
    rw [e1, e2]
    nlinarith
  · subst hr
    have e1 : (2 * r + 1) / 2 = r := by omega
    have e2 : (2 * r + 1) - r = r + 1 := by omega
    rw [e1, e2]
    nlinarith

/-- For any `k, n` with `k + n = p`, there is a bipartite graph on `Fin p` with exactly `k * n`
edges (a complete bipartite graph split into parts of sizes `k` and `n`). -/
theorem exists_bip (p k n : ℕ) (h : k + n = p) :
    ∃ G : SimpleGraph (Fin p), G.IsBipartite ∧ edges G = k * n := by
  subst h
  set G' := completeBipartiteGraph (Fin k) (Fin n) with hG'
  set e : Fin (k + n) ≃ Fin k ⊕ Fin n := finSumFinEquiv.symm with he
  set G := G'.comap e.toEmbedding with hGdef
  have hiso : G ≃g G' := SimpleGraph.Iso.comap e G'
  refine ⟨G, ?_, ?_⟩
  · have hcol : G'.Colorable 2 :=
      ⟨Coloring.mk (Sum.elim (fun _ => (0 : Fin 2)) (fun _ => (1 : Fin 2)))
        (by
          rintro (a | a) (b | b) hadj <;>
            simp_all [hG', completeBipartiteGraph_adj])⟩
    exact Colorable.of_hom hiso.toHom hcol
  · have hedge : G.edgeSet.encard = G'.edgeSet.encard := ENat.card_congr hiso.mapEdgeSet
    have h1 : G'.edgeSet.encard = (k : ℕ∞) * (n : ℕ∞) := by
      rw [hG', encard_edgeSet_completeBipartiteGraph, ENat.card_eq_coe_fintype_card,
        ENat.card_eq_coe_fintype_card]
      simp
    have hfin : G.edgeSet.Finite := Set.toFinite _
    have hcast : (edges G : ℕ∞) = ((k * n : ℕ) : ℕ∞) := by
      show ((G.edgeSet.ncard : ℕ) : ℕ∞) = ((k * n : ℕ) : ℕ∞)
      rw [hfin.cast_ncard_eq, hedge, h1]
      push_cast
      ring
    exact_mod_cast hcast

/-- Upper bound: every bipartite edge count on `Fin p` is at most `max_edges p`. -/
theorem upper_bound (p : ℕ) : ∀ m ∈ BipCounts p, m ≤ max_edges p := by
  rintro m ⟨G, hG, rfl⟩
  have hb := hG.four_mul_encard_edgeSet_le
  have hcard : ENat.card (Fin p) = (p : ℕ∞) := by
    rw [ENat.card_eq_coe_fintype_card]; simp
  rw [hcard] at hb
  have hfin : G.edgeSet.Finite := Set.toFinite _
  have hcast : (4 : ℕ∞) * (edges G : ℕ∞) ≤ (p : ℕ∞) ^ 2 := by
    show (4 : ℕ∞) * ((G.edgeSet.ncard : ℕ) : ℕ∞) ≤ (p : ℕ∞) ^ 2
    rw [hfin.cast_ncard_eq]
    exact hb
  have hnat : 4 * edges G ≤ p ^ 2 := by exact_mod_cast hcast
  have haux := aux_le p
  unfold max_edges
  omega

end Census_SE_math_1868681__q
