/-!
# The pullback lemma in general form (target C)

Core Lean only (no imports); compiles under Lean 4.34.0 and 4.30.0. The axioms each headline theorem depends
on are printed by the `#print axioms` lines at the end and recorded in `RECEIPT.json`.

Model (the same as in the generated certificates `Cube5Mod16.lean`, `Cube7Mod24.lean`, `Cube8Mod36.lean`
and their template `QuotientObstruction.template.lean`): an element of Z_N is a natural number below N;
the group sum of a family is its ordinary sum reduced modulo N; a multiset of size d is a list of length d;
an index subset is a Boolean mask, nonempty when some entry is true; the full index set is included;
there is no base point. A subset of Z_M is a predicate `A : Nat → Bool` read on representatives below M,
and `card A M` counts the representatives below M that satisfy it.

Statement. Let `M ∣ N` and let `A` be a set of residues modulo `M` with no projective d-cube. Then its
preimage `pull M A = {x : x mod M ∈ A}` in Z_N has no projective d-cube (`pullback_cubeFree`) and has
exactly `|A| * (N / M)` elements (`pullback_card`). The generated certificates prove this for one fixed
`M` and one fixed `A` each (their theorems `cube_free` and `card_A`); here `M`, `N`, `d` and `A` are
arbitrary. `pullback_refutes` is the general form of their theorem `family`. The converse also holds
(`pullback_cubeFree_iff`): for `N > 0` the preimage is d-cube-free exactly when `A` is.
-/
-- `if_true` is a deprecated name in Lean 4.34 and a current name in 4.30; both compile.
set_option linter.deprecated false

namespace Pullback

/-- Sum of the entries selected by a Boolean mask. -/
def subSum : List Bool → List Nat → Nat
  | b :: m, x :: a => (if b then x else 0) + subSum m a
  | _, _ => 0

/-- Number of x < n with A x. -/
def card (A : Nat → Bool) : Nat → Nat
  | 0 => 0
  | n + 1 => card A n + (if A n then 1 else 0)

/-- A (read on representatives below N) contains no projective d-cube of Z_N: every list of d residues
has a nonempty index subset whose Z_N sum lies outside A. -/
def CubeFree (d N : Nat) (A : Nat → Bool) : Prop :=
  ∀ a : List Nat, a.length = d → (∀ x, x ∈ a → x < N) →
    ∃ m : List Bool, m.length = d ∧ m.any id = true ∧ A (subSum m a % N) = false

/-- The preimage of `A ⊆ Z_M` under reduction modulo `M`. -/
def pull (M : Nat) (A : Nat → Bool) : Nat → Bool := fun x => A (x % M)

/-! ### Cube-freeness is inherited by the preimage -/

theorem subSum_mod (M : Nat) : ∀ (m : List Bool) (a : List Nat),
    subSum m (a.map (· % M)) % M = subSum m a % M
  | [], a => by cases a <;> simp [subSum]
  | _ :: _, [] => by simp [subSum]
  | b :: m, x :: a => by
    have ih := subSum_mod M m a
    cases b
    · simpa [subSum] using ih
    · simp only [subSum, List.map_cons, if_true]
      rw [Nat.add_mod, ih, ← Nat.add_mod, Nat.mod_add_mod]

/-- Strong form: for EVERY list of d natural numbers (no size bound on the entries), some nonempty
index subset has its Z_N sum outside the preimage. -/
theorem pullback_cubeFree_all {d M N : Nat} (hM : 0 < M) (hMN : M ∣ N) {A : Nat → Bool}
    (hA : CubeFree d M A) (a : List Nat) (hlen : a.length = d) :
    ∃ m : List Bool, m.length = d ∧ m.any id = true ∧ pull M A (subSum m a % N) = false := by
  obtain ⟨m, hm, hne, hb⟩ := hA (a.map (· % M)) (by simpa using hlen) (by
    intro x hx
    obtain ⟨y, _, rfl⟩ := List.mem_map.mp hx
    exact Nat.mod_lt _ hM)
  refine ⟨m, hm, hne, ?_⟩
  show A ((subSum m a % N) % M) = false
  rw [Nat.mod_mod_of_dvd _ hMN, ← subSum_mod M m a]
  exact hb

/-- **Pullback lemma, cube-freeness.** If `M ∣ N` and `A ⊆ Z_M` has no projective d-cube, then the
preimage of `A` in `Z_N` has none. (`M = 0` forces `N = 0`, where the statement is vacuous.) -/
theorem pullback_cubeFree {d M N : Nat} (hMN : M ∣ N) {A : Nat → Bool} (hA : CubeFree d M A) :
    CubeFree d N (pull M A) := by
  intro a hlen hlt
  cases M with
  | succ M' => exact pullback_cubeFree_all (Nat.succ_pos M') hMN hA a hlen
  | zero =>
    have hN : N = 0 := Nat.eq_zero_of_zero_dvd hMN
    subst hN
    cases a with
    | cons x a => exact absurd (hlt x (List.mem_cons_self ..)) (Nat.not_lt_zero _)
    | nil =>
      obtain ⟨m, hm, hne, _⟩ := hA [] hlen (fun x hx => absurd hx (List.not_mem_nil))
      have hd : d = 0 := hlen.symm
      subst hd
      have hm' : m = [] := List.eq_nil_of_length_eq_zero hm
      subst hm'
      exact absurd hne (by decide)

/-- `CubeFree d N A` only reads `A` on representatives below `N`. -/
theorem cubeFree_congr {d N : Nat} {A B : Nat → Bool} (hN : 0 < N)
    (hAB : ∀ x, x < N → A x = B x) (hA : CubeFree d N A) : CubeFree d N B := by
  intro a hlen hlt
  obtain ⟨m, hm, hne, hb⟩ := hA a hlen hlt
  refine ⟨m, hm, hne, ?_⟩
  rw [← hAB _ (Nat.mod_lt _ hN)]
  exact hb

/-- Converse of the pullback lemma: a projective d-cube in `A ⊆ Z_M` lifts to one in the preimage. -/
theorem cubeFree_of_pullback {d M N : Nat} (hN : 0 < N) (hMN : M ∣ N) {A : Nat → Bool}
    (h : CubeFree d N (pull M A)) : CubeFree d M A := by
  intro a hlen hlt
  have hle : M ≤ N := Nat.le_of_dvd hN hMN
  obtain ⟨m, hm, hne, hb⟩ := h a hlen (fun x hx => Nat.lt_of_lt_of_le (hlt x hx) hle)
  refine ⟨m, hm, hne, ?_⟩
  have e : pull M A (subSum m a % N) = A (subSum m a % M) := by
    show A ((subSum m a % N) % M) = A (subSum m a % M)
    rw [Nat.mod_mod_of_dvd _ hMN]
  rw [← e]
  exact hb

/-- For `N > 0` and `M ∣ N`: the preimage of `A` in `Z_N` is d-cube-free iff `A ⊆ Z_M` is. -/
theorem pullback_cubeFree_iff {d M N : Nat} (hN : 0 < N) (hMN : M ∣ N) {A : Nat → Bool} :
    CubeFree d N (pull M A) ↔ CubeFree d M A :=
  ⟨cubeFree_of_pullback hN hMN, pullback_cubeFree hMN⟩

/-! ### The preimage has |A| (N / M) elements -/

/-- Number of x in [n, n + j) with A x. -/
def cardFrom (A : Nat → Bool) (n : Nat) : Nat → Nat
  | 0 => 0
  | j + 1 => cardFrom A n j + (if A (n + j) then 1 else 0)

theorem card_eq_cardFrom (A : Nat → Bool) : ∀ n, card A n = cardFrom A 0 n
  | 0 => rfl
  | n + 1 => by
    show card A n + (if A n then 1 else 0) = cardFrom A 0 n + (if A (0 + n) then 1 else 0)
    rw [card_eq_cardFrom A n, Nat.zero_add]

theorem cardFrom_add (A : Nat → Bool) (n : Nat) :
    ∀ j : Nat, cardFrom A 0 (n + j) = cardFrom A 0 n + cardFrom A n j
  | 0 => rfl
  | j + 1 => by
    have ih := cardFrom_add A n j
    show cardFrom A 0 (n + j) + (if A (0 + (n + j)) then 1 else 0) =
      cardFrom A 0 n + (cardFrom A n j + (if A (n + j) then 1 else 0))
    rw [ih, Nat.zero_add, Nat.add_assoc]

theorem cardFrom_pull_shift (M : Nat) (A : Nat → Bool) (k : Nat) :
    ∀ j : Nat, cardFrom (pull M A) (M * k) j = cardFrom (pull M A) 0 j
  | 0 => rfl
  | j + 1 => by
    have ih := cardFrom_pull_shift M A k j
    have e : pull M A (M * k + j) = pull M A (0 + j) := by
      simp only [pull, Nat.mul_add_mod, Nat.zero_add]
    show cardFrom (pull M A) (M * k) j + (if pull M A (M * k + j) then 1 else 0) =
      cardFrom (pull M A) 0 j + (if pull M A (0 + j) then 1 else 0)
    rw [ih, e]

theorem cardFrom_pull_block (M : Nat) (A : Nat → Bool) :
    ∀ j : Nat, j ≤ M → cardFrom (pull M A) 0 j = cardFrom A 0 j
  | 0, _ => rfl
  | j + 1, hj => by
    have ih := cardFrom_pull_block M A j (Nat.le_of_succ_le hj)
    have e : pull M A (0 + j) = A (0 + j) := by
      simp only [pull, Nat.zero_add]
      rw [Nat.mod_eq_of_lt hj]
    show cardFrom (pull M A) 0 j + (if pull M A (0 + j) then 1 else 0) =
      cardFrom A 0 j + (if A (0 + j) then 1 else 0)
    rw [ih, e]

theorem card_pull_mul (M : Nat) (A : Nat → Bool) : ∀ k : Nat, card (pull M A) (M * k) = card A M * k
  | 0 => rfl
  | k + 1 => by
    have ih := card_pull_mul M A k
    rw [card_eq_cardFrom] at ih
    rw [card_eq_cardFrom, Nat.mul_succ, cardFrom_add, cardFrom_pull_shift, ih,
      cardFrom_pull_block M A M (Nat.le_refl M), ← card_eq_cardFrom A M, Nat.mul_succ]

/-- **Pullback lemma, cardinality.** If `M ∣ N` then the preimage of `A ⊆ Z_M` in `Z_N` has
`|A| * (N / M)` elements. -/
theorem pullback_card {M N : Nat} (hMN : M ∣ N) (A : Nat → Bool) :
    card (pull M A) N = card A M * (N / M) := by
  obtain ⟨k, rfl⟩ := hMN
  cases M with
  | zero => simp [card]
  | succ M' => rw [card_pull_mul, Nat.mul_div_cancel_left k (Nat.succ_pos M')]

/-- The density is unchanged: `|pull| * M = |A| * N`. -/
theorem pullback_density {M N : Nat} (hMN : M ∣ N) (A : Nat → Bool) :
    card (pull M A) N * M = card A M * N := by
  obtain ⟨k, rfl⟩ := hMN
  rw [card_pull_mul, Nat.mul_assoc, Nat.mul_comm k M]

/-- General form of the generated certificates' `family`: a d-cube-free `A ⊆ Z_M` of density above
`(d - 1)/d` yields, at every positive multiple `N` of `M`, a d-cube-free subset of `Z_N` of more than
`((d - 1)/d) N` elements. (Whether `d ∣ N`, as Conjecture 4 of Meng requires, is a condition on `N` only.) -/
theorem pullback_refutes {d M N : Nat} (hN : 0 < N) (hMN : M ∣ N) {A : Nat → Bool}
    (hA : CubeFree d M A) (hbig : (d - 1) * M < d * card A M) :
    CubeFree d N (pull M A) ∧ (d - 1) * N < d * card (pull M A) N := by
  refine ⟨pullback_cubeFree hMN hA, ?_⟩
  obtain ⟨k, rfl⟩ := hMN
  have hk : 0 < k := Nat.pos_of_ne_zero (by
    intro h0
    rw [h0, Nat.mul_zero] at hN
    exact Nat.lt_irrefl 0 hN)
  rw [card_pull_mul, ← Nat.mul_assoc, ← Nat.mul_assoc]
  exact Nat.mul_lt_mul_of_pos_right hbig hk

end Pullback

#print axioms Pullback.pullback_cubeFree_all
#print axioms Pullback.pullback_cubeFree
#print axioms Pullback.pullback_cubeFree_iff
#print axioms Pullback.pullback_card
#print axioms Pullback.pullback_density
#print axioms Pullback.pullback_refutes
