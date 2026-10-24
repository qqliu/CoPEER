/-
  RookSpectrum.lean  --  core Lean 4 only (no Mathlib, no lake project).

  Source: J. B. Lewis and R. Won, "Non-attacking rook placements on crossword
  grids", arXiv:2609.03081v1 (2 September 2026), Section 2 (definitions),
  Section 3.2 (permutation grids), Conjecture 3.10:

    "A positive integer r occurs as the rook placement count of a permutation
     grid if and only if r != 4, r != 12, and r is not congruent to 3 (mod 4)."

  This file defines crossword grids, across and down words, complete
  non-attacking rook placements and their number |RP(G)| in general, defines
  Grid(w), states Conjecture 3.10 as a general proposition `Conjecture310`,
  and proves `not_conjecture310 : ¬ Conjecture310` from the kernel-certified
  value |RP(Grid(2 7 4 8 1 6 3 5))| = 155 = 3 (mod 4).

  The count is DEFINED by plain include/exclude enumeration of all sub-selections
  of the white squares (`bf`, 2^56 candidates for the witness).  It is COMPUTED by
  a pruned search `pr` that is PROVED equal to `bf` for every grid
  (`rpCount_eq_pr`).  `rpCount_faithful` proves, for every grid, that the enumerated
  candidates are the subsets of the white squares, each exactly once.  Words and white squares of the witness grid are computed
  inside Lean from `w8`; the displayed literal lists are checked equal to the
  computed ones by the kernel.

  No sorry, no native_decide, no axiom declarations, no unsafe / implemented_by /
  extern / csimp / partial.
-/

set_option maxRecDepth 100000

namespace RookSpectrum

/-! ## 1. Counting sub-selections of a list -/

section Counting
variable {α : Type}

/-- Number of elements of `l` that satisfy `p`. -/
def cnt (p : α → Bool) : List α → Nat
  | [] => 0
  | x :: l => (if p x then 1 else 0) + cnt p l

theorem cnt_eq_length_filter (p : α → Bool) (l : List α) :
    cnt p l = (l.filter p).length := by
  induction l with
  | nil => rfl
  | cons x l ih =>
    cases h : p x <;> simp [cnt, List.filter, h, ih] <;> omega

/-- All sub-selections of `rest`, each pushed on top of `acc`: for every element of
`rest` in turn, either take it or skip it. `subs rest []` lists every subset of a
duplicate-free list `rest` exactly once. -/
def subs : List α → List α → List (List α)
  | [], acc => [acc]
  | s :: rest, acc => subs rest (s :: acc) ++ subs rest acc

/-- Brute-force count: the number of sub-selections that satisfy `P`. -/
def bf (P : List α → Bool) : List α → List α → Nat
  | [], acc => if P acc then 1 else 0
  | s :: rest, acc => bf P rest (s :: acc) + bf P rest acc

theorem bf_eq_cnt_subs (P : List α → Bool) :
    ∀ rest acc, bf P rest acc = cnt P (subs rest acc) := by
  intro rest
  induction rest with
  | nil => intro acc; simp [bf, subs, cnt]
  | cons s rest ih =>
    intro acc
    have happ : ∀ (l1 l2 : List (List α)), cnt P (l1 ++ l2) = cnt P l1 + cnt P l2 := by
      intro l1 l2
      induction l1 with
      | nil => simp [cnt]
      | cons x l1 ih1 => simp [cnt, ih1]; omega
    simp [bf, subs, happ, ih]

theorem length_subs : ∀ (rest acc : List α), (subs rest acc).length = 2 ^ rest.length := by
  intro rest
  induction rest with
  | nil => intro acc; simp [subs]
  | cons s rest ih =>
    intro acc
    simp [subs, List.length_append, ih, Nat.pow_succ]; omega

/-- Every sub-selection consists of elements of `acc` and of `rest`. -/
theorem mem_of_mem_subs : ∀ (rest acc S : List α), S ∈ subs rest acc →
    ∀ x, x ∈ S → x ∈ acc ∨ x ∈ rest := by
  intro rest
  induction rest with
  | nil =>
    intro acc S hS x hx
    simp [subs] at hS; subst hS; exact Or.inl hx
  | cons s rest ih =>
    intro acc S hS x hx
    simp only [subs, List.mem_append] at hS
    cases hS with
    | inl h =>
      cases ih (s :: acc) S h x hx with
      | inl h1 =>
        cases List.mem_cons.mp h1 with
        | inl h2 => subst h2; exact Or.inr (List.mem_cons_self ..)
        | inr h2 => exact Or.inl h2
      | inr h1 => exact Or.inr (List.mem_cons_of_mem _ h1)
    | inr h =>
      cases ih acc S h x hx with
      | inl h1 => exact Or.inl h1
      | inr h1 => exact Or.inr (List.mem_cons_of_mem _ h1)

theorem nodup_append_of : ∀ (l1 l2 : List α), l1.Nodup → l2.Nodup →
    (∀ a, a ∈ l1 → a ∈ l2 → False) → (l1 ++ l2).Nodup := by
  intro l1
  induction l1 with
  | nil => intro l2 _ h2 _; simpa using h2
  | cons x l1 ih =>
    intro l2 h1 h2 hd
    rw [List.nodup_cons] at h1
    simp only [List.cons_append, List.nodup_cons, List.mem_append]
    refine ⟨?_, ih l2 h1.2 h2 (fun a ha hb => hd a (List.mem_cons_of_mem _ ha) hb)⟩
    intro h
    cases h with
    | inl h => exact h1.1 h
    | inr h => exact hd x (List.mem_cons_self ..) h

/-- Every sub-selection contains `acc`. -/
theorem acc_subset_of_mem_subs : ∀ (rest acc S : List α), S ∈ subs rest acc →
    ∀ x, x ∈ acc → x ∈ S := by
  intro rest
  induction rest with
  | nil => intro acc S hS x hx; simp [subs] at hS; subst hS; exact hx
  | cons s rest ih =>
    intro acc S hS x hx
    simp only [subs, List.mem_append] at hS
    cases hS with
    | inl h => exact ih (s :: acc) S h x (List.mem_cons_of_mem _ hx)
    | inr h => exact ih acc S h x hx

/-- A list cannot arise both after taking `s` and after skipping `s`. -/
theorem take_skip_disjoint (s : α) (rest acc S S' : List α) (hs1 : s ∉ rest) (hs2 : s ∉ acc)
    (h : S ∈ subs rest (s :: acc)) (h' : S' ∈ subs rest acc) : ¬ (∀ x, x ∈ S ↔ x ∈ S') := by
  intro he
  have h1 : s ∈ S := acc_subset_of_mem_subs rest (s :: acc) S h s (List.mem_cons_self ..)
  have h2 : s ∈ S' := (he s).mp h1
  cases mem_of_mem_subs rest acc S' h' s h2 with
  | inl h3 => exact hs2 h3
  | inr h3 => exact hs1 h3

/-- Two listed sub-selections with the same elements are the same list: no subset is listed
twice under two names. -/
theorem subs_ext : ∀ (rest acc : List α), rest.Nodup → (∀ x, x ∈ rest → x ∉ acc) →
    ∀ S S', S ∈ subs rest acc → S' ∈ subs rest acc → (∀ x, x ∈ S ↔ x ∈ S') → S = S' := by
  intro rest
  induction rest with
  | nil =>
    intro acc _ _ S S' hS hS' _
    simp [subs] at hS hS'; rw [hS, hS']
  | cons s rest ih =>
    intro acc hnd hdis S S' hS hS' he
    rw [List.nodup_cons] at hnd
    have hs2 : s ∉ acc := hdis s (List.mem_cons_self ..)
    have hdis1 : ∀ x, x ∈ rest → x ∉ s :: acc := by
      intro x hx hm
      cases List.mem_cons.mp hm with
      | inl h => subst h; exact hnd.1 hx
      | inr h => exact hdis x (List.mem_cons_of_mem _ hx) h
    have hdis2 : ∀ x, x ∈ rest → x ∉ acc := fun x hx => hdis x (List.mem_cons_of_mem _ hx)
    simp only [subs, List.mem_append] at hS hS'
    cases hS with
    | inl h =>
      cases hS' with
      | inl h' => exact ih (s :: acc) hnd.2 hdis1 S S' h h' he
      | inr h' => exact absurd he (take_skip_disjoint s rest acc S S' hnd.1 hs2 h h')
    | inr h =>
      cases hS' with
      | inl h' =>
        exact absurd (fun x => (he x).symm) (take_skip_disjoint s rest acc S' S hnd.1 hs2 h' h)
      | inr h' => exact ih acc hnd.2 hdis2 S S' h h' he

/-- The list of sub-selections has no repetition. -/
theorem nodup_subs : ∀ (rest acc : List α), rest.Nodup → (∀ x, x ∈ rest → x ∉ acc) →
    (subs rest acc).Nodup := by
  intro rest
  induction rest with
  | nil => intro acc _ _; simp [subs]
  | cons s rest ih =>
    intro acc hnd hdis
    rw [List.nodup_cons] at hnd
    have hs2 : s ∉ acc := hdis s (List.mem_cons_self ..)
    have hdis1 : ∀ x, x ∈ rest → x ∉ s :: acc := by
      intro x hx hm
      cases List.mem_cons.mp hm with
      | inl h => subst h; exact hnd.1 hx
      | inr h => exact hdis x (List.mem_cons_of_mem _ hx) h
    have hdis2 : ∀ x, x ∈ rest → x ∉ acc := fun x hx => hdis x (List.mem_cons_of_mem _ hx)
    simp only [subs]
    refine nodup_append_of _ _ (ih (s :: acc) hnd.2 hdis1) (ih acc hnd.2 hdis2) ?_
    intro S h h'
    exact take_skip_disjoint s rest acc S S hnd.1 hs2 h h' (fun _ => Iff.rfl)

/-- Each listed sub-selection is itself free of repetition. -/
theorem nodup_of_mem_subs : ∀ (rest acc : List α), rest.Nodup → acc.Nodup →
    (∀ x, x ∈ rest → x ∉ acc) → ∀ S, S ∈ subs rest acc → S.Nodup := by
  intro rest
  induction rest with
  | nil => intro acc _ ha _ S hS; simp [subs] at hS; subst hS; exact ha
  | cons s rest ih =>
    intro acc hnd ha hdis S hS
    rw [List.nodup_cons] at hnd
    have hs2 : s ∉ acc := hdis s (List.mem_cons_self ..)
    have hdis1 : ∀ x, x ∈ rest → x ∉ s :: acc := by
      intro x hx hm
      cases List.mem_cons.mp hm with
      | inl h => subst h; exact hnd.1 hx
      | inr h => exact hdis x (List.mem_cons_of_mem _ hx) h
    have hdis2 : ∀ x, x ∈ rest → x ∉ acc := fun x hx => hdis x (List.mem_cons_of_mem _ hx)
    simp only [subs, List.mem_append] at hS
    cases hS with
    | inl h => exact ih (s :: acc) hnd.2 (List.nodup_cons.mpr ⟨hs2, ha⟩) hdis1 S h
    | inr h => exact ih acc hnd.2 ha hdis2 S h

/-- Every subset of `rest` (given by a Boolean predicate `T`) is listed. -/
theorem subs_complete (T : α → Bool) : ∀ (rest acc : List α),
    ∃ S, S ∈ subs rest acc ∧ ∀ x, x ∈ S ↔ (x ∈ acc ∨ (x ∈ rest ∧ T x = true)) := by
  intro rest
  induction rest with
  | nil =>
    intro acc
    refine ⟨acc, by simp [subs], ?_⟩
    intro x
    constructor
    · intro h; exact Or.inl h
    · intro h
      cases h with
      | inl h => exact h
      | inr h => cases h.1
  | cons s rest ih =>
    intro acc
    cases hT : T s
    · obtain ⟨S, hS, hx⟩ := ih acc
      refine ⟨S, by simp only [subs, List.mem_append]; exact Or.inr hS, ?_⟩
      intro x
      rw [hx x]
      constructor
      · intro h
        cases h with
        | inl h => exact Or.inl h
        | inr h => exact Or.inr ⟨List.mem_cons_of_mem _ h.1, h.2⟩
      · intro h
        cases h with
        | inl h => exact Or.inl h
        | inr h =>
          cases List.mem_cons.mp h.1 with
          | inl h1 => subst h1; rw [hT] at h; cases h.2
          | inr h1 => exact Or.inr ⟨h1, h.2⟩
    · obtain ⟨S, hS, hx⟩ := ih (s :: acc)
      refine ⟨S, by simp only [subs, List.mem_append]; exact Or.inl hS, ?_⟩
      intro x
      rw [hx x]
      constructor
      · intro h
        cases h with
        | inl h =>
          cases List.mem_cons.mp h with
          | inl h1 => subst h1; exact Or.inr ⟨List.mem_cons_self .., hT⟩
          | inr h1 => exact Or.inl h1
        | inr h => exact Or.inr ⟨List.mem_cons_of_mem _ h.1, h.2⟩
      · intro h
        cases h with
        | inl h => exact Or.inl (List.mem_cons_of_mem _ h)
        | inr h =>
          cases List.mem_cons.mp h.1 with
          | inl h1 => subst h1; exact Or.inl (List.mem_cons_self ..)
          | inr h1 => exact Or.inr ⟨h1, h.2⟩

theorem bf_eq_zero (P : List α → Bool) :
    ∀ rest acc, (∀ S, S ∈ subs rest acc → P S = false) → bf P rest acc = 0 := by
  intro rest
  induction rest with
  | nil =>
    intro acc h
    have : P acc = false := h acc (by simp [subs])
    simp [bf, this]
  | cons s rest ih =>
    intro acc h
    have h1 : bf P rest (s :: acc) = 0 :=
      ih (s :: acc) (fun S hS => h S (by simp only [subs, List.mem_append]; exact Or.inl hS))
    have h2 : bf P rest acc = 0 :=
      ih acc (fun S hS => h S (by simp only [subs, List.mem_append]; exact Or.inr hS))
    simp [bf, h1, h2]

theorem bf_congr (P Q : List α → Bool) (h : ∀ S, P S = Q S) :
    ∀ rest acc, bf P rest acc = bf Q rest acc := by
  intro rest
  induction rest with
  | nil => intro acc; simp [bf, h]
  | cons s rest ih => intro acc; simp [bf, ih]

theorem cnt_cons_le (p : α → Bool) (s : α) (l : List α) : cnt p l ≤ cnt p (s :: l) := by
  simp [cnt]

/-- A sub-selection contains at least as many `p`-elements as `acc`. -/
theorem cnt_mono_subs (p : α → Bool) : ∀ (rest acc S : List α), S ∈ subs rest acc →
    cnt p acc ≤ cnt p S := by
  intro rest
  induction rest with
  | nil => intro acc S hS; simp [subs] at hS; subst hS; exact Nat.le_refl _
  | cons s rest ih =>
    intro acc S hS
    simp only [subs, List.mem_append] at hS
    cases hS with
    | inl h => exact Nat.le_trans (cnt_cons_le p s acc) (ih (s :: acc) S h)
    | inr h => exact ih acc S h

/-- A sub-selection contains at most the `p`-elements of `acc` and of `rest`. -/
theorem cnt_le_subs (p : α → Bool) : ∀ (rest acc S : List α), S ∈ subs rest acc →
    cnt p S ≤ cnt p acc + cnt p rest := by
  intro rest
  induction rest with
  | nil => intro acc S hS; simp [subs] at hS; subst hS; simp [cnt]
  | cons s rest ih =>
    intro acc S hS
    simp only [subs, List.mem_append] at hS
    cases hS with
    | inl h =>
      have := ih (s :: acc) S h
      simp only [cnt] at this ⊢; omega
    | inr h =>
      have := ih acc S h
      simp only [cnt] at this ⊢; omega

theorem cnt_pos_of_mem (p : α → Bool) : ∀ (l : List α) (t : α), t ∈ l → p t = true →
    1 ≤ cnt p l := by
  intro l
  induction l with
  | nil => intro t ht; cases ht
  | cons x l ih =>
    intro t ht hp
    cases List.mem_cons.mp ht with
    | inl h => subst h; simp [cnt, hp]
    | inr h => have := ih t h hp; simp only [cnt]; omega

theorem cnt_eq_zero_of_any_false (p : α → Bool) : ∀ (l : List α), l.any p = false →
    cnt p l = 0 := by
  intro l
  induction l with
  | nil => intro _; rfl
  | cons x l ih =>
    intro h
    simp only [List.any_cons, Bool.or_eq_false_iff] at h
    simp [cnt, h.1, ih h.2]

/-- Pruned count: the take-branch is cut when `cin` fires, the skip-branch when `cout` fires. -/
def pr (P : List α → Bool) (cin : α → List α → Bool) (cout : α → List α → List α → Bool) :
    List α → List α → Nat
  | [], acc => if P acc then 1 else 0
  | s :: rest, acc =>
      (if cin s acc then 0 else pr P cin cout rest (s :: acc)) +
      (if cout s rest acc then 0 else pr P cin cout rest acc)

/-- Soundness of pruning: if every cut only removes branches without solutions, the pruned
count equals the brute-force count. -/
theorem pr_eq_bf (P : List α → Bool) (cin : α → List α → Bool)
    (cout : α → List α → List α → Bool)
    (hin : ∀ s rest acc, cin s acc = true → ∀ S, S ∈ subs rest (s :: acc) → P S = false)
    (hout : ∀ s rest acc, cout s rest acc = true → ∀ S, S ∈ subs rest acc → P S = false) :
    ∀ rest acc, pr P cin cout rest acc = bf P rest acc := by
  intro rest
  induction rest with
  | nil => intro acc; simp [pr, bf]
  | cons s rest ih =>
    intro acc
    simp only [pr, bf]
    have e1 : (if cin s acc then 0 else pr P cin cout rest (s :: acc)) = bf P rest (s :: acc) := by
      cases h : cin s acc
      · simp [ih]
      · simp [bf_eq_zero P rest (s :: acc) (hin s rest acc h)]
    have e2 : (if cout s rest acc then 0 else pr P cin cout rest acc) = bf P rest acc := by
      cases h : cout s rest acc
      · simp [ih]
      · simp [bf_eq_zero P rest acc (hout s rest acc h)]
    rw [e1, e2]

end Counting

/-! ## 2. Crossword grids, words, complete rook placements (source, Section 2) -/

/-- An `m × n` crossword grid. Squares are `(i, j)` with `1 ≤ i ≤ m`, `1 ≤ j ≤ n` (the
source's matrix convention); `black i j = true` means the square is black. Values of `black`
outside the grid are never consulted. -/
structure Grid where
  m : Nat
  n : Nat
  black : Nat → Nat → Bool

abbrev Sq := Nat × Nat

/-- `(i, j)` is a white square of `G`. -/
def White (G : Grid) (s : Sq) : Prop :=
  1 ≤ s.1 ∧ s.1 ≤ G.m ∧ 1 ≤ s.2 ∧ s.2 ≤ G.n ∧ G.black s.1 s.2 = false

/-- "An across word is a maximal contiguous sequence of white squares within a single row":
the squares `(i, a), ..., (i, b)` are white, and the sequence cannot be extended to the west
(`a = 1` or `(i, a-1)` is black) nor to the east (`b = n` or `(i, b+1)` is black). -/
def AcrossWord (G : Grid) (i a b : Nat) : Prop :=
  1 ≤ i ∧ i ≤ G.m ∧ 1 ≤ a ∧ a ≤ b ∧ b ≤ G.n ∧
  (∀ j, j < b + 1 → a ≤ j → G.black i j = false) ∧
  (a = 1 ∨ G.black i (a - 1) = true) ∧
  (b = G.n ∨ G.black i (b + 1) = true)

/-- "Similarly, a down word is a maximal contiguous sequence of white squares within a single
column": the squares `(a, j), ..., (b, j)`. -/
def DownWord (G : Grid) (j a b : Nat) : Prop :=
  1 ≤ j ∧ j ≤ G.n ∧ 1 ≤ a ∧ a ≤ b ∧ b ≤ G.m ∧
  (∀ i, i < b + 1 → a ≤ i → G.black i j = false) ∧
  (a = 1 ∨ G.black (a - 1) j = true) ∧
  (b = G.m ∨ G.black (b + 1) j = true)

instance (G : Grid) (i a b : Nat) : Decidable (AcrossWord G i a b) := by
  unfold AcrossWord; exact inferInstance

instance (G : Grid) (j a b : Nat) : Decidable (DownWord G j a b) := by
  unfold DownWord; exact inferInstance

/-- A word: `down = false` is the across word in row `line` from column `lo` to column `hi`;
`down = true` is the down word in column `line` from row `lo` to row `hi`. -/
structure Word where
  down : Bool
  line : Nat
  lo : Nat
  hi : Nat
deriving DecidableEq

def IsWord (G : Grid) (W : Word) : Prop :=
  (W.down = false ∧ AcrossWord G W.line W.lo W.hi) ∨
  (W.down = true ∧ DownWord G W.line W.lo W.hi)

instance (G : Grid) (W : Word) : Decidable (IsWord G W) := by
  unfold IsWord; exact inferInstance

/-- The square `s` lies in the word `W`. -/
def inWord (W : Word) (s : Sq) : Bool :=
  if W.down then (s.2 == W.line && decide (W.lo ≤ s.1) && decide (s.1 ≤ W.hi))
  else (s.1 == W.line && decide (W.lo ≤ s.2) && decide (s.2 ≤ W.hi))

/-- "R is called complete if R contains exactly one white square in every across word and
every down word of G."  `R` is a selection of white squares, given as a list. -/
def Complete (G : Grid) (R : List Sq) : Prop :=
  ∀ W : Word, IsWord G W → cnt (inWord W) R = 1

/-! ### Enumerating squares and words -/

/-- `fromTo k s = [s, s+1, ..., s+k-1]`. -/
def fromTo : Nat → Nat → List Nat
  | 0, _ => []
  | k + 1, s => s :: fromTo k (s + 1)

theorem mem_fromTo : ∀ (k s x : Nat), x ∈ fromTo k s ↔ s ≤ x ∧ x < s + k := by
  intro k
  induction k with
  | zero => intro s x; simp [fromTo]
  | succ k ih =>
    intro s x
    simp only [fromTo, List.mem_cons, ih]
    omega

/-- All squares of the grid in row-major order, white ones only. -/
def whiteSquares (G : Grid) : List Sq :=
  ((fromTo G.m 1).flatMap (fun i => (fromTo G.n 1).map (fun j => (i, j)))).filter
    (fun s => !G.black s.1 s.2)

theorem mem_whiteSquares (G : Grid) (s : Sq) : s ∈ whiteSquares G ↔ White G s := by
  obtain ⟨i, j⟩ := s
  simp only [whiteSquares, White, List.mem_filter, List.mem_flatMap, List.mem_map, mem_fromTo]
  constructor
  · rintro ⟨⟨i', hi', j', hj', heq⟩, hb⟩
    have h1 : i' = i := congrArg Prod.fst heq
    have h2 : j' = j := congrArg Prod.snd heq
    subst h1; subst h2
    refine ⟨hi'.1, by omega, hj'.1, by omega, ?_⟩
    simpa using hb
  · rintro ⟨h1, h2, h3, h4, h5⟩
    refine ⟨⟨i, ⟨h1, by omega⟩, j, ⟨h3, by omega⟩, rfl⟩, ?_⟩
    simp [h5]

theorem nodup_fromTo : ∀ (k s : Nat), (fromTo k s).Nodup := by
  intro k
  induction k with
  | zero => intro s; simp [fromTo]
  | succ k ih =>
    intro s
    simp only [fromTo, List.nodup_cons]
    refine ⟨?_, ih (s + 1)⟩
    intro h
    have := (mem_fromTo k (s + 1) s).mp h
    omega

theorem nodup_row (i : Nat) : ∀ (l : List Nat), l.Nodup → (l.map (fun j => ((i, j) : Sq))).Nodup := by
  intro l
  induction l with
  | nil => intro _; simp
  | cons x l ih =>
    intro h
    rw [List.nodup_cons] at h
    simp only [List.map_cons, List.nodup_cons]
    refine ⟨?_, ih h.2⟩
    intro hm
    rw [List.mem_map] at hm
    obtain ⟨y, hy, he⟩ := hm
    have : y = x := congrArg Prod.snd he
    subst this
    exact h.1 hy

theorem nodup_grid (cols : List Nat) (hc : cols.Nodup) : ∀ (rows : List Nat), rows.Nodup →
    (rows.flatMap (fun i => cols.map (fun j => ((i, j) : Sq)))).Nodup := by
  intro rows
  induction rows with
  | nil => intro _; simp
  | cons r rows ih =>
    intro h
    rw [List.nodup_cons] at h
    simp only [List.flatMap_cons]
    refine nodup_append_of _ _ (nodup_row r cols hc) (ih h.2) ?_
    intro a ha hb
    rw [List.mem_map] at ha
    rw [List.mem_flatMap] at hb
    obtain ⟨j, _, hj⟩ := ha
    obtain ⟨i, hi, hm⟩ := hb
    rw [List.mem_map] at hm
    obtain ⟨j', _, hj'⟩ := hm
    have : i = r := by
      have := congrArg Prod.fst (hj'.trans hj.symm)
      simpa using this
    subst this
    exact h.1 hi

theorem nodup_filter {α : Type} (p : α → Bool) : ∀ (l : List α), l.Nodup → (l.filter p).Nodup := by
  intro l
  induction l with
  | nil => intro _; simp
  | cons x l ih =>
    intro h
    rw [List.nodup_cons] at h
    rw [List.filter_cons]
    split
    · rw [List.nodup_cons]
      exact ⟨fun hm => h.1 (List.mem_filter.mp hm).1, ih h.2⟩
    · exact ih h.2

/-- For EVERY grid the list of white squares has no repetition. -/
theorem whiteSquares_nodup (G : Grid) : (whiteSquares G).Nodup :=
  nodup_filter _ _ (nodup_grid _ (nodup_fromTo _ _) _ (nodup_fromTo _ _))

/-- Candidate words with `line ≤ L` and `lo, hi ≤ K`. -/
def triples (d : Bool) (L K : Nat) : List Word :=
  (fromTo L 1).flatMap (fun l => (fromTo K 1).flatMap (fun a => (fromTo K 1).map
    (fun b => Word.mk d l a b)))

theorem mem_triples (d : Bool) (L K : Nat) (W : Word) :
    W ∈ triples d L K ↔
      W.down = d ∧ 1 ≤ W.line ∧ W.line ≤ L ∧ 1 ≤ W.lo ∧ W.lo ≤ K ∧ 1 ≤ W.hi ∧ W.hi ≤ K := by
  obtain ⟨d', l, a, b⟩ := W
  simp only [triples, List.mem_flatMap, List.mem_map, mem_fromTo]
  constructor
  · rintro ⟨l', hl', a', ha', b', hb', heq⟩
    injection heq with e1 e2 e3 e4
    subst e1; subst e2; subst e3; subst e4
    exact ⟨rfl, hl'.1, by omega, ha'.1, by omega, hb'.1, by omega⟩
  · rintro ⟨h0, h1, h2, h3, h4, h5, h6⟩
    subst h0
    exact ⟨l, ⟨h1, by omega⟩, a, ⟨h3, by omega⟩, b, ⟨h5, by omega⟩, rfl⟩

/-- All across words and all down words of `G`. -/
def allWords (G : Grid) : List Word :=
  (triples false G.m G.n ++ triples true G.n G.m).filter (fun W => decide (IsWord G W))

theorem mem_allWords (G : Grid) (W : Word) : W ∈ allWords G ↔ IsWord G W := by
  simp only [allWords, List.mem_filter, List.mem_append, mem_triples, decide_eq_true_eq]
  constructor
  · exact fun h => h.2
  · intro h
    refine ⟨?_, h⟩
    cases h with
    | inl h =>
      obtain ⟨hd, h1, h2, h3, h4, h5, _⟩ := h
      exact Or.inl ⟨hd, h1, h2, h3, by omega, by omega, h5⟩
    | inr h =>
      obtain ⟨hd, h1, h2, h3, h4, h5, _⟩ := h
      exact Or.inr ⟨hd, h1, h2, h3, by omega, by omega, h5⟩

/-- Boolean completeness test against a list of words. -/
def fastC (Wl : List Word) (R : List Sq) : Bool :=
  Wl.all (fun W => cnt (inWord W) R == 1)

theorem complete_iff_fastC (G : Grid) (R : List Sq) :
    Complete G R ↔ fastC (allWords G) R = true := by
  simp only [Complete, fastC, List.all_eq_true, beq_iff_eq]
  constructor
  · intro h W hW; exact h W ((mem_allWords G W).mp hW)
  · intro h W hW; exact h W ((mem_allWords G W).mpr hW)

instance (G : Grid) (R : List Sq) : Decidable (Complete G R) :=
  decidable_of_iff _ (complete_iff_fastC G R).symm

theorem decide_complete (G : Grid) (R : List Sq) :
    decide (Complete G R) = fastC (allWords G) R := by
  cases h : fastC (allWords G) R
  · have hn : ¬ Complete G R := by
      intro hc
      rw [(complete_iff_fastC G R).mp hc] at h
      cases h
    exact decide_eq_false hn
  · exact decide_eq_true ((complete_iff_fastC G R).mpr h)

/-- `|RP(G)|`: the number of selections of white squares of `G` that are complete
(non-attacking) rook placements. -/
def rpCount (G : Grid) : Nat :=
  bf (fun R => decide (Complete G R)) (whiteSquares G) []

/-- The same number, read as: among all `2 ^ (number of white squares)` sub-selections of the
white squares, how many are complete. -/
theorem rpCount_eq_cnt (G : Grid) :
    rpCount G = cnt (fun R => decide (Complete G R)) (subs (whiteSquares G) []) :=
  bf_eq_cnt_subs _ _ _

/-- Every counted selection consists of white squares of `G`. -/
theorem counted_are_white (G : Grid) (R : List Sq) (hR : R ∈ subs (whiteSquares G) []) :
    ∀ s, s ∈ R → White G s := by
  intro s hs
  cases mem_of_mem_subs _ _ _ hR s hs with
  | inl h => cases h
  | inr h => exact (mem_whiteSquares G s).mp h

/-- `rpCount G` is the cardinality of the set RP(G), for EVERY grid: the candidates
`subs (whiteSquares G) []` are listed without repetition, each candidate is a repetition-free
list of white squares, two candidates with the same elements are equal, and every set of white
squares (given by a Boolean predicate `T`) is one of the candidates. So the candidates are the
subsets of the white squares, each exactly once, and `rpCount G` counts the complete ones
(`rpCount_eq_cnt`). -/
theorem rpCount_faithful (G : Grid) :
    (subs (whiteSquares G) []).Nodup ∧
    (∀ S, S ∈ subs (whiteSquares G) [] → S.Nodup ∧ ∀ s, s ∈ S → White G s) ∧
    (∀ S S', S ∈ subs (whiteSquares G) [] → S' ∈ subs (whiteSquares G) [] →
      (∀ x, x ∈ S ↔ x ∈ S') → S = S') ∧
    (∀ T : Sq → Bool, ∃ S, S ∈ subs (whiteSquares G) [] ∧
      ∀ x, x ∈ S ↔ (White G x ∧ T x = true)) := by
  have hnd := whiteSquares_nodup G
  have hdis : ∀ x, x ∈ whiteSquares G → x ∉ ([] : List Sq) := fun _ _ h => by cases h
  refine ⟨nodup_subs _ _ hnd hdis, ?_, subs_ext _ _ hnd hdis, ?_⟩
  · intro S hS
    exact ⟨nodup_of_mem_subs _ _ hnd (by simp) hdis S hS, counted_are_white G S hS⟩
  · intro T
    obtain ⟨S, hS, hx⟩ := subs_complete T (whiteSquares G) []
    refine ⟨S, hS, ?_⟩
    intro x
    rw [hx x, mem_whiteSquares]
    constructor
    · intro h
      cases h with
      | inl h => cases h
      | inr h => exact h
    · intro h; exact Or.inr h

/-! ### Pruning cuts and their soundness -/

/-- Cut the take-branch: some word contains the new rook `s` and a rook already placed. -/
def cutIn (Wl : List Word) (s : Sq) (acc : List Sq) : Bool :=
  Wl.any (fun W => inWord W s && acc.any (inWord W))

/-- Cut the skip-branch: some word through `s` has no rook and no undecided square left. -/
def cutOut (Wl : List Word) (s : Sq) (rest acc : List Sq) : Bool :=
  Wl.any (fun W => inWord W s && !(acc.any (inWord W)) && !(rest.any (inWord W)))

theorem fastC_false_of_cnt_ne (Wl : List Word) (R : List Sq) (W : Word) (hW : W ∈ Wl)
    (hne : cnt (inWord W) R ≠ 1) : fastC Wl R = false := by
  cases h : fastC Wl R
  · rfl
  · simp only [fastC, List.all_eq_true, beq_iff_eq] at h
    exact absurd (h W hW) hne

theorem cutIn_sound (Wl : List Word) (s : Sq) (rest acc : List Sq)
    (h : cutIn Wl s acc = true) : ∀ S, S ∈ subs rest (s :: acc) → fastC Wl S = false := by
  intro S hS
  simp only [cutIn, List.any_eq_true, Bool.and_eq_true] at h
  obtain ⟨W, hW, hs, t, ht, hWt⟩ := h
  have h1 : 1 ≤ cnt (inWord W) acc := cnt_pos_of_mem _ acc t ht hWt
  have h2 : cnt (inWord W) (s :: acc) = 1 + cnt (inWord W) acc := by simp [cnt, hs]
  have h3 := cnt_mono_subs (inWord W) rest (s :: acc) S hS
  exact fastC_false_of_cnt_ne Wl S W hW (by omega)

theorem cutOut_sound (Wl : List Word) (s : Sq) (rest acc : List Sq)
    (h : cutOut Wl s rest acc = true) : ∀ S, S ∈ subs rest acc → fastC Wl S = false := by
  intro S hS
  simp only [cutOut, List.any_eq_true, Bool.and_eq_true, Bool.not_eq_true'] at h
  obtain ⟨W, hW, ⟨_, ha⟩, hr⟩ := h
  have h1 := cnt_eq_zero_of_any_false (inWord W) acc ha
  have h2 := cnt_eq_zero_of_any_false (inWord W) rest hr
  have h3 := cnt_le_subs (inWord W) rest acc S hS
  exact fastC_false_of_cnt_ne Wl S W hW (by omega)

/-- For EVERY grid, `|RP(G)|` equals the pruned search over its words and white squares. -/
theorem rpCount_eq_pr (G : Grid) :
    rpCount G =
      pr (fastC (allWords G)) (cutIn (allWords G)) (cutOut (allWords G)) (whiteSquares G) [] := by
  unfold rpCount
  rw [bf_congr _ (fastC (allWords G)) (decide_complete G)]
  exact (pr_eq_bf _ _ _ (fun s rest acc h => cutIn_sound _ s rest acc h)
    (fun s rest acc h => cutOut_sound _ s rest acc h) _ _).symm

/-! ## 3. Permutation grids (source, Section 3.2) -/

/-- `w ∈ S_n`: `w` maps `[n] = {1, ..., n}` into itself, injectively and surjectively. (Values of
`w` outside `[n]` are irrelevant and never consulted by `permGrid`.) -/
def IsPerm (n : Nat) (w : Nat → Nat) : Prop :=
  (∀ i, 1 ≤ i → i ≤ n → 1 ≤ w i ∧ w i ≤ n) ∧
  (∀ i j, 1 ≤ i → i ≤ n → 1 ≤ j → j ≤ n → w i = w j → i = j) ∧
  (∀ j, 1 ≤ j → j ≤ n → ∃ i, 1 ≤ i ∧ i ≤ n ∧ w i = j)

/-- "for a permutation w in S_n, we define the crossword grid Grid(w) to be the grid with black
squares in (i, w(i)) for all i in [n]." -/
def permGrid (n : Nat) (w : Nat → Nat) : Grid :=
  { m := n, n := n, black := fun i j => decide (j = w i) }

/-- Conjecture 3.10 of the source: "A positive integer r occurs as the rook placement count of
a permutation grid if and only if r ≠ 4, r ≠ 12, and r ≢ 3 (mod 4)." -/
def Conjecture310 : Prop :=
  ∀ r : Nat, 0 < r →
    ((∃ (n : Nat) (w : Nat → Nat), 1 ≤ n ∧ IsPerm n w ∧ rpCount (permGrid n w) = r) ↔
      (r ≠ 4 ∧ r ≠ 12 ∧ r % 4 ≠ 3))

/-- The "only if" half alone, which is the half that fails. -/
def Conjecture310_onlyIf : Prop :=
  ∀ r : Nat, 0 < r →
    (∃ (n : Nat) (w : Nat → Nat), 1 ≤ n ∧ IsPerm n w ∧ rpCount (permGrid n w) = r) →
      (r ≠ 4 ∧ r ≠ 12 ∧ r % 4 ≠ 3)

/-! ## 4. The witness w = 2 7 4 8 1 6 3 5 -/

/-- One-line notation to a function on `{1, ..., n}`. -/
def ofList (l : List Nat) (i : Nat) : Nat := l.getD (i - 1) 0

def w8 : Nat → Nat := ofList [2, 7, 4, 8, 1, 6, 3, 5]

theorem isPerm_of_bounded (n : Nat) (w : Nat → Nat)
    (h : ∀ i, i < n + 1 → 1 ≤ i → (1 ≤ w i ∧ w i ≤ n) ∧
      (∀ j, j < n + 1 → 1 ≤ j → w i = w j → i = j) ∧
      (∃ k, k < n + 1 ∧ 1 ≤ k ∧ w k = i)) : IsPerm n w :=
  ⟨fun i h1 h2 => (h i (by omega) h1).1,
   fun i j h1 h2 h3 h4 he => (h i (by omega) h1).2.1 j (by omega) h3 he,
   fun j h1 h2 => by
     obtain ⟨k, hk1, hk2, hk3⟩ := (h j (by omega) h1).2.2
     exact ⟨k, hk2, by omega, hk3⟩⟩

theorem w8_isPerm : IsPerm 8 w8 := isPerm_of_bounded 8 w8 (by decide +kernel)

def G8 : Grid := permGrid 8 w8

/-- The 14 across words and 14 down words of `Grid(w8)`, computed from `w8` in the kernel. -/
theorem words8 : allWords G8 =
    [⟨false,1,1,1⟩, ⟨false,1,3,8⟩, ⟨false,2,1,6⟩, ⟨false,2,8,8⟩, ⟨false,3,1,3⟩, ⟨false,3,5,8⟩,
     ⟨false,4,1,7⟩, ⟨false,5,2,8⟩, ⟨false,6,1,5⟩, ⟨false,6,7,8⟩, ⟨false,7,1,2⟩, ⟨false,7,4,8⟩,
     ⟨false,8,1,4⟩, ⟨false,8,6,8⟩,
     ⟨true,1,1,4⟩, ⟨true,1,6,8⟩, ⟨true,2,2,8⟩, ⟨true,3,1,6⟩, ⟨true,3,8,8⟩, ⟨true,4,1,2⟩,
     ⟨true,4,4,8⟩, ⟨true,5,1,7⟩, ⟨true,6,1,5⟩, ⟨true,6,7,8⟩, ⟨true,7,1,1⟩, ⟨true,7,3,8⟩,
     ⟨true,8,1,3⟩, ⟨true,8,5,8⟩] := by decide +kernel

/-- The 56 white squares of `Grid(w8)`, computed from `w8` in the kernel. -/
theorem squares8 : whiteSquares G8 =
    [(1,1),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),
     (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,8),
     (3,1),(3,2),(3,3),(3,5),(3,6),(3,7),(3,8),
     (4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),
     (5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),
     (6,1),(6,2),(6,3),(6,4),(6,5),(6,7),(6,8),
     (7,1),(7,2),(7,4),(7,5),(7,6),(7,7),(7,8),
     (8,1),(8,2),(8,3),(8,4),(8,6),(8,7),(8,8)] := by decide +kernel

/-- **|RP(Grid(2 7 4 8 1 6 3 5))| = 155.** -/
theorem rpCount_G8 : rpCount G8 = 155 := by
  rw [rpCount_eq_pr, words8, squares8]
  decide +kernel

theorem mod_155 : 155 % 4 = 3 := by decide

/-- The witness, with every hypothesis of the conjecture: `155` is a positive integer, `w8 ∈ S_8`,
`|RP(Grid(w8))| = 155`, and `155 ≡ 3 (mod 4)`. -/
theorem witness : 0 < 155 ∧ IsPerm 8 w8 ∧ rpCount (permGrid 8 w8) = 155 ∧ 155 % 4 = 3 :=
  ⟨by decide, w8_isPerm, rpCount_G8, mod_155⟩

theorem not_conjecture310_onlyIf : ¬ Conjecture310_onlyIf := by
  intro h
  have := h 155 (by decide) ⟨8, w8, by decide, w8_isPerm, rpCount_G8⟩
  exact this.2.2 mod_155

/-- **Conjecture 3.10 of arXiv:2609.03081v1 is false.** -/
theorem not_conjecture310 : ¬ Conjecture310 := by
  intro h
  have := (h 155 (by decide)).mp ⟨8, w8, by decide, w8_isPerm, rpCount_G8⟩
  exact this.2.2 mod_155

/-! ## 5. Further facts about the witness grid -/

/-- The white squares of the witness grid are listed without repetition, so `subs` lists every
subset of them exactly once. -/
theorem squares8_nodup : (whiteSquares G8).Nodup := whiteSquares_nodup G8

/-- "no two squares in R lie in the same across word or the same down word". -/
def NonAttacking (G : Grid) (R : List Sq) : Prop :=
  ∀ W : Word, IsWord G W → cnt (inWord W) R ≤ 1

theorem Complete.nonAttacking {G : Grid} {R : List Sq} (h : Complete G R) : NonAttacking G R :=
  fun W hW => Nat.le_of_eq (h W hW)

/-- The other reading of the permutation-matrix convention: black squares in `(w(i), i)`.
`Grid` of this reading is the transpose; the count is the same. -/
def permGridT (n : Nat) (w : Nat → Nat) : Grid :=
  { m := n, n := n, black := fun i j => decide (i = w j) }

theorem rpCount_G8_transposed : rpCount (permGridT 8 w8) = 155 := by
  rw [rpCount_eq_pr]
  decide +kernel

/-! Two more values congruent to 3 mod 4 in S_8. -/

def w191 : Nat → Nat := ofList [3, 6, 1, 8, 5, 2, 7, 4]
def w195 : Nat → Nat := ofList [3, 7, 1, 4, 8, 6, 2, 5]

theorem witness191 : IsPerm 8 w191 ∧ rpCount (permGrid 8 w191) = 191 ∧ 191 % 4 = 3 :=
  ⟨isPerm_of_bounded 8 w191 (by decide +kernel),
   by rw [rpCount_eq_pr]; decide +kernel, by decide⟩

theorem witness195 : IsPerm 8 w195 ∧ rpCount (permGrid 8 w195) = 195 ∧ 195 % 4 = 3 :=
  ⟨isPerm_of_bounded 8 w195 (by decide +kernel),
   by rw [rpCount_eq_pr]; decide +kernel, by decide⟩

/-! ## 6. The definitions reproduce values that the source itself states

Section 2 of the source: an `n × n` grid with no black square has `n!` placements; with one black
corner square `n! - (n-1)!`; with one black edge (non-corner) square `0`; with one black interior
square `(i,j)` it has `(i-1)(j-1)(n-i)(n-j)(n-3)!`; the two grids of display (2.1) have none.
Section 3: `2 5 3 1 4` admits exactly one placement and `2 4 1 3` does not; `2 6 3 1 5 4`
admits 5 and `2 5 1 4 3` admits 6; the maximum over `S_4` is 5 (attained by the layered `2 1 4 3`). -/

def gridOf (m n : Nat) (blacks : List Sq) : Grid :=
  { m := m, n := n, black := fun i j => decide ((i, j) ∈ blacks) }

theorem src_empty_3 : rpCount (gridOf 3 3 []) = 6 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_empty_4 : rpCount (gridOf 4 4 []) = 24 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_corner_3 : rpCount (gridOf 3 3 [(1, 1)]) = 4 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_edge_3 : rpCount (gridOf 3 3 [(1, 2)]) = 0 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_centre_3 : rpCount (gridOf 3 3 [(2, 2)]) = 1 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_interior_4 : rpCount (gridOf 4 4 [(2, 3)]) = 4 := by rw [rpCount_eq_pr]; decide +kernel
theorem src_display21_first : rpCount (gridOf 3 3 [(1, 3), (3, 2)]) = 0 := by
  rw [rpCount_eq_pr]; decide +kernel
theorem src_display21_second : rpCount (gridOf 3 3 [(1, 1), (1, 3), (3, 1), (3, 3)]) = 0 := by
  rw [rpCount_eq_pr]; decide +kernel

theorem src_25314 : rpCount (permGrid 5 (ofList [2, 5, 3, 1, 4])) = 1 := by
  rw [rpCount_eq_pr]; decide +kernel
theorem src_2413 : rpCount (permGrid 4 (ofList [2, 4, 1, 3])) = 2 := by
  rw [rpCount_eq_pr]; decide +kernel
theorem src_263154 : rpCount (permGrid 6 (ofList [2, 6, 3, 1, 5, 4])) = 5 := by
  rw [rpCount_eq_pr]; decide +kernel
theorem src_25143 : rpCount (permGrid 5 (ofList [2, 5, 1, 4, 3])) = 6 := by
  rw [rpCount_eq_pr]; decide +kernel
theorem src_2143 : rpCount (permGrid 4 (ofList [2, 1, 4, 3])) = 5 := by
  rw [rpCount_eq_pr]; decide +kernel

end RookSpectrum

#print axioms RookSpectrum.not_conjecture310
#print axioms RookSpectrum.not_conjecture310_onlyIf
#print axioms RookSpectrum.witness
#print axioms RookSpectrum.rpCount_G8
#print axioms RookSpectrum.w8_isPerm
#print axioms RookSpectrum.words8
#print axioms RookSpectrum.squares8
#print axioms RookSpectrum.squares8_nodup
#print axioms RookSpectrum.rpCount_eq_pr
#print axioms RookSpectrum.rpCount_faithful
#print axioms RookSpectrum.whiteSquares_nodup
#print axioms RookSpectrum.rpCount_eq_cnt
#print axioms RookSpectrum.counted_are_white
#print axioms RookSpectrum.mem_allWords
#print axioms RookSpectrum.mem_whiteSquares
#print axioms RookSpectrum.complete_iff_fastC
#print axioms RookSpectrum.pr_eq_bf
#print axioms RookSpectrum.rpCount_G8_transposed
#print axioms RookSpectrum.witness191
#print axioms RookSpectrum.witness195
#print axioms RookSpectrum.src_empty_3
#print axioms RookSpectrum.src_interior_4
#print axioms RookSpectrum.src_263154
