import Mathlib.Combinatorics.SimpleGraph.Coloring.VertexColoring
import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic

/-!
# `C_11[K_3]`: frozen 8-colouring, proper 7-colouring, and `χ = 7` (kernel-checked)

Source of the two colourings: `astra/story_20260922/LOWER_PALETTE_EXPLORATION.md`
(22 September 2026).  Nothing else from that file is used.

* Graph (Section 1, lines 9-15 of the source, and the task statement): vertex set
  `Fin 11 × Fin 3`; `(i,a) ~ (j,b)` iff `i = j ∧ a ≠ b` (same bag) or `j = i ± 1 (mod 11)`
  (adjacent bags, any labels).  In `Fin 11`, `+ 1` is addition modulo 11, so `j = i + 1`
  or `i = j + 1` is exactly "adjacent bags", including the closing edge `10 ~ 0`.
* Frozen 8-colouring `c8` (Section 2): the bag palettes copied verbatim from lines 39-40,
      {0,1,2}, {3,4,5}, {0,6,7}, {1,2,3}, {0,4,5}, {1,6,7},
      {0,2,3}, {4,5,6}, {0,1,7}, {2,3,4}, {5,6,7}.
  Line 43: "Assign each displayed palette in increasing order to the three labeled vertices
  of its bag."  So `c8 (i, a)` is the `a`-th smallest element of palette `i`.
* Proper 7-colouring `c7` (Section 3): the bag palettes copied verbatim from lines 50-51,
      {1,2,3}, {4,5,6}, {1,2,3}, {4,5,6}, {0,1,2}, {3,4,5},
      {0,1,6}, {2,3,4}, {0,5,6}, {1,2,3}, {4,5,6},
  assigned the same way (increasing order within each bag).

What is proved (every proof is checked by the Lean kernel; no native evaluation, no
unfinished proofs; `#print axioms` at the end of the file lists the axioms):
1. `proper8`  : `c8` is a proper colouring.
2. `frozen8`  : every vertex `v` and every colour `col ≠ c8 v` has a neighbour `u` of `v`
                with `c8 u = col`  (closed neighbourhood sees all 8 colours);
   `frozen8_noSingleRecolour` : consequently no proper 8-colouring differs from `c8` at
                exactly one vertex (the reconfiguration-graph form of "frozen").
3. `proper7`  : `c7` is a proper colouring.
4. `chromatic_ge_7` : `∀ c : Fin 11 × Fin 3 → Fin 6, ¬ Proper c`.
   Proof: a colour class is independent; an independent set meets each bag at most once
   (`adj_of_same_bag`) and its set of bags is independent in `C_11` (`adj_of_next`), which
   has at most 5 elements (`cycle11_indep_card_le`, a counting argument: `T` and `T + 1`
   are disjoint subsets of `Fin 11`, so `2 |T| ≤ 11`).  Hence each class has `≤ 5`
   vertices and six classes cover `≤ 30 < 33` vertices.
5. Mathlib form: `G : SimpleGraph (Fin 11 × Fin 3)` with `G.Adj u v ↔ adj u v = true`;
   `colorable7 : G.Colorable 7`, `not_colorable6 : ¬ G.Colorable 6`,
   `chromaticNumber_eq_7 : G.chromaticNumber = 7`.

Finite checks are Boolean computations over the explicit vertex list `verts` (33 vertices)
and `List.finRange k`, discharged by `decide` (kernel evaluation), with soundness lemmas
`properB_sound` / `seesB_sound` relating them to the `Prop`-level definitions.
-/

set_option linter.unusedSectionVars false

namespace C11K3

/-- Vertex set: bag `i : Fin 11`, label `a : Fin 3`. -/
abbrev V : Type := Fin 11 × Fin 3

/-- Boolean adjacency of `C_11[K_3]`: same bag and different label, or adjacent bags
(`j = i + 1` or `i = j + 1` in `Fin 11`, i.e. modulo 11). -/
def adj (u v : V) : Bool :=
  (u.1 == v.1 && u.2 != v.2) || (v.1 == u.1 + 1) || (u.1 == v.1 + 1)

/-- A proper colouring with colours `Fin k`: adjacent vertices receive different colours. -/
def Proper {k : ℕ} (c : V → Fin k) : Prop :=
  ∀ u v, adj u v = true → c u ≠ c v

/-- Frozen, closed-neighbourhood form: every colour other than `c v` occurs on a
neighbour of `v`. -/
def Sees {k : ℕ} (c : V → Fin k) : Prop :=
  ∀ v : V, ∀ col : Fin k, col ≠ c v → ∃ u, adj v u = true ∧ c u = col

/-- Frozen, reconfiguration form: a proper colouring `g` that agrees with `c` off `v`
also agrees with `c` at `v`; i.e. no single-vertex recolouring of `c` is proper. -/
def NoSingleRecolour {k : ℕ} (c : V → Fin k) : Prop :=
  ∀ g : V → Fin k, Proper g → ∀ v, (∀ u, u ≠ v → g u = c u) → g v = c v

/-! ## Finite Boolean checks and their soundness -/

/-- The list of all 33 vertices. -/
def verts : List V :=
  (List.finRange 11).flatMap fun i => (List.finRange 3).map fun a => (i, a)

/-- Boolean properness check over `verts × verts`. -/
def properB {k : ℕ} (c : V → Fin k) : Bool :=
  verts.all fun u => verts.all fun v => !(adj u v) || (c u != c v)

/-- Boolean "sees every other colour" check over `verts × Fin k × verts`. -/
def seesB {k : ℕ} (c : V → Fin k) : Bool :=
  verts.all fun v => (List.finRange k).all fun col =>
    (col == c v) || verts.any fun u => adj v u && (c u == col)

theorem mem_verts (v : V) : v ∈ verts := by
  obtain ⟨i, a⟩ := v
  simp [verts, List.mem_flatMap, List.mem_map, List.mem_finRange]

theorem properB_sound {k : ℕ} (c : V → Fin k) (h : properB c = true) : Proper c := by
  intro u v hadj heq
  simp only [properB, List.all_eq_true] at h
  have := h u (mem_verts u) v (mem_verts v)
  simp [hadj, heq] at this

theorem seesB_sound {k : ℕ} (c : V → Fin k) (h : seesB c = true) : Sees c := by
  intro v col hne
  simp only [seesB, List.all_eq_true] at h
  have := h v (mem_verts v) col (List.mem_finRange col)
  simp only [Bool.or_eq_true, beq_iff_eq, List.any_eq_true, Bool.and_eq_true] at this
  rcases this with h1 | ⟨u, _, hu1, hu2⟩
  · exact absurd h1 hne
  · exact ⟨u, hu1, hu2⟩

/-! ## The two colourings, verbatim from LOWER_PALETTE_EXPLORATION.md -/

/-- Bag palettes of the frozen 8-colouring, source lines 39-40, bag order `i = 0,…,10`,
each palette listed in increasing order (source line 43). -/
def pal8 : Fin 11 → Fin 3 → Fin 8 :=
  ![![0, 1, 2], ![3, 4, 5], ![0, 6, 7], ![1, 2, 3], ![0, 4, 5], ![1, 6, 7],
    ![0, 2, 3], ![4, 5, 6], ![0, 1, 7], ![2, 3, 4], ![5, 6, 7]]

/-- The frozen 8-colouring: `c8 (i, a)` is the `a`-th smallest colour of palette `i`. -/
def c8 (v : V) : Fin 8 := pal8 v.1 v.2

/-- Bag palettes of the proper 7-colouring, source lines 50-51, bag order `i = 0,…,10`. -/
def pal7 : Fin 11 → Fin 3 → Fin 7 :=
  ![![1, 2, 3], ![4, 5, 6], ![1, 2, 3], ![4, 5, 6], ![0, 1, 2], ![3, 4, 5],
    ![0, 1, 6], ![2, 3, 4], ![0, 5, 6], ![1, 2, 3], ![4, 5, 6]]

/-- The proper 7-colouring. -/
def c7 (v : V) : Fin 7 := pal7 v.1 v.2

/-! ## 1-3: properness and frozenness, by kernel evaluation -/

theorem proper8 : Proper c8 := properB_sound c8 (by decide)

theorem frozen8 : Sees c8 := seesB_sound c8 (by decide)

theorem proper7 : Proper c7 := properB_sound c7 (by decide)

theorem adj_irrefl : ∀ v : V, adj v v = false := by decide

theorem adj_symm : ∀ u v : V, adj u v = adj v u := by decide

/-- From the closed-neighbourhood form to the reconfiguration form (generic argument). -/
theorem noSingleRecolour_of_sees {k : ℕ} (c : V → Fin k) (hs : Sees c) :
    NoSingleRecolour c := by
  intro g hg v hagree
  by_contra hne
  obtain ⟨u, hadj, hcu⟩ := hs v (g v) hne
  have huv : u ≠ v := by
    rintro rfl
    rw [adj_irrefl] at hadj
    exact Bool.false_ne_true hadj
  exact hg v u hadj (by rw [hagree u huv, hcu])

theorem frozen8_noSingleRecolour : NoSingleRecolour c8 :=
  noSingleRecolour_of_sees c8 frozen8

/-! ## 4: no proper 6-colouring -/

theorem adj_of_same_bag {u v : V} (h1 : u.1 = v.1) (h2 : u ≠ v) : adj u v = true := by
  have h3 : u.2 ≠ v.2 := fun h => h2 (Prod.ext h1 h)
  simp [adj, h1, h3]

theorem adj_of_next {u v : V} (h : v.1 = u.1 + 1) : adj u v = true := by
  simp [adj, h]

/-- An independent set of the 11-cycle (no `i` with `i + 1` both present) has at most 5
elements: `T` and `T + 1` are disjoint subsets of `Fin 11`, so `2 |T| ≤ 11`. -/
theorem cycle11_indep_card_le (T : Finset (Fin 11)) (h : ∀ i ∈ T, i + 1 ∉ T) :
    T.card ≤ 5 := by
  have hdisj : Disjoint T (T.image (· + 1)) := by
    rw [Finset.disjoint_left]
    intro i hi hi'
    obtain ⟨j, hj, hji⟩ := Finset.mem_image.mp hi'
    exact h j hj (hji ▸ hi)
  have himg : (T.image (· + 1)).card = T.card :=
    Finset.card_image_of_injective _ (add_left_injective (1 : Fin 11))
  have hle : (T ∪ T.image (· + 1)).card ≤ 11 := by
    have := Finset.card_le_univ (T ∪ T.image (· + 1))
    simpa using this
  rw [Finset.card_union_of_disjoint hdisj, himg] at hle
  omega

/-- Each colour class of a proper colouring has at most 5 vertices. -/
theorem colourClass_card_le {k : ℕ} (c : V → Fin k) (hc : Proper c) (col : Fin k) :
    (Finset.univ.filter fun v : V => c v = col).card ≤ 5 := by
  set S := Finset.univ.filter fun v : V => c v = col with hS
  have hmem : ∀ v, v ∈ S ↔ c v = col := by intro v; simp [hS]
  have hinj : Set.InjOn Prod.fst (S : Set V) := by
    intro u hu v hv huv
    by_contra hne
    exact hc u v (adj_of_same_bag huv hne)
      (((hmem u).1 (Finset.mem_coe.1 hu)).trans ((hmem v).1 (Finset.mem_coe.1 hv)).symm)
  rw [← Finset.card_image_of_injOn hinj]
  apply cycle11_indep_card_le
  intro i hi hi1
  obtain ⟨u, hu, rfl⟩ := Finset.mem_image.mp hi
  obtain ⟨w, hw, hw1⟩ := Finset.mem_image.mp hi1
  exact hc u w (adj_of_next hw1) (((hmem u).1 hu).trans ((hmem w).1 hw).symm)

/-- `C_11[K_3]` has no proper colouring with 6 colours. -/
theorem chromatic_ge_7 : ∀ c : Fin 11 × Fin 3 → Fin 6, ¬ Proper c := by
  intro c hc
  have h33 : (Finset.univ : Finset V).card = 33 := by simp
  have hsum : (Finset.univ : Finset V).card =
      ∑ col : Fin 6, (Finset.univ.filter fun v : V => c v = col).card :=
    Finset.card_eq_sum_card_fiberwise (fun x _ => Finset.mem_univ (c x))
  have hle : ∑ col : Fin 6, (Finset.univ.filter fun v : V => c v = col).card
      ≤ ∑ _col : Fin 6, 5 :=
    Finset.sum_le_sum fun col _ => colourClass_card_le c hc col
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul] at hle
  omega

/-! ## 5: Mathlib `SimpleGraph` form and `χ = 7` -/

/-- `C_11[K_3]` as a Mathlib simple graph. -/
def G : SimpleGraph V where
  Adj u v := adj u v = true
  symm := fun u v (h : adj u v = true) => by
    show adj v u = true
    rw [adj_symm]; exact h
  loopless := ⟨fun v (h : adj v v = true) => by
    rw [adj_irrefl] at h; exact Bool.false_ne_true h⟩

theorem G_adj (u v : V) : G.Adj u v ↔ adj u v = true := Iff.rfl

/-- Every `Proper` colouring is a Mathlib colouring and conversely. -/
theorem proper_iff_coloring {k : ℕ} (c : V → Fin k) :
    Proper c ↔ ∀ {u v}, G.Adj u v → c u ≠ c v :=
  ⟨fun h _ _ hadj => h _ _ hadj, fun h u v hadj => @h u v hadj⟩

theorem colorable7 : G.Colorable 7 :=
  ⟨SimpleGraph.Coloring.mk c7 fun h => proper7 _ _ h⟩

theorem not_colorable6 : ¬ G.Colorable 6 :=
  fun ⟨C⟩ => chromatic_ge_7 C fun _ _ h => C.valid h

theorem chromaticNumber_eq_7 : G.chromaticNumber = 7 := by
  have := SimpleGraph.chromaticNumber_eq_iff_colorable_not_colorable.mpr
    ⟨colorable7, not_colorable6⟩
  simpa using this

end C11K3

#print axioms C11K3.proper8
#print axioms C11K3.frozen8
#print axioms C11K3.frozen8_noSingleRecolour
#print axioms C11K3.proper7
#print axioms C11K3.chromatic_ge_7
#print axioms C11K3.cycle11_indep_card_le
#print axioms C11K3.colourClass_card_le
#print axioms C11K3.colorable7
#print axioms C11K3.not_colorable6
#print axioms C11K3.chromaticNumber_eq_7
