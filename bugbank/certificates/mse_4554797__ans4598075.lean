import Mathlib.Analysis.Convex.Segment
import Mathlib.Combinatorics.SimpleGraph.Finite
import Mathlib.Tactic

set_option maxHeartbeats 8000000
set_option maxRecDepth 10000

namespace MSE4554797ans4598075

/-- Vertices of the three K4 blocks, with shared vertices 3 and 6.
Coordinates are points of the real plane, not a finite sample. -/
def pathPositions (v : Fin 10) : ℝ × ℝ :=
  match v.val with
  | 0 => (0, 0)
  | 1 => (0, 3)
  | 2 => (1, 1)
  | 3 => (3, 0)
  | 4 => (3, 3)
  | 5 => (4, 1)
  | 6 => (6, 0)
  | 7 => (6, 3)
  | 8 => (7, 1)
  | _ => (9, 0)

def pathEndpoints (e : Fin 18) : Fin 10 × Fin 10 :=
  match e.val with
  | 0 => (0, 1)
  | 1 => (0, 2)
  | 2 => (0, 3)
  | 3 => (1, 2)
  | 4 => (1, 3)
  | 5 => (2, 3)
  | 6 => (3, 4)
  | 7 => (3, 5)
  | 8 => (3, 6)
  | 9 => (4, 5)
  | 10 => (4, 6)
  | 11 => (5, 6)
  | 12 => (6, 7)
  | 13 => (6, 8)
  | 14 => (6, 9)
  | 15 => (7, 8)
  | 16 => (7, 9)
  | _ => (8, 9)

noncomputable def pathEdgePoint (e : Fin 18) (t : ℝ) : ℝ × ℝ :=
  (1-t) • pathPositions (pathEndpoints e).1 + t • pathPositions (pathEndpoints e).2

theorem path_positions_injective : Function.Injective pathPositions := by
  intro u v h
  fin_cases u <;> fin_cases v <;> first | rfl | norm_num [pathPositions] at h

theorem path_edge_interiors_avoid_vertices
    (e : Fin 18) (v : Fin 10) (t : ℝ) (ht : 0 < t) (ht1 : t < 1) :
    pathEdgePoint e t ≠ pathPositions v := by
  intro h
  have hx := congrArg Prod.fst h
  have hy := congrArg Prod.snd h
  fin_cases e <;> fin_cases v
  all_goals try norm_num [pathEdgePoint, pathPositions, pathEndpoints, Prod.smul_mk, smul_eq_mul] at hx
  all_goals try norm_num [pathEdgePoint, pathPositions, pathEndpoints, Prod.smul_mk, smul_eq_mul] at hy
  all_goals linarith

theorem path_edge_interiors_do_not_cross
    (e f : Fin 18) (hne : e ≠ f) (t u : ℝ)
    (ht : 0 < t) (ht1 : t < 1) (hu : 0 < u) (hu1 : u < 1) :
    pathEdgePoint e t ≠ pathEdgePoint f u := by
  intro h
  have hx := congrArg Prod.fst h
  have hy := congrArg Prod.snd h
  fin_cases e <;> fin_cases f
  all_goals try norm_num at hne
  all_goals try norm_num [pathEdgePoint, pathPositions, pathEndpoints, Prod.smul_mk, smul_eq_mul] at hx
  all_goals try norm_num [pathEdgePoint, pathPositions, pathEndpoints, Prod.smul_mk, smul_eq_mul] at hy
  all_goals linarith

/-- Actual Mathlib open segments contain no vertex of the drawing. -/
theorem path_open_segments_avoid_vertices (e : Fin 18) (v : Fin 10) :
    pathPositions v ∉ openSegment ℝ (pathPositions (pathEndpoints e).1)
      (pathPositions (pathEndpoints e).2) := by
  rw [openSegment_eq_image]
  rintro ⟨t, ht, he⟩
  exact path_edge_interiors_avoid_vertices e v t ht.1 ht.2 he

/-- Distinct drawn edges have disjoint interiors in the real plane. -/
theorem path_open_segments_disjoint (e f : Fin 18) (hne : e ≠ f) :
    Disjoint
      (openSegment ℝ (pathPositions (pathEndpoints e).1) (pathPositions (pathEndpoints e).2))
      (openSegment ℝ (pathPositions (pathEndpoints f).1) (pathPositions (pathEndpoints f).2)) := by
  rw [Set.disjoint_left]
  intro p hp hq
  rw [openSegment_eq_image] at hp hq
  rcases hp with ⟨t, ht, he⟩
  rcases hq with ⟨u, hu, hf⟩
  exact path_edge_interiors_do_not_cross e f hne t u ht.1 ht.2 hu.1 hu.2 (he.trans hf.symm)

def pathGraph : SimpleGraph (Fin 10) where
  Adj x y := x ≠ y ∧ ((x ≤ 3 ∧ y ≤ 3) ∨
    (3 ≤ x ∧ x ≤ 6 ∧ 3 ≤ y ∧ y ≤ 6) ∨ (6 ≤ x ∧ 6 ≤ y))
  symm := by intro x y h; tauto
  loopless := ⟨by simp⟩
instance : DecidableRel pathGraph.Adj := fun x y => inferInstanceAs (Decidable
  (x ≠ y ∧ ((x ≤ 3 ∧ y ≤ 3) ∨ (3 ≤ x ∧ x ≤ 6 ∧ 3 ≤ y ∧ y ≤ 6) ∨ (6 ≤ x ∧ 6 ≤ y))))

def starGraph : SimpleGraph (Fin 10) where
  Adj x y := x ≠ y ∧ (x = 0 ∨ y = 0 ∨
    (x ≤ 3 ∧ y ≤ 3) ∨ (4 ≤ x ∧ x ≤ 6 ∧ 4 ≤ y ∧ y ≤ 6) ∨ (7 ≤ x ∧ 7 ≤ y))
  symm := by intro x y h; tauto
  loopless := ⟨by simp⟩
instance : DecidableRel starGraph.Adj := fun x y => inferInstanceAs (Decidable
  (x ≠ y ∧ (x = 0 ∨ y = 0 ∨ (x ≤ 3 ∧ y ≤ 3) ∨
    (4 ≤ x ∧ x ≤ 6 ∧ 4 ≤ y ∧ y ≤ 6) ∨ (7 ≤ x ∧ 7 ≤ y))))

theorem drawn_edges_are_exact : ∀ x y : Fin 10,
    pathGraph.Adj x y ↔ ∃ e : Fin 18,
      (pathEndpoints e = (x,y) ∨ pathEndpoints e = (y,x)) := by decide

def ContainsC5 (G : SimpleGraph (Fin 10)) : Prop :=
  ∃ f : Fin 5 → Fin 10, Function.Injective f ∧ ∀ i : Fin 5, G.Adj (f i) (f (i+1))

instance (G : SimpleGraph (Fin 10)) [DecidableRel G.Adj] : Decidable (ContainsC5 G) :=
  inferInstanceAs (Decidable (∃ f : Fin 5 → Fin 10, Function.Injective f ∧
    ∀ i : Fin 5, G.Adj (f i) (f (i+1))))

/-- Enumerate adjacent vertices before testing distinctness. This is the exact
finite C5 predicate, with a short-circuit order that avoids enumerating function
extensionality proofs for all 100,000 maps. Kernel reduction only. -/
theorem no_five_distinct_adjacent : ∀ a b c d e : Fin 10,
    pathGraph.Adj a b → pathGraph.Adj b c → pathGraph.Adj c d →
    pathGraph.Adj d e → pathGraph.Adj e a → ¬ [a,b,c,d,e].Nodup := by
  decide +kernel

theorem path_has_no_C5 : ¬ ContainsC5 pathGraph := by
  rintro ⟨f, hf, he⟩
  have hn : [f 0,f 1,f 2,f 3,f 4].Nodup :=
    (by decide : ([0,1,2,3,4] : List (Fin 5)).Nodup).map hf
  exact no_five_distinct_adjacent (f 0) (f 1) (f 2) (f 3) (f 4)
    (he 0) (he 1) (he 2) (he 3) (he 4) hn

theorem not_isomorphic : ¬ Nonempty (starGraph ≃g pathGraph) := by
  rintro ⟨f⟩
  have hs : starGraph.degree 0 = 9 := by decide
  have hp : ∀ v : Fin 10, pathGraph.degree v ≤ 6 := by decide
  have hf := f.degree_eq 0
  have hb := hp (f 0)
  omega

theorem certificate :
    pathGraph.edgeFinset.card = 18 ∧ ¬ ContainsC5 pathGraph ∧
    ¬ Nonempty (starGraph ≃g pathGraph) ∧
    Function.Injective pathPositions ∧
    (∀ e : Fin 18, ∀ v : Fin 10, pathPositions v ∉
      openSegment ℝ (pathPositions (pathEndpoints e).1) (pathPositions (pathEndpoints e).2)) ∧
    (∀ e f : Fin 18, e ≠ f → Disjoint
      (openSegment ℝ (pathPositions (pathEndpoints e).1) (pathPositions (pathEndpoints e).2))
      (openSegment ℝ (pathPositions (pathEndpoints f).1) (pathPositions (pathEndpoints f).2))) :=
  ⟨by decide,path_has_no_C5,not_isomorphic,path_positions_injective,
    path_open_segments_avoid_vertices,path_open_segments_disjoint⟩

end MSE4554797ans4598075
