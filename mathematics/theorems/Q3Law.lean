import Mathlib.Combinatorics.SimpleGraph.Coloring.VertexColoring
import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic

/-!
# The exact lower-palette law for `C_n[K_3]` at eight colours (kernel-checked)

Source: `astra/story_20260922/LOWER_PALETTE_EXPLORATION.md`, Section 8 ("Exact frozen
eight-coloring criterion for bag size three"), and the four literal palette loops of
`astra/story_20260922/check_rotated_domination_family.py` (`check_fixed_palette`).

**Theorem (Section 8).** For every `n ≥ 4`, `C_n[K_3]` has a frozen proper 8-colouring iff
`8 ⌈n/3⌉ ≤ 3n`, i.e. iff `n ∈ {6, 8, 9, 11, 12}` or `n ≥ 14`.

* Graph: vertex set `V n := Fin n × Fin 3`; `(i,a) ~ (j,b)` iff `i = j ∧ a ≠ b` (same bag) or
  `j = i + 1` or `i = j + 1` in `Fin n` (adjacent bags, addition modulo `n`).  Same conventions
  as the sibling certificate `C11K3.lean`, with `11` replaced by a parameter `n` (`[NeZero n]`
  is needed for `1 : Fin n`).
* `Proper c` : adjacent vertices get different colours.
* `Sees c`   : every colour other than `c v` occurs on a neighbour of `v` (frozen, closed
  neighbourhood form); `NoSingleRecolour` is the reconfiguration form, derived from it.

## Necessity (`necessity`, universal in `n`, needs only `Sees`)
Each colour class meets every closed bag-neighbourhood `{i-1, i, i+1}`, so its bag set
dominates the cycle (`bags_dominating`); a dominating set of `C_n` has `n ≤ 3 |D|`
(`cycle_dominating_card`: `univ ⊆ ⋃_{d ∈ D} {d-1, d, d+1}`), i.e. `|D| ≥ ⌈n/3⌉ = (n+2)/3`;
the eight classes partition the `3n` vertices, so `8 ⌈n/3⌉ ≤ 3n`.

## Sufficiency (`sufficiency`, universal in `n`)
A word is a list of bag palettes `Fin 3 → Fin 8`.  `LinGood w` says every window of three
consecutive palettes `(a, b, c)` has `a` injective, `a`, `b` disjoint and `a ∪ b ∪ c` all eight
colours.  `Loop w` says `LinGood (w ++ [A₀, B₀])` and `w` is empty or starts with `A₀ = 012`,
`B₀ = 345`.  A loop of length `n ≥ 2` read cyclically gives a proper frozen colouring
(`colouring_of_loop`), loops concatenate (`Loop.append`, from the sliding-window lemma
`linGood_append`), the four literal loops `L6 L8 L9 L11` are loops by kernel evaluation
(`decide`), and every admissible `n` is `6a + 8b + 9c + 11d` (`rep_of_ge14`, strong induction).

## The law (`exact_law`, `exact_law_explicit`)
For `n ≥ 4`: `(∃ c, Proper c ∧ Sees c) ↔ 8 * ((n + 2) / 3) ≤ 3 * n ↔ n ∈ {6,8,9,11,12} ∨ 14 ≤ n`.

Every proof is checked by the Lean kernel; the only computation is `decide` on the four
finite Boolean window checks `linGoodB (L ++ [A₀, B₀])`.  `#print axioms` at the end.
-/

set_option linter.unusedSectionVars false

namespace Q3Law

/-! ## The graph `C_n[K_3]` for a general cycle length `n` -/

/-- Vertex set: bag `i : Fin n`, label `a : Fin 3`. -/
abbrev V (n : ℕ) : Type := Fin n × Fin 3

/-- Boolean adjacency of `C_n[K_3]`: same bag and different label, or adjacent bags
(`j = i + 1` or `i = j + 1` in `Fin n`, i.e. modulo `n`). -/
def adj {n : ℕ} [NeZero n] (u v : V n) : Bool :=
  (u.1 == v.1 && u.2 != v.2) || (v.1 == u.1 + 1) || (u.1 == v.1 + 1)

/-- A proper colouring with colours `Fin k`. -/
def Proper {n : ℕ} [NeZero n] {k : ℕ} (c : V n → Fin k) : Prop :=
  ∀ u v, adj u v = true → c u ≠ c v

/-- Frozen, closed-neighbourhood form: every colour other than `c v` occurs on a
neighbour of `v`. -/
def Sees {n : ℕ} [NeZero n] {k : ℕ} (c : V n → Fin k) : Prop :=
  ∀ v : V n, ∀ col : Fin k, col ≠ c v → ∃ u, adj v u = true ∧ c u = col

/-- Frozen, reconfiguration form: no single-vertex recolouring of `c` is proper. -/
def NoSingleRecolour {n : ℕ} [NeZero n] {k : ℕ} (c : V n → Fin k) : Prop :=
  ∀ g : V n → Fin k, Proper g → ∀ v, (∀ u, u ≠ v → g u = c u) → g v = c v

/-- `(i + 1).val = (i.val + 1) % n` for `n ≥ 2`. -/
theorem val_add_one' {n : ℕ} [NeZero n] (hn : 2 ≤ n) (i : Fin n) :
    (i + 1).val = (i.val + 1) % n := by
  rw [Fin.val_add, Fin.val_one', Nat.mod_eq_of_lt hn]

theorem ne_add_one {n : ℕ} [NeZero n] (hn : 2 ≤ n) (i : Fin n) : i ≠ i + 1 := by
  intro h
  have hv := congrArg Fin.val h
  rw [val_add_one' hn] at hv
  have hi := i.isLt
  by_cases hlt : i.val + 1 < n
  · rw [Nat.mod_eq_of_lt hlt] at hv; omega
  · rw [show i.val + 1 = n by omega, Nat.mod_self] at hv; omega

theorem adj_irrefl {n : ℕ} [NeZero n] (hn : 2 ≤ n) (v : V n) : adj v v = false := by
  have h := ne_add_one hn v.1
  simp [adj, h]

/-- From the closed-neighbourhood form to the reconfiguration form (generic argument). -/
theorem noSingleRecolour_of_sees {n : ℕ} [NeZero n] (hn : 2 ≤ n) {k : ℕ} (c : V n → Fin k)
    (hs : Sees c) : NoSingleRecolour c := by
  intro g hg v hagree
  by_contra hne
  obtain ⟨u, hadj, hcu⟩ := hs v (g v) hne
  have huv : u ≠ v := by
    rintro rfl
    rw [adj_irrefl hn] at hadj
    exact Bool.false_ne_true hadj
  exact hg v u hadj (by rw [hagree u huv, hcu])

/-! ## Part 1: necessity, by independent-domination incidence counting -/

/-- Domination bound on the cycle `C_n`: if every bag `i` has one of `i-1, i, i+1` in `D`,
then `n ≤ 3 |D|` (each element of `D` dominates at most three bags). Equivalently
`|D| ≥ ⌈n/3⌉`. -/
theorem cycle_dominating_card {n : ℕ} [NeZero n] (D : Finset (Fin n))
    (hD : ∀ i : Fin n, i - 1 ∈ D ∨ i ∈ D ∨ i + 1 ∈ D) : n ≤ 3 * D.card := by
  have hcover : (Finset.univ : Finset (Fin n)) ⊆
      D.biUnion fun d => ({d - 1, d, d + 1} : Finset (Fin n)) := by
    intro i _
    rw [Finset.mem_biUnion]
    rcases hD i with h | h | h
    · exact ⟨i - 1, h, by simp⟩
    · exact ⟨i, h, by simp⟩
    · exact ⟨i + 1, h, by simp⟩
  have h1 := Finset.card_le_card hcover
  have h2 := Finset.card_biUnion_le (s := D)
    (t := fun d => ({d - 1, d, d + 1} : Finset (Fin n)))
  have h3 : ∑ d ∈ D, ({d - 1, d, d + 1} : Finset (Fin n)).card ≤ ∑ _d ∈ D, 3 :=
    Finset.sum_le_sum fun d _ => Finset.card_le_three
  simp only [Finset.card_univ, Fintype.card_fin, Finset.sum_const, smul_eq_mul] at h1 h3
  omega

theorem ceil_le_of_dominating {n : ℕ} [NeZero n] (D : Finset (Fin n))
    (hD : ∀ i : Fin n, i - 1 ∈ D ∨ i ∈ D ∨ i + 1 ∈ D) : (n + 2) / 3 ≤ D.card := by
  have := cycle_dominating_card D hD
  omega

/-- The colour class of `col`. -/
def cls {n : ℕ} {k : ℕ} (c : V n → Fin k) (col : Fin k) : Finset (V n) :=
  Finset.univ.filter fun v => c v = col

/-- The bag set of the colour class of `col`. -/
def bags {n : ℕ} {k : ℕ} (c : V n → Fin k) (col : Fin k) : Finset (Fin n) :=
  (cls c col).image Prod.fst

theorem mem_bags {n : ℕ} {k : ℕ} (c : V n → Fin k) (col : Fin k) (j : Fin n) :
    j ∈ bags c col ↔ ∃ a : Fin 3, c (j, a) = col := by
  simp only [bags, cls, Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨⟨j', a⟩, h, rfl⟩; exact ⟨a, h⟩
  · rintro ⟨a, h⟩; exact ⟨(j, a), h, rfl⟩

/-- In a frozen colouring, every colour class hits one of the bags `i-1, i, i+1`. -/
theorem bags_dominating {n : ℕ} [NeZero n] {k : ℕ} (c : V n → Fin k) (hs : Sees c)
    (col : Fin k) (i : Fin n) : i - 1 ∈ bags c col ∨ i ∈ bags c col ∨ i + 1 ∈ bags c col := by
  by_cases h0 : c (i, 0) = col
  · exact Or.inr (Or.inl ((mem_bags c col i).2 ⟨0, h0⟩))
  · obtain ⟨⟨j, a⟩, hadj, hu⟩ := hs (i, 0) col (Ne.symm h0)
    simp only [adj, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq] at hadj
    rcases hadj with (⟨h1, _⟩ | h1) | h1
    · subst h1; exact Or.inr (Or.inl ((mem_bags c col i).2 ⟨a, hu⟩))
    · subst h1; exact Or.inr (Or.inr ((mem_bags c col (i + 1)).2 ⟨a, hu⟩))
    · subst h1; rw [add_sub_cancel_right]; exact Or.inl ((mem_bags c col j).2 ⟨a, hu⟩)

theorem bags_card_le {n : ℕ} {k : ℕ} (c : V n → Fin k) (col : Fin k) :
    (bags c col).card ≤ (cls c col).card :=
  Finset.card_image_le

/-- Every colour class of a frozen colouring has at least `⌈n/3⌉ = (n+2)/3` vertices. -/
theorem cls_card_ge {n : ℕ} [NeZero n] {k : ℕ} (c : V n → Fin k) (hs : Sees c) (col : Fin k) :
    (n + 2) / 3 ≤ (cls c col).card :=
  (ceil_le_of_dominating (bags c col) (bags_dominating c hs col)).trans (bags_card_le c col)

/-- **Necessity** (only frozenness is used): a frozen 8-colouring of `C_n[K_3]` forces
`8 ⌈n/3⌉ ≤ 3n`. -/
theorem necessity_of_sees {n : ℕ} [NeZero n] (c : V n → Fin 8) (hs : Sees c) :
    8 * ((n + 2) / 3) ≤ 3 * n := by
  have hsum : (Finset.univ : Finset (V n)).card = ∑ col : Fin 8, (cls c col).card :=
    Finset.card_eq_sum_card_fiberwise (fun x _ => Finset.mem_univ (c x))
  have hcard : (Finset.univ : Finset (V n)).card = n * 3 := by simp
  have hle : ∑ _col : Fin 8, (n + 2) / 3 ≤ ∑ col : Fin 8, (cls c col).card :=
    Finset.sum_le_sum fun col _ => cls_card_ge c hs col
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul] at hle
  omega

/-- **Necessity**, as stated in the task: a proper frozen 8-colouring of `C_n[K_3]` forces
`8 ⌈n/3⌉ ≤ 3n` (the properness hypothesis is not needed; see `necessity_of_sees`). -/
theorem necessity {n : ℕ} [NeZero n] (c : V n → Fin 8) (_hc : Proper c) (hs : Sees c) :
    8 * ((n + 2) / 3) ≤ 3 * n :=
  necessity_of_sees c hs

/-! ## Part 2: sufficiency, by concatenating palette loops -/

/-- A bag palette: the three colours of a bag, indexed by label. -/
abbrev P : Type := Fin 3 → Fin 8

/-- The three labels of a bag get distinct colours. -/
def injP (a : P) : Bool :=
  (List.finRange 3).all fun x => (List.finRange 3).all fun y => (x == y) || (a x != a y)

/-- Two palettes are disjoint. -/
def disjP (a b : P) : Bool :=
  (List.finRange 3).all fun x => (List.finRange 3).all fun y => a x != b y

/-- Three palettes together cover all eight colours. -/
def coverP (a b c : P) : Bool :=
  (List.finRange 8).all fun col => (List.finRange 3).any fun x =>
    (a x == col) || (b x == col) || (c x == col)

/-- A good window of three consecutive palettes. -/
def winGood (a b c : P) : Bool := injP a && disjP a b && coverP a b c

theorem injP_sound {a : P} (h : injP a = true) {x y : Fin 3} (hxy : x ≠ y) : a x ≠ a y := by
  simp only [injP, List.all_eq_true, List.mem_finRange, true_implies] at h
  simpa [hxy] using h x y

theorem disjP_sound {a b : P} (h : disjP a b = true) (x y : Fin 3) : a x ≠ b y := by
  simp only [disjP, List.all_eq_true, List.mem_finRange, true_implies] at h
  simpa using h x y

theorem coverP_sound {a b c : P} (h : coverP a b c = true) (col : Fin 8) :
    ∃ x : Fin 3, a x = col ∨ b x = col ∨ c x = col := by
  simp only [coverP, List.all_eq_true, List.mem_finRange, true_implies, List.any_eq_true,
    true_and] at h
  obtain ⟨x, hx⟩ := h col
  exact ⟨x, by simpa [or_assoc] using hx⟩

theorem winGood_inj {a b c : P} (h : winGood a b c = true) : injP a = true := by
  simp only [winGood, Bool.and_eq_true] at h; exact h.1.1

theorem winGood_disj {a b c : P} (h : winGood a b c = true) : disjP a b = true := by
  simp only [winGood, Bool.and_eq_true] at h; exact h.1.2

theorem winGood_cover {a b c : P} (h : winGood a b c = true) : coverP a b c = true := by
  simp only [winGood, Bool.and_eq_true] at h; exact h.2

/-- The base state: the two palettes every loop starts with (`012 345` in the source). -/
def A₀ : P := ![0, 1, 2]
def B₀ : P := ![3, 4, 5]

/-- Linear sliding-window goodness of a word (total indexing via `List.getD`). -/
def LinGood (w : List P) : Prop :=
  ∀ j, j + 2 < w.length →
    winGood (w.getD j A₀) (w.getD (j + 1) A₀) (w.getD (j + 2) A₀) = true

/-- Boolean version of `LinGood`, for kernel evaluation. -/
def linGoodB (w : List P) : Bool :=
  (List.range w.length).all fun j =>
    if j + 2 < w.length then
      winGood (w.getD j A₀) (w.getD (j + 1) A₀) (w.getD (j + 2) A₀)
    else true

theorem linGoodB_sound {w : List P} (h : linGoodB w = true) : LinGood w := by
  intro j hj
  simp only [linGoodB, List.all_eq_true, List.mem_range] at h
  have := h j (by omega)
  rwa [if_pos hj] at this

/-! ### `getD` on appended and truncated lists -/

theorem getD_append_left {u v : List P} {k : ℕ} (h : k < u.length) (d : P) :
    (u ++ v).getD k d = u.getD k d := by
  rw [List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD, List.getElem?_append_left h]

theorem getD_append_right {u v : List P} {k : ℕ} (h : u.length ≤ k) (d : P) :
    (u ++ v).getD k d = v.getD (k - u.length) d := by
  rw [List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD, List.getElem?_append_right h]

theorem getD_take {v : List P} {m k : ℕ} (h : k < m) (d : P) :
    (v.take m).getD k d = v.getD k d := by
  rw [List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD, List.getElem?_take, if_pos h]

theorem getD_append_take2 (u v : List P) (k : ℕ) (hk : k < u.length + 2) :
    (u ++ v.take 2).getD k A₀ = (u ++ v).getD k A₀ := by
  by_cases h : k < u.length
  · rw [getD_append_left h, getD_append_left h]
  · rw [getD_append_right (by omega), getD_append_right (by omega), getD_take (by omega)]

/-- **Sliding-window lemma.** Every window of `u ++ v` lies inside `u ++ v.take 2` or
inside `v`. -/
theorem linGood_append {u v : List P} (hu : LinGood (u ++ v.take 2)) (hv : LinGood v) :
    LinGood (u ++ v) := by
  intro j hj
  rw [List.length_append] at hj
  by_cases h : j < u.length
  · have := hu j (by simp only [List.length_append, List.length_take]; omega)
    rwa [getD_append_take2 u v j (by omega), getD_append_take2 u v (j + 1) (by omega),
      getD_append_take2 u v (j + 2) (by omega)] at this
  · have := hv (j - u.length) (by omega)
    rw [getD_append_right (by omega), getD_append_right (by omega),
      getD_append_right (by omega)]
    rwa [show j + 1 - u.length = j - u.length + 1 by omega,
      show j + 2 - u.length = j - u.length + 2 by omega]

/-- A palette loop based at `(A₀, B₀)`: read cyclically (closing with `A₀, B₀`), every window
is good; and the word is empty or starts with `A₀, B₀`. -/
def Loop (w : List P) : Prop :=
  LinGood (w ++ [A₀, B₀]) ∧ (w = [] ∨ ∃ t, w = A₀ :: B₀ :: t)

theorem Loop.nil : Loop [] := by
  refine ⟨?_, Or.inl rfl⟩
  intro j hj
  simp at hj

/-- **Concatenation of loops.** -/
theorem Loop.append {u v : List P} (hu : Loop u) (hv : Loop v) : Loop (u ++ v) := by
  obtain ⟨hu1, hu2⟩ := hu
  obtain ⟨hv1, hv2⟩ := hv
  rcases hv2 with rfl | ⟨tv, rfl⟩
  · rw [List.append_nil]; exact ⟨hu1, hu2⟩
  rcases hu2 with rfl | ⟨tu, rfl⟩
  · exact ⟨hv1, Or.inr ⟨tv, rfl⟩⟩
  refine ⟨?_, Or.inr ⟨tu ++ A₀ :: B₀ :: tv, by simp⟩⟩
  rw [List.append_assoc]
  exact linGood_append hu1 hv1

theorem Loop.flatten_replicate {w : List P} (hw : Loop w) (a : ℕ) :
    Loop (List.replicate a w).flatten := by
  induction a with
  | zero => exact Loop.nil
  | succ a ih => rw [List.replicate_succ, List.flatten_cons]; exact hw.append ih

theorem length_flatten_replicate (w : List P) (a : ℕ) :
    (List.replicate a w).flatten.length = a * w.length := by
  simp [List.length_flatten, List.sum_replicate]

/-! ### From a loop to a colouring of `C_n[K_3]` -/

/-- Bag palette `i` of the word `w` (read cyclically once `w.length = n`). -/
def pal (w : List P) {n : ℕ} (i : Fin n) : P := w.getD i.val A₀

/-- The colouring of `C_n[K_3]` induced by a word of length `n`. -/
def colOf (n : ℕ) (w : List P) (v : V n) : Fin 8 := pal w v.1 v.2

theorem ext_get0 (t : List P) (j : ℕ) (hj : j < (A₀ :: B₀ :: t).length) :
    ((A₀ :: B₀ :: t) ++ [A₀, B₀]).getD j A₀ = (A₀ :: B₀ :: t).getD j A₀ :=
  getD_append_left hj A₀

theorem ext_get1 {n : ℕ} [NeZero n] (hn : 2 ≤ n) (t : List P)
    (hw : (A₀ :: B₀ :: t).length = n) (i : Fin n) :
    ((A₀ :: B₀ :: t) ++ [A₀, B₀]).getD (i.val + 1) A₀ =
      (A₀ :: B₀ :: t).getD (i + 1).val A₀ := by
  have hi := i.isLt
  rw [val_add_one' hn]
  by_cases h : i.val + 1 < n
  · rw [Nat.mod_eq_of_lt h, getD_append_left (by omega)]
  · rw [show i.val + 1 = n by omega, Nat.mod_self, getD_append_right (by omega), hw,
      Nat.sub_self]
    rfl

theorem ext_get2 {n : ℕ} [NeZero n] (hn : 2 ≤ n) (t : List P)
    (hw : (A₀ :: B₀ :: t).length = n) (i : Fin n) :
    ((A₀ :: B₀ :: t) ++ [A₀, B₀]).getD (i.val + 2) A₀ =
      (A₀ :: B₀ :: t).getD (i + 1 + 1).val A₀ := by
  have hi := i.isLt
  rw [val_add_one' hn, val_add_one' hn]
  by_cases h : i.val + 2 < n
  · rw [Nat.mod_eq_of_lt (by omega : i.val + 1 < n), Nat.mod_eq_of_lt h,
      getD_append_left (by omega)]
  · by_cases h2 : i.val + 2 = n
    · rw [Nat.mod_eq_of_lt (by omega : i.val + 1 < n), show i.val + 1 + 1 = n by omega,
        Nat.mod_self, getD_append_right (by omega), hw, Nat.sub_self]
      rfl
    · rw [show i.val + 1 = n by omega, Nat.mod_self, Nat.zero_add,
        Nat.mod_eq_of_lt (by omega : 1 < n), show i.val + 2 = n + 1 by omega,
        getD_append_right (by omega), hw, Nat.add_sub_cancel_left]
      rfl

/-- Every cyclic window `(i, i+1, i+2)` of a loop of length `n ≥ 2` is good. -/
theorem window {n : ℕ} [NeZero n] (hn : 2 ≤ n) (w : List P) (hL : Loop w)
    (hw : w.length = n) (i : Fin n) :
    winGood (pal w i) (pal w (i + 1)) (pal w (i + 1 + 1)) = true := by
  obtain ⟨hlin, hw2⟩ := hL
  rcases hw2 with rfl | ⟨t, rfl⟩
  · simp at hw; omega
  have hi := i.isLt
  have := hlin i.val (by simp only [List.length_append, List.length_cons] at hw ⊢; omega)
  rwa [ext_get0 t i.val (by omega), ext_get1 hn t hw, ext_get2 hn t hw] at this

theorem proper_of_loop {n : ℕ} [NeZero n] (hn : 2 ≤ n) (w : List P) (hL : Loop w)
    (hw : w.length = n) : Proper (colOf n w) := by
  have hwin := window hn w hL hw
  intro u v hadj
  simp only [adj, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq] at hadj
  show pal w u.1 u.2 ≠ pal w v.1 v.2
  rcases hadj with (⟨h1, h2⟩ | h1) | h1
  · rw [← h1]; exact injP_sound (winGood_inj (hwin u.1)) h2
  · rw [h1]; exact disjP_sound (winGood_disj (hwin u.1)) u.2 v.2
  · rw [h1]; exact (disjP_sound (winGood_disj (hwin v.1)) v.2 u.2).symm

theorem sees_of_loop {n : ℕ} [NeZero n] (hn : 2 ≤ n) (w : List P) (hL : Loop w)
    (hw : w.length = n) : Sees (colOf n w) := by
  have hwin := window hn w hL hw
  rintro ⟨i, a⟩ col hcol
  have hc := winGood_cover (hwin (i - 1))
  rw [sub_add_cancel] at hc
  obtain ⟨x, hx | hx | hx⟩ := coverP_sound hc col
  · exact ⟨(i - 1, x), by simp [adj], hx⟩
  · have hxa : a ≠ x := by
      rintro rfl
      exact hcol hx.symm
    exact ⟨(i, x), by simp [adj, hxa], hx⟩
  · exact ⟨(i + 1, x), by simp [adj], hx⟩

/-- **A loop of length `n ≥ 2`, read cyclically, is a proper frozen 8-colouring.** -/
theorem colouring_of_loop {n : ℕ} [NeZero n] (hn : 2 ≤ n) (w : List P) (hL : Loop w)
    (hw : w.length = n) : Proper (colOf n w) ∧ Sees (colOf n w) :=
  ⟨proper_of_loop hn w hL hw, sees_of_loop hn w hL hw⟩

/-! ### The four literal loops (`check_rotated_domination_family.py`, `check_fixed_palette`)

    "012 345 067 123 045 367"
    "012 345 067 123 456 017 234 567"
    "012 345 067 123 045 167 023 145 367"
    "012 345 067 123 045 167 023 456 017 234 567"
-/

def L6 : List P :=
  [![0,1,2], ![3,4,5], ![0,6,7], ![1,2,3], ![0,4,5], ![3,6,7]]

def L8 : List P :=
  [![0,1,2], ![3,4,5], ![0,6,7], ![1,2,3], ![4,5,6], ![0,1,7], ![2,3,4], ![5,6,7]]

def L9 : List P :=
  [![0,1,2], ![3,4,5], ![0,6,7], ![1,2,3], ![0,4,5], ![1,6,7], ![0,2,3], ![1,4,5], ![3,6,7]]

def L11 : List P :=
  [![0,1,2], ![3,4,5], ![0,6,7], ![1,2,3], ![0,4,5], ![1,6,7], ![0,2,3], ![4,5,6], ![0,1,7],
   ![2,3,4], ![5,6,7]]

theorem loop6 : Loop L6 := ⟨linGoodB_sound (by decide), Or.inr ⟨_, rfl⟩⟩
theorem loop8 : Loop L8 := ⟨linGoodB_sound (by decide), Or.inr ⟨_, rfl⟩⟩
theorem loop9 : Loop L9 := ⟨linGoodB_sound (by decide), Or.inr ⟨_, rfl⟩⟩
theorem loop11 : Loop L11 := ⟨linGoodB_sound (by decide), Or.inr ⟨_, rfl⟩⟩

/-- The concatenation `L6^a L8^b L9^c L11^d`. -/
def word (a b c d : ℕ) : List P :=
  (List.replicate a L6).flatten ++ (List.replicate b L8).flatten ++
    (List.replicate c L9).flatten ++ (List.replicate d L11).flatten

theorem word_loop (a b c d : ℕ) : Loop (word a b c d) :=
  (((loop6.flatten_replicate a).append (loop8.flatten_replicate b)).append
    (loop9.flatten_replicate c)).append (loop11.flatten_replicate d)

theorem word_length (a b c d : ℕ) :
    (word a b c d).length = 6 * a + 8 * b + 9 * c + 11 * d := by
  simp only [word, List.length_append, length_flatten_replicate, L6, L8, L9, L11,
    List.length_cons, List.length_nil]
  ring

/-! ### Every admissible length is `6a + 8b + 9c + 11d` -/

/-- `n` is a nonnegative combination of the loop lengths. -/
def Rep (n : ℕ) : Prop := ∃ a b c d : ℕ, n = 6 * a + 8 * b + 9 * c + 11 * d

theorem rep_of_ge14 (n : ℕ) (hn : 14 ≤ n) : Rep n := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    by_cases h : 20 ≤ n
    · obtain ⟨a, b, c, d, hab⟩ := ih (n - 6) (by omega) (by omega)
      exact ⟨a + 1, b, c, d, by omega⟩
    · interval_cases n
      · exact ⟨1, 1, 0, 0, by norm_num⟩
      · exact ⟨1, 0, 1, 0, by norm_num⟩
      · exact ⟨0, 2, 0, 0, by norm_num⟩
      · exact ⟨1, 0, 0, 1, by norm_num⟩
      · exact ⟨0, 0, 2, 0, by norm_num⟩
      · exact ⟨0, 1, 0, 1, by norm_num⟩

theorem rep_of_admissible (n : ℕ)
    (hn : n = 6 ∨ n = 8 ∨ n = 9 ∨ n = 11 ∨ n = 12 ∨ 14 ≤ n) : Rep n := by
  rcases hn with rfl | rfl | rfl | rfl | rfl | h
  · exact ⟨1, 0, 0, 0, by norm_num⟩
  · exact ⟨0, 1, 0, 0, by norm_num⟩
  · exact ⟨0, 0, 1, 0, by norm_num⟩
  · exact ⟨0, 0, 0, 1, by norm_num⟩
  · exact ⟨2, 0, 0, 0, by norm_num⟩
  · exact rep_of_ge14 n h

/-- For `n ≥ 4`, the incidence inequality `8 ⌈n/3⌉ ≤ 3n` (with `⌈n/3⌉ = (n+2)/3`) holds
exactly for `n ∈ {6, 8, 9, 11, 12}` and `n ≥ 14`. -/
theorem admissible_iff (n : ℕ) (hn : 4 ≤ n) :
    8 * ((n + 2) / 3) ≤ 3 * n ↔ (n = 6 ∨ n = 8 ∨ n = 9 ∨ n = 11 ∨ n = 12 ∨ 14 ≤ n) := by
  omega

/-- **Sufficiency**: for `n ∈ {6, 8, 9, 11, 12}` and every `n ≥ 14`, `C_n[K_3]` has a proper
frozen 8-colouring, namely the cyclic reading of `L6^a L8^b L9^c L11^d`. -/
theorem sufficiency (n : ℕ) [NeZero n]
    (hn : n = 6 ∨ n = 8 ∨ n = 9 ∨ n = 11 ∨ n = 12 ∨ 14 ≤ n) :
    ∃ c : V n → Fin 8, Proper c ∧ Sees c := by
  obtain ⟨a, b, c, d, hrep⟩ := rep_of_admissible n hn
  have hw : (word a b c d).length = n := by rw [word_length]; omega
  have h2 : 2 ≤ n := by omega
  exact ⟨colOf n (word a b c d), colouring_of_loop h2 _ (word_loop a b c d) hw⟩

/-! ## Part 3: the exact law -/

/-- **Exact lower-palette law.** For `n ≥ 4`, `C_n[K_3]` has a proper frozen 8-colouring iff
`8 ⌈n/3⌉ ≤ 3n`. -/
theorem exact_law (n : ℕ) [NeZero n] (hn : 4 ≤ n) :
    (∃ c : V n → Fin 8, Proper c ∧ Sees c) ↔ 8 * ((n + 2) / 3) ≤ 3 * n := by
  constructor
  · rintro ⟨c, hc, hs⟩; exact necessity c hc hs
  · intro h; exact sufficiency n ((admissible_iff n hn).1 h)

/-- `⌈n/3⌉ = (n + 2) / 3` (the ceiling as Mathlib's `Nat.ceil` on `ℚ`). -/
theorem ceil_div_three (n : ℕ) : ⌈(n : ℚ) / 3⌉₊ = (n + 2) / 3 := by
  apply le_antisymm
  · rw [Nat.ceil_le]
    have h : n ≤ 3 * ((n + 2) / 3) := by omega
    have h' : (n : ℚ) ≤ 3 * (((n + 2) / 3 : ℕ) : ℚ) := by exact_mod_cast h
    linarith
  · by_cases h0 : (n + 2) / 3 = 0
    · rw [h0]; exact Nat.zero_le _
    · have : (n + 2) / 3 - 1 < ⌈(n : ℚ) / 3⌉₊ := by
        rw [Nat.lt_ceil]
        have h : 3 * ((n + 2) / 3 - 1) < n := by omega
        have h' : (3 : ℚ) * (((n + 2) / 3 - 1 : ℕ) : ℚ) < n := by exact_mod_cast h
        linarith
      omega

/-- The law with a literal ceiling: `8 ⌈n/3⌉ ≤ 3n`. -/
theorem exact_law_ceil (n : ℕ) [NeZero n] (hn : 4 ≤ n) :
    (∃ c : V n → Fin 8, Proper c ∧ Sees c) ↔ 8 * ⌈(n : ℚ) / 3⌉₊ ≤ 3 * n := by
  rw [ceil_div_three]; exact exact_law n hn

/-- The law with the admissible lengths listed explicitly. -/
theorem exact_law_explicit (n : ℕ) [NeZero n] (hn : 4 ≤ n) :
    (∃ c : V n → Fin 8, Proper c ∧ Sees c) ↔
      (n = 6 ∨ n = 8 ∨ n = 9 ∨ n = 11 ∨ n = 12 ∨ 14 ≤ n) :=
  (exact_law n hn).trans (admissible_iff n hn)

/-- The reconfiguration form of the frozen half: for admissible `n`, some proper 8-colouring
admits no single-vertex recolouring. -/
theorem exists_noSingleRecolour (n : ℕ) [NeZero n]
    (hn : n = 6 ∨ n = 8 ∨ n = 9 ∨ n = 11 ∨ n = 12 ∨ 14 ≤ n) :
    ∃ c : V n → Fin 8, Proper c ∧ NoSingleRecolour c := by
  obtain ⟨c, hc, hs⟩ := sufficiency n hn
  exact ⟨c, hc, noSingleRecolour_of_sees (by omega) c hs⟩

/-- The five excluded lengths in `[4, 13]`: no frozen 8-colouring at all (proper or not). -/
theorem no_frozen_4 (c : V 4 → Fin 8) : ¬ Sees c := fun hs => by
  have := necessity_of_sees c hs; omega
theorem no_frozen_5 (c : V 5 → Fin 8) : ¬ Sees c := fun hs => by
  have := necessity_of_sees c hs; omega
theorem no_frozen_7 (c : V 7 → Fin 8) : ¬ Sees c := fun hs => by
  have := necessity_of_sees c hs; omega
theorem no_frozen_10 (c : V 10 → Fin 8) : ¬ Sees c := fun hs => by
  have := necessity_of_sees c hs; omega
theorem no_frozen_13 (c : V 13 → Fin 8) : ¬ Sees c := fun hs => by
  have := necessity_of_sees c hs; omega

end Q3Law

#print axioms Q3Law.cycle_dominating_card
#print axioms Q3Law.bags_dominating
#print axioms Q3Law.necessity_of_sees
#print axioms Q3Law.necessity
#print axioms Q3Law.noSingleRecolour_of_sees
#print axioms Q3Law.cls_card_ge
#print axioms Q3Law.linGood_append
#print axioms Q3Law.Loop.append
#print axioms Q3Law.colouring_of_loop
#print axioms Q3Law.loop6
#print axioms Q3Law.loop8
#print axioms Q3Law.loop9
#print axioms Q3Law.loop11
#print axioms Q3Law.word_loop
#print axioms Q3Law.rep_of_ge14
#print axioms Q3Law.admissible_iff
#print axioms Q3Law.sufficiency
#print axioms Q3Law.exact_law
#print axioms Q3Law.exact_law_explicit
#print axioms Q3Law.ceil_div_three
#print axioms Q3Law.exact_law_ceil
#print axioms Q3Law.exists_noSingleRecolour
#print axioms Q3Law.no_frozen_4
#print axioms Q3Law.no_frozen_5
#print axioms Q3Law.no_frozen_7
#print axioms Q3Law.no_frozen_10
#print axioms Q3Law.no_frozen_13
