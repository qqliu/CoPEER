import Mathlib.Combinatorics.SimpleGraph.Coloring.VertexColoring
import Mathlib.Tactic

/-!
# Every odd cycle `C_n`, `n ≥ 9`, has a non-recolorable uniform clique blowup (kernel-checked)

Source: `astra/story_20260922/LOWER_PALETTE_EXPLORATION.md`, Section 7, and the coordinator's
finite check `check_rotated_domination_family.py` (function `check(n)`), whose definitions are
copied here for a *general* parameter `n : ℕ` with hypotheses `n % 2 = 1` and `9 ≤ n`.

* `q n = (n + 2) / 3` (`r = ceil(n/3)` of the source), `deficit n = 3 q - n ∈ {0,1,2}`
  (the script's `deficit`), `support n k = 2 k + (k - deficit)` = the script's `support[k]`
  (cumulative sums of `deficit` gaps of length 2 followed by gaps of length 3; `support_succ`).
* Graph `Blow n q` on `Fin n × Fin q`: same bag and different label, or bags `i, i ± 1 (mod n)`.
* Frozen `n`-colouring `cF n (i, j) = (i - support j) mod n`, the script's
  `frozen[i] = {(i - x) % n : x in support}` with slot `j` receiving the element for
  `x = support[j]`.
* Fold `fold n i = i` for `i < m`, `(i - m) % 2` otherwise, `m n = 2 q + 1`; lower colouring
  `cL n (i, j) = (fold i + 2 j) mod m`, the script's `lower[i] = {(h[i] + 2 j) % m}`.

Theorems (all general in `n`; none uses enumeration):
`cF_proper`, `cF_sees`, `cF_frozen`, `proper_frozen_n`, `cL_proper`, `m_lt`, `fold_proper`,
`nonrecolorable_blowup`, plus the Mathlib bridge (`colorable`, `chromaticNumber_le`,
`not_colorable`, `chromaticNumber_eq`) and the reconfiguration graph `RGraph` being
disconnected (`RGraph_not_connected`).
-/

set_option linter.unusedSectionVars false

namespace AllOdd

/-! ## Parameters, taken from `check(n)` in the script -/

/-- Bag size `q = (n + 2) / 3` (`= ⌈n/3⌉`). -/
def q (n : ℕ) : ℕ := (n + 2) / 3

/-- Number of gaps of length two, `3 q - n ∈ {0, 1, 2}`. -/
def deficit (n : ℕ) : ℕ := 3 * q n - n

/-- The `k`-th element of the dominating set: `2 k` for `k ≤ deficit`, then steps of `3`. -/
def support (n k : ℕ) : ℕ := 2 * k + (k - deficit n)

/-- The smaller palette `m = 2 q + 1`. -/
def m (n : ℕ) : ℕ := 2 * q n + 1

/-- The folding `C_n → C_m` of the script: identity on `[0, m)`, then alternating `0, 1`. -/
def fold (n i : ℕ) : ℕ := if i < m n then i else (i - m n) % 2

theorem q_spec (n : ℕ) : 3 * q n ≤ n + 2 ∧ n ≤ 3 * q n := by unfold q; omega
theorem deficit_le (n : ℕ) : deficit n ≤ 2 := by unfold deficit q; omega
theorem deficit_spec (n : ℕ) : deficit n + n = 3 * q n := by unfold deficit q; omega
theorem three_le_q {n : ℕ} (hn : 9 ≤ n) : 3 ≤ q n := by unfold q; omega
/-- `2 q + 1 < n` for every `n ≥ 9`. -/
theorem m_lt {n : ℕ} (hn : 9 ≤ n) : m n < n := by unfold m q; omega

theorem support_zero (n : ℕ) : support n 0 = 0 := by unfold support; omega
/-- The gap rule of the script: `deficit` gaps of length two, then gaps of length three. -/
theorem support_succ (n k : ℕ) :
    support n (k + 1) = support n k + (if k < deficit n then 2 else 3) := by
  unfold support; split_ifs <;> omega
theorem support_last {n : ℕ} (hn : 9 ≤ n) : support n (q n - 1) + 3 = n := by
  have := q_spec n; have := deficit_spec n; have := deficit_le n; unfold support; omega
theorem support_add_three_le {n k : ℕ} (hn : 9 ≤ n) (hk : k < q n) : support n k + 3 ≤ n := by
  have := q_spec n; have := deficit_spec n; have := deficit_le n; unfold support; omega
theorem support_inj {n k k' : ℕ} (h : support n k = support n k') : k = k' := by
  unfold support at h; omega
/-- Independence: no two elements of the dominating set are consecutive. -/
theorem support_ne_succ (n k k' : ℕ) : support n k' ≠ support n k + 1 := by
  unfold support; omega

/-- Reduction of `x % n` for `x < 2 n`, in a form `omega` can use (the positivity hypothesis
is kept only for readability at call sites; it is not needed). -/
theorem mod_cases (n x : ℕ) (_hn : 0 < n) (hx : x < 2 * n) :
    (x < n ∧ x % n = x) ∨ (n ≤ x ∧ x % n = x - n) := by
  rcases Nat.lt_or_ge x n with h | h
  · exact Or.inl ⟨h, Nat.mod_eq_of_lt h⟩
  · refine Or.inr ⟨h, ?_⟩
    rw [Nat.mod_eq_sub_mod h, Nat.mod_eq_of_lt (by omega)]

/-- Domination: every residue `t` is in the set, or one below it, or one above it (mod `n`). -/
theorem dominating {n : ℕ} (hn : 9 ≤ n) (t : ℕ) (ht : t < n) :
    ∃ j, j < q n ∧ (support n j = t ∨ support n j + 1 = t ∨ support n j = (t + 1) % n) := by
  have hd := deficit_le n
  have hq := q_spec n
  have hq3 := three_le_q hn
  have hdq := deficit_spec n
  have ht1 := mod_cases n (t + 1) (by omega) (by omega)
  by_cases h4 : t + 4 ≤ n
  · rcases Nat.lt_or_ge t (2 * deficit n) with h2 | h2
    · refine ⟨t / 2, by omega, ?_⟩
      unfold support; omega
    · by_cases hr : (t - 2 * deficit n) % 3 = 2
      · refine ⟨deficit n + (t - 2 * deficit n) / 3 + 1, by omega, ?_⟩
        unfold support; omega
      · refine ⟨deficit n + (t - 2 * deficit n) / 3, by omega, ?_⟩
        unfold support; omega
  · by_cases h1 : t = n - 1
    · refine ⟨0, by omega, Or.inr (Or.inr ?_)⟩
      rw [support_zero]; omega
    · refine ⟨q n - 1, by omega, ?_⟩
      have := support_last hn
      omega

/-! ## The blowup graph `C_n[K_q]` on `Fin n × Fin q` -/

/-- `C_n[K_q]`: `(i,a) ~ (j,b)` iff `i = j ∧ a ≠ b`, or `i ≠ j` and `j ≡ i + 1` or
`i ≡ j + 1 (mod n)`. -/
def Blow (n q : ℕ) : SimpleGraph (Fin n × Fin q) where
  Adj u v := (u.1 = v.1 ∧ u.2 ≠ v.2) ∨
    (u.1 ≠ v.1 ∧ (v.1.val = (u.1.val + 1) % n ∨ u.1.val = (v.1.val + 1) % n))
  symm := by
    rintro u v (⟨h1, h2⟩ | ⟨h1, h2⟩)
    · exact Or.inl ⟨h1.symm, fun h => h2 h.symm⟩
    · exact Or.inr ⟨fun h => h1 h.symm, h2.symm⟩
  loopless := ⟨by
    rintro u (⟨_, h⟩ | ⟨h, _⟩)
    · exact h rfl
    · exact h rfl⟩

theorem Blow_adj {n q : ℕ} (u v : Fin n × Fin q) :
    (Blow n q).Adj u v ↔ (u.1 = v.1 ∧ u.2 ≠ v.2) ∨
      (u.1 ≠ v.1 ∧ (v.1.val = (u.1.val + 1) % n ∨ u.1.val = (v.1.val + 1) % n)) := Iff.rfl

/-- Proper colouring with colours `Fin k`. -/
def Proper (n q : ℕ) {k : ℕ} (c : Fin n × Fin q → Fin k) : Prop :=
  ∀ u v, (Blow n q).Adj u v → c u ≠ c v

/-- Every vertex sees every other colour on a neighbour (closed neighbourhood form). -/
def Sees (n q : ℕ) {k : ℕ} (c : Fin n × Fin q → Fin k) : Prop :=
  ∀ v col, col ≠ c v → ∃ u, (Blow n q).Adj v u ∧ c u = col

/-- Adjacency in the reconfiguration graph: differ at exactly one vertex (`Recol.RAdj`). -/
def RAdj {V : Type} {k : ℕ} (f g : V → Fin k) : Prop :=
  ∃ v, f v ≠ g v ∧ ∀ w, w ≠ v → f w = g w

/-- Frozen, as in `Recol.Frozen` of `CycleBlowupAllN.lean`: proper, and no proper colouring
differs from it at exactly one vertex. -/
def Frozen (n q : ℕ) {k : ℕ} (c : Fin n × Fin q → Fin k) : Prop :=
  Proper n q c ∧ ∀ g, Proper n q g → ¬ RAdj c g

theorem frozen_of_sees {n q k : ℕ} {c : Fin n × Fin q → Fin k}
    (hp : Proper n q c) (hs : Sees n q c) : Frozen n q c := by
  refine ⟨hp, fun g hg ⟨v, hne, hagree⟩ => ?_⟩
  obtain ⟨u, hadj, hcu⟩ := hs v (g v) (Ne.symm hne)
  have huv : u ≠ v := fun h => SimpleGraph.irrefl (G := Blow n q) (h ▸ hadj)
  exact hg v u hadj (((hagree u huv).symm.trans hcu).symm)

/-! ## The frozen `n`-colouring -/

/-- `cF n (i, j) = (i - support j) mod n`. -/
def cF (n : ℕ) (v : Fin n × Fin (q n)) : Fin n :=
  ⟨(v.1.val + n - support n v.2.val) % n, Nat.mod_lt _ v.1.pos⟩

theorem cF_val (n : ℕ) (v : Fin n × Fin (q n)) :
    (cF n v).val = (v.1.val + n - support n v.2.val) % n := rfl

theorem cF_proper {n : ℕ} (hn : 9 ≤ n) : Proper n (q n) (cF n) := by
  rintro ⟨i, a⟩ ⟨j, b⟩ hadj heq
  have hv : (i.val + n - support n a.val) % n = (j.val + n - support n b.val) % n :=
    congrArg Fin.val heq
  have hi := i.isLt
  have hj := j.isLt
  have hsa := support_add_three_le hn a.isLt
  have hsb := support_add_three_le hn b.isLt
  have hn0 : 0 < n := by omega
  have h1 := mod_cases n (i.val + n - support n a.val) hn0 (by omega)
  have h2 := mod_cases n (j.val + n - support n b.val) hn0 (by omega)
  rw [Blow_adj] at hadj
  rcases hadj with ⟨hij, hab⟩ | ⟨_, hnext | hnext⟩
  · have hij' : i.val = j.val := congrArg Fin.val hij
    have hs : support n a.val = support n b.val := by omega
    exact hab (Fin.ext (support_inj hs))
  · have h3 := mod_cases n (i.val + 1) hn0 (by omega)
    have hnext' : j.val = (i.val + 1) % n := hnext
    exact support_ne_succ n a.val b.val (by omega)
  · have h3 := mod_cases n (j.val + 1) hn0 (by omega)
    have hnext' : i.val = (j.val + 1) % n := hnext
    exact support_ne_succ n b.val a.val (by omega)

theorem cF_sees {n : ℕ} (hn : 9 ≤ n) : Sees n (q n) (cF n) := by
  rintro ⟨i, a⟩ col hne
  have hi := i.isLt
  have hcol := col.isLt
  have hn0 : 0 < n := by omega
  have ht := mod_cases n (i.val + n - col.val) hn0 (by omega)
  obtain ⟨j, hj, hcase⟩ := dominating hn ((i.val + n - col.val) % n) (Nat.mod_lt _ hn0)
  have hsj := support_add_three_le hn hj
  have hval : ∀ b : Fin n, (cF n (b, ⟨j, hj⟩)).val = (b.val + n - support n j) % n :=
    fun b => rfl
  rcases hcase with h | h | h
  · -- colour `col` sits in bag `i` itself
    have hc : cF n (i, ⟨j, hj⟩) = col := by
      apply Fin.ext
      rw [hval]
      have := mod_cases n (i.val + n - support n j) hn0 (by omega)
      omega
    refine ⟨(i, ⟨j, hj⟩), ?_, hc⟩
    rw [Blow_adj]
    refine Or.inl ⟨rfl, fun hab => hne ?_⟩
    have hab' : a = ⟨j, hj⟩ := hab
    subst hab'
    exact hc.symm
  · -- colour `col` sits in the previous bag `i - 1`
    have hb1 := mod_cases n (i.val + n - 1) hn0 (by omega)
    set b : Fin n := ⟨(i.val + n - 1) % n, Nat.mod_lt _ hn0⟩ with hb
    have hbv : b.val = (i.val + n - 1) % n := rfl
    have hb2 := mod_cases n (b.val + 1) hn0 (by omega)
    have hc : cF n (b, ⟨j, hj⟩) = col := by
      apply Fin.ext
      rw [hval]
      have := mod_cases n (b.val + n - support n j) hn0 (by omega)
      omega
    refine ⟨(b, ⟨j, hj⟩), ?_, hc⟩
    rw [Blow_adj]
    refine Or.inr ⟨fun hib => ?_, Or.inr ?_⟩
    · have : i.val = b.val := congrArg Fin.val hib
      omega
    · show i.val = (b.val + 1) % n
      omega
  · -- colour `col` sits in the next bag `i + 1`
    have ht1 := mod_cases n ((i.val + n - col.val) % n + 1) hn0 (by omega)
    have hb1 := mod_cases n (i.val + 1) hn0 (by omega)
    set b : Fin n := ⟨(i.val + 1) % n, Nat.mod_lt _ hn0⟩ with hb
    have hbv : b.val = (i.val + 1) % n := rfl
    have hc : cF n (b, ⟨j, hj⟩) = col := by
      apply Fin.ext
      rw [hval]
      have := mod_cases n (b.val + n - support n j) hn0 (by omega)
      omega
    refine ⟨(b, ⟨j, hj⟩), ?_, hc⟩
    rw [Blow_adj]
    refine Or.inr ⟨fun hib => ?_, Or.inl ?_⟩
    · have : i.val = b.val := congrArg Fin.val hib
      omega
    · show b.val = (i.val + 1) % n
      exact hbv

theorem cF_frozen {n : ℕ} (hn : 9 ≤ n) : Frozen n (q n) (cF n) :=
  frozen_of_sees (cF_proper hn) (cF_sees hn)

/-- (1) For every odd `n ≥ 9`, `cF n` is a proper `n`-colouring of `C_n[K_q]` that is frozen
(sees all `n` colours in every closed neighbourhood, hence isolated in `R_n`).  Oddness is
not used here: the frozen colouring exists for every `n ≥ 9`. -/
theorem proper_frozen_n (n : ℕ) (_hodd : n % 2 = 1) (hn : 9 ≤ n) :
    Proper n (q n) (cF n) ∧ Sees n (q n) (cF n) ∧ Frozen n (q n) (cF n) :=
  ⟨cF_proper hn, cF_sees hn, cF_frozen hn⟩

/-! ## The folded `(2q+1)`-colouring -/

theorem fold_lt {n : ℕ} (hn : 9 ≤ n) (i : ℕ) : fold n i < m n := by
  unfold fold m q; split_ifs <;> omega

/-- The fold maps every cycle edge of `C_n` (including the closing edge) to an edge of `C_m`. -/
theorem fold_step {n : ℕ} (hodd : n % 2 = 1) (hn : 9 ≤ n) (i : ℕ) (hi : i < n) :
    fold n ((i + 1) % n) = fold n i + 1 ∨ (fold n i + 1 = m n ∧ fold n ((i + 1) % n) = 0) ∨
    fold n ((i + 1) % n) + 1 = fold n i ∨ (fold n i = 0 ∧ fold n ((i + 1) % n) + 1 = m n) := by
  have := mod_cases n (i + 1) (by omega) (by omega)
  unfold fold m q
  split_ifs <;> omega

/-- `cL n (i, j) = (fold i + 2 j) mod m`. -/
def cL (n : ℕ) (v : Fin n × Fin (q n)) : Fin (m n) :=
  ⟨(fold n v.1.val + 2 * v.2.val) % m n, Nat.mod_lt _ (by unfold m; omega)⟩

theorem cL_proper {n : ℕ} (hodd : n % 2 = 1) (hn : 9 ≤ n) : Proper n (q n) (cL n) := by
  rintro ⟨i, a⟩ ⟨j, b⟩ hadj heq
  have hv : (fold n i.val + 2 * a.val) % m n = (fold n j.val + 2 * b.val) % m n :=
    congrArg Fin.val heq
  have hfi := fold_lt hn i.val
  have hfj := fold_lt hn j.val
  have ha := a.isLt
  have hb := b.isLt
  have hm : m n = 2 * q n + 1 := rfl
  have hm0 : 0 < m n := by omega
  have h1 := mod_cases (m n) (fold n i.val + 2 * a.val) hm0 (by omega)
  have h2 := mod_cases (m n) (fold n j.val + 2 * b.val) hm0 (by omega)
  rw [Blow_adj] at hadj
  rcases hadj with ⟨hij, hab⟩ | ⟨_, hnext | hnext⟩
  · have hij' : i.val = j.val := congrArg Fin.val hij
    rw [hij'] at hv h1
    have hab' : a ≠ b := hab
    exact hab' (Fin.ext (by omega))
  · have hs := fold_step hodd hn i.val i.isLt
    have hnext' : j.val = (i.val + 1) % n := hnext
    rw [← hnext'] at hs
    omega
  · have hs := fold_step hodd hn j.val j.isLt
    have hnext' : i.val = (j.val + 1) % n := hnext
    rw [← hnext'] at hs
    omega

/-- (2) For every odd `n ≥ 9`, `cL n` is a proper colouring with `2 q + 1 < n` colours. -/
theorem fold_proper (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    Proper n (q n) (cL n) ∧ m n < n :=
  ⟨cL_proper hodd hn, m_lt hn⟩

/-! ## Corollary: not recolorable at palette size `n` -/

/-- `cL` viewed inside the `n` colours. -/
def cLn (n : ℕ) (hn : 9 ≤ n) (v : Fin n × Fin (q n)) : Fin n :=
  ⟨(cL n v).val, lt_trans (cL n v).isLt (m_lt hn)⟩

theorem cLn_proper {n : ℕ} (hodd : n % 2 = 1) (hn : 9 ≤ n) : Proper n (q n) (cLn n hn) := by
  intro u v hadj heq
  have h' : (cLn n hn u).val = (cLn n hn v).val := congrArg Fin.val heq
  exact cL_proper hodd hn u v hadj (Fin.ext h')

/-- A proper colouring with an unused colour is not frozen. -/
theorem not_frozen_of_unused {n q k : ℕ} (c : Fin n × Fin q → Fin k) (hp : Proper n q c)
    (col : Fin k) (hun : ∀ w, c w ≠ col) (v : Fin n × Fin q) : ¬ Frozen n q c := by
  intro hf
  apply hf.2 (Function.update c v col)
  · intro x y hxy hxy'
    by_cases hx : x = v
    · subst hx
      have hy : y ≠ x := fun h => SimpleGraph.irrefl (G := Blow n q) (h ▸ hxy)
      rw [Function.update_self, Function.update_of_ne hy] at hxy'
      exact hun y hxy'.symm
    · rw [Function.update_of_ne hx] at hxy'
      by_cases hy : y = v
      · subst hy
        rw [Function.update_self] at hxy'
        exact hun x hxy'
      · rw [Function.update_of_ne hy] at hxy'
        exact hp x y hxy hxy'
  · refine ⟨v, ?_, fun w hw => by rw [Function.update_of_ne hw]⟩
    rw [Function.update_self]
    exact hun v

theorem cLn_not_frozen {n : ℕ} (hodd : n % 2 = 1) (hn : 9 ≤ n) : ¬ Frozen n (q n) (cLn n hn) := by
  have hm := m_lt hn
  refine not_frozen_of_unused _ (cLn_proper hodd hn) ⟨n - 1, by omega⟩ ?_
    (⟨0, by omega⟩, ⟨0, by have := three_le_q hn; omega⟩)
  intro w h
  have h1 : (cL n w).val = n - 1 := congrArg Fin.val h
  have h2 := (cL n w).isLt
  omega

/-- (3) For every odd `n ≥ 9`: `C_n[K_q]` with `q = (n+2)/3` has a proper `(2q+1)`-colouring,
`2q + 1 < n`, and a frozen proper `n`-colouring (an isolated vertex of `R_n`), while the
`(2q+1)`-colouring seen in `n` colours is a proper `n`-colouring that is not frozen. -/
theorem nonrecolorable_blowup (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    (∃ c : Fin n × Fin (q n) → Fin (m n), Proper n (q n) c) ∧ m n < n ∧
    (∃ c : Fin n × Fin (q n) → Fin n, Frozen n (q n) c) ∧
    (∃ c : Fin n × Fin (q n) → Fin n, Proper n (q n) c ∧ ¬ Frozen n (q n) c) :=
  ⟨⟨cL n, cL_proper hodd hn⟩, m_lt hn, ⟨cF n, cF_frozen hn⟩,
    ⟨cLn n hn, cLn_proper hodd hn, cLn_not_frozen hodd hn⟩⟩

/-! ## Mathlib bridge: colourability and the chromatic number -/

theorem colorable (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) : (Blow n (q n)).Colorable (m n) :=
  ⟨SimpleGraph.Coloring.mk (cL n) fun h => cL_proper hodd hn _ _ h⟩

theorem chromaticNumber_le (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    (Blow n (q n)).chromaticNumber ≤ m n :=
  (colorable n hodd hn).chromaticNumber_le

theorem chromaticNumber_lt (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    (Blow n (q n)).chromaticNumber < n :=
  lt_of_le_of_lt (chromaticNumber_le n hodd hn) (by exact_mod_cast m_lt hn)

/-- Bag successor `i ↦ i + 1 (mod n)`. -/
def succ (n : ℕ) (i : Fin n) : Fin n := ⟨(i.val + 1) % n, Nat.mod_lt _ i.pos⟩

theorem succ_injective (n : ℕ) : Function.Injective (succ n) := by
  intro i j h
  have h' : (i.val + 1) % n = (j.val + 1) % n := congrArg Fin.val h
  have hi := i.isLt
  have hj := j.isLt
  have h1 := mod_cases n (i.val + 1) i.pos (by omega)
  have h2 := mod_cases n (j.val + 1) j.pos (by omega)
  exact Fin.ext (by omega)

/-- An independent set of `C_n` has at most `n / 2` elements (`T` and `T + 1` are disjoint). -/
theorem cycle_indep_card_le (n : ℕ) (T : Finset (Fin n)) (h : ∀ i ∈ T, succ n i ∉ T) :
    2 * T.card ≤ n := by
  have hdisj : Disjoint T (T.image (succ n)) := by
    rw [Finset.disjoint_left]
    intro i hi hi'
    obtain ⟨j, hj, hji⟩ := Finset.mem_image.mp hi'
    exact h j hj (hji ▸ hi)
  have himg : (T.image (succ n)).card = T.card :=
    Finset.card_image_of_injective _ (succ_injective n)
  have hle : (T ∪ T.image (succ n)).card ≤ n := by
    have := Finset.card_le_univ (T ∪ T.image (succ n))
    simpa using this
  rw [Finset.card_union_of_disjoint hdisj, himg] at hle
  omega

/-- Each colour class of a proper colouring of `C_n[K_q]` (`n ≥ 2`) has at most `n / 2`
vertices: at most one per bag, and its bags form an independent set of `C_n`. -/
theorem colourClass_card_le {n q : ℕ} (hn : 2 ≤ n) {k : ℕ} (c : Fin n × Fin q → Fin k)
    (hc : Proper n q c) (col : Fin k) :
    2 * (Finset.univ.filter fun v : Fin n × Fin q => c v = col).card ≤ n := by
  set S := Finset.univ.filter fun v : Fin n × Fin q => c v = col with hS
  have hmem : ∀ v, v ∈ S ↔ c v = col := by intro v; simp [hS]
  have hinj : Set.InjOn Prod.fst (S : Set (Fin n × Fin q)) := by
    intro u hu v hv huv
    by_contra hne
    have hadj : (Blow n q).Adj u v := by
      rw [Blow_adj]; exact Or.inl ⟨huv, fun h2 => hne (Prod.ext huv h2)⟩
    exact hc u v hadj
      (((hmem u).1 (Finset.mem_coe.1 hu)).trans ((hmem v).1 (Finset.mem_coe.1 hv)).symm)
  rw [← Finset.card_image_of_injOn hinj]
  apply cycle_indep_card_le
  intro i hi hi1
  obtain ⟨u, hu, rfl⟩ := Finset.mem_image.mp hi
  obtain ⟨w, hw, hw1⟩ := Finset.mem_image.mp hi1
  have hwv : w.1.val = (u.1.val + 1) % n := by rw [hw1]; rfl
  have hadj : (Blow n q).Adj u w := by
    rw [Blow_adj]
    refine Or.inr ⟨fun huw => ?_, Or.inl hwv⟩
    have h1 : u.1.val = w.1.val := congrArg Fin.val huw
    have h2 := u.1.isLt
    have h3 := mod_cases n (u.1.val + 1) (by omega) (by omega)
    omega
  exact hc u w hadj (((hmem u).1 hu).trans ((hmem w).1 hw).symm)

/-- No proper colouring of `C_n[K_q]` with `k ≤ 2 q` colours (odd `n ≥ 9`): `k` classes of
size `≤ (n-1)/2` cover at most `q (n - 1) < q n` vertices. -/
theorem not_proper_of_le (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) {k : ℕ} (hk : k ≤ 2 * q n)
    (c : Fin n × Fin (q n) → Fin k) : ¬ Proper n (q n) c := by
  intro hc
  have hq := three_le_q hn
  obtain ⟨h, rfl⟩ : ∃ h, n = 2 * h + 1 := ⟨(n - 1) / 2, by omega⟩
  have hcard : (Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))).card =
      (2 * h + 1) * q (2 * h + 1) := by simp
  have hfib : ∀ col ∈ (Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))).image c,
      (Finset.univ.filter fun v => c v = col).card ≤ h := by
    intro col _
    have := colourClass_card_le (by omega) c hc col
    omega
  have h1 := Finset.card_le_mul_card_image (Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))) h hfib
  have h2 : ((Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))).image c).card ≤ k := by
    have := Finset.card_le_univ ((Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))).image c)
    simpa using this
  have h3 : h * ((Finset.univ : Finset (Fin (2 * h + 1) × Fin (q (2 * h + 1)))).image c).card
      ≤ h * (2 * q (2 * h + 1)) := Nat.mul_le_mul_left h (le_trans h2 hk)
  have h4 : h * (2 * q (2 * h + 1)) = 2 * (h * q (2 * h + 1)) := by ring
  have h5 : (2 * h + 1) * q (2 * h + 1) = 2 * (h * q (2 * h + 1)) + q (2 * h + 1) := by ring
  omega

theorem not_colorable (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    ¬ (Blow n (q n)).Colorable (2 * q n) :=
  fun ⟨C⟩ => not_proper_of_le n hodd hn le_rfl C fun _ _ h => C.valid h

/-- `χ(C_n[K_q]) = 2 q + 1` exactly, for every odd `n ≥ 9`. -/
theorem chromaticNumber_eq (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    (Blow n (q n)).chromaticNumber = m n := by
  have := SimpleGraph.chromaticNumber_eq_iff_colorable_not_colorable.mpr
    ⟨colorable n hodd hn, not_colorable n hodd hn⟩
  simpa [m] using this

/-! ## The reconfiguration graph `R_n` is disconnected -/

/-- `R_k(C_n[K_q])`: proper `k`-colourings, adjacent when they differ at exactly one vertex. -/
def RGraph (n q k : ℕ) : SimpleGraph {f : Fin n × Fin q → Fin k // Proper n q f} where
  Adj f g := RAdj f.1 g.1
  symm := by
    rintro f g ⟨v, hne, hag⟩
    exact ⟨v, fun e => hne e.symm, fun w hw => (hag w hw).symm⟩
  loopless := ⟨by
    rintro f ⟨v, hne, _⟩
    exact hne rfl⟩

theorem frozen_isolated {n q k : ℕ} (f g : {f : Fin n × Fin q → Fin k // Proper n q f})
    (hf : Frozen n q f.1) : ¬ (RGraph n q k).Adj f g :=
  fun h => hf.2 g.1 g.2 h

theorem frozen_reachable_eq {n q k : ℕ} (f g : {f : Fin n × Fin q → Fin k // Proper n q f})
    (hf : Frozen n q f.1) (h : (RGraph n q k).Reachable f g) : f = g := by
  obtain ⟨p⟩ := h
  cases p with
  | nil => rfl
  | cons hadj _ => exact absurd hadj (frozen_isolated f _ hf)

/-- The `n`-colour reconfiguration graph of `C_n[K_q]` is not connected (odd `n ≥ 9`):
the frozen colouring `cF` is isolated and `cLn` is a different proper `n`-colouring. -/
theorem RGraph_not_connected (n : ℕ) (hodd : n % 2 = 1) (hn : 9 ≤ n) :
    ¬ (RGraph n (q n) n).Connected := by
  intro hconn
  have hq := three_le_q hn
  have hm := m_lt hn
  have heq := frozen_reachable_eq ⟨cF n, cF_proper hn⟩ ⟨cLn n hn, cLn_proper hodd hn⟩
    (cF_frozen hn) (hconn.preconnected _ _)
  have hfun : cF n = cLn n hn := congrArg Subtype.val heq
  -- `cF` uses colour `n - 1` somewhere (it is frozen), `cLn` never does.
  have h0 : (⟨n - 1, by omega⟩ : Fin n) ≠ cF n (⟨0, by omega⟩, ⟨0, by omega⟩) := by
    intro h
    have h' : n - 1 = (0 + n - support n 0) % n := congrArg Fin.val h
    rw [support_zero, Nat.zero_add, Nat.sub_zero, Nat.mod_self] at h'
    omega
  obtain ⟨u, _, hu⟩ := cF_sees hn (⟨0, by omega⟩, ⟨0, by omega⟩) _ h0
  have h1 : (cF n u).val = n - 1 := congrArg Fin.val hu
  have h2 : (cLn n hn u).val < m n := (cL n u).isLt
  rw [hfun] at h1
  omega

end AllOdd

#print axioms AllOdd.dominating
#print axioms AllOdd.support_ne_succ
#print axioms AllOdd.cF_proper
#print axioms AllOdd.cF_sees
#print axioms AllOdd.cF_frozen
#print axioms AllOdd.proper_frozen_n
#print axioms AllOdd.fold_step
#print axioms AllOdd.cL_proper
#print axioms AllOdd.m_lt
#print axioms AllOdd.fold_proper
#print axioms AllOdd.cLn_not_frozen
#print axioms AllOdd.nonrecolorable_blowup
#print axioms AllOdd.colorable
#print axioms AllOdd.chromaticNumber_le
#print axioms AllOdd.chromaticNumber_lt
#print axioms AllOdd.cycle_indep_card_le
#print axioms AllOdd.colourClass_card_le
#print axioms AllOdd.not_proper_of_le
#print axioms AllOdd.not_colorable
#print axioms AllOdd.chromaticNumber_eq
#print axioms AllOdd.frozen_reachable_eq
#print axioms AllOdd.RGraph_not_connected
