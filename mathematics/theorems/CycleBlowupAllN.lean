import Mathlib.Data.ZMod.Basic
import Mathlib.Data.ZMod.Coprime
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Fintype.Perm
import Mathlib.SetTheory.Cardinal.Finite
import Mathlib.Logic.Equiv.Fin.Basic
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Connected
import Mathlib.Tactic

/-!
# Frozen colourings in odd-cycle blowups, for ALL `n` (Lean 4 + Mathlib)

Paper statement (Proposition "Frozen colorings in odd-cycle blowups",
label `prop:cycle-blowup-frozen`):

  "For every odd n >= 5, C_n is prime and every induced subgraph is recolorable. Its blowup
   H_n = C_n[K_2] has chromatic number 5 and has a frozen proper coloring with the six
   labeled colors [6] if and only if 3 | n. When 3 | n, there are exactly 90 * 2^n frozen
   labeled colorings, and R_6(H_n) has at least 90 * 2^n + 1 connected components."

Headline theorem: `Recol.cycle_blowup_frozen`, quantified over every `n` with
`n % 2 = 1` and `5 ≤ n`. Nothing in this file is a finite check standing in for a statement
about all `n`; the only kernel evaluations (`decide`) are side bindings at `n = 3, 4, 9`,
small facts about `Fin 2`, `Fin 3`, `Fin 4`, and the number 90 of ordered pair-partitions.

Component theorems and the widest ranges proved (each range was first determined by an
independent brute-force count, see STATEMENT.md):

* `frozen_exists_iff` (A): for every `n ≥ 1`, a frozen proper 6-colouring of `H_n` exists
  iff `3 ∣ n`. Key steps: `win_surj` / `win_bij` (the closed neighbourhood of a bag uses
  all six colours), `palSub_three` (palettes repeat with period three),
  `step_one_of_coprime` (period `m` coprime to `n` forces period one), `mk_frozen`.
* `card_frozen` (B): for every `n ≥ 1` with `3 ∣ n`, exactly `90 * 2 ^ n` frozen labelled
  colourings (`Nat.card`; `card_frozen_fintype` for `Fintype.card`). Explicit form:
  `frozenEquivPartitions : FrozenCol n ≃ PairPartition × (ZMod n → Bool)` with
  `card_pairPartition : Fintype.card PairPartition = 90`.
* `components_R6` (C): for `3 ∣ n`, `n ≥ 4`: at least `90 * 2 ^ n + 1` connected components
  of `R_6(H_n)`, as `SimpleGraph.ConnectedComponent` of `RGraph`. Sharp:
  `components_R6_three` shows that `R_6(H_3)` has exactly `90 * 2 ^ 3` components.
* (D): `Cyc_prime` (every `n ≥ 5`; `Cyc4_not_prime`), `Cyc_induced_recolorable`
  (every odd `n ≥ 3`, all `2 ^ n` vertex subsets, every `l ≥ χ + 1`),
  `Hn_isChi5` (every odd `n ≥ 5`): explicit 5-colouring `five` for every `n ≥ 4`, and
  `Hn_not_colourable4` for every odd `n ≥ 3`.
* Consequences: `family_6r3`, `witness_family`, `not_conjecture1_of`, `card_isolated_nine`.
* The written proof's own route to the lower bound: `independence_number`
  (`α(H_n) = (n - 1) / 2` for every odd `n ≥ 3`) and `Hn_not_colourable4_via_alpha`.

Reuse. The block between the BEGIN/END markers below is a verbatim copy of lines 39-418 of
the certified rank 1 file `research_case_kernels/01_prime_blowup/PrimeBlowup.lean`
(sha256 016a2a6d31be7a684d6c686014ec0c5b8969000e6aecee855ab69a978a63468f):
general graphs, proper colourings, `RAdj`, `Path`, `Mixing`, `Recolorable`, modules,
`Prime`, `blowup`, `induce`, `Conjecture1`, and the degeneracy lemma `mix_rel` /
`recolorable_induce`. Everything after the END marker is new.

Vertex set of `C_n`: `ZMod n`. `H_n` is the general `blowup` with every bag of size 2, so
its vertices are pairs `⟨i, s⟩` with `i : ZMod n`, `s : Fin 2`; `Hn_adj_iff_diff` states
adjacency as "distinct, and `j - i` is `0`, `1` or `-1`".
-/

-- BEGIN verbatim copy of PrimeBlowup.lean lines 39-418
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
-- END verbatim copy of PrimeBlowup.lean lines 39-418

/-! ## New material: cycles on `ZMod n`, their `K_2` blowups, frozen colourings -/

/-- A proper colouring is frozen when it has no neighbour in the reconfiguration graph:
no proper colouring differs from it at exactly one vertex. -/
def Frozen (G : SGraph V) {k : Nat} (f : V → Fin k) : Prop :=
  Proper G f ∧ ∀ g : V → Fin k, Proper G g → ¬ RAdj f g

/-- Frozen, in the paper's words: every vertex sees every other colour on a neighbour. -/
theorem frozen_iff_sees [DecidableEq V] (G : SGraph V) {k : Nat} (f : V → Fin k) :
    Frozen G f ↔ Proper G f ∧ ∀ v c, c ≠ f v → ∃ w, G.adj w v = true ∧ f w = c := by
  constructor
  · rintro ⟨hp, hfr⟩
    refine ⟨hp, ?_⟩
    intro v c hc
    by_contra hno
    have hno' : ∀ w, G.adj w v = true → f w ≠ c := fun w hw e => hno ⟨w, hw, e⟩
    apply hfr (upd f v c)
    · intro a b hab
      by_cases ha : a = v
      · have hb : b ≠ v := by
          intro hb; rw [ha, hb, G.irrefl] at hab; cases hab
        simp only [upd, ha, hb, if_true, if_false]
        have : G.adj b v = true := by rw [G.symm]; rw [ha] at hab; exact hab
        exact fun e => hno' b this e.symm
      · by_cases hb : b = v
        · simp only [upd, ha, hb, if_true, if_false]
          rw [hb] at hab
          exact hno' a hab
        · simp only [upd, ha, hb, if_false]
          exact hp a b hab
    · refine ⟨v, ?_, ?_⟩
      · simp only [upd, if_true]; exact fun e => hc e.symm
      · intro w hw; simp only [upd, hw, if_false]
  · rintro ⟨hp, hs⟩
    refine ⟨hp, ?_⟩
    rintro g hg ⟨v, hne, hag⟩
    obtain ⟨w, hw, hc⟩ := hs v (g v) (fun e => hne e.symm)
    have hwv : w ≠ v := by
      intro e; rw [e, G.irrefl] at hw; cases hw
    apply hg w v hw
    rw [← hag w hwv]; exact hc

/-- The cycle `C_n` on `ZMod n`: `u ~ v` iff `u ≠ v` and `v = u + 1` or `u = v + 1`. -/
def Cyc (n : ℕ) : SGraph (ZMod n) where
  adj u v := decide (u ≠ v) && (decide (v = u + 1) || decide (u = v + 1))
  symm u v := by
    by_cases h : u = v
    · subst h; rfl
    · have h' : v ≠ u := fun e => h e.symm
      simp only [ne_eq, h, h', not_false_eq_true, decide_true, Bool.true_and]
      exact Bool.or_comm _ _
  irrefl u := by simp

theorem Cyc_adj_iff {n : ℕ} (u v : ZMod n) :
    (Cyc n).adj u v = true ↔ u ≠ v ∧ (v = u + 1 ∨ u = v + 1) := by
  simp [Cyc]

/-- Vertex type of `H_n`: pairs (bag, slot). -/
abbrev VH (n : ℕ) : Type := Σ _ : ZMod n, Fin 2

/-- `H_n = C_n[K_2]`, as an instance of the general blowup. -/
abbrev Hn (n : ℕ) : SGraph (VH n) := blowup (Cyc n) (fun _ => 2)

theorem Hn_adj_iff {n : ℕ} (i j : ZMod n) (s t : Fin 2) :
    (Hn n).adj ⟨i, s⟩ ⟨j, t⟩ = true ↔
      (i = j ∧ s ≠ t) ∨ (i ≠ j ∧ (j = i + 1 ∨ i = j + 1)) := by
  show (if i = j then decide (s.val ≠ t.val) else (Cyc n).adj i j) = true ↔ _
  by_cases h : i = j
  · simp [h, Fin.val_inj]
  · simp [h, Cyc_adj_iff]

/-- Binding to the task's wording: `(i,s) ~ (j,t)` iff they are distinct and `j - i` is
`0`, `1` or `-1` in `ZMod n`. -/
theorem Hn_adj_iff_diff {n : ℕ} (x y : VH n) :
    (Hn n).adj x y = true ↔ x ≠ y ∧ (y.1 - x.1 = 0 ∨ y.1 - x.1 = 1 ∨ y.1 - x.1 = -1) := by
  obtain ⟨i, s⟩ := x
  obtain ⟨j, t⟩ := y
  rw [Hn_adj_iff]
  constructor
  · rintro (⟨h, hst⟩ | ⟨h, h1 | h1⟩)
    · subst h
      refine ⟨?_, Or.inl (sub_self _)⟩
      intro e; apply hst
      have := (Sigma.mk.inj_iff.1 e).2
      exact eq_of_heq this
    · refine ⟨fun e => h (Sigma.mk.inj_iff.1 e).1, Or.inr (Or.inl ?_)⟩
      rw [h1]; ring
    · refine ⟨fun e => h (Sigma.mk.inj_iff.1 e).1, Or.inr (Or.inr ?_)⟩
      rw [h1]; ring
  · rintro ⟨hne, h0 | h1 | h1⟩
    · have e : i = j := (sub_eq_zero.1 h0).symm
      subst e
      refine Or.inl ⟨rfl, ?_⟩
      intro e; apply hne; rw [e]
    · by_cases e : i = j
      · subst e
        refine Or.inl ⟨rfl, ?_⟩
        intro e; apply hne; rw [e]
      · exact Or.inr ⟨e, Or.inl (by rw [← h1]; ring)⟩
    · by_cases e : i = j
      · subst e
        refine Or.inl ⟨rfl, ?_⟩
        intro e; apply hne; rw [e]
      · refine Or.inr ⟨e, Or.inr ?_⟩
        have : j = i - 1 := by
          have := congrArg (fun z => z + i) h1
          simp only [sub_add_cancel] at this
          rw [this]; ring
        rw [this]; ring

section Windows

variable {n : ℕ}

/-- The three bags `i-1, i, i+1`. -/
def bag3 (i : ZMod n) : Fin 3 → ZMod n := ![i - 1, i, i + 1]

/-- The colouring read on the closed neighbourhood of bag `i`. -/
def win (f : VH n → Fin 6) (i : ZMod n) (p : Fin 3 × Fin 2) : Fin 6 := f ⟨bag3 i p.1, p.2⟩

theorem win0 (f : VH n → Fin 6) (i : ZMod n) (s : Fin 2) : win f i (0, s) = f ⟨i - 1, s⟩ := rfl
theorem win1 (f : VH n → Fin 6) (i : ZMod n) (s : Fin 2) : win f i (1, s) = f ⟨i, s⟩ := rfl
theorem win2 (f : VH n → Fin 6) (i : ZMod n) (s : Fin 2) : win f i (2, s) = f ⟨i + 1, s⟩ := rfl

/-- Key step: in a frozen colouring the closed neighbourhood of a bag uses all six colours. -/
theorem win_surj (f : VH n → Fin 6) (hf : Frozen (Hn n) f) (i : ZMod n) :
    Function.Surjective (win f i) := by
  have hs := ((frozen_iff_sees _ f).1 hf).2
  intro c
  by_cases h : c = f ⟨i, 0⟩
  · exact ⟨(1, 0), by rw [win1, h]⟩
  · obtain ⟨⟨j, t⟩, hadj, hc⟩ := hs ⟨i, 0⟩ c h
    rw [Hn_adj_iff] at hadj
    rcases hadj with ⟨e, _⟩ | ⟨_, e | e⟩
    · subst e; exact ⟨(1, t), by rw [win1, hc]⟩
    · refine ⟨(0, t), ?_⟩
      rw [win0, ← hc, e, add_sub_cancel_right]
    · refine ⟨(2, t), ?_⟩
      rw [win2, ← hc, e]

theorem win_bij (f : VH n → Fin 6) (hf : Frozen (Hn n) f) (i : ZMod n) :
    Function.Bijective (win f i) :=
  (Fintype.bijective_iff_surjective_and_card _).2 ⟨win_surj f hf i, by simp⟩

/-- Palette inclusion: every colour of bag `i` occurs in bag `j`. -/
def PalSub {k : ℕ} (f : VH n → Fin k) (i j : ZMod n) : Prop := ∀ t, ∃ s, f ⟨i, t⟩ = f ⟨j, s⟩

/-- Palettes repeat with period three. -/
theorem palSub_three (f : VH n → Fin 6) (hf : Frozen (Hn n) f) (i : ZMod n) :
    PalSub f (i + 3) i := by
  intro t
  obtain ⟨⟨a, s⟩, ha⟩ := win_surj f hf (i + 1) (f ⟨i + 3, t⟩)
  have inj := (win_bij f hf (i + 2)).1
  have e1 : i + 2 - 1 = i + 1 := by ring
  have e2 : i + 2 + 1 = i + 3 := by ring
  have w0 : ∀ s, win f (i + 2) (0, s) = f ⟨i + 1, s⟩ := fun s => by rw [win0, e1]
  have w2 : ∀ s, win f (i + 2) (2, s) = f ⟨i + 3, s⟩ := fun s => by rw [win2, e2]
  fin_cases a
  · refine ⟨s, ?_⟩
    have : win f (i + 1) (0, s) = f ⟨i, s⟩ := by rw [win0, add_sub_cancel_right]
    rw [← this]; exact ha.symm
  · exfalso
    have h1 : win f (i + 1) (1, s) = f ⟨i + 1, s⟩ := win1 _ _ _
    have : win f (i + 2) (0, s) = win f (i + 2) (2, t) := by
      rw [w0, w2, ← h1]; exact ha
    have := inj this
    simp at this
  · exfalso
    have h1 : win f (i + 1) (2, s) = f ⟨i + 2, s⟩ := by
      rw [win2]; congr 2; ring
    have : win f (i + 2) (1, s) = win f (i + 2) (2, t) := by
      rw [win1, w2, ← h1]; exact ha
    have := inj this
    simp at this

end Windows

/-- A relation on `ZMod n` that is reflexive, transitive and holds along steps of length `m`
coprime to `n` holds along steps of length one. -/
theorem step_one_of_coprime {n m : ℕ} [NeZero n] (hc : Nat.Coprime m n)
    (R : ZMod n → ZMod n → Prop) (hrefl : ∀ i, R i i)
    (htrans : ∀ i j k, R i j → R j k → R i k) (hstep : ∀ i, R (i + (m : ZMod n)) i) :
    ∀ i, R (i + 1) i := by
  have hk : ∀ (k : ℕ) (i : ZMod n), R (i + (m : ZMod n) * (k : ZMod n)) i := by
    intro k
    induction k with
    | zero => intro i; simpa using hrefl i
    | succ k ih =>
      intro i
      have e : i + (m : ZMod n) * ((k + 1 : ℕ) : ZMod n) = (i + (m : ZMod n) * (k : ZMod n)) + (m : ZMod n) := by
        push_cast; ring
      rw [e]
      exact htrans _ _ _ (hstep _) (ih i)
  intro i
  have h1 : (m : ZMod n) * (((m : ZMod n)⁻¹).val : ZMod n) = 1 := by
    rw [ZMod.natCast_zmod_val]; exact ZMod.coe_mul_inv_eq_one m hc
  have := hk ((m : ZMod n)⁻¹).val i
  rw [h1] at this
  exact this

theorem val_succ {n : ℕ} [NeZero n] (i : ZMod n) : (i + 1).val = (i.val + 1) % n := by
  rw [ZMod.val_add, ZMod.val_one_eq_one_mod, Nat.add_mod_mod]

theorem val_succ_mod3 {n : ℕ} [NeZero n] (h3 : 3 ∣ n) (i : ZMod n) :
    (i + 1).val % 3 = (i.val + 1) % 3 := by
  rw [val_succ, Nat.mod_mod_of_dvd _ h3]

theorem val_pred_mod3 {n : ℕ} [NeZero n] (h3 : 3 ∣ n) (i : ZMod n) :
    (i - 1).val % 3 = (i.val + 2) % 3 := by
  have := val_succ_mod3 h3 (i - 1)
  rw [sub_add_cancel] at this
  omega

/-- Necessity: a frozen proper six-colouring of `H_n` forces `3 ∣ n`. -/
theorem three_dvd_of_frozen {n : ℕ} [NeZero n] (f : VH n → Fin 6) (hf : Frozen (Hn n) f) :
    3 ∣ n := by
  by_contra h3
  have hc : Nat.Coprime 3 n := (Nat.Prime.coprime_iff_not_dvd Nat.prime_three).2 h3
  have key := step_one_of_coprime hc (PalSub f) (fun i t => ⟨t, rfl⟩)
    (fun i j k hij hjk t => by
      obtain ⟨s, hs⟩ := hij t
      obtain ⟨u, hu⟩ := hjk s
      exact ⟨u, hs.trans hu⟩)
    (fun i => by simpa using palSub_three f hf i)
  obtain ⟨s, hs⟩ := key 0 0
  have inj := (win_bij f hf 0).1
  have : win f 0 (2, 0) = win f 0 (1, s) := by rw [win2, win1]; exact hs
  have := inj this
  simp at this

/-! ## Sufficiency and the exact count when `3 ∣ n` -/

section Count

variable {n : ℕ} [NeZero n]

/-- The residue of a bag modulo three. -/
def r3 (i : ZMod n) : Fin 3 := ⟨i.val % 3, Nat.mod_lt _ (by decide)⟩

theorem r3_succ (h3 : 3 ∣ n) (i : ZMod n) : r3 (i + 1) = r3 i + 1 := by
  apply Fin.ext
  have := val_succ_mod3 h3 i
  simp only [r3, Fin.val_add]
  show (i + 1).val % 3 = (i.val % 3 + 1) % 3
  omega

theorem r3_pred (h3 : 3 ∣ n) (i : ZMod n) : r3 (i - 1) = r3 i + 2 := by
  apply Fin.ext
  have := val_pred_mod3 h3 i
  simp only [r3, Fin.val_add]
  show (i - 1).val % 3 = (i.val % 3 + 2) % 3
  omega

theorem r3_cast (h3 : 3 ∣ n) (a : Fin 3) : r3 ((a.val : ℕ) : ZMod n) = a := by
  apply Fin.ext
  have hn : 3 ≤ n := Nat.le_of_dvd (Nat.pos_of_ne_zero (NeZero.ne n)) h3
  have ha := a.isLt
  show ((a.val : ℕ) : ZMod n).val % 3 = a.val
  rw [ZMod.val_natCast]
  have h1 : a.val % n = a.val := Nat.mod_eq_of_lt (by omega)
  rw [h1]
  exact Nat.mod_eq_of_lt ha

/-- The colouring with palette `w (r, ·)` on the bags `≡ r (mod 3)` and orientation bits `b`. -/
def mk (w : Fin 3 × Fin 2 ≃ Fin 6) (b : ZMod n → Fin 2) : VH n → Fin 6 :=
  fun x => w (r3 x.1, x.2 + b x.1)

theorem fin3_ne_succ : ∀ a : Fin 3, a ≠ a + 1 := by decide
theorem fin3_ne_succ2 : ∀ a : Fin 3, a ≠ a + 2 := by decide
theorem fin3_cases : ∀ a r : Fin 3, a = r ∨ a = r + 1 ∨ a = r + 2 := by decide

theorem succ_ne (h3 : 3 ∣ n) (i : ZMod n) : i + 1 ≠ i := by
  intro e
  have := r3_succ h3 i
  rw [e] at this
  exact fin3_ne_succ _ this

theorem pred_ne (h3 : 3 ∣ n) (i : ZMod n) : i - 1 ≠ i := by
  intro e
  have := r3_pred h3 i
  rw [e] at this
  exact fin3_ne_succ2 _ this

/-- Sufficiency, in full generality: every choice of ordered pair-partition data `w` and
orientation bits `b` gives a frozen colouring when `3 ∣ n`. -/
theorem mk_frozen (h3 : 3 ∣ n) (w : Fin 3 × Fin 2 ≃ Fin 6) (b : ZMod n → Fin 2) :
    Frozen (Hn n) (mk w b) := by
  rw [frozen_iff_sees]
  constructor
  · rintro ⟨i, s⟩ ⟨j, t⟩ hadj e
    rw [Hn_adj_iff] at hadj
    have e' := w.injective e
    rcases hadj with ⟨hij, hst⟩ | ⟨_, hij | hij⟩
    · subst hij
      exact hst (add_right_cancel (Prod.ext_iff.1 e').2)
    · have h1 := (Prod.ext_iff.1 e').1
      simp only at h1
      rw [hij, r3_succ h3] at h1
      exact fin3_ne_succ _ h1
    · have h1 := (Prod.ext_iff.1 e').1
      simp only at h1
      rw [hij, r3_succ h3] at h1
      exact fin3_ne_succ _ h1.symm
  · rintro ⟨i, s⟩ c hc
    obtain ⟨⟨a, u⟩, hau⟩ : ∃ p, w p = c := ⟨w.symm c, w.apply_symm_apply c⟩
    rcases fin3_cases a (r3 i) with ha | ha | ha
    · refine ⟨⟨i, u - b i⟩, ?_, ?_⟩
      · rw [Hn_adj_iff]
        refine Or.inl ⟨rfl, ?_⟩
        intro e
        apply hc
        show c = w (r3 i, s + b i)
        rw [← e, sub_add_cancel, ← ha, hau]
      · show w (r3 i, u - b i + b i) = c
        rw [sub_add_cancel, ← ha, hau]
    · refine ⟨⟨i + 1, u - b (i + 1)⟩, ?_, ?_⟩
      · rw [Hn_adj_iff]
        exact Or.inr ⟨succ_ne h3 i, Or.inr rfl⟩
      · show w (r3 (i + 1), u - b (i + 1) + b (i + 1)) = c
        rw [sub_add_cancel, r3_succ h3, ← ha, hau]
    · refine ⟨⟨i - 1, u - b (i - 1)⟩, ?_, ?_⟩
      · rw [Hn_adj_iff]
        exact Or.inr ⟨pred_ne h3 i, Or.inl (sub_add_cancel i 1).symm⟩
      · show w (r3 (i - 1), u - b (i - 1) + b (i - 1)) = c
        rw [sub_add_cancel, r3_pred h3, ← ha, hau]

/-- The standard pair-partition data: palettes `{0,1}, {2,3}, {4,5}`. -/
def w0 : Fin 3 × Fin 2 ≃ Fin 6 := finProdFinEquiv

/-- **(A)** `H_n` has a frozen proper six-colouring if and only if `3 ∣ n` (every `n ≥ 1`). -/
theorem frozen_exists_iff (n : ℕ) [NeZero n] :
    (∃ f : VH n → Fin 6, Frozen (Hn n) f) ↔ 3 ∣ n :=
  ⟨fun ⟨f, hf⟩ => three_dvd_of_frozen f hf, fun h3 => ⟨mk w0 (fun _ => 0), mk_frozen h3 _ _⟩⟩

/-- The frozen proper six-colourings of `H_n`, as a type. -/
abbrev FrozenCol (n : ℕ) : Type := {f : VH n → Fin 6 // Frozen (Hn n) f}

theorem palSub_base (f : VH n → Fin 6) (hf : Frozen (Hn n) f) (i : ZMod n) :
    PalSub f i (((r3 i).val : ℕ) : ZMod n) := by
  have key : ∀ q r : ℕ, PalSub f ((3 * q + r : ℕ) : ZMod n) ((r : ℕ) : ZMod n) := by
    intro q
    induction q with
    | zero => intro r t; exact ⟨t, by simp⟩
    | succ q ih =>
      intro r t
      have e : ((3 * (q + 1) + r : ℕ) : ZMod n) = ((3 * q + r : ℕ) : ZMod n) + 3 := by
        push_cast; ring
      rw [e]
      obtain ⟨s, hs⟩ := palSub_three f hf ((3 * q + r : ℕ) : ZMod n) t
      obtain ⟨u, hu⟩ := ih r s
      exact ⟨u, hs.trans hu⟩
  have := key (i.val / 3) (i.val % 3)
  rw [Nat.div_add_mod, ZMod.natCast_zmod_val] at this
  exact this

/-- Read the base window (bags `0, 1, 2`) of a colouring, twisted by `e`. -/
def wFun (f : VH n → Fin 6) (e : Fin 3 → Fin 2) (p : Fin 3 × Fin 2) : Fin 6 :=
  f ⟨((p.1.val : ℕ) : ZMod n), p.2 + e p.1⟩

theorem cast_eq_bag3 (a : Fin 3) : (((a.val : ℕ) : ZMod n)) = bag3 (1 : ZMod n) a := by
  fin_cases a
  · simp [bag3]
  · simp [bag3]
  · simp [bag3, one_add_one_eq_two]

theorem wFun_bij (f : VH n → Fin 6) (hf : Frozen (Hn n) f) (e : Fin 3 → Fin 2) :
    Function.Bijective (wFun f e) := by
  refine (Fintype.bijective_iff_injective_and_card _).2 ⟨?_, by simp⟩
  rintro ⟨a, s⟩ ⟨a', s'⟩ h
  have h' : win f 1 (a, s + e a) = win f 1 (a', s' + e a') := by
    show f ⟨bag3 1 a, _⟩ = f ⟨bag3 1 a', _⟩
    rw [← cast_eq_bag3, ← cast_eq_bag3]; exact h
  have := (win_bij f hf 1).1 h'
  obtain ⟨h1, h2⟩ := Prod.ext_iff.1 this
  simp only at h1 h2
  subst h1
  rw [add_right_cancel h2]

noncomputable def wOf (f : FrozenCol n) (e : Fin 3 → Fin 2) : Fin 3 × Fin 2 ≃ Fin 6 :=
  Equiv.ofBijective (wFun f.1 e) (wFun_bij f.1 f.2 e)

/-- Orientation bits of a colouring relative to pair-partition data `w`. -/
def bits (w : Fin 3 × Fin 2 ≃ Fin 6) (f : VH n → Fin 6) (i : ZMod n) : Fin 2 :=
  (w.symm (f ⟨i, 0⟩)).2

theorem fin2_neg : ∀ x : Fin 2, -x = x := by decide
theorem fin2_add_self : ∀ s x : Fin 2, s + x + x = s := by decide
theorem fin2_of_ne : ∀ s x y : Fin 2, (s = 0 → y = x) → (s ≠ 0 → y ≠ x) → y = s + x := by decide

theorem wOf_symm (f : FrozenCol n) (e : Fin 3 → Fin 2) (i : ZMod n) (t : Fin 2) :
    ((wOf f e).symm (f.1 ⟨i, t⟩)).1 = r3 i := by
  obtain ⟨s, hs⟩ := palSub_base f.1 f.2 i t
  have : f.1 ⟨i, t⟩ = wOf f e (r3 i, s - e (r3 i)) := by
    show _ = f.1 ⟨(((r3 i).val : ℕ) : ZMod n), s - e (r3 i) + e (r3 i)⟩
    rw [sub_add_cancel]; exact hs
  rw [this, Equiv.symm_apply_apply]

theorem mk_wOf (f : FrozenCol n) (e : Fin 3 → Fin 2) :
    mk (wOf f e) (bits (wOf f e) f.1) = f.1 := by
  funext ⟨i, s⟩
  show wOf f e (r3 i, s + (((wOf f e).symm (f.1 ⟨i, 0⟩)).2)) = f.1 ⟨i, s⟩
  have hs : (wOf f e).symm (f.1 ⟨i, s⟩) = (r3 i, ((wOf f e).symm (f.1 ⟨i, s⟩)).2) :=
    Prod.ext (wOf_symm f e i s) rfl
  have h0 : (wOf f e).symm (f.1 ⟨i, 0⟩) = (r3 i, ((wOf f e).symm (f.1 ⟨i, 0⟩)).2) :=
    Prod.ext (wOf_symm f e i 0) rfl
  have key : ((wOf f e).symm (f.1 ⟨i, s⟩)).2 = s + ((wOf f e).symm (f.1 ⟨i, 0⟩)).2 := by
    apply fin2_of_ne
    · intro h; rw [h]
    · intro h e2
      have : (wOf f e).symm (f.1 ⟨i, s⟩) = (wOf f e).symm (f.1 ⟨i, 0⟩) := by
        rw [hs, h0, e2]
      have := (wOf f e).symm.injective this
      have hadj : (Hn n).adj ⟨i, s⟩ ⟨i, 0⟩ = true := by
        rw [Hn_adj_iff]; exact Or.inl ⟨rfl, h⟩
      exact f.2.1 _ _ hadj this
  rw [← key, ← hs, Equiv.apply_symm_apply]

theorem bits_wOf_cast (f : FrozenCol n) (e : Fin 3 → Fin 2) (a : Fin 3) :
    bits (wOf f e) f.1 ((a.val : ℕ) : ZMod n) = e a := by
  have : f.1 ⟨((a.val : ℕ) : ZMod n), 0⟩ = wOf f e (a, - e a) := by
    show _ = f.1 ⟨((a.val : ℕ) : ZMod n), - e a + e a⟩
    rw [neg_add_cancel]
  show ((wOf f e).symm (f.1 ⟨((a.val : ℕ) : ZMod n), 0⟩)).2 = e a
  rw [this, Equiv.symm_apply_apply]
  exact fin2_neg _

theorem wOf_mk (h3 : 3 ∣ n) (w : Fin 3 × Fin 2 ≃ Fin 6) (b : ZMod n → Fin 2) :
    wOf ⟨mk w b, mk_frozen h3 w b⟩ (fun a => b ((a.val : ℕ) : ZMod n)) = w := by
  apply Equiv.ext
  rintro ⟨a, s⟩
  show w (r3 ((a.val : ℕ) : ZMod n), s + b ((a.val : ℕ) : ZMod n) + b ((a.val : ℕ) : ZMod n)) = w (a, s)
  rw [r3_cast h3, fin2_add_self]

theorem bits_mk (w : Fin 3 × Fin 2 ≃ Fin 6) (b : ZMod n → Fin 2) : bits w (mk w b) = b := by
  funext i
  show (w.symm (w (r3 i, 0 + b i))).2 = b i
  rw [Equiv.symm_apply_apply, zero_add]

/-- The counting bijection: a frozen colouring together with three auxiliary bits is the same
as pair-partition data (a bijection `Fin 3 × Fin 2 ≃ Fin 6`) together with one orientation
bit per bag. -/
noncomputable def countEquiv (h3 : 3 ∣ n) :
    FrozenCol n × (Fin 3 → Fin 2) ≃ (Fin 3 × Fin 2 ≃ Fin 6) × (ZMod n → Fin 2) where
  toFun x := (wOf x.1 x.2, bits (wOf x.1 x.2) x.1.1)
  invFun y := (⟨mk y.1 y.2, mk_frozen h3 y.1 y.2⟩, fun a => y.2 ((a.val : ℕ) : ZMod n))
  left_inv := by
    rintro ⟨f, e⟩
    refine Prod.ext (Subtype.ext (mk_wOf f e)) ?_
    funext a
    exact bits_wOf_cast f e a
  right_inv := by
    rintro ⟨w, b⟩
    have h := wOf_mk h3 w b
    refine Prod.ext h ?_
    show bits (wOf ⟨mk w b, mk_frozen h3 w b⟩ (fun a => b ((a.val : ℕ) : ZMod n))) (mk w b) = b
    rw [h, bits_mk]

/-- **(B)** When `3 ∣ n` (and `n ≥ 1`) there are exactly `90 * 2 ^ n` frozen proper
six-colourings of `H_n` (labelled vertices, labelled colours). -/
theorem card_frozen (n : ℕ) [NeZero n] (h3 : 3 ∣ n) : Nat.card (FrozenCol n) = 90 * 2 ^ n := by
  have h := Nat.card_congr (countEquiv (n := n) h3)
  rw [Nat.card_prod, Nat.card_prod] at h
  have h8 : Nat.card (Fin 3 → Fin 2) = 8 := by
    rw [Nat.card_eq_fintype_card]; simp
  have h720 : Nat.card (Fin 3 × Fin 2 ≃ Fin 6) = 720 := by
    rw [Nat.card_eq_fintype_card, Fintype.card_equiv w0]; simp [Nat.factorial]
  have h2n : Nat.card (ZMod n → Fin 2) = 2 ^ n := by
    rw [Nat.card_fun, Nat.card_zmod, Nat.card_fin]
  rw [h8, h720, h2n] at h
  omega

end Count

/-! ## The reconfiguration graph as a Mathlib `SimpleGraph`; components -/

/-- The reconfiguration graph `R_k(G)`: vertices are the proper `k`-colourings (surjectivity
not required), edges join colourings that differ at exactly one vertex. -/
def RGraph (G : SGraph V) (k : ℕ) : SimpleGraph {f : V → Fin k // Proper G f} where
  Adj f g := RAdj f.1 g.1
  symm := by
    rintro f g ⟨v, hne, hag⟩
    exact ⟨v, fun e => hne e.symm, fun w hw => (hag w hw).symm⟩
  loopless := ⟨by
    rintro f ⟨v, hne, _⟩
    exact hne rfl⟩

/-- A frozen colouring is an isolated vertex of `R_k(G)`: it has no neighbour. -/
theorem frozen_isolated (G : SGraph V) {k : ℕ} (f g : {f : V → Fin k // Proper G f})
    (hf : Frozen G f.1) : ¬ (RGraph G k).Adj f g :=
  fun h => hf.2 g.1 g.2 h

/-- Conversely an isolated vertex of `R_k(G)` is a frozen colouring. -/
theorem frozen_iff_isolated (G : SGraph V) {k : ℕ} (f : {f : V → Fin k // Proper G f}) :
    Frozen G f.1 ↔ ∀ g, ¬ (RGraph G k).Adj f g :=
  ⟨fun hf g => frozen_isolated G f g hf, fun h => ⟨f.2, fun g hg => h ⟨g, hg⟩⟩⟩

/-- The component of a frozen colouring is a singleton. -/
theorem frozen_reachable_eq (G : SGraph V) {k : ℕ} (f g : {f : V → Fin k // Proper G f})
    (hf : Frozen G f.1) (h : (RGraph G k).Reachable f g) : f = g := by
  obtain ⟨p⟩ := h
  cases p with
  | nil => rfl
  | cons hadj _ => exact absurd hadj (frozen_isolated G f _ hf)

/-- `Mixing` (the repository's walk-based definition) agrees with Mathlib preconnectedness
of `RGraph` in the direction used here: a path gives reachability. -/
theorem reachable_of_path (G : SGraph V) {k : ℕ} {f g : V → Fin k} (hf : Proper G f)
    (hg : Proper G g) (h : Path G f g) : (RGraph G k).Reachable ⟨f, hf⟩ ⟨g, hg⟩ := by
  induction h with
  | refl f => exact SimpleGraph.Reachable.refl _
  | @step f m g hm hadj _ ih =>
    exact SimpleGraph.Reachable.trans (SimpleGraph.Adj.reachable (G := RGraph G k)
      (u := ⟨f, hf⟩) (v := ⟨m, hm⟩) hadj) (ih hm hg)

/-- Every frozen colouring is its own component, so one further proper colouring that is not
frozen gives at least `#frozen + 1` components. -/
theorem components_ge [Finite V] (G : SGraph V) (k : ℕ) (g0 : {f : V → Fin k // Proper G f})
    (hg0 : ¬ Frozen G g0.1) :
    Nat.card {f : V → Fin k // Frozen G f} + 1 ≤ Nat.card (RGraph G k).ConnectedComponent := by
  classical
  let φ : Option {f : V → Fin k // Frozen G f} → (RGraph G k).ConnectedComponent := fun o =>
    match o with
    | some f => (RGraph G k).connectedComponentMk ⟨f.1, f.2.1⟩
    | none => (RGraph G k).connectedComponentMk g0
  have hφ : Function.Injective φ := by
    intro a b hab
    match a, b with
    | some f, some f' =>
      have := frozen_reachable_eq G ⟨f.1, f.2.1⟩ ⟨f'.1, f'.2.1⟩ f.2
        (SimpleGraph.ConnectedComponent.exact hab)
      have e : f.1 = f'.1 := by injection this
      rw [Subtype.ext e]
    | some f, none =>
      have := frozen_reachable_eq G ⟨f.1, f.2.1⟩ g0 f.2 (SimpleGraph.ConnectedComponent.exact hab)
      exact absurd (this ▸ f.2) hg0
    | none, some f =>
      have := frozen_reachable_eq G ⟨f.1, f.2.1⟩ g0 f.2
        (SimpleGraph.ConnectedComponent.exact hab.symm)
      exact absurd (this ▸ f.2) hg0
    | none, none => rfl
  haveI : Finite (RGraph G k).ConnectedComponent :=
    Finite.of_surjective (RGraph G k).connectedComponentMk Quot.mk_surjective
  have h := Nat.card_le_card_of_injective φ hφ
  rw [Finite.card_option] at h
  exact h

theorem not_frozen_of_unused [DecidableEq V] (G : SGraph V) {k : ℕ} (f : V → Fin k) (v : V)
    (c : Fin k) (hc : ∀ w, f w ≠ c) : ¬ Frozen G f := by
  intro hf
  obtain ⟨w, _, hw⟩ := ((frozen_iff_sees G f).1 hf).2 v c (fun e => hc v e.symm)
  exact hc w hw

/-! ## An explicit proper five-colouring of `H_n` for every `n ≥ 4` -/

theorem val_lt' {n : ℕ} [NeZero n] (i : ZMod n) : i.val < n := ZMod.val_lt i

/-- A colouring of `H_n` given by position: vertex `(i, s)` gets `c i.val s.val`. -/
theorem ofPos_proper {n k : ℕ} [NeZero n] (c : ℕ → ℕ → Fin k)
    (h0 : ∀ p, p < n → c p 0 ≠ c p 1)
    (h1 : ∀ p, p < n → ∀ s t, s < 2 → t < 2 → c p s ≠ c ((p + 1) % n) t) :
    Proper (Hn n) (fun x => c x.1.val x.2.val) := by
  rintro ⟨i, s⟩ ⟨j, t⟩ hadj
  rw [Hn_adj_iff] at hadj
  have hi := val_lt' i
  rcases hadj with ⟨e, hst⟩ | ⟨_, e | e⟩
  · subst e
    show c i.val s.val ≠ c i.val t.val
    have : (s.val = 0 ∧ t.val = 1) ∨ (s.val = 1 ∧ t.val = 0) := by
      have := s.isLt
      have := t.isLt
      have : s.val ≠ t.val := fun e => hst (Fin.ext e)
      omega
    rcases this with ⟨a, b⟩ | ⟨a, b⟩
    · rw [a, b]; exact h0 _ hi
    · rw [a, b]; exact (h0 _ hi).symm
  · show c i.val s.val ≠ c j.val t.val
    rw [e, val_succ]
    exact h1 _ hi _ _ s.isLt t.isLt
  · show c i.val s.val ≠ c j.val t.val
    rw [e, val_succ]
    exact (h1 _ (val_lt' j) _ _ t.isLt s.isLt).symm

/-- The paper's five-colouring by position (colours shifted to start at `0`): for odd `n`
the first `n - 3` bags alternate `{0,1}, {2,3}` and the last three bags are
`{0,4}, {1,2}, {3,4}`; for even `n` all bags alternate `{0,1}, {2,3}`. -/
def c5 (n p s : ℕ) : ℕ :=
  if n % 2 = 0 ∨ p + 3 < n then 2 * (p % 2) + s % 2
  else if p + 3 = n then (if s % 2 = 0 then 0 else 4)
  else if p + 2 = n then 1 + s % 2
  else 3 + s % 2

theorem c5_lt (n p s : ℕ) : c5 n p s < 5 := by
  unfold c5; split_ifs <;> omega

def five (n : ℕ) : VH n → Fin 5 := fun x => ⟨c5 n x.1.val x.2.val, c5_lt _ _ _⟩

theorem five_proper (n : ℕ) [NeZero n] (hn : 4 ≤ n) : Proper (Hn n) (five n) := by
  apply ofPos_proper (fun p s => (⟨c5 n p s, c5_lt _ _ _⟩ : Fin 5))
  · intro p hp e
    have e' : c5 n p 0 = c5 n p 1 := congrArg Fin.val e
    simp only [c5] at e'
    split_ifs at e' <;> omega
  · intro p hp s t hs ht e
    have e' : c5 n p s = c5 n ((p + 1) % n) t := congrArg Fin.val e
    clear e
    have hq : ((p + 1) % n = p + 1 ∧ p + 1 < n) ∨ ((p + 1) % n = 0 ∧ p + 1 = n) := by
      by_cases h : p + 1 < n
      · exact Or.inl ⟨Nat.mod_eq_of_lt h, h⟩
      · have : p + 1 = n := by omega
        exact Or.inr ⟨by rw [this, Nat.mod_self], this⟩
    rcases hq with ⟨hq, hq'⟩ | ⟨hq, hq'⟩
    · rw [hq] at e'
      simp only [c5] at e'
      split_ifs at e' <;> omega
    · rw [hq] at e'
      simp only [c5] at e'
      split_ifs at e' <;> omega

theorem Hn_colourable5 (n : ℕ) [NeZero n] (hn : 4 ≤ n) : Colourable (Hn n) 5 :=
  ⟨five n, five_proper n hn⟩

/-- The five-colouring regarded as a six-colouring (colour `5` unused). -/
def five6 (n : ℕ) : VH n → Fin 6 := fun x => ⟨(five n x).val, by have := (five n x).isLt; omega⟩

theorem five6_proper (n : ℕ) [NeZero n] (hn : 4 ≤ n) : Proper (Hn n) (five6 n) := by
  intro a b hab e
  apply five_proper n hn a b hab
  apply Fin.ext
  have e' : (five6 n a).val = (five6 n b).val := congrArg Fin.val e
  exact e'

theorem five6_not_frozen (n : ℕ) [NeZero n] : ¬ Frozen (Hn n) (five6 n) := by
  apply not_frozen_of_unused (Hn n) (five6 n) ⟨0, 0⟩ ⟨5, by decide⟩
  intro w e
  have h := (five n w).isLt
  have e' : (five n w).val = 5 := congrArg Fin.val e
  omega

/-- **(C)** For `3 ∣ n`, `n ≥ 4` (so `n ≥ 6`): every frozen colouring is an isolated vertex of
`R_6(H_n)`, a non-frozen proper six-colouring exists, and hence `R_6(H_n)` has at least
`90 * 2 ^ n + 1` connected components (Mathlib's `SimpleGraph.ConnectedComponent`). -/
theorem components_R6 (n : ℕ) [NeZero n] (h3 : 3 ∣ n) (hn : 4 ≤ n) :
    90 * 2 ^ n + 1 ≤ Nat.card (RGraph (Hn n) 6).ConnectedComponent := by
  have h := components_ge (Hn n) 6 ⟨five6 n, five6_proper n hn⟩ (five6_not_frozen n)
  have hc : Nat.card {f : VH n → Fin 6 // Frozen (Hn n) f} = 90 * 2 ^ n := card_frozen n h3
  rw [hc] at h
  exact h

/-- In the repository's walk-based vocabulary: `R_6(H_n)` is disconnected. -/
theorem Hn_not_mixing6 (n : ℕ) [NeZero n] (h3 : 3 ∣ n) (hn : 4 ≤ n) : ¬ Mixing (Hn n) 6 := by
  intro hm
  have hf := mk_frozen h3 w0 (fun _ : ZMod n => (0 : Fin 2))
  have hp := hm _ _ hf.1 (five6_proper n hn)
  have := frozen_reachable_eq (Hn n) ⟨_, hf.1⟩ ⟨_, five6_proper n hn⟩ hf
    (reachable_of_path (Hn n) hf.1 (five6_proper n hn) hp)
  have e : mk w0 (fun _ : ZMod n => (0 : Fin 2)) = five6 n := congrArg Subtype.val this
  exact five6_not_frozen n (e ▸ hf)

/-! ## The remaining clauses: `χ(H_n) = 5`, `C_n` prime, induced subgraphs recolorable -/

theorem cast_ne_zero {n : ℕ} (k : ℕ) (hk : 0 < k) (hkn : k < n) : ((k : ℕ) : ZMod n) ≠ 0 := by
  intro h
  have := Nat.le_of_dvd hk ((ZMod.natCast_eq_zero_iff k n).1 h)
  omega

theorem zmod_one_ne_zero {n : ℕ} (hn : 2 ≤ n) : (1 : ZMod n) ≠ 0 := by
  have := cast_ne_zero (n := n) 1 (by decide) (by omega)
  simpa using this

theorem zmod_two_ne_zero {n : ℕ} (hn : 3 ≤ n) : (2 : ZMod n) ≠ 0 := by
  have := cast_ne_zero (n := n) 2 (by decide) (by omega)
  simpa using this

theorem zmod_three_ne_zero {n : ℕ} (hn : 4 ≤ n) : (3 : ZMod n) ≠ 0 := by
  have := cast_ne_zero (n := n) 3 (by decide) (by omega)
  simpa using this

theorem zmod_four_ne_zero {n : ℕ} (hn : 5 ≤ n) : (4 : ZMod n) ≠ 0 := by
  have := cast_ne_zero (n := n) 4 (by decide) (by omega)
  simpa using this

theorem Cyc_adj_succ {n : ℕ} (hn : 2 ≤ n) (i : ZMod n) : (Cyc n).adj i (i + 1) = true := by
  rw [Cyc_adj_iff]
  refine ⟨fun e => zmod_one_ne_zero hn ?_, Or.inl rfl⟩
  linear_combination -e

theorem Hn_adj_succ {n : ℕ} (hn : 2 ≤ n) (i : ZMod n) (s t : Fin 2) :
    (Hn n).adj ⟨i, s⟩ ⟨i + 1, t⟩ = true := by
  rw [Hn_adj_iff]
  refine Or.inr ⟨fun e => zmod_one_ne_zero hn ?_, Or.inl rfl⟩
  linear_combination -e

theorem Hn_adj_twin {n : ℕ} (i : ZMod n) : (Hn n).adj ⟨i, 0⟩ ⟨i, 1⟩ = true := by
  rw [Hn_adj_iff]
  exact Or.inl ⟨rfl, by decide⟩

theorem fin4_cover : ∀ a b c d x : Fin 4, a ≠ b → a ≠ c → a ≠ d → b ≠ c → b ≠ d → c ≠ d →
    x = a ∨ x = b ∨ x = c ∨ x = d := by decide

/-- Lower bound: for odd `n ≥ 3` the graph `H_n` is not 4-colourable (palettes of two
consecutive bags exhaust four colours, so palettes repeat with period two around an odd cycle). -/
theorem Hn_not_colourable4 (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (hn : 3 ≤ n) :
    ¬ Colourable (Hn n) 4 := by
  rintro ⟨f, hf⟩
  have hn2 : 2 ≤ n := by omega
  have hc : Nat.Coprime 2 n := (Nat.Prime.coprime_iff_not_dvd Nat.prime_two).2 (by omega)
  have hstep : ∀ i, PalSub f (i + 2) i := by
    intro i t
    have e2 : i + 1 + 1 = i + 2 := by ring
    have hx := fin4_cover (f ⟨i, 0⟩) (f ⟨i, 1⟩) (f ⟨i + 1, 0⟩) (f ⟨i + 1, 1⟩) (f ⟨i + 2, t⟩)
      (hf _ _ (Hn_adj_twin i)) (hf _ _ (Hn_adj_succ hn2 i 0 0)) (hf _ _ (Hn_adj_succ hn2 i 0 1))
      (hf _ _ (Hn_adj_succ hn2 i 1 0)) (hf _ _ (Hn_adj_succ hn2 i 1 1))
      (hf _ _ (Hn_adj_twin (i + 1)))
    have h0 := hf _ _ (Hn_adj_succ hn2 (i + 1) 0 t)
    have h1 := hf _ _ (Hn_adj_succ hn2 (i + 1) 1 t)
    rw [e2] at h0 h1
    rcases hx with h | h | h | h
    · exact ⟨0, h⟩
    · exact ⟨1, h⟩
    · exact absurd h.symm h0
    · exact absurd h.symm h1
  have key := step_one_of_coprime hc (PalSub f) (fun i t => ⟨t, rfl⟩)
    (fun i j k hij hjk t => by
      obtain ⟨s, hs⟩ := hij t
      obtain ⟨u, hu⟩ := hjk s
      exact ⟨u, hs.trans hu⟩)
    (fun i => by simpa using hstep i)
  obtain ⟨s, hs⟩ := key 0 0
  exact hf _ _ (Hn_adj_succ hn2 0 s 0) hs.symm

/-- `χ(H_n) = 5` for every odd `n ≥ 5`. -/
theorem Hn_isChi5 (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (h5 : 5 ≤ n) : IsChi (Hn n) 5 :=
  ⟨Hn_colourable5 n (by omega), fun _ hk hc =>
    Hn_not_colourable4 n hodd (by omega) (colourable_mono (Hn n) (by omega) hc)⟩

/-- For odd `n ≥ 5` divisible by three, `H_n` is not recolorable: `χ = 5` and `R_6` is
disconnected. -/
theorem Hn_not_recolorable (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (h5 : 5 ≤ n) (h3 : 3 ∣ n) :
    ¬ Recolorable (Hn n) :=
  fun h => Hn_not_mixing6 n h3 (by omega) (h 5 (Hn_isChi5 n hodd h5) 6 (Nat.le_refl _))

/-- A property of `ZMod n` that holds somewhere and fails somewhere has a boundary. -/
theorem exists_boundary {n : ℕ} [NeZero n] (P : ZMod n → Prop) (a x : ZMod n) (ha : P a)
    (hx : ¬ P x) : ∃ i, P i ∧ ¬ P (i + 1) := by
  by_contra hno
  have hno : ∀ i, P i → P (i + 1) := fun i hi => by
    by_contra h
    exact hno ⟨i, hi, h⟩
  have hall : ∀ k : ℕ, P (a + (k : ZMod n)) := by
    intro k
    induction k with
    | zero => simpa using ha
    | succ k ih =>
      have := hno _ ih
      rw [Nat.cast_succ, ← add_assoc]
      exact this
  have := hall (x - a).val
  rw [ZMod.natCast_zmod_val, add_sub_cancel] at this
  exact hx this

/-- `C_n` is prime for every `n ≥ 5`. -/
theorem Cyc_prime (n : ℕ) [NeZero n] (h5 : 5 ≤ n) : Prime (Cyc n) := by
  rintro ⟨S, ⟨_, hmod⟩, ⟨a, b, hab, ha, hb⟩, ⟨x, hx⟩⟩
  have h1 := zmod_one_ne_zero (n := n) (by omega)
  have h2 := zmod_two_ne_zero (n := n) (by omega)
  have h3 := zmod_three_ne_zero (n := n) (by omega)
  have h4 := zmod_four_ne_zero (n := n) (by omega)
  obtain ⟨i, hi, hi1⟩ := exists_boundary (fun v => S v = true) a x ha (by simp [hx])
  have hi1' : S (i + 1) = false := by simpa using hi1
  have hcomp : ∀ s, S s = true → (Cyc n).adj (i + 1) s = true := by
    rcases hmod (i + 1) hi1' with h | h
    · exact h
    · have := h i hi
      rw [(Cyc n).symm, Cyc_adj_succ (by omega)] at this
      cases this
  have hsub : ∀ s, S s = true → s = i ∨ s = i + 2 := by
    intro s hs
    rcases ((Cyc_adj_iff _ _).1 (hcomp s hs)).2 with e | e
    · right; rw [e]; ring
    · left; exact (add_right_cancel e).symm
  have hi2 : S (i + 2) = true := by
    rcases hsub a ha with e | e <;> rcases hsub b hb with e' | e'
    · exact absurd (e.trans e'.symm) hab
    · rw [← e']; exact hb
    · rw [← e]; exact ha
    · exact absurd (e.trans e'.symm) hab
  have hx' : S (i - 1) = false := by
    by_contra hne
    have ht : S (i - 1) = true := by simpa using hne
    rcases hsub _ ht with e | e
    · apply h1; linear_combination -e
    · apply h3; linear_combination -e
  rcases hmod (i - 1) hx' with h | h
  · rcases ((Cyc_adj_iff _ _).1 (h (i + 2) hi2)).2 with e | e
    · apply h2; linear_combination e
    · apply h4; linear_combination -e
  · have := h i hi
    have ht : (Cyc n).adj (i - 1) i = true := by
      have := Cyc_adj_succ (n := n) (by omega) (i - 1)
      rwa [sub_add_cancel] at this
    rw [ht] at this
    cases this

/-- From a degeneracy property to an elimination order in the sense of `elimB`. -/
theorem exists_elim [DecidableEq V] (G : SGraph V) (d : ℕ) :
    ∀ (m : ℕ) (T : Finset V), T.card = m →
      (∀ U : Finset V, U ⊆ T → U.Nonempty →
        ∃ v ∈ U, (U.filter (fun u => G.adj v u = true)).card ≤ d) →
      ∃ L : List V, L.Nodup ∧ (∀ u, u ∈ L ↔ u ∈ T) ∧ elimB G d L = true := by
  intro m
  induction m with
  | zero =>
    intro T hT _
    refine ⟨[], List.nodup_nil, ?_, rfl⟩
    intro u
    rw [Finset.card_eq_zero.1 hT]
    simp
  | succ m ih =>
    intro T hT hdeg
    have hne : T.Nonempty := by
      rw [← Finset.card_pos]; omega
    obtain ⟨v, hv, hvd⟩ := hdeg T (Finset.Subset.refl _) hne
    obtain ⟨L, hnd, hL, hE⟩ := ih (T.erase v) (by rw [Finset.card_erase_of_mem hv]; omega)
      (fun U hU hUne => hdeg U (hU.trans (Finset.erase_subset _ _)) hUne)
    have hvL : v ∉ L := by
      intro h
      have := (hL v).1 h
      simp at this
    refine ⟨v :: L, List.nodup_cons.2 ⟨hvL, hnd⟩, ?_, ?_⟩
    · intro u
      rw [List.mem_cons, hL, Finset.mem_erase]
      constructor
      · rintro (e | ⟨_, h⟩)
        · rw [e]; exact hv
        · exact h
      · intro h
        by_cases e : u = v
        · exact Or.inl e
        · exact Or.inr ⟨e, h⟩
    · simp only [elimB, Bool.and_eq_true, decide_eq_true_eq]
      refine ⟨⟨hvL, ?_⟩, hE⟩
      have hnd' : (L.filter (fun u => G.adj v u)).Nodup := hnd.filter _
      rw [← List.toFinset_card_of_nodup hnd']
      refine le_trans (Finset.card_le_card ?_) hvd
      intro u hu
      rw [List.mem_toFinset, List.mem_filter] at hu
      rw [Finset.mem_filter]
      exact ⟨Finset.mem_of_mem_erase ((hL u).1 hu.1), hu.2⟩

theorem fin2_alt : ∀ a b c : Fin 2, a ≠ b → b ≠ c → a = c := by decide

/-- An odd cycle (`n ≥ 3`) is not 2-colourable. -/
theorem Cyc_not_two_colourable (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (hn : 3 ≤ n)
    (g : ZMod n → Fin 2) (hg : ∀ a b, (Cyc n).adj a b = true → g a ≠ g b) : False := by
  have hc : Nat.Coprime 2 n := (Nat.Prime.coprime_iff_not_dvd Nat.prime_two).2 (by omega)
  have hstep : ∀ i, g (i + 2) = g i := by
    intro i
    have h1 := hg _ _ (Cyc_adj_succ (n := n) (by omega) i)
    have h2 := hg _ _ (Cyc_adj_succ (n := n) (by omega) (i + 1))
    have e2 : i + 1 + 1 = i + 2 := by ring
    rw [e2] at h2
    exact (fin2_alt _ _ _ h1 h2).symm
  have key := step_one_of_coprime hc (fun i j => g i = g j) (fun _ => rfl)
    (fun _ _ _ h h' => h.trans h') (fun i => by simpa using hstep i)
  exact hg _ _ (Cyc_adj_succ (n := n) (by omega) 0) (key 0).symm

/-- Every induced subgraph of `C_n` (all `2 ^ n` vertex subsets, the empty one and `C_n`
itself included) is recolorable, for every odd `n ≥ 3`. -/
theorem Cyc_induced_recolorable (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (hn : 3 ≤ n)
    (S : ZMod n → Bool) : Recolorable (induce (Cyc n) S) := by
  classical
  have hmemT : ∀ u, u ∈ (Finset.univ.filter (fun v => S v = true)) ↔ S u = true := by
    intro u; simp
  by_cases hall : ∀ v, S v = true
  · -- the whole cycle: width 2, not 2-colourable
    obtain ⟨L, _, hL, hE⟩ := exists_elim (Cyc n) 2 _ (Finset.univ.filter (fun v => S v = true)) rfl
      (by
        intro U _ hUne
        obtain ⟨v, hv⟩ := hUne
        refine ⟨v, hv, ?_⟩
        refine le_trans (Finset.card_le_card (t := {v + 1, v - 1}) ?_) Finset.card_le_two
        intro u hu
        rw [Finset.mem_filter, Cyc_adj_iff] at hu
        rw [Finset.mem_insert, Finset.mem_singleton]
        rcases hu.2.2 with e | e
        · exact Or.inl e
        · right; rw [e]; ring)
    refine recolorable_induce (Cyc n) S 2 L (fun u => (hL u).trans (hmemT u)) hE ?_
    rintro _ _ ⟨f, hf⟩
    exact Cyc_not_two_colourable n hodd hn (fun v => f ⟨v, hall v⟩)
      (fun a b hab => hf ⟨a, hall a⟩ ⟨b, hall b⟩ hab)
  · obtain ⟨x, hx⟩ := not_forall.1 hall
    by_cases hedge : ∃ a b, S a = true ∧ S b = true ∧ (Cyc n).adj a b = true
    · -- a proper subset spanning an edge: width 1 (a disjoint union of paths), not 1-colourable
      obtain ⟨L, _, hL, hE⟩ := exists_elim (Cyc n) 1 _ (Finset.univ.filter (fun v => S v = true)) rfl
        (by
          intro U hU hUne
          obtain ⟨a, ha⟩ := hUne
          have hxU : x ∉ U := fun h => hx ((hmemT x).1 (hU h))
          obtain ⟨i, hi, hi1⟩ := exists_boundary (fun v => v ∈ U) a x ha hxU
          refine ⟨i, hi, ?_⟩
          refine le_trans (Finset.card_le_card (t := {i - 1}) ?_) (by simp)
          intro u hu
          rw [Finset.mem_filter, Cyc_adj_iff] at hu
          rw [Finset.mem_singleton]
          rcases hu.2.2 with e | e
          · exact absurd (e ▸ hu.1) hi1
          · rw [e]; ring)
      refine recolorable_induce (Cyc n) S 1 L (fun u => (hL u).trans (hmemT u)) hE ?_
      rintro _ _ ⟨f, hf⟩
      obtain ⟨a, b, ha, hb, hab⟩ := hedge
      exact hf ⟨a, ha⟩ ⟨b, hb⟩ hab (Subsingleton.elim _ _)
    · -- an edgeless subset: width 0, not 0-colourable when non-empty
      obtain ⟨L, _, hL, hE⟩ := exists_elim (Cyc n) 0 _ (Finset.univ.filter (fun v => S v = true)) rfl
        (by
          intro U hU hUne
          obtain ⟨a, ha⟩ := hUne
          refine ⟨a, ha, ?_⟩
          rw [Nat.le_zero, Finset.card_eq_zero, Finset.filter_eq_empty_iff]
          intro u hu hau
          exact hedge ⟨a, u, (hmemT a).1 (hU ha), (hmemT u).1 (hU hu), hau⟩)
      refine recolorable_induce (Cyc n) S 0 L (fun u => (hL u).trans (hmemT u)) hE ?_
      rintro u hu ⟨f, _⟩
      exact (f ⟨u, hu⟩).elim0

/-- Non-vacuity of the recolorability clause: for odd `n ≥ 3` the whole cycle has chromatic
number exactly 3, so the clause asserts that `C_n` is `l`-mixing for every `l ≥ 4`. -/
theorem Cyc_whole_isChi3 (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (hn : 3 ≤ n) :
    IsChi (induce (Cyc n) (fun _ => true)) 3 := by
  refine ⟨?_, ?_⟩
  · -- colour position p by p % 2, except the last position, which gets colour 2
    refine ⟨fun x => ⟨if x.1.val + 1 = n then 2 else x.1.val % 2, by split_ifs <;> omega⟩, ?_⟩
    rintro ⟨a, _⟩ ⟨b, _⟩ hab e
    have hab' : (Cyc n).adj a b = true := hab
    have e' : (if a.val + 1 = n then 2 else a.val % 2) = (if b.val + 1 = n then 2 else b.val % 2) :=
      congrArg Fin.val e
    have ha := val_lt' a
    have hb := val_lt' b
    rw [Cyc_adj_iff] at hab'
    rcases hab'.2 with h | h
    · have hv := val_succ a
      rw [← h] at hv
      by_cases hw : a.val + 1 < n
      · rw [Nat.mod_eq_of_lt hw] at hv
        split_ifs at e' <;> omega
      · have : a.val + 1 = n := by omega
        rw [this, Nat.mod_self] at hv
        split_ifs at e' <;> omega
    · have hv := val_succ b
      rw [← h] at hv
      by_cases hw : b.val + 1 < n
      · rw [Nat.mod_eq_of_lt hw] at hv
        split_ifs at e' <;> omega
      · have : b.val + 1 = n := by omega
        rw [this, Nat.mod_self] at hv
        split_ifs at e' <;> omega
  · intro k hk ⟨f, hf⟩
    obtain ⟨g, hg⟩ := colourable_mono (induce (Cyc n) (fun _ => true)) (show k ≤ 2 by omega) ⟨f, hf⟩
    exact Cyc_not_two_colourable n hodd hn (fun v => g ⟨v, rfl⟩)
      (fun a b hab => hg ⟨a, rfl⟩ ⟨b, rfl⟩ hab)

/-- So the recolorability clause really asserts that `C_n` is `l`-mixing for every `l ≥ 4`. -/
theorem Cyc_whole_mixing (n : ℕ) [NeZero n] (hodd : n % 2 = 1) (hn : 3 ≤ n) (l : ℕ)
    (hl : 4 ≤ l) : Mixing (induce (Cyc n) (fun _ => true)) l :=
  Cyc_induced_recolorable n hodd hn _ 3 (Cyc_whole_isChi3 n hodd hn) l hl

/-! ## The proposition, assembled -/

/-- **Proposition (frozen colourings in odd-cycle blowups), full stated scope.**
For every odd `n ≥ 5`: `C_n` is prime; every induced subgraph of `C_n` is recolorable;
`H_n = C_n[K_2]` has chromatic number 5; `H_n` has a frozen proper colouring with the six
labelled colours iff `3 ∣ n`; and when `3 ∣ n` there are exactly `90 * 2 ^ n` frozen labelled
colourings and `R_6(H_n)` has at least `90 * 2 ^ n + 1` connected components. -/
theorem cycle_blowup_frozen (n : ℕ) (hodd : n % 2 = 1) (h5 : 5 ≤ n) :
    Prime (Cyc n) ∧
    (∀ S : ZMod n → Bool, Recolorable (induce (Cyc n) S)) ∧
    IsChi (Hn n) 5 ∧
    ((∃ f : VH n → Fin 6, Frozen (Hn n) f) ↔ 3 ∣ n) ∧
    (3 ∣ n → Nat.card {f : VH n → Fin 6 // Frozen (Hn n) f} = 90 * 2 ^ n ∧
      90 * 2 ^ n + 1 ≤ Nat.card (RGraph (Hn n) 6).ConnectedComponent) := by
  haveI : NeZero n := ⟨by omega⟩
  exact ⟨Cyc_prime n h5, Cyc_induced_recolorable n hodd (by omega), Hn_isChi5 n hodd h5,
    frozen_exists_iff n, fun h3 => ⟨card_frozen n h3, components_R6 n h3 (by omega)⟩⟩

/-! ## Bindings, sanity checks and sharpness of the stated ranges -/

/-- A frozen six-colouring of `H_n` uses all six labelled colours. -/
theorem frozen_surjective {n : ℕ} (f : VH n → Fin 6) (hf : Frozen (Hn n) f) :
    Function.Surjective f := by
  intro c
  obtain ⟨p, hp⟩ := win_surj f hf 0 c
  exact ⟨_, hp⟩

/-- Both readings of "a frozen proper coloring with the six labeled colors" agree: a frozen
colouring into `Fin 6` automatically uses all six colours. -/
theorem frozen_onto_exists_iff (n : ℕ) [NeZero n] :
    (∃ f : VH n → Fin 6, Frozen (Hn n) f ∧ Function.Surjective f) ↔ 3 ∣ n := by
  rw [← frozen_exists_iff n]
  exact ⟨fun ⟨f, hf, _⟩ => ⟨f, hf⟩, fun ⟨f, hf⟩ => ⟨f, hf, frozen_surjective f hf⟩⟩

/-- Non-vacuity on the negative side: `H_5` has no frozen six-colouring. -/
theorem no_frozen_five : ¬ ∃ f : VH 5 → Fin 6, Frozen (Hn 5) f := by
  rw [frozen_exists_iff 5]
  decide

theorem path_of_walk (G : SGraph V) {k : ℕ} {f g : {f : V → Fin k // Proper G f}}
    (p : (RGraph G k).Walk f g) : Path G f.1 g.1 := by
  induction p with
  | nil => exact Path.refl _
  | cons hadj _ ih => exact Path.step (Subtype.property _) hadj ih

/-- The repository's `Mixing` is Mathlib preconnectedness of `RGraph`. -/
theorem mixing_iff_preconnected (G : SGraph V) (k : ℕ) :
    Mixing G k ↔ (RGraph G k).Preconnected := by
  constructor
  · intro h f g
    exact reachable_of_path G f.2 g.2 (h f.1 g.1 f.2 g.2)
  · intro h f g hf hg
    obtain ⟨p⟩ := h ⟨f, hf⟩ ⟨g, hg⟩
    exact path_of_walk G p

/-- The count as a `Fintype.card`, for any `Fintype` instance. -/
theorem card_frozen_fintype (n : ℕ) [NeZero n] (h3 : 3 ∣ n)
    [Fintype {f : VH n → Fin 6 // Frozen (Hn n) f}] :
    Fintype.card {f : VH n → Fin 6 // Frozen (Hn n) f} = 90 * 2 ^ n := by
  rw [← Nat.card_eq_fintype_card]
  exact card_frozen n h3

/-- Sharpness of the range in (C): `H_3 = K_6`, every proper six-colouring is frozen, and
`R_6(H_3)` has exactly `90 * 2 ^ 3 = 720` components, not `721`. -/
theorem H3_complete : ∀ x y : VH 3, x ≠ y → (Hn 3).adj x y = true := by decide

theorem H3_proper_frozen (f : VH 3 → Fin 6) (hf : Proper (Hn 3) f) : Frozen (Hn 3) f := by
  rw [frozen_iff_sees]
  refine ⟨hf, ?_⟩
  have hinj : Function.Injective f := by
    intro x y e
    by_contra hne
    exact hf x y (H3_complete x y hne) e
  have hbij := (Fintype.bijective_iff_injective_and_card f).2 ⟨hinj, by decide⟩
  intro v c hc
  obtain ⟨w, hw⟩ := hbij.2 c
  refine ⟨w, H3_complete w v ?_, hw⟩
  intro e
  apply hc
  rw [← hw, e]

theorem components_R6_three :
    Nat.card (RGraph (Hn 3) 6).ConnectedComponent = 90 * 2 ^ 3 := by
  have hbij : Function.Bijective (RGraph (Hn 3) 6).connectedComponentMk :=
    ⟨fun f g h => frozen_reachable_eq _ f g (H3_proper_frozen f.1 f.2)
      (SimpleGraph.ConnectedComponent.exact h), Quot.mk_surjective⟩
  rw [← Nat.card_congr (Equiv.ofBijective _ hbij), ← card_frozen 3 (by decide)]
  exact Nat.card_congr (Equiv.subtypeEquivRight (fun f => ⟨H3_proper_frozen f, fun h => h.1⟩))

/-- Sanity: `Prime` is not vacuous, and the range `n ≥ 5` is sharp: `C_4` is not prime. -/
theorem Cyc4_not_prime : ¬ Prime (Cyc 4) := fun h =>
  h ⟨fun v => decide (v.val % 2 = 0), by unfold NontrivialModule IsModule; decide⟩

/-- Binding at `n = 9`: `Cyc 9` has the adjacency rule of the certified `C9`. -/
theorem Cyc9_matches_C9 : ∀ u v : ZMod 9, (Cyc 9).adj u v =
    (decide ((u.val + 1) % 9 = v.val) || decide ((v.val + 1) % 9 = u.val)) := by decide

/-- Binding at `n = 9`: the five-colouring is the archived one. -/
theorem five9_archived : ∀ (v : ZMod 9) (s : Fin 2), (five 9 ⟨v, s⟩).val =
    [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 4, 1, 2, 3, 4].getD (2 * v.val + s.val) 0 := by
  decide

/-- Binding at `n = 9`: the standard frozen colouring is the archived `six`. -/
theorem six9_archived : ∀ (v : ZMod 9) (s : Fin 2),
    (mk w0 (fun _ => 0) (⟨v, s⟩ : VH 9)).val = (2 * v.val + s.val) % 6 := by
  decide

/-! ## The count in the paper's form: ordered pair-partitions times orientation bits -/

/-- An ordered partition of the six colours into three pairs: `p c` is the index of the pair
containing colour `c`, and every index class has exactly two colours. -/
abbrev PairPartition : Type :=
  {p : Fin 6 → Fin 3 // ∀ j, (Finset.univ.filter (fun c => p c = j)).card = 2}

/-- There are `6! / (2!)^3 = 90` ordered partitions of six colours into three pairs. -/
theorem card_pairPartition : Fintype.card PairPartition = 90 := by decide +kernel

/-- The pair index of a colour with respect to pair-partition data `w`. -/
def classOf (w : Fin 3 × Fin 2 ≃ Fin 6) (c : Fin 6) : Fin 3 := (w.symm c).1

theorem fin2_cases : ∀ u : Fin 2, u = 0 ∨ u = 1 := by decide

theorem classOf_fibre (w : Fin 3 × Fin 2 ≃ Fin 6) (j : Fin 3) :
    Finset.univ.filter (fun c => classOf w c = j) = {w (j, 0), w (j, 1)} := by
  ext c
  simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_insert,
    Finset.mem_singleton, classOf]
  constructor
  · intro h
    have hc : w (w.symm c) = c := w.apply_symm_apply c
    have hs : w.symm c = (j, (w.symm c).2) := Prod.ext h rfl
    rcases fin2_cases (w.symm c).2 with e | e
    · left; rw [← hc, hs, e]
    · right; rw [← hc, hs, e]
  · rintro (h | h) <;> rw [h, Equiv.symm_apply_apply]

theorem classOf_balanced (w : Fin 3 × Fin 2 ≃ Fin 6) (j : Fin 3) :
    (Finset.univ.filter (fun c => classOf w c = j)).card = 2 := by
  rw [classOf_fibre, Finset.card_pair]
  intro e
  have := w.injective e
  simp at this

theorem pair_cases {α : Type} (x y f0 f1 g0 g1 : α) (hf : f0 ≠ f1) (hg : g0 ≠ g1)
    (hf0 : f0 = x ∨ f0 = y) (hf1 : f1 = x ∨ f1 = y) (hg0 : g0 = x ∨ g0 = y)
    (hg1 : g1 = x ∨ g1 = y) : (g0 = f0 ∧ g1 = f1) ∨ (g0 = f1 ∧ g1 = f0) := by
  rcases hf0 with rfl | rfl <;> rcases hf1 with rfl | rfl <;> rcases hg0 with rfl | rfl <;>
    rcases hg1 with rfl | rfl <;> simp_all

section Partition

variable {n : ℕ} [NeZero n]

/-- Orientation bit of bag `i`: is the colour of slot `0` the smaller one? -/
def orient (f : VH n → Fin 6) (i : ZMod n) : Bool := decide (f ⟨i, 0⟩ < f ⟨i, 1⟩)

/-- A frozen colouring determines an ordered pair-partition (the palettes of the bags
`≡ 0, 1, 2 (mod 3)`) and one orientation bit per bag. -/
noncomputable def toPartition (f : FrozenCol n) : PairPartition × (ZMod n → Bool) :=
  (⟨classOf (wOf f 0), classOf_balanced _⟩, orient f.1)

/-- Meaning of the first component: the colours on bag `i` form pair number `i mod 3`. -/
theorem toPartition_spec (f : FrozenCol n) (i : ZMod n) (t : Fin 2) :
    (toPartition f).1.1 (f.1 ⟨i, t⟩) = r3 i := wOf_symm f 0 i t

theorem toPartition_injective : Function.Injective (toPartition (n := n)) := by
  intro f g h
  have hp : classOf (wOf f 0) = classOf (wOf g 0) := congrArg (fun z => z.1.1) h
  have ho : orient f.1 = orient g.1 := congrArg (fun z => z.2) h
  apply Subtype.ext
  funext ⟨i, t⟩
  have hf : ∀ t, classOf (wOf f 0) (f.1 ⟨i, t⟩) = r3 i := fun t => wOf_symm f 0 i t
  have hg : ∀ t, classOf (wOf f 0) (g.1 ⟨i, t⟩) = r3 i := fun t => by
    rw [hp]; exact wOf_symm g 0 i t
  have mem : ∀ c, classOf (wOf f 0) c = r3 i →
      c = wOf f 0 (r3 i, 0) ∨ c = wOf f 0 (r3 i, 1) := by
    intro c hc
    have : c ∈ Finset.univ.filter (fun c => classOf (wOf f 0) c = r3 i) := by
      simp [hc]
    rw [classOf_fibre] at this
    simpa using this
  have hfne : f.1 ⟨i, 0⟩ ≠ f.1 ⟨i, 1⟩ := f.2.1 _ _ (Hn_adj_twin i)
  have hgne : g.1 ⟨i, 0⟩ ≠ g.1 ⟨i, 1⟩ := g.2.1 _ _ (Hn_adj_twin i)
  have key := pair_cases _ _ _ _ _ _ hfne hgne (mem _ (hf 0)) (mem _ (hf 1)) (mem _ (hg 0))
    (mem _ (hg 1))
  have hgood : g.1 ⟨i, 0⟩ = f.1 ⟨i, 0⟩ ∧ g.1 ⟨i, 1⟩ = f.1 ⟨i, 1⟩ := by
    rcases key with h | ⟨e0, e1⟩
    · exact h
    · exfalso
      have hoi : decide (f.1 ⟨i, 0⟩ < f.1 ⟨i, 1⟩) = decide (g.1 ⟨i, 0⟩ < g.1 ⟨i, 1⟩) :=
        congrFun ho i
      rw [e0, e1, decide_eq_decide] at hoi
      rcases lt_or_gt_of_ne hfne with h | h
      · exact absurd (hoi.1 h) (lt_asymm h)
      · exact absurd (hoi.2 h) (lt_asymm h)
  rcases fin2_cases t with e | e
  · rw [e]; exact hgood.1.symm
  · rw [e]; exact hgood.2.symm

theorem toPartition_bijective (h3 : 3 ∣ n) : Function.Bijective (toPartition (n := n)) := by
  apply Function.Injective.bijective_of_nat_card_le toPartition_injective
  rw [card_frozen n h3, Nat.card_prod, Nat.card_eq_fintype_card, card_pairPartition,
    Nat.card_fun, Nat.card_zmod, Nat.card_eq_fintype_card, Fintype.card_bool]

/-- **(B), explicit form.** When `3 ∣ n`, frozen colourings of `H_n` are in bijection with
(ordered partitions of the six colours into three pairs) × (one orientation bit per bag). -/
noncomputable def frozenEquivPartitions (h3 : 3 ∣ n) :
    FrozenCol n ≃ PairPartition × (ZMod n → Bool) :=
  Equiv.ofBijective toPartition (toPartition_bijective h3)

end Partition

/-! ## The family refutes Conjecture 1 of the rank 1 file, member by member -/

/-- For every odd `n ≥ 5` divisible by three (`n = 9, 15, 21, ...`): `C_n` is prime, all its
induced subgraphs are recolorable, and its blowup by `K_2` is not recolorable. -/
theorem witness_family (n : ℕ) (hodd : n % 2 = 1) (h5 : 5 ≤ n) (h3 : 3 ∣ n) :
    Prime (Cyc n) ∧ (∀ S : ZMod n → Bool, Recolorable (induce (Cyc n) S)) ∧
    ∃ m : ZMod n → Nat, (∀ v, 1 ≤ m v) ∧ ¬ Recolorable (blowup (Cyc n) m) := by
  haveI : NeZero n := ⟨by omega⟩
  exact ⟨Cyc_prime n h5, Cyc_induced_recolorable n hodd (by omega), fun _ => 2,
    fun _ => (by decide : 1 ≤ 2), Hn_not_recolorable n hodd h5 h3⟩

/-- Each member of the family refutes `Conjecture1` exactly as stated in the rank 1 file
(graphs on `Fin n`; `ZMod (m + 1)` is `Fin (m + 1)` by definition). -/
theorem not_conjecture1_of (m : ℕ) (hodd : (m + 1) % 2 = 1) (h5 : 5 ≤ m + 1) (h3 : 3 ∣ m + 1) :
    ¬ Conjecture1 := fun h =>
  Hn_not_recolorable (m + 1) hodd h5 h3
    ((h (m + 1) (Cyc (m + 1)) (Cyc_prime (m + 1) h5)).2
      (Cyc_induced_recolorable (m + 1) hodd (by omega)) (fun _ => 2)
      (fun _ => (by decide : 1 ≤ 2)))

/-! ## The surrounding sentences of the paper -/

/-- Isolated vertices of `R_k(G)` are exactly the frozen colourings (as types). -/
def isolatedEquivFrozen (G : SGraph V) (k : ℕ) :
    {f : {f : V → Fin k // Proper G f} // ∀ g, ¬ (RGraph G k).Adj f g} ≃
      {f : V → Fin k // Frozen G f} where
  toFun x := ⟨x.1.1, (frozen_iff_isolated G x.1).2 x.2⟩
  invFun y := ⟨⟨y.1, y.2.1⟩, (frozen_iff_isolated G ⟨y.1, y.2.1⟩).1 y.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

/-- When `3 ∣ n`, `R_6(H_n)` has exactly `90 * 2 ^ n` isolated vertices. -/
theorem card_isolated (n : ℕ) [NeZero n] (h3 : 3 ∣ n) :
    Nat.card {f : {f : VH n → Fin 6 // Proper (Hn n) f} // ∀ g, ¬ (RGraph (Hn n) 6).Adj f g} =
      90 * 2 ^ n := by
  rw [Nat.card_congr (isolatedEquivFrozen (Hn n) 6)]
  exact card_frozen n h3

/-- "The original `C_9[K_2]` has 46,080 isolated six-colorings." -/
theorem card_isolated_nine :
    Nat.card {f : {f : VH 9 → Fin 6 // Proper (Hn 9) f} // ∀ g, ¬ (RGraph (Hn 9) 6).Adj f g} =
      46080 := by
  rw [card_isolated 9 (by decide)]
  norm_num

/-- "Thus `C_{6r+3}[K_2]`, for every `r ≥ 1`, is a counterexample to the same preservation
claim": the hypotheses of Conjecture 1 hold for `C_{6r+3}` and its conclusion fails. -/
theorem family_6r3 (r : ℕ) (hr : 1 ≤ r) :
    Prime (Cyc (6 * r + 3)) ∧
    (∀ S : ZMod (6 * r + 3) → Bool, Recolorable (induce (Cyc (6 * r + 3)) S)) ∧
    IsChi (Hn (6 * r + 3)) 5 ∧ ¬ Mixing (Hn (6 * r + 3)) 6 ∧ ¬ Recolorable (Hn (6 * r + 3)) := by
  haveI : NeZero (6 * r + 3) := ⟨by omega⟩
  have hodd : (6 * r + 3) % 2 = 1 := by omega
  have h5 : 5 ≤ 6 * r + 3 := by omega
  have h3 : 3 ∣ 6 * r + 3 := ⟨2 * r + 1, by ring⟩
  exact ⟨Cyc_prime _ h5, Cyc_induced_recolorable _ hodd (by omega), Hn_isChi5 _ hodd h5,
    Hn_not_mixing6 _ h3 (by omega), Hn_not_recolorable _ hodd h5 h3⟩

/-! ## The written proof's own route to `χ(H_n) ≥ 5`: the independence number

The written proof derives the lower bound from `α(H_n) = (n - 1) / 2`. The certified lower
bound above (`Hn_not_colourable4`) uses palettes instead; this section certifies the written
route as well, so that no intermediate claim of the written proof is left unchecked. -/

section Independence

variable {n : ℕ} [NeZero n]

/-- `I` is an independent set of `G`. -/
def Independent (G : SGraph V) (I : Finset V) : Prop := ∀ a ∈ I, ∀ b ∈ I, G.adj a b = false

/-- Upper bound: an independent set of `H_n` (odd `n ≥ 3`) has at most `(n - 1) / 2`
vertices. -/
theorem indep_card_le (hodd : n % 2 = 1) (hn : 3 ≤ n) (I : Finset (VH n))
    (hI : Independent (Hn n) I) : 2 * I.card + 1 ≤ n := by
  classical
  have hn2 : 2 ≤ n := by omega
  have hcard : (I.image Sigma.fst).card = I.card := by
    apply Finset.card_image_of_injOn
    intro x hx y hy hxy
    by_contra hne
    have hadj : (Hn n).adj x y = true := by
      obtain ⟨i, s⟩ := x
      obtain ⟨j, t⟩ := y
      have hij : i = j := hxy
      subst hij
      rw [Hn_adj_iff]
      refine Or.inl ⟨rfl, ?_⟩
      intro e
      apply hne
      rw [e]
    rw [hI x hx y hy] at hadj
    cases hadj
  have hdisj : Disjoint (I.image Sigma.fst) ((I.image Sigma.fst).image (· + 1)) := by
    rw [Finset.disjoint_left]
    intro j hj hj'
    obtain ⟨i, hi, hij⟩ := Finset.mem_image.1 hj'
    obtain ⟨x, hx, hxi⟩ := Finset.mem_image.1 hi
    obtain ⟨y, hy, hyj⟩ := Finset.mem_image.1 hj
    have hadj : (Hn n).adj x y = true := by
      obtain ⟨i', s⟩ := x
      obtain ⟨j', t⟩ := y
      have h1 : i' = i := hxi
      have h2 : j' = j := hyj
      rw [h1, h2, ← hij]
      exact Hn_adj_succ hn2 i s t
    rw [hI x hx y hy] at hadj
    cases hadj
  have hcard2 : ((I.image Sigma.fst).image (· + 1)).card = (I.image Sigma.fst).card :=
    Finset.card_image_of_injective _ (add_left_injective 1)
  have hle : ((I.image Sigma.fst) ∪ (I.image Sigma.fst).image (· + 1)).card ≤ n := by
    have := Finset.card_le_univ ((I.image Sigma.fst) ∪ (I.image Sigma.fst).image (· + 1))
    rwa [ZMod.card] at this
  rw [Finset.card_union_of_disjoint hdisj, hcard2, hcard] at hle
  omega

/-- Lower bound: the bags `1, 3, ..., n - 2` give an independent set of size `(n - 1) / 2`. -/
theorem indep_exists (hodd : n % 2 = 1) (hn : 3 ≤ n) :
    ∃ I : Finset (VH n), Independent (Hn n) I ∧ 2 * I.card + 1 = n := by
  classical
  have hval : ∀ k, k < (n - 1) / 2 → ((2 * k + 1 : ℕ) : ZMod n).val = 2 * k + 1 := by
    intro k hk
    rw [ZMod.val_natCast]
    exact Nat.mod_eq_of_lt (by omega)
  refine ⟨(Finset.range ((n - 1) / 2)).image
    (fun k => (⟨((2 * k + 1 : ℕ) : ZMod n), 0⟩ : VH n)), ?_, ?_⟩
  · intro a ha b hb
    obtain ⟨k, hk, rfl⟩ := Finset.mem_image.1 ha
    obtain ⟨l, hl, rfl⟩ := Finset.mem_image.1 hb
    rw [Finset.mem_range] at hk hl
    by_contra hne
    have hadj : (Hn n).adj (⟨((2 * k + 1 : ℕ) : ZMod n), 0⟩ : VH n)
        ⟨((2 * l + 1 : ℕ) : ZMod n), 0⟩ = true := by simpa using hne
    rw [Hn_adj_iff] at hadj
    rcases hadj with ⟨_, h⟩ | ⟨_, h | h⟩
    · exact h rfl
    · have := congrArg ZMod.val h
      rw [val_succ, hval k hk, hval l hl, Nat.mod_eq_of_lt (by omega)] at this
      omega
    · have := congrArg ZMod.val h
      rw [val_succ, hval k hk, hval l hl, Nat.mod_eq_of_lt (by omega)] at this
      omega
  · rw [Finset.card_image_of_injOn, Finset.card_range]
    · omega
    · intro k hk l hl h
      have hk' : k < (n - 1) / 2 := Finset.mem_range.1 hk
      have hl' : l < (n - 1) / 2 := Finset.mem_range.1 hl
      have h1 : ((2 * k + 1 : ℕ) : ZMod n) = ((2 * l + 1 : ℕ) : ZMod n) :=
        (Sigma.mk.inj_iff.1 h).1
      have := congrArg ZMod.val h1
      rw [hval k hk', hval l hl'] at this
      omega

/-- `α(H_n) = (n - 1) / 2` for odd `n ≥ 3`, in one statement. -/
theorem independence_number (hodd : n % 2 = 1) (hn : 3 ≤ n) :
    (∀ I : Finset (VH n), Independent (Hn n) I → I.card ≤ (n - 1) / 2) ∧
    ∃ I : Finset (VH n), Independent (Hn n) I ∧ I.card = (n - 1) / 2 := by
  refine ⟨fun I hI => ?_, ?_⟩
  · have := indep_card_le hodd hn I hI
    omega
  · obtain ⟨I, hI, hc⟩ := indep_exists (n := n) hodd hn
    exact ⟨I, hI, by omega⟩

/-- The written route: four colour classes are four independent sets covering `2 n` vertices,
impossible when each has at most `(n - 1) / 2` vertices. -/
theorem Hn_not_colourable4_via_alpha (hodd : n % 2 = 1) (hn : 3 ≤ n) :
    ¬ Colourable (Hn n) 4 := by
  classical
  rintro ⟨f, hf⟩
  have hclass : ∀ c : Fin 4, 2 * (Finset.univ.filter (fun x => f x = c)).card + 1 ≤ n := by
    intro c
    apply indep_card_le hodd hn
    intro a ha b hb
    by_contra hne
    have hadj : (Hn n).adj a b = true := by simpa using hne
    rw [Finset.mem_filter] at ha hb
    exact hf a b hadj (ha.2.trans hb.2.symm)
  have hsum : (Finset.univ : Finset (VH n)).card =
      ∑ c : Fin 4, (Finset.univ.filter (fun x => f x = c)).card :=
    Finset.card_eq_sum_card_fiberwise (fun x _ => Finset.mem_univ (f x))
  have hV : (Finset.univ : Finset (VH n)).card = 2 * n := by
    rw [Finset.card_univ, Fintype.card_sigma]
    simp [ZMod.card, mul_comm]
  rw [hV, Fin.sum_univ_four] at hsum
  have h0 := hclass 0
  have h1 := hclass 1
  have h2 := hclass 2
  have h3 := hclass 3
  omega

end Independence

end Recol

#print axioms Recol.cycle_blowup_frozen
#print axioms Recol.frozen_exists_iff
#print axioms Recol.three_dvd_of_frozen
#print axioms Recol.mk_frozen
#print axioms Recol.card_frozen
#print axioms Recol.card_frozen_fintype
#print axioms Recol.frozenEquivPartitions
#print axioms Recol.card_pairPartition
#print axioms Recol.components_R6
#print axioms Recol.components_R6_three
#print axioms Recol.frozen_iff_sees
#print axioms Recol.frozen_iff_isolated
#print axioms Recol.mixing_iff_preconnected
#print axioms Recol.Cyc_prime
#print axioms Recol.Cyc4_not_prime
#print axioms Recol.Cyc_induced_recolorable
#print axioms Recol.Cyc_whole_isChi3
#print axioms Recol.Cyc_whole_mixing
#print axioms Recol.Hn_isChi5
#print axioms Recol.Hn_not_colourable4
#print axioms Recol.Hn_colourable5
#print axioms Recol.Hn_not_mixing6
#print axioms Recol.Hn_not_recolorable
#print axioms Recol.Hn_adj_iff_diff
#print axioms Recol.frozen_surjective
#print axioms Recol.frozen_onto_exists_iff
#print axioms Recol.no_frozen_five
#print axioms Recol.Cyc9_matches_C9
#print axioms Recol.five9_archived
#print axioms Recol.six9_archived
#print axioms Recol.card_isolated
#print axioms Recol.card_isolated_nine
#print axioms Recol.family_6r3
#print axioms Recol.witness_family
#print axioms Recol.not_conjecture1_of
#print axioms Recol.mix_rel
#print axioms Recol.recolorable_induce
#print axioms Recol.independence_number
#print axioms Recol.Hn_not_colourable4_via_alpha
