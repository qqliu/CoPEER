/-!
# Prime clique blowups: Conjecture 1 of "Recoloring via modular decomposition" is false

Source: M. Belavadi, K. Cameron, N. L. D. Sintiari, "Recoloring via modular decomposition",
arXiv:2405.06446v2 (14 Nov 2024), Section 6, Conjecture 1; version of record
J. Graph Theory 111(4) (2026) 113-123.

  "Conjecture 1. Let G be a prime graph. Every blowup of G is recolorable if and only if
   every induced subgraph of G is recolorable."

This file defines, in core Lean (no Mathlib), finite simple graphs, proper `k`-colourings,
the reconfiguration graph `R_k`, `k`-mixing, the chromatic number, recolorability
(`R_l` connected for ALL `l ≥ χ + 1`), modules, prime graphs, clique blowups and induced
subgraphs; states the conjecture as the general proposition `Conjecture1`; and proves
`not_conjecture1 : ¬ Conjecture1`.

Witness: `G = C_9`.
* `c9_prime`: `C_9` has no non-trivial module (kernel evaluation over all 512 subsets).
* `c9_induced_recolorable`: every induced subgraph of `C_9` (all 512 vertex subsets, the
  empty one and `C_9` itself included) is recolorable. The infinite range of `l` is handled
  by a general degeneracy lemma proved here (`mix_rel`, `recolorable_induce`): a graph with
  an elimination order of width `d` is `l`-mixing for every `l ≥ d + 2`. The elimination
  orders are found and checked by kernel evaluation (`c9_elim`); the chromatic lower bounds
  that turn `l ≥ χ + 1` into `l ≥ d + 2` are proved in `c9_chi`.
* `H_not_recolorable`: the blowup `H = C_9[K_2]` (every vertex replaced by a 2-clique) has
  `χ(H) = 5` (`H_isChi5`: an explicit proper 5-colouring, and no proper 4-colouring) and a
  frozen proper 6-colouring (periodic palettes `{0,1},{2,3},{4,5}`), so `R_6(H)` is
  disconnected although `6 = χ(H) + 1`.

Only the direction "every induced subgraph recolorable ⟹ every blowup recolorable" is
refuted; the converse direction is not addressed. `not_conjecture1Connected` refutes the
narrower reading in which `G` is also required to be connected.

No proof holes, no compiler-trusted evaluation, no added axioms: every headline theorem
depends on `propext` and `Quot.sound` only (see the `#print axioms` lines at the end).
Outside the frozen 285-record release.
-/

set_option maxRecDepth 100000
set_option linter.unusedSectionVars false
set_option linter.deprecated false

namespace Recol

/-! ## General definitions (finite simple graphs, colourings, reconfiguration graph) -/

/-- A simple graph on a vertex type `V`: symmetric irreflexive Boolean adjacency. -/
structure SGraph (V : Type) where
  adj : V → V → Bool
  symm : ∀ a b, adj a b = adj b a
  irrefl : ∀ a, adj a a = false

variable {V : Type}

/-- A proper `k`-colouring: adjacent vertices receive different colours
(the source's colour set `{1,...,k}` is `Fin k` here). -/
def Proper (G : SGraph V) {k : Nat} (f : V → Fin k) : Prop :=
  ∀ a b, G.adj a b = true → f a ≠ f b

def Colourable (G : SGraph V) (k : Nat) : Prop := ∃ f : V → Fin k, Proper G f

/-- `c` is the chromatic number: `c`-colourable and not `k`-colourable for any `k < c`. -/
def IsChi (G : SGraph V) (c : Nat) : Prop :=
  Colourable G c ∧ ∀ k, k < c → ¬ Colourable G k

/-- Adjacency in the reconfiguration graph: the colourings differ on exactly one vertex. -/
def RAdj {k : Nat} (f g : V → Fin k) : Prop :=
  ∃ v, f v ≠ g v ∧ ∀ w, w ≠ v → f w = g w

/-- A walk in `R_k(G)`: every colouring visited after the first is a proper colouring. -/
inductive Path (G : SGraph V) {k : Nat} : (V → Fin k) → (V → Fin k) → Prop
  | refl (f : V → Fin k) : Path G f f
  | step {f m g : V → Fin k} : Proper G m → RAdj f m → Path G m g → Path G f g

/-- `G` is `k`-mixing: `R_k(G)` is connected. -/
def Mixing (G : SGraph V) (k : Nat) : Prop :=
  ∀ f g : V → Fin k, Proper G f → Proper G g → Path G f g

/-- `G` is recolorable: `R_l(G)` is connected for all `l ≥ χ(G) + 1`. -/
def Recolorable (G : SGraph V) : Prop :=
  ∀ c, IsChi G c → ∀ l, c + 1 ≤ l → Mixing G l

/-! ## Modules, prime graphs, blowups, induced subgraphs -/

/-- `S` is a module: non-empty, and every outside vertex is complete or anticomplete to it. -/
def IsModule (G : SGraph V) (S : V → Bool) : Prop :=
  (∃ v, S v = true) ∧
  ∀ x, S x = false →
    (∀ s, S s = true → G.adj x s = true) ∨ (∀ s, S s = true → G.adj x s = false)

/-- A non-trivial module: a module that is a proper subset with at least two vertices. -/
def NontrivialModule (G : SGraph V) (S : V → Bool) : Prop :=
  IsModule G S ∧ (∃ a b, a ≠ b ∧ S a = true ∧ S b = true) ∧ (∃ x, S x = false)

def Prime (G : SGraph V) : Prop := ¬ ∃ S : V → Bool, NontrivialModule G S

/-- The blowup of `G` in which vertex `v` is replaced by a clique on `m v` vertices. -/
def blowup [DecidableEq V] (G : SGraph V) (m : V → Nat) : SGraph (Σ v : V, Fin (m v)) where
  adj x y := if x.1 = y.1 then decide (x.2.val ≠ y.2.val) else G.adj x.1 y.1
  symm x y := by
    by_cases h : x.1 = y.1
    · rw [if_pos h, if_pos h.symm]
      exact decide_eq_decide.2 ⟨fun q r => q r.symm, fun q r => q r.symm⟩
    · rw [if_neg h, if_neg (fun q => h q.symm)]
      exact G.symm _ _
  irrefl x := by simp

/-- The subgraph of `G` induced by the vertex set `S`. -/
def induce (G : SGraph V) (S : V → Bool) : SGraph {v : V // S v = true} where
  adj x y := G.adj x.1 y.1
  symm _ _ := G.symm _ _
  irrefl _ := G.irrefl _

/-- Conjecture 1 of the source, for finite simple graphs (vertex set `Fin n`). -/
def Conjecture1 : Prop :=
  ∀ (n : Nat) (G : SGraph (Fin n)), Prime G →
    ((∀ m : Fin n → Nat, (∀ v, 1 ≤ m v) → Recolorable (blowup G m)) ↔
     (∀ S : Fin n → Bool, Recolorable (induce G S)))

/-- Walks in a graph, and connectedness (the source assumes its graphs connected "unless
stated otherwise"). -/
inductive Walk (G : SGraph V) : V → V → Prop
  | refl (a : V) : Walk G a a
  | step {a m b : V} : G.adj a m = true → Walk G m b → Walk G a b

def GConnected (G : SGraph V) : Prop := ∀ a b, Walk G a b

/-- Conjecture 1 restricted to connected prime graphs (the narrower reading). -/
def Conjecture1Connected : Prop :=
  ∀ (n : Nat) (G : SGraph (Fin n)), GConnected G → Prime G →
    ((∀ m : Fin n → Nat, (∀ v, 1 ≤ m v) → Recolorable (blowup G m)) ↔
     (∀ S : Fin n → Bool, Recolorable (induce G S)))

/-! ## Small general lemmas -/

theorem colourable_mono (G : SGraph V) {k k' : Nat} (h : k ≤ k') :
    Colourable G k → Colourable G k' := by
  intro ⟨f, hf⟩
  refine ⟨fun a => ⟨(f a).val, Nat.lt_of_lt_of_le (f a).isLt h⟩, ?_⟩
  intro a b hab e
  apply hf a b hab
  apply Fin.ext
  have e' := congrArg Fin.val e
  exact e'

theorem exists_isChi_aux (G : SGraph V) :
    ∀ n k, k ≤ n → Colourable G k → ∃ c, c ≤ k ∧ IsChi G c := by
  intro n
  induction n with
  | zero =>
    intro k hk hc
    refine ⟨k, Nat.le_refl _, hc, ?_⟩
    intro j hj
    omega
  | succ n ih =>
    intro k hk hc
    by_cases h : ∃ j, j < k ∧ Colourable G j
    · obtain ⟨j, hj, hcj⟩ := h
      obtain ⟨c, hc1, hc2⟩ := ih j (by omega) hcj
      exact ⟨c, by omega, hc2⟩
    · exact ⟨k, Nat.le_refl _, hc, fun j hj hcj => h ⟨j, hj, hcj⟩⟩

/-- A colourable graph has a chromatic number, and it is at most any colourable `k`. -/
theorem exists_isChi (G : SGraph V) {k : Nat} (h : Colourable G k) :
    ∃ c, c ≤ k ∧ IsChi G c := exists_isChi_aux G k k (Nat.le_refl _) h

/-! ## Pigeonhole: a short list of colours misses a colour -/

theorem length_filter_ne_lt (a : Nat) :
    ∀ xs : List Nat, a ∈ xs → (xs.filter (fun x => decide (x ≠ a))).length < xs.length := by
  intro xs
  induction xs with
  | nil => intro h; cases h
  | cons x xs ih =>
    intro h
    by_cases e : x = a
    · have hle := List.length_filter_le (fun x => decide (x ≠ a)) xs
      rw [List.filter_cons_of_neg (by simp [e])]
      simp only [List.length_cons]
      omega
    · have hm : a ∈ xs := by
        rcases List.mem_cons.1 h with q | q
        · exact absurd q.symm e
        · exact q
      have := ih hm
      rw [List.filter_cons_of_pos (by simp [e])]
      simp only [List.length_cons]
      omega

theorem exists_not_mem_nat : ∀ (l : Nat) (xs : List Nat), xs.length < l → ∃ c, c < l ∧ c ∉ xs := by
  intro l
  induction l with
  | zero => intro xs h; omega
  | succ l ih =>
    intro xs h
    by_cases hm : l ∈ xs
    · have h1 := length_filter_ne_lt l xs hm
      obtain ⟨c, hc, hcn⟩ := ih (xs.filter (fun x => decide (x ≠ l))) (by omega)
      refine ⟨c, by omega, ?_⟩
      intro hcx
      apply hcn
      apply List.mem_filter.2
      refine ⟨hcx, ?_⟩
      have : c ≠ l := by omega
      simp [this]
    · exact ⟨l, by omega, hm⟩

theorem exists_fresh {l : Nat} (xs : List (Fin l)) (h : xs.length < l) : ∃ c : Fin l, c ∉ xs := by
  obtain ⟨c, hc, hcn⟩ := exists_not_mem_nat l (xs.map (fun x => x.val)) (by simpa using h)
  refine ⟨⟨c, hc⟩, ?_⟩
  intro hm
  apply hcn
  exact List.mem_map.2 ⟨⟨c, hc⟩, hm, rfl⟩

/-! ## The degeneracy lemma, relative to a vertex list -/

section Degeneracy

variable [DecidableEq V]

/-- Recolour the single vertex `v` with colour `c`. -/
def upd {k : Nat} (f : V → Fin k) (v : V) (c : Fin k) : V → Fin k :=
  fun w => if w = v then c else f w

/-- Properness restricted to the vertices of the list `L`. -/
def ProperOn (G : SGraph V) (L : List V) {k : Nat} (f : V → Fin k) : Prop :=
  ∀ a b, a ∈ L → b ∈ L → G.adj a b = true → f a ≠ f b

/-- Sequences of single-vertex recolourings at vertices of `L`, each proper on `L`. -/
inductive Reach (G : SGraph V) (L : List V) {k : Nat} : (V → Fin k) → (V → Fin k) → Prop
  | refl (f : V → Fin k) : Reach G L f f
  | step {f h : V → Fin k} (u : V) (c : Fin k) :
      u ∈ L → ProperOn G L (upd f u c) → Reach G L (upd f u c) h → Reach G L f h

theorem Reach.trans {G : SGraph V} {L : List V} {k : Nat} {f g h : V → Fin k}
    (h1 : Reach G L f g) (h2 : Reach G L g h) : Reach G L f h := by
  induction h1 with
  | refl _ => exact h2
  | step u c hu hp _ ih => exact Reach.step u c hu hp (ih h2)

/-- `L` is an elimination order of width `d`: no repeats, and every vertex has at most `d`
neighbours later in the list. -/
def elimB (G : SGraph V) (d : Nat) : List V → Bool
  | [] => true
  | v :: rest =>
    decide (v ∉ rest) && decide ((rest.filter (fun u => G.adj v u)).length ≤ d) && elimB G d rest

theorem proper_cons (G : SGraph V) {L : List V} {v : V} {l : Nat} {k k0 : V → Fin l}
    (h0 : ProperOn G L k0) (hag : ∀ u, u ∈ L → k u = k0 u)
    (hvn : ∀ b, b ∈ L → G.adj v b = true → k v ≠ k b) : ProperOn G (v :: L) k := by
  intro a b ha hb hab
  rcases List.mem_cons.1 ha with ea | ha'
  · rcases List.mem_cons.1 hb with eb | hb'
    · rw [ea, eb, G.irrefl] at hab; cases hab
    · rw [ea] at hab ⊢; exact hvn b hb' hab
  · rcases List.mem_cons.1 hb with eb | hb'
    · rw [eb] at hab ⊢
      intro e
      exact hvn a ha' (by rw [G.symm]; exact hab) e.symm
    · rw [hag a ha', hag b hb']; exact h0 a b ha' hb' hab

theorem properOn_tail (G : SGraph V) {L : List V} {v : V} {l : Nat} {f : V → Fin l}
    (h : ProperOn G (v :: L) f) : ProperOn G L f :=
  fun a b ha hb => h a b (List.mem_cons_of_mem _ ha) (List.mem_cons_of_mem _ hb)

theorem properOn_congr (G : SGraph V) {L : List V} {l : Nat} {k g : V → Fin l}
    (hg : ProperOn G L g) (hag : ∀ u, u ∈ L → k u = g u) : ProperOn G L k := by
  intro a b ha hb hab
  rw [hag a ha, hag b hb]
  exact hg a b ha hb hab

/-- Lifting a recolouring sequence on `L` to `v :: L` when `v` has at most `d` neighbours in
`L` and there are at least `d + 2` colours. -/
theorem lift (G : SGraph V) (L : List V) (v : V) (d l : Nat) (hv : v ∉ L)
    (hdeg : (L.filter (fun u => G.adj v u)).length ≤ d) (hl : d + 2 ≤ l)
    {f h : V → Fin l} (hr : Reach G L f h) :
    ∀ f' : V → Fin l, (∀ u, u ∈ L → f' u = f u) → ProperOn G (v :: L) f' →
      ∃ h', (∀ u, u ∈ L → h' u = h u) ∧ ProperOn G (v :: L) h' ∧ Reach G (v :: L) f' h' := by
  induction hr with
  | refl f => intro f' hag hp; exact ⟨f', hag, hp, Reach.refl _⟩
  | @step f h u c hu hp _ ih =>
    intro f' hag hp'
    obtain ⟨c', hc'⟩ := exists_fresh (c :: (L.filter (fun w => G.adj v w)).map f')
      (by simp only [List.length_cons, List.length_map]; omega)
    have hc'c : c' ≠ c := fun e => hc' (by rw [e]; exact List.mem_cons_self ..)
    have hc'N : ∀ b, b ∈ L → G.adj v b = true → c' ≠ f' b := by
      intro b hb hab e
      apply hc'
      apply List.mem_cons_of_mem
      exact List.mem_map.2 ⟨b, List.mem_filter.2 ⟨hb, hab⟩, e.symm⟩
    have huv : u ≠ v := fun e => hv (e ▸ hu)
    have hne : ∀ b, b ∈ L → b ≠ v := fun b hb e => hv (e ▸ hb)
    have hp'' : ProperOn G (v :: L) (upd f' v c') := by
      apply proper_cons G (properOn_tail G hp')
      · intro w hw; simp [upd, hne w hw]
      · intro b hb hab
        simp only [upd, ite_true, hne b hb, ite_false]
        exact hc'N b hb hab
    have hagk : ∀ w, w ∈ L → upd (upd f' v c') u c w = upd f u c w := by
      intro w hw
      by_cases e : w = u
      · simp [upd, e]
      · simp [upd, e, hne w hw, hag w hw]
    have hk : ProperOn G (v :: L) (upd (upd f' v c') u c) := by
      apply proper_cons G hp hagk
      intro b hb hab
      have e1 : upd (upd f' v c') u c v = c' := by
        have : ¬ v = u := fun q => huv q.symm
        simp [upd, this]
      rw [e1]
      by_cases e : b = u
      · simp only [upd, e, ite_true]; exact hc'c
      · simp only [upd, e, ite_false, hne b hb]; exact hc'N b hb hab
    obtain ⟨h', h1, h2, h3⟩ := ih (upd (upd f' v c') u c) hagk hk
    exact ⟨h', h1, h2, Reach.step v c' (List.mem_cons_self ..) hp''
      (Reach.step u c (List.mem_cons_of_mem _ hu) hk h3)⟩

/-- Degeneracy lemma, relative form: along an elimination order of width `d`, with at least
`d + 2` colours, any colouring proper on `L` can be recoloured to agree with any other. -/
theorem mix_rel (G : SGraph V) (d l : Nat) :
    ∀ L : List V, elimB G d L = true → (L ≠ [] → d + 2 ≤ l) →
      ∀ f g : V → Fin l, ProperOn G L f → ProperOn G L g →
        ∃ h, (∀ u, u ∈ L → h u = g u) ∧ ProperOn G L h ∧ Reach G L f h := by
  intro L
  induction L with
  | nil =>
    intro _ _ f g hf _
    exact ⟨f, fun u hu => (by cases hu), hf, Reach.refl _⟩
  | cons v L ih =>
    intro he hl f g hf hg
    have hl' : d + 2 ≤ l := hl (by simp)
    simp only [elimB, Bool.and_eq_true, decide_eq_true_eq] at he
    obtain ⟨⟨hv, hdeg⟩, he'⟩ := he
    obtain ⟨h0, h0g, _, h0r⟩ :=
      ih he' (fun _ => hl') f g (properOn_tail G hf) (properOn_tail G hg)
    obtain ⟨h', h1, _, h3⟩ := lift G L v d l hv hdeg hl' h0r f (fun _ _ => rfl) hf
    have hag : ∀ u, u ∈ v :: L → upd h' v (g v) u = g u := by
      intro u hu
      by_cases e : u = v
      · simp [upd, e]
      · rcases List.mem_cons.1 hu with q | q
        · exact absurd q e
        · simp only [upd, e, ite_false]; exact (h1 u q).trans (h0g u q)
    have hpf : ProperOn G (v :: L) (upd h' v (g v)) := properOn_congr G hg hag
    exact ⟨upd h' v (g v), hag, hpf,
      h3.trans (Reach.step v (g v) (List.mem_cons_self ..) hpf (Reach.refl _))⟩

/-! ## Transfer to the induced subgraph as a graph in its own right -/

/-- Restrict a colouring of the ambient vertex set to the induced subgraph. -/
def res {S : V → Bool} {l : Nat} (a : V → Fin l) : {v : V // S v = true} → Fin l :=
  fun x => a x.1

theorem reach_to_path (G : SGraph V) (S : V → Bool) (L : List V)
    (hL : ∀ u, u ∈ L ↔ S u = true) {l : Nat} {a b : V → Fin l} (hr : Reach G L a b) :
    Path (induce G S) (res a) (res b) := by
  induction hr with
  | refl _ => exact Path.refl _
  | @step a b u c hu hp _ ih =>
    by_cases e : a u = c
    · have : upd a u c = a := by
        funext w
        by_cases e' : w = u
        · simp [upd, e', e]
        · simp [upd, e']
      rw [this] at ih
      exact ih
    · refine Path.step (m := res (upd a u c)) ?_ ?_ ih
      · intro x y hxy
        exact hp x.1 y.1 ((hL _).2 x.2) ((hL _).2 y.2) hxy
      · refine ⟨⟨u, (hL u).1 hu⟩, ?_, ?_⟩
        · simp only [res, upd, ite_true]; exact e
        · intro w hw
          have : ¬ w.1 = u := fun q => hw (Subtype.ext q)
          simp [res, upd, this]

/-- Degeneracy lemma for an induced subgraph: if the vertices of `S` admit an elimination
order of width `d` and (when `S` is non-empty) `G[S]` is not `d`-colourable, then `G[S]`
is recolorable. -/
theorem recolorable_induce (G : SGraph V) (S : V → Bool) (d : Nat) (L : List V)
    (hL : ∀ u, u ∈ L ↔ S u = true) (hE : elimB G d L = true)
    (hchi : ∀ u, S u = true → ¬ Colourable (induce G S) d) : Recolorable (induce G S) := by
  intro c hc l hl f g hf hg
  cases L with
  | nil =>
    have : f = g := funext (fun x => by have := (hL x.1).2 x.2; cases this)
    rw [this]; exact Path.refl _
  | cons v L' =>
    have hSv : S v = true := (hL v).1 (List.mem_cons_self ..)
    have hcd : d < c := by
      apply Nat.lt_of_not_le
      intro hle
      exact hchi v hSv (colourable_mono _ hle hc.1)
    have hl2 : d + 2 ≤ l := by omega
    have c0 : Fin l := ⟨0, by omega⟩
    let ext : ({v : V // S v = true} → Fin l) → V → Fin l :=
      fun k u => if h : S u = true then k ⟨u, h⟩ else c0
    have hext : ∀ k : {v : V // S v = true} → Fin l, Proper (induce G S) k →
        ProperOn G (v :: L') (ext k) := by
      intro k hk a b ha hb hab
      have ha' := (hL a).1 ha
      have hb' := (hL b).1 hb
      simp only [ext, ha', hb', dif_pos]
      exact hk ⟨a, ha'⟩ ⟨b, hb'⟩ hab
    have hres : ∀ k : {v : V // S v = true} → Fin l, res (ext k) = k := by
      intro k; funext x
      simp only [res, ext, x.2, dif_pos]
    obtain ⟨h, hag, _, hr⟩ :=
      mix_rel G d l (v :: L') hE (fun _ => hl2) (ext f) (ext g) (hext f hf) (hext g hg)
    have hp := reach_to_path G S (v :: L') hL hr
    have hh : (res h : {v : V // S v = true} → Fin l) = g := by
      funext x
      have := hag x.1 ((hL x.1).2 x.2)
      simp only [res, this, ext, x.2, dif_pos]
    rw [hres f, hh] at hp
    exact hp

end Degeneracy

/-! ## Deciding statements quantified over vertex subsets of `Fin n` -/

def consB {n : Nat} (b : Bool) (f : Fin n → Bool) : Fin (n + 1) → Bool :=
  fun i => if h : i.val = 0 then b else f ⟨i.val - 1, by omega⟩

theorem consB_eta {n : Nat} (f : Fin (n + 1) → Bool) :
    consB (f ⟨0, by omega⟩) (fun i => f ⟨i.val + 1, by omega⟩) = f := by
  funext i
  unfold consB
  by_cases h : i.val = 0
  · simp only [h, dif_pos]; congr 1; exact Fin.ext h.symm
  · simp only [h, dif_neg, not_false_eq_true]; congr 1; apply Fin.ext; show i.val - 1 + 1 = i.val; omega

def decFB : (n : Nat) → (P : (Fin n → Bool) → Prop) → [DecidablePred P] → Decidable (∀ f, P f)
  | 0, P, _ =>
    decidable_of_iff (P (fun i => i.elim0))
      ⟨fun h f => by
          have : (fun i => i.elim0) = f := funext (fun i => i.elim0)
          rw [← this]; exact h,
       fun h => h _⟩
  | n + 1, P, _ =>
    have := decFB n (fun f' => P (consB true f'))
    have := decFB n (fun f' => P (consB false f'))
    decidable_of_iff ((∀ f', P (consB true f')) ∧ (∀ f', P (consB false f')))
      ⟨fun h f => by
          rw [← consB_eta f]
          cases f ⟨0, by omega⟩
          · exact h.2 _
          · exact h.1 _,
       fun h => ⟨fun f' => h _, fun f' => h _⟩⟩

instance instDecFB {n : Nat} (P : (Fin n → Bool) → Prop) [DecidablePred P] :
    Decidable (∀ f, P f) := decFB n P

/-! ## The witness: the nine-cycle and its blowup by `K_2` -/

def C9 : SGraph (Fin 9) where
  adj u v := decide ((u.val + 1) % 9 = v.val) || decide ((v.val + 1) % 9 = u.val)
  symm := by decide
  irrefl := by decide

/-- Every vertex of `C9` has exactly two neighbours, and `C9` has the nine edges `i ~ i+1`. -/
theorem c9_two_regular :
    ∀ v : Fin 9, ((List.finRange 9).filter (fun u => C9.adj v u)).length = 2 := by decide

theorem c9_no_nontrivial_module : ∀ S : Fin 9 → Bool, ¬ NontrivialModule C9 S := by
  unfold NontrivialModule IsModule
  decide +kernel

theorem c9_prime : Prime C9 := fun ⟨S, h⟩ => c9_no_nontrivial_module S h

/-- Sanity check that `Prime` is not vacuous: the four-cycle is not prime. -/
def C4 : SGraph (Fin 4) where
  adj u v := decide ((u.val + 1) % 4 = v.val) || decide ((v.val + 1) % 4 = u.val)
  symm := by decide
  irrefl := by decide

theorem c4_not_prime : ¬ Prime C4 := fun h =>
  h ⟨fun v => decide (v.val % 2 = 0), by unfold NontrivialModule IsModule; decide⟩

/-- Bounded walk search in `C9`. -/
def walkB : Nat → Fin 9 → Fin 9 → Bool
  | 0, a, b => decide (a = b)
  | n + 1, a, b => decide (a = b) || (List.finRange 9).any (fun m => C9.adj a m && walkB n m b)

theorem walkB_sound : ∀ n a b, walkB n a b = true → Walk C9 a b := by
  intro n
  induction n with
  | zero =>
    intro a b h
    have e : a = b := by simpa [walkB] using h
    rw [e]; exact Walk.refl _
  | succ n ih =>
    intro a b h
    simp only [walkB, Bool.or_eq_true, decide_eq_true_eq, List.any_eq_true,
      Bool.and_eq_true] at h
    rcases h with e | ⟨m, _, hm, hw⟩
    · rw [e]; exact Walk.refl _
    · exact Walk.step hm (ih m b hw)

theorem c9_walkB : ∀ a b : Fin 9, walkB 4 a b = true := by decide +kernel

theorem c9_connected : GConnected C9 := fun a b => walkB_sound 4 a b (c9_walkB a b)

/-! ### Antecedent: every induced subgraph of `C9` is recolorable -/

/-- The cyclic order `r+1, r+2, ..., r+9` (mod 9). -/
def rot (r : Fin 9) : List (Fin 9) :=
  (List.finRange 9).map (fun i => ⟨(r.val + 1 + i.val) % 9, Nat.mod_lt _ (by decide)⟩)

theorem mem_rot : ∀ r u : Fin 9, u ∈ rot r := by decide

/-- Width used for `C9[S]`: 2 for the whole cycle, 1 if `S` spans an edge, 0 otherwise. -/
def dS (S : Fin 9 → Bool) : Nat :=
  if (∀ v, S v = true) then 2
  else if (∃ a b, S a = true ∧ S b = true ∧ C9.adj a b = true) then 1 else 0

/-- For every vertex subset `S` some rotation of the cyclic order, filtered by `S`, is an
elimination order of width `dS S`. Checked by kernel evaluation over all 512 subsets. -/
theorem c9_elim : ∀ S : Fin 9 → Bool, ∃ r : Fin 9, elimB C9 (dS S) ((rot r).filter S) = true := by
  decide +kernel

/-- `C9[S]` (for non-empty `S`) is not `dS S`-colourable. -/
theorem c9_chi (S : Fin 9 → Bool) (u : Fin 9) (hu : S u = true) :
    ¬ Colourable (induce C9 S) (dS S) := by
  intro hcol
  by_cases hall : ∀ v, S v = true
  · have hd : dS S = 2 := by unfold dS; rw [if_pos hall]
    rw [hd] at hcol
    obtain ⟨f, hf⟩ := hcol
    have key : ∀ a b : Fin 9, C9.adj a b = true → (f ⟨a, hall a⟩).val ≠ (f ⟨b, hall b⟩).val :=
      fun a b hab e => hf ⟨a, hall a⟩ ⟨b, hall b⟩ hab (Fin.ext e)
    have h0 := key 0 1 (by decide)
    have h1 := key 1 2 (by decide)
    have h2 := key 2 3 (by decide)
    have h3 := key 3 4 (by decide)
    have h4 := key 4 5 (by decide)
    have h5 := key 5 6 (by decide)
    have h6 := key 6 7 (by decide)
    have h7 := key 7 8 (by decide)
    have h8 := key 8 0 (by decide)
    have b0 := (f ⟨0, hall 0⟩).isLt
    have b1 := (f ⟨1, hall 1⟩).isLt
    have b2 := (f ⟨2, hall 2⟩).isLt
    have b3 := (f ⟨3, hall 3⟩).isLt
    have b4 := (f ⟨4, hall 4⟩).isLt
    have b5 := (f ⟨5, hall 5⟩).isLt
    have b6 := (f ⟨6, hall 6⟩).isLt
    have b7 := (f ⟨7, hall 7⟩).isLt
    have b8 := (f ⟨8, hall 8⟩).isLt
    omega
  · by_cases hedge : ∃ a b, S a = true ∧ S b = true ∧ C9.adj a b = true
    · have hd : dS S = 1 := by unfold dS; rw [if_neg hall, if_pos hedge]
      rw [hd] at hcol
      obtain ⟨f, hf⟩ := hcol
      obtain ⟨a, b, ha, hb, hab⟩ := hedge
      apply hf ⟨a, ha⟩ ⟨b, hb⟩ hab
      apply Fin.ext
      have := (f ⟨a, ha⟩).isLt
      have := (f ⟨b, hb⟩).isLt
      omega
    · have hd : dS S = 0 := by unfold dS; rw [if_neg hall, if_neg hedge]
      rw [hd] at hcol
      obtain ⟨f, _⟩ := hcol
      exact (f ⟨u, hu⟩).elim0

/-- The antecedent of Conjecture 1 for `G = C9`. -/
theorem c9_induced_recolorable : ∀ S : Fin 9 → Bool, Recolorable (induce C9 S) := by
  intro S
  obtain ⟨r, hr⟩ := c9_elim S
  refine recolorable_induce C9 S (dS S) ((rot r).filter S) ?_ hr (c9_chi S)
  intro u
  constructor
  · intro h; exact (List.mem_filter.1 h).2
  · intro h; exact List.mem_filter.2 ⟨mem_rot r u, h⟩

/-- Non-vacuity of the antecedent: the whole cycle has chromatic number exactly 3, so the
antecedent really asserts (and the file proves) that `C9` is 4-mixing, 5-mixing, ... -/
theorem c9_whole_isChi3 : IsChi (induce C9 (fun _ => true)) 3 := by
  refine ⟨⟨fun x => ⟨x.1.val % 3, Nat.mod_lt _ (by decide)⟩, ?_⟩, ?_⟩
  · intro x y hxy e
    have key : ∀ a b : Fin 9, C9.adj a b = true → a.val % 3 ≠ b.val % 3 := by decide
    exact key x.1 y.1 hxy (congrArg Fin.val e)
  · intro k hk hc
    have h2 : dS (fun _ => true) = 2 := by decide
    have h := c9_chi (fun _ => true) 0 rfl
    rw [h2] at h
    exact h (colourable_mono _ (by omega) hc)

theorem c9_whole_mixing (l : Nat) (hl : 4 ≤ l) : Mixing (induce C9 (fun _ => true)) l :=
  c9_induced_recolorable _ 3 c9_whole_isChi3 l hl

/-! ### The blowup `H = C9[K_2]` is not recolorable -/

/-- The blowup of `C9` replacing every vertex by a clique on two vertices. -/
abbrev H : SGraph (Σ _ : Fin 9, Fin 2) := blowup C9 (fun _ => 2)

/-- The archived six-colouring: periodic palettes `{0,1},{2,3},{4,5}` around the cycle. -/
def six (x : Σ _ : Fin 9, Fin 2) : Fin 6 := ⟨(2 * x.1.val + x.2.val) % 6, Nat.mod_lt _ (by decide)⟩

def fiveList : List Nat := [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 4, 1, 2, 3, 4]

/-- The archived five-colouring (colours shifted to start at 0). -/
def five (x : Σ _ : Fin 9, Fin 2) : Fin 5 :=
  ⟨(fiveList.getD (2 * x.1.val + x.2.val) 0) % 5, Nat.mod_lt _ (by decide)⟩

/-- The same colouring regarded as a six-colouring. -/
def five6 (x : Σ _ : Fin 9, Fin 2) : Fin 6 := ⟨(five x).val, by have := (five x).isLt; omega⟩

/-- The edge rule of the archived checker and of the earlier finite core on `Fin 18`
(vertex `2 v + i`, clique index `u / 2`). -/
def adj18 (u v : Fin 18) : Bool :=
  decide (u ≠ v) &&
    (decide (u.val / 2 = v.val / 2) ||
     decide ((u.val / 2 + 9 - v.val / 2) % 9 = 1) ||
     decide ((u.val / 2 + 9 - v.val / 2) % 9 = 8))

/-- The general blowup of `C9` by `K_2` is the archived 18-vertex graph. -/
theorem H_adj_archived : ∀ (v w : Fin 9) (i j : Fin 2),
    H.adj ⟨v, i⟩ ⟨w, j⟩ =
      adj18 ⟨2 * v.val + i.val, by omega⟩ ⟨2 * w.val + j.val, by omega⟩ := by decide +kernel

/-- `H` is 5-regular (18 vertices, 45 edges). -/
theorem H_five_regular : ∀ (v : Fin 9) (i : Fin 2),
    ((List.finRange 9).map (fun w => ((List.finRange 2).filter
      (fun j => H.adj ⟨v, i⟩ ⟨w, j⟩)).length)).sum = 5 := by decide +kernel

theorem six_proper : Proper H six := by
  have h : ∀ (v w : Fin 9) (i j : Fin 2), H.adj ⟨v, i⟩ ⟨w, j⟩ = true → six ⟨v, i⟩ ≠ six ⟨w, j⟩ := by
    decide +kernel
  intro ⟨v, i⟩ ⟨w, j⟩
  exact h v w i j

theorem five_proper : Proper H five := by
  have h : ∀ (v w : Fin 9) (i j : Fin 2), H.adj ⟨v, i⟩ ⟨w, j⟩ = true → five ⟨v, i⟩ ≠ five ⟨w, j⟩ := by
    decide +kernel
  intro ⟨v, i⟩ ⟨w, j⟩
  exact h v w i j

theorem five6_proper : Proper H five6 := by
  intro a b hab e
  apply five_proper a b hab
  apply Fin.ext
  have e' := congrArg Fin.val e
  exact e'

theorem five6_ne_six : five6 ≠ six := by
  intro e
  have := congrFun e ⟨6, 1⟩
  revert this
  decide

/-- Saturation: every vertex of `H` sees each of the five other colours on a neighbour. -/
theorem six_saturated : ∀ (v : Fin 9) (i : Fin 2) (c : Fin 6), c ≠ six ⟨v, i⟩ →
    ∃ (w : Fin 9) (j : Fin 2), H.adj ⟨w, j⟩ ⟨v, i⟩ = true ∧ six ⟨w, j⟩ = c := by decide +kernel

/-- `six` is frozen: it has no neighbour in `R_6(H)`. -/
theorem six_frozen (k : (Σ _ : Fin 9, Fin 2) → Fin 6) (hk : Proper H k) : ¬ RAdj six k := by
  intro ⟨⟨v, i⟩, hne, hag⟩
  obtain ⟨w, j, hadj, hc⟩ := six_saturated v i (k ⟨v, i⟩) (fun e => hne e.symm)
  have hwv : (⟨w, j⟩ : Σ _ : Fin 9, Fin 2) ≠ ⟨v, i⟩ := by
    intro e
    rw [e, H.irrefl] at hadj
    cases hadj
  apply hk ⟨w, j⟩ ⟨v, i⟩ hadj
  rw [← hag ⟨w, j⟩ hwv]
  exact hc

/-- `R_6(H)` is disconnected: no walk from `six` to the other proper six-colouring. -/
theorem path_from_six {f g : (Σ _ : Fin 9, Fin 2) → Fin 6} (hp : Path H f g) (hf : f = six) :
    g = six := by
  cases hp with
  | refl => exact hf
  | step hm hadj _ => rw [hf] at hadj; exact absurd hadj (six_frozen _ hm)

theorem H_not_mixing6 : ¬ Mixing H 6 := by
  intro h
  exact five6_ne_six (path_from_six (h six five6 six_proper five6_proper) rfl)

theorem H_colourable5 : Colourable H 5 := ⟨five, five_proper⟩

/-- Already from `χ(H) ≤ 5`: `H` is not recolorable (uses the classical existence of the
chromatic number; the choice-free version `H_not_recolorable` is below). -/
theorem H_not_recolorable_of_le : ¬ Recolorable H := by
  intro h
  obtain ⟨c, hc5, hchi⟩ := exists_isChi H H_colourable5
  exact H_not_mixing6 (h c hchi 6 (by omega))

/-! ### Sharper: `χ(H) = 5` exactly, so `6 = χ(H) + 1` -/

/-- Two colour pairs are the same unordered pair. -/
def SameP (a b e g : Fin 4) : Prop := (e = a ∧ g = b) ∨ (e = b ∧ g = a)

instance (a b e g : Fin 4) : Decidable (SameP a b e g) := by unfold SameP; exact inferInstance

/-- In a 4-colouring, two 4-cliques `{a,b,c,d}` and `{c,d,e,g}` force `{e,g} = {a,b}`. -/
theorem k4_pair_aux : ∀ a b c d e g : Fin 4,
    ((a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d) ∧
     (c ≠ e ∧ c ≠ g ∧ d ≠ e ∧ d ≠ g ∧ e ≠ g)) → SameP a b e g := by decide +kernel

theorem k4_pair (a b c d e g : Fin 4) (h1 : a ≠ b) (h2 : a ≠ c) (h3 : a ≠ d) (h4 : b ≠ c)
    (h5 : b ≠ d) (h6 : c ≠ d) (h7 : c ≠ e) (h8 : c ≠ g) (h9 : d ≠ e) (h10 : d ≠ g)
    (h11 : e ≠ g) : SameP a b e g :=
  k4_pair_aux a b c d e g ⟨⟨h1, h2, h3, h4, h5, h6⟩, ⟨h7, h8, h9, h10, h11⟩⟩

theorem sameP_trans : ∀ a b c d e g : Fin 4, SameP a b c d → SameP c d e g → SameP a b e g := by
  decide +kernel

theorem sameP_clash : ∀ a b e g : Fin 4, SameP a b e g → e ≠ a → e ≠ b → False := by
  decide +kernel

theorem H_adj_next : ∀ (v w : Fin 9) (i j : Fin 2), w.val = (v.val + 1) % 9 →
    H.adj ⟨v, i⟩ ⟨w, j⟩ = true := by decide +kernel

theorem H_adj_twin : ∀ v : Fin 9, H.adj ⟨v, 0⟩ ⟨v, 1⟩ = true := by decide +kernel

theorem palette_step (f : (Σ _ : Fin 9, Fin 2) → Fin 4) (hf : Proper H f) (v w u : Fin 9)
    (hw : w.val = (v.val + 1) % 9) (hu : u.val = (w.val + 1) % 9) :
    SameP (f ⟨v, 0⟩) (f ⟨v, 1⟩) (f ⟨u, 0⟩) (f ⟨u, 1⟩) :=
  k4_pair (f ⟨v, 0⟩) (f ⟨v, 1⟩) (f ⟨w, 0⟩) (f ⟨w, 1⟩) (f ⟨u, 0⟩) (f ⟨u, 1⟩)
    (hf _ _ (H_adj_twin v)) (hf _ _ (H_adj_next v w 0 0 hw)) (hf _ _ (H_adj_next v w 0 1 hw))
    (hf _ _ (H_adj_next v w 1 0 hw)) (hf _ _ (H_adj_next v w 1 1 hw)) (hf _ _ (H_adj_twin w))
    (hf _ _ (H_adj_next w u 0 0 hu)) (hf _ _ (H_adj_next w u 0 1 hu))
    (hf _ _ (H_adj_next w u 1 0 hu)) (hf _ _ (H_adj_next w u 1 1 hu)) (hf _ _ (H_adj_twin u))

/-- `H` is not 4-colourable: palettes repeat with period two around an odd cycle. -/
theorem H_not_colourable4 : ¬ Colourable H 4 := by
  intro ⟨f, hf⟩
  have s02 := palette_step f hf 0 1 2 (by decide) (by decide)
  have s24 := palette_step f hf 2 3 4 (by decide) (by decide)
  have s46 := palette_step f hf 4 5 6 (by decide) (by decide)
  have s68 := palette_step f hf 6 7 8 (by decide) (by decide)
  have s08 := sameP_trans _ _ _ _ _ _ (sameP_trans _ _ _ _ _ _ (sameP_trans _ _ _ _ _ _ s02 s24) s46) s68
  exact sameP_clash _ _ _ _ s08 (hf _ _ (H_adj_next 8 0 0 0 (by decide)))
    (hf _ _ (H_adj_next 8 0 0 1 (by decide)))

/-- The chromatic number of `H` is exactly 5. -/
theorem H_isChi5 : IsChi H 5 :=
  ⟨H_colourable5, fun _ hk hc => H_not_colourable4 (colourable_mono H (by omega) hc)⟩

/-- In the source's words: `H` is 5-chromatic and `R_6(H)` is disconnected. -/
theorem H_chi5_and_R6_disconnected : IsChi H 5 ∧ ¬ Mixing H 6 := ⟨H_isChi5, H_not_mixing6⟩

/-- `H = C9[K_2]` is not recolorable: `χ(H) = 5` and `R_6(H)` is disconnected. -/
theorem H_not_recolorable : ¬ Recolorable H :=
  fun h => H_not_mixing6 (h 5 H_isChi5 6 (Nat.le_refl _))

/-! ### The refutation -/

/-- The witness in one statement: `C9` is prime, every induced subgraph of `C9` is
recolorable, and a blowup of `C9` by non-empty cliques is not recolorable. -/
theorem witness :
    Prime C9 ∧ (∀ S : Fin 9 → Bool, Recolorable (induce C9 S)) ∧
    ∃ m : Fin 9 → Nat, (∀ v, 1 ≤ m v) ∧ ¬ Recolorable (blowup C9 m) :=
  ⟨c9_prime, c9_induced_recolorable, fun _ => 2, fun _ => (by decide : 1 ≤ 2), H_not_recolorable⟩

/-- Conjecture 1 of the source is false (its "if" direction fails for `G = C9`). -/
theorem not_conjecture1 : ¬ Conjecture1 := fun h =>
  H_not_recolorable ((h 9 C9 c9_prime).2 c9_induced_recolorable (fun _ => 2) (fun _ => (by decide : 1 ≤ 2)))

/-- The narrower reading (connected prime graphs only) is refuted by the same witness. -/
theorem not_conjecture1Connected : ¬ Conjecture1Connected := fun h =>
  H_not_recolorable
    ((h 9 C9 c9_connected c9_prime).2 c9_induced_recolorable (fun _ => 2)
      (fun _ => (by decide : 1 ≤ 2)))

end Recol

#print axioms Recol.c9_whole_isChi3
#print axioms Recol.c9_whole_mixing
#print axioms Recol.exists_isChi
#print axioms Recol.H_not_recolorable_of_le
#print axioms Recol.H_isChi5
#print axioms Recol.H_chi5_and_R6_disconnected
#print axioms Recol.c9_connected
#print axioms Recol.c4_not_prime
#print axioms Recol.H_adj_archived
#print axioms Recol.mix_rel
#print axioms Recol.not_conjecture1Connected
#print axioms Recol.c9_prime
#print axioms Recol.c9_elim
#print axioms Recol.c9_induced_recolorable
#print axioms Recol.recolorable_induce
#print axioms Recol.six_proper
#print axioms Recol.six_frozen
#print axioms Recol.H_not_mixing6
#print axioms Recol.H_not_recolorable
#print axioms Recol.witness
#print axioms Recol.not_conjecture1
