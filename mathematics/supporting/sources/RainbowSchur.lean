/-
Rainbow Schur triples: kernel certificate for research case rank 3
(record ext5_rainbow_schur_density_two_fifths).

Source: O. Parczyk and C. Spiegel, An Unsure Note on an Un-Schur Problem,
Electron. J. Combin. 33(1) (2026) P1.45; arXiv:2410.22024. "We conjecture the lower bound to be
tight": the maximum fraction of rainbow ordered Schur triples over 3-colourings of [n] is
asymptotically 2/5.

Headlines.
  witness_count                  : for ALL m, the colouring col m of [22m] has exactly 99 m^2 + 3 m
                                   rainbow ordered Schur triples.
  family_above                   : for all m >= 1, 22 * 2R > 9 * n(n-1) at n = 22m.
  everywhere_above               : for EVERY n >= 3608 some 3-colouring has R > (2/5 + 1/220) binom(n,2).
  not_tightnessConjecture        : the epsilon-N (limsup) form of the conjecture is false.
  not_tightnessConjectureLiminf  : the weakest (liminf) reading is false as well.

Core Lean only: no Mathlib, no sorry, no native_decide, no axiom declarations.

Choices made for tractability and not dictated by the source (see BINDING.md):
  * the count is sum_{z<=n} r(z) with r(z) = #{x in [1,z-1] : (x, z-x, z) rainbow}; this is the
    source's own r(z) and |S_R| = sum_z r(z) (Section 2.2), but it is a nested sum of indicators,
    not a cardinality of a set of triples;
  * colours are compared through Fin.val (rainbowInd_fin shows this is the Fin 3 comparison);
  * epsilon ranges over positive rationals p/q, cross-multiplied; no real numbers occur;
  * omega, grind and simp bring in propext, Classical.choice and Quot.sound; only the three
    `decide +kernel` cross-checks are axiom-free.
The count is tied to a cardinality in general: `rainbowCount_eq_length` (length of the rainbow
sublist of `schurPairs n`), `mem_schurPairs`, `nodup_schurPairs`, `schurPairs_length`.
`bruteCount` is a further, differently shaped definition checked only at n = 22 and n = 44.

Development record: this is the fourth proof design. Three earlier designs of the inner-sum lemma
ended in deterministic timeouts (closed forms with min, truncated subtraction and /2 under
`repeat' split <;> omega`), and one later draft failed on a mis-edited case split and a rewrite that
matched the wrong segment. The counts are in RECEIPT.json.
-/

def sumTo (f : Nat → Nat) : Nat → Nat
  | 0 => 0
  | n+1 => sumTo f n + f (n+1)

def rainbowInd (c : Nat → Nat) (x y z : Nat) : Nat :=
  if c x ≠ c y ∧ c x ≠ c z ∧ c y ≠ c z then 1 else 0

def rz (c : Nat → Nat) (z : Nat) : Nat := sumTo (fun x => rainbowInd c x (z - x) z) (z - 1)

def rainbowCount (c : Nat → Nat) (n : Nat) : Nat := sumTo (rz c) n

def col (m k : Nat) : Nat :=
  if k % 2 = 0 then 0 else if k ≤ 8*m then 1 else if k ≤ 20*m then 2 else 1

theorem col_spec (m k : Nat) :
    (col m k = 0 ∧ k % 2 = 0) ∨ (col m k = 1 ∧ k % 2 = 1 ∧ (k ≤ 8*m ∨ 20*m < k)) ∨
    (col m k = 2 ∧ k % 2 = 1 ∧ 8*m < k ∧ k ≤ 20*m) := by
  unfold col; repeat' split
  all_goals omega

/-! generic sum lemmas -/
theorem sumTo_congr {f g : Nat → Nat} : ∀ n, (∀ k, 1 ≤ k → k ≤ n → f k = g k) → sumTo f n = sumTo g n := by
  intro n
  induction n with
  | zero => intro _; rfl
  | succ n ih =>
    intro h
    simp only [sumTo]
    rw [ih (fun k h1 h2 => h k h1 (by omega)), h (n+1) (by omega) (by omega)]

theorem sumTo_add (f g : Nat → Nat) : ∀ n, sumTo (fun k => f k + g k) n = sumTo f n + sumTo g n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => simp only [sumTo]; rw [ih]; omega

def parIn (par lo hi x : Nat) : Nat := if x % 2 = par ∧ lo < x ∧ x ≤ hi then 1 else 0

theorem sum_parIn (par lo hi : Nat) (hp : par ≤ 1) : ∀ t,
    sumTo (parIn par lo hi) t = (min t hi + par)/2 - (lo + par)/2 := by
  intro t
  induction t with
  | zero => simp only [sumTo]; omega
  | succ t ih =>
    simp only [sumTo]; rw [ih]; unfold parIn
    split <;> omega


theorem rainbowInd_spec (c : Nat → Nat) (x y z : Nat) :
    (rainbowInd c x y z = 1 ∧ c x ≠ c y ∧ c x ≠ c z ∧ c y ≠ c z) ∨
    (rainbowInd c x y z = 0 ∧ (c x = c y ∨ c x = c z ∨ c y = c z)) := by
  unfold rainbowInd; split <;> omega

theorem parIn_spec (par lo hi x : Nat) :
    (parIn par lo hi x = 1 ∧ x % 2 = par ∧ lo < x ∧ x ≤ hi) ∨
    (parIn par lo hi x = 0 ∧ (x % 2 ≠ par ∨ x ≤ lo ∨ hi < x)) := by
  unfold parIn; split <;> omega

macro "pt_tac" m:term "," z:term "," x:term "," a:term "," b:term : tactic => `(tactic| (
  have cx := col_spec $m $x
  have cy := col_spec $m ($z - $x)
  have cz := col_spec $m $z
  have hr := rainbowInd_spec (col $m) $x ($z - $x) $z
  have ha := $a
  have hb := $b
  rcases cx with ⟨cx, px⟩ | ⟨cx, px, qx⟩ | ⟨cx, px, qx, qx'⟩ <;>
  rcases cy with ⟨cy, py⟩ | ⟨cy, py, qy⟩ | ⟨cy, py, qy, qy'⟩ <;>
  rcases cz with ⟨cz, pz⟩ | ⟨cz, pz, qz⟩ | ⟨cz, pz, qz, qz'⟩ <;>
  first
  | omega
  | (rw [cx, cy, cz] at hr
     rcases hr with ⟨hr, _⟩ | ⟨hr, _⟩ <;>
     rcases ha with ⟨ha, _⟩ | ⟨ha, _⟩ <;>
     rcases hb with ⟨hb, _⟩ | ⟨hb, _⟩ <;> omega)))

set_option maxHeartbeats 1000000 in
theorem pt_odd_mid (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 1) (ha : 8*m < z) (hb : z ≤ 20*m) :
    rainbowInd (col m) x (z - x) z = parIn 0 (z-8*m-1) (z-1) x + parIn 1 0 (8*m) x := by
  pt_tac m, z, x, parIn_spec 0 (z-8*m-1) (z-1) x, parIn_spec 1 0 (8*m) x

set_option maxHeartbeats 1000000 in
theorem pt_low (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1) (hb : z ≤ 8*m) :
    rainbowInd (col m) x (z - x) z = 0 := by
  pt_tac m, z, x, parIn_spec 0 0 0 x, parIn_spec 0 0 0 x

set_option maxHeartbeats 1000000 in
theorem pt_odd_high (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 1) (ha : 20*m < z) :
    rainbowInd (col m) x (z - x) z = parIn 0 (z-20*m-1) (z-8*m-1) x + parIn 1 (8*m) (20*m) x := by
  pt_tac m, z, x, parIn_spec 0 (z-20*m-1) (z-8*m-1) x, parIn_spec 1 (8*m) (20*m) x

set_option maxHeartbeats 1000000 in
theorem pt_even_a (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 0) (ha : 8*m < z) (hb : z ≤ 16*m) :
    rainbowInd (col m) x (z - x) z = parIn 1 (8*m) z x + parIn 1 0 (z-8*m-1) x := by
  pt_tac m, z, x, parIn_spec 1 (8*m) z x, parIn_spec 1 0 (z-8*m-1) x

set_option maxHeartbeats 1000000 in
theorem pt_even_b (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 0) (ha : 16*m < z) (hb : z ≤ 20*m) :
    rainbowInd (col m) x (z - x) z = parIn 1 (z-8*m-1) z x + parIn 1 0 (8*m) x := by
  pt_tac m, z, x, parIn_spec 1 (z-8*m-1) z x, parIn_spec 1 0 (8*m) x

set_option maxHeartbeats 1000000 in
theorem pt_even_c (m z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 0) (ha : 20*m < z) (hb : z ≤ 22*m) :
    rainbowInd (col m) x (z - x) z = parIn 1 (z-8*m-1) (20*m) x + parIn 1 (z-20*m-1) (8*m) x := by
  pt_tac m, z, x, parIn_spec 1 (z-8*m-1) (20*m) x, parIn_spec 1 (z-20*m-1) (8*m) x

/-- closed form of r(z) for the witness colouring -/
def rzc (m z : Nat) : Nat :=
  if z ≤ 8*m then 0
  else if z % 2 = 1 then (if z ≤ 20*m then 8*m else 12*m)
  else if z ≤ 16*m then z - 8*m
  else if z ≤ 20*m then 8*m
  else 28*m - z

theorem rz_two (m z a1 a2 a3 b1 b2 b3 : Nat) (ha : a1 ≤ 1) (hb : b1 ≤ 1)
    (h : ∀ x, 1 ≤ x → x ≤ z - 1 →
      rainbowInd (col m) x (z - x) z = parIn a1 a2 a3 x + parIn b1 b2 b3 x) :
    rz (col m) z = ((min (z-1) a3 + a1)/2 - (a2 + a1)/2) + ((min (z-1) b3 + b1)/2 - (b2 + b1)/2) := by
  unfold rz
  rw [sumTo_congr (z-1) h, sumTo_add, sum_parIn a1 a2 a3 ha, sum_parIn b1 b2 b3 hb]

theorem sumTo_zero : ∀ n, sumTo (fun _ => 0) n = 0 := by
  intro n; induction n with
  | zero => rfl
  | succ n ih => simp only [sumTo]; omega

theorem rz_col (m z : Nat) (hz : z ≤ 22*m) : rz (col m) z = rzc m z := by
  unfold rzc
  by_cases c1 : z ≤ 8*m
  · simp only [c1, ↓reduceIte]
    unfold rz
    rw [sumTo_congr (g := fun _ => 0) (z-1) (fun x h1 h2 => pt_low m z x h1 h2 c1)]
    exact sumTo_zero _
  · simp only [c1, ↓reduceIte]
    by_cases c2 : z % 2 = 1
    · simp only [c2, ↓reduceIte]
      by_cases c3 : z ≤ 20*m
      · simp only [c3, ↓reduceIte]
        rw [rz_two m z _ _ _ _ _ _ (by omega) (by omega)
          (fun x h1 h2 => pt_odd_mid m z x h1 h2 c2 (by omega) c3)]
        omega
      · simp only [c3, ↓reduceIte]
        rw [rz_two m z _ _ _ _ _ _ (by omega) (by omega)
          (fun x h1 h2 => pt_odd_high m z x h1 h2 c2 (by omega))]
        omega
    · simp only [c2, ↓reduceIte]
      by_cases c4 : z ≤ 16*m
      · simp only [c4, ↓reduceIte]
        rw [rz_two m z _ _ _ _ _ _ (by omega) (by omega)
          (fun x h1 h2 => pt_even_a m z x h1 h2 (by omega) (by omega) c4)]
        omega
      · simp only [c4, ↓reduceIte]
        by_cases c5 : z ≤ 20*m
        · simp only [c5, ↓reduceIte]
          rw [rz_two m z _ _ _ _ _ _ (by omega) (by omega)
            (fun x h1 h2 => pt_even_b m z x h1 h2 (by omega) (by omega) c5)]
          omega
        · simp only [c5, ↓reduceIte]
          rw [rz_two m z _ _ _ _ _ _ (by omega) (by omega)
            (fun x h1 h2 => pt_even_c m z x h1 h2 (by omega) (by omega) hz)]
          omega

/-! outer sum -/
theorem sumTo_pairs (g : Nat → Nat) : ∀ K, sumTo g (2*K) = sumTo (fun k => g (2*k-1) + g (2*k)) K := by
  intro K
  induction K with
  | zero => rfl
  | succ K ih =>
    have e2 : 2*(K+1) = (2*K+1)+1 := by omega
    have e1 : 2*(K+1)-1 = 2*K+1 := by omega
    show sumTo g (2*(K+1)) = sumTo (fun k => g (2*k-1) + g (2*k)) K + (g (2*(K+1)-1) + g (2*(K+1)))
    rw [e1, e2]
    show sumTo g (2*K) + g (2*K+1) + g (2*K+1+1) = _
    rw [ih]; omega

theorem sumTo_split (f : Nat → Nat) (a : Nat) : ∀ d, sumTo f (a+d) = sumTo f a + sumTo (fun j => f (a+j)) d := by
  intro d
  induction d with
  | zero => rfl
  | succ d ih =>
    have e : a + (d+1) = (a+d)+1 := by omega
    rw [e]; simp only [sumTo]; rw [ih, e]; omega

theorem sumTo_const (c : Nat) : ∀ n, sumTo (fun _ => c) n = n*c := by
  intro n
  induction n with
  | zero => simp [sumTo]
  | succ n ih => simp only [sumTo]; rw [ih]; grind

theorem sumTo_lin (A : Nat) : ∀ n, sumTo (fun j => A + 2*j) n = n*A + n*(n+1) := by
  intro n
  induction n with
  | zero => simp [sumTo]
  | succ n ih => simp only [sumTo]; rw [ih]; grind

theorem sumTo_linsub (A : Nat) : ∀ n, 2*n ≤ A → sumTo (fun j => A - 2*j) n + n*(n+1) = n*A := by
  intro n
  induction n with
  | zero => intro _; simp [sumTo]
  | succ n ih =>
    intro h
    have ih' := ih (by omega)
    simp only [sumTo]
    obtain ⟨d, hd⟩ : ∃ d, A - 2*(n+1) = d ∧ A = 2*(n+1) + d := ⟨A - 2*(n+1), rfl, by omega⟩
    rw [hd.1]
    have hA := hd.2
    grind

/-- pair sums r(2k-1) + r(2k) for the witness -/
theorem pair_a (m k : Nat) (h : k ≤ 4*m) : rzc m (2*k-1) + rzc m (2*k) = 0 := by
  unfold rzc; repeat' split
  all_goals omega
theorem pair_b (m j : Nat) (h1 : 1 ≤ j) (h : j ≤ 4*m) :
    rzc m (2*(4*m+j)-1) + rzc m (2*(4*m+j)) = 8*m + 2*j := by
  unfold rzc; repeat' split
  all_goals omega
theorem pair_c (m j : Nat) (h1 : 1 ≤ j) (h : j ≤ 2*m) :
    rzc m (2*(4*m+4*m+j)-1) + rzc m (2*(4*m+4*m+j)) = 16*m := by
  unfold rzc; repeat' split
  all_goals omega
theorem pair_d (m j : Nat) (h1 : 1 ≤ j) (h : j ≤ m) :
    rzc m (2*(4*m+4*m+2*m+j)-1) + rzc m (2*(4*m+4*m+2*m+j)) = 20*m - 2*j := by
  unfold rzc; repeat' split
  all_goals omega

theorem witness_count (m : Nat) : rainbowCount (col m) (22*m) = 99*(m*m) + 3*m := by
  unfold rainbowCount
  have e : 22*m = 2*(4*m+4*m+2*m+m) := by omega
  rw [e, sumTo_pairs, sumTo_split, sumTo_split, sumTo_split]
  have s1 : sumTo (fun k => rz (col m) (2*k-1) + rz (col m) (2*k)) (4*m) = 0 := by
    rw [sumTo_congr (g := fun _ => 0) (4*m) (fun k h1 h2 => by
        rw [rz_col m _ (by omega), rz_col m _ (by omega)]; exact pair_a m k h2)]
    exact sumTo_zero _
  have s2 : sumTo (fun j => rz (col m) (2*(4*m+j)-1) + rz (col m) (2*(4*m+j))) (4*m)
      = (4*m)*(8*m) + (4*m)*(4*m+1) := by
    rw [sumTo_congr (g := fun j => 8*m + 2*j) (4*m) (fun j h1 h2 => by
        rw [rz_col m _ (by omega), rz_col m _ (by omega)]; exact pair_b m j h1 h2)]
    exact sumTo_lin _ _
  have s3 : sumTo (fun j => rz (col m) (2*(4*m+4*m+j)-1) + rz (col m) (2*(4*m+4*m+j))) (2*m)
      = (2*m)*(16*m) := by
    rw [sumTo_congr (g := fun _ => 16*m) (2*m) (fun j h1 h2 => by
        rw [rz_col m _ (by omega), rz_col m _ (by omega)]; exact pair_c m j h1 h2)]
    exact sumTo_const _ _
  have s4 : sumTo (fun j => rz (col m) (2*(4*m+4*m+2*m+j)-1) + rz (col m) (2*(4*m+4*m+2*m+j))) m
      + m*(m+1) = m*(20*m) := by
    rw [sumTo_congr (g := fun j => 20*m - 2*j) m (fun j h1 h2 => by
        rw [rz_col m _ (by omega), rz_col m _ (by omega)]; exact pair_d m j h1 h2)]
    exact sumTo_linsub _ _ (by omega)
  rw [s1, s2, s3]
  grind


/-! ## Normalisation: the source's equations (1), (2), (3) -/

/-- Source eq. (2): `|S^(z)| = z - 1`; eq. (1): `|S| = binom(n,2)`. Twice the number of ordered
Schur triples in `[n]` is `n (n-1)`. -/
theorem schur_total : ∀ n, 2 * sumTo (fun z => z - 1) n = n * (n - 1) := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [sumTo]
    cases n with
    | zero => rfl
    | succ k =>
      have e : k + 1 + 1 - 1 = k + 1 := by omega
      have e' : k + 1 - 1 = k := by omega
      rw [e] at *
      rw [e'] at ih
      grind

theorem rainbowInd_le_one (c : Nat → Nat) (x y z : Nat) : rainbowInd c x y z ≤ 1 := by
  unfold rainbowInd; split <;> omega

theorem sumTo_le {f g : Nat → Nat} (h : ∀ k, f k ≤ g k) : ∀ n, sumTo f n ≤ sumTo g n := by
  intro n
  induction n with
  | zero => exact Nat.le_refl _
  | succ n ih => simp only [sumTo]; have := h (n+1); omega

/-- Source eq. (3): `r(z) ≤ |S^(z)| = z - 1`. -/
theorem rz_le (c : Nat → Nat) (z : Nat) : rz c z ≤ z - 1 := by
  unfold rz
  have h := sumTo_le (f := fun x => rainbowInd c x (z - x) z) (g := fun _ => 1)
    (fun k => rainbowInd_le_one c k (z - k) z) (z - 1)
  rw [sumTo_const] at h; omega

/-- The rainbow count never exceeds the number of Schur triples: the fraction is at most 1. -/
theorem rainbowCount_le (c : Nat → Nat) (n : Nat) : 2 * rainbowCount c n ≤ n * (n - 1) := by
  rw [← schur_total n]
  have := sumTo_le (rz_le c) n
  unfold rainbowCount; omega

/-- Only the colours of `1, ..., n` matter: the count is a function of a colouring of `[n]`. -/
theorem rainbowCount_congr (c c' : Nat → Nat) (n : Nat) (h : ∀ k, 1 ≤ k → k ≤ n → c k = c' k) :
    rainbowCount c n = rainbowCount c' n := by
  unfold rainbowCount
  apply sumTo_congr
  intro z hz1 hz2
  unfold rz
  apply sumTo_congr
  intro x hx1 hx2
  unfold rainbowInd
  rw [h x hx1 (by omega), h (z - x) (by omega) (by omega), h z hz1 hz2]

/-- Monotonicity in `n`: a colouring of `[n+d]` restricted to `[n]` keeps its rainbow triples. -/
theorem rainbowCount_mono (c : Nat → Nat) (n d : Nat) : rainbowCount c n ≤ rainbowCount c (n + d) := by
  unfold rainbowCount; rw [sumTo_split]; omega

/-! ## Colourings with three colours, and the conjecture -/

/-- Number of rainbow ordered Schur triples of a 3-colouring. `Fin 3` values are compared through
`Fin.val`, which is injective (`rainbowInd_fin`). -/
def rainbow3 (c : Nat → Fin 3) (n : Nat) : Nat := rainbowCount (fun k => (c k).val) n

theorem rainbowInd_fin (c : Nat → Fin 3) (x y z : Nat) :
    rainbowInd (fun k => (c k).val) x y z = if c x ≠ c y ∧ c x ≠ c z ∧ c y ≠ c z then 1 else 0 := by
  unfold rainbowInd
  simp only [ne_eq, Fin.val_inj]

theorem col_lt (m k : Nat) : col m k < 3 := by
  have := col_spec m k; omega

/-- The witness as a `Fin 3`-valued colouring. -/
def colFin (m : Nat) : Nat → Fin 3 := fun k => ⟨col m k, col_lt m k⟩

theorem rainbow3_colFin (m n : Nat) : rainbow3 (colFin m) n = rainbowCount (col m) n := rfl

/-- **The source conjecture, tightness half** ("We conjecture the lower bound to be tight"):
the maximum fraction of rainbow Schur triples is asymptotically at most 2/5, i.e.
for every rational `ε = p/q > 0` there is `N` such that for all `n ≥ N` and all 3-colourings `c`,
`R_n(c) ≤ (2/5 + p/q) * binom(n,2)`.  Cross-multiplied by `10 q`:
`5 q * (2 R) ≤ (2 q + 5 p) * (n (n-1))`.  Rational `ε` loses nothing: every real `ε > 0` lies
above some `p/q > 0`, and the bound is monotone in `ε`. -/
def TightnessConjecture : Prop :=
  ∀ p q : Nat, 0 < p → 0 < q → ∃ N : Nat, ∀ n, N ≤ n → ∀ c : Nat → Fin 3,
    5 * q * (2 * rainbow3 c n) ≤ (2 * q + 5 * p) * (n * (n - 1))

/-- The weakest asymptotic reading (a statement about `liminf` only): for every `ε = p/q > 0`
the bound holds for infinitely many `n`. -/
def TightnessConjectureLiminf : Prop :=
  ∀ p q : Nat, 0 < p → 0 < q → ∀ N : Nat, ∃ n, N ≤ n ∧ ∀ c : Nat → Fin 3,
    5 * q * (2 * rainbow3 c n) ≤ (2 * q + 5 * p) * (n * (n - 1))

/-! ## The refutation -/

/-- For every `m ≥ 1` and `n = 22 m` the witness has strictly more than `(9/22) binom(n,2)`
rainbow Schur triples: `22 * 2R > 9 * n(n-1)`. -/
theorem family_above (m : Nat) (hm : 1 ≤ m) :
    9 * ((22*m) * (22*m - 1)) < 22 * (2 * rainbow3 (colFin m) (22*m)) := by
  rw [rainbow3_colFin, witness_count]
  obtain ⟨k, rfl⟩ : ∃ k, m = k + 1 := ⟨m - 1, by omega⟩
  have e : (22*(k+1)) * (22*(k+1) - 1) + 22*(k+1) = 484*((k+1)*(k+1)) := by grind
  omega

/-- For EVERY `n ≥ 3608` some 3-colouring of `[n]` has more than `(2/5 + 1/220) binom(n,2)`
rainbow Schur triples: `220 * 2R > 89 * n(n-1)`. -/
theorem everywhere_above (n : Nat) (hn : 3608 ≤ n) :
    ∃ c : Nat → Fin 3, 89 * (n * (n - 1)) < 220 * (2 * rainbow3 c n) := by
  refine ⟨colFin (n / 22), ?_⟩
  rw [rainbow3_colFin]
  have hm : 164 ≤ n / 22 := by omega
  have hsplit : n = 22 * (n/22) + n % 22 := by omega
  have hr : n % 22 < 22 := Nat.mod_lt _ (by decide)
  generalize n / 22 = m at *
  generalize n % 22 = r at *
  have hmono := rainbowCount_mono (col m) (22*m) r
  rw [witness_count] at hmono
  rw [← hsplit] at hmono
  have h1 : n * (n - 1) ≤ (22*m + 21) * (22*m + 20) := Nat.mul_le_mul (by omega) (by omega)
  have h2 : (22*m + 21) * (22*m + 20) = 484*(m*m) + 902*m + 420 := by grind
  have h3 : 164 * m ≤ m * m := Nat.mul_le_mul_right m hm
  omega

/-- **Headline.** The tightness conjecture of the source is false. -/
theorem not_tightnessConjecture : ¬ TightnessConjecture := by
  intro h
  obtain ⟨N, hN⟩ := h 1 110 (by decide) (by decide)
  have h1 := hN (22*(N+1)) (by omega) (colFin (N+1))
  have h2 := family_above (N+1) (by omega)
  omega

/-- Even the weakest (liminf) reading is false. -/
theorem not_tightnessConjectureLiminf : ¬ TightnessConjectureLiminf := by
  intro h
  obtain ⟨n, hn, hc⟩ := h 1 220 (by decide) (by decide) 3608
  obtain ⟨c, hc'⟩ := everywhere_above n hn
  have := hc c
  omega

/-! ## Kernel cross-checks of the definitions against the recorded enumeration -/

/-- A differently shaped definition: filter all pairs `(x,y)` of `[n]²`. -/
def bruteCount (c : Nat → Nat) (n : Nat) : Nat :=
  ((List.range (n+1)).flatMap fun x => (List.range (n+1)).filter fun y =>
    decide (1 ≤ x) && decide (1 ≤ y) && decide (x + y ≤ n) &&
    decide (c x ≠ c y) && decide (c x ≠ c (x+y)) && decide (c y ≠ c (x+y))).length

set_option maxRecDepth 100000 in
theorem check_m1 : rainbowCount (col 1) 22 = 102 ∧ bruteCount (col 1) 22 = 102 ∧ 22 * 21 / 2 = 231 := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem check_m2 : rainbowCount (col 2) 44 = 402 ∧ bruteCount (col 2) 44 = 402 := by
  decide +kernel

/-- The source's own colouring `c0` (odd `i ≤ 2n/5`, odd `i > 2n/5`, even), at `n = 22`: fewer
rainbow triples than the witness, as a sanity check that the definitions separate the two. -/
def c0 (n k : Nat) : Nat := if k % 2 = 0 then 2 else if 5 * k ≤ 2 * n then 0 else 1

set_option maxRecDepth 100000 in
theorem check_c0 : rainbowCount (c0 22) 22 = 100 ∧ bruteCount (c0 22) 22 = 100 := by
  decide +kernel


/-! ## The same count indexed by the summands `(x, y)`, and as the length of a duplicate-free list

`rainbowCount` sums the source's `r(z)` over the largest element `z`.  Below: (i) the same number
summed over the summands `(x, y)` (the form `R_n(c)` used by Hegde, Kumar and Pratibha), for every
colouring and every `n`; (ii) the same number as the length of the rainbow sublist of an explicit
duplicate-free list `schurPairs n` whose members are exactly the pairs `1 ≤ x`, `1 ≤ y`,
`x + y ≤ n`; (iii) that list has `binom(n,2)` elements. -/

/-- Summation over the largest element equals summation over the summands, for any weight `f`. -/
theorem sum_swap (f : Nat → Nat → Nat → Nat) : ∀ n,
    sumTo (fun z => sumTo (fun x => f x (z - x) z) (z - 1)) n
      = sumTo (fun x => sumTo (fun y => f x y (x + y)) (n - x)) n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    show sumTo (fun z => sumTo (fun x => f x (z - x) z) (z - 1)) n
        + sumTo (fun x => f x (n + 1 - x) (n + 1)) (n + 1 - 1) =
      sumTo (fun x => sumTo (fun y => f x y (x + y)) (n + 1 - x)) n
        + sumTo (fun y => f (n+1) y (n + 1 + y)) (n + 1 - (n + 1))
    have e0 : n + 1 - (n + 1) = 0 := by omega
    have e3 : n + 1 - 1 = n := by omega
    rw [e0, e3]
    show _ = _ + 0
    have hx : ∀ x, 1 ≤ x → x ≤ n →
        sumTo (fun y => f x y (x + y)) (n + 1 - x)
          = sumTo (fun y => f x y (x + y)) (n - x) + f x (n + 1 - x) (n + 1) := by
      intro x h1 h2
      have e1 : n + 1 - x = (n - x) + 1 := by omega
      have e2 : x + ((n - x) + 1) = n + 1 := by omega
      rw [e1]
      show sumTo (fun y => f x y (x + y)) (n - x) + f x (n - x + 1) (x + (n - x + 1)) = _
      rw [e2]
    rw [sumTo_congr n hx, sumTo_add, ih]; omega

/-- Count indexed by the summands: `#{(x,y) : 1 ≤ x, 1 ≤ y, x + y ≤ n, (x,y,x+y) rainbow}`. -/
def pairCount (c : Nat → Nat) (n : Nat) : Nat :=
  sumTo (fun x => sumTo (fun y => rainbowInd c x y (x + y)) (n - x)) n

theorem rainbowCount_eq_pairCount (c : Nat → Nat) (n : Nat) : rainbowCount c n = pairCount c n :=
  sum_swap (rainbowInd c) n

/-- A sum of indicators is the length of a filtered list. -/
theorem sumTo_ind_eq_length (p : Nat → Bool) : ∀ n,
    sumTo (fun k => if p k then 1 else 0) n = ((List.range' 1 n).filter p).length := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [sumTo]
    rw [ih, List.range'_concat, List.filter_append, List.length_append]
    have e : 1 + 1 * n = n + 1 := by omega
    rw [e]
    cases h : p (n+1) <;> simp [List.filter, h]

/-- All ordered pairs `(x, y)` with `1 ≤ x`, `1 ≤ y`, `x + y ≤ n`: the Schur triples `(x, y, x+y)` of `[n]`. -/
def schurPairs (n : Nat) : List (Nat × Nat) :=
  (List.range' 1 n).flatMap fun x => (List.range' 1 (n - x)).map fun y => (x, y)

theorem mem_schurPairs (n x y : Nat) : (x, y) ∈ schurPairs n ↔ 1 ≤ x ∧ 1 ≤ y ∧ x + y ≤ n := by
  unfold schurPairs
  simp only [List.mem_flatMap, List.mem_map, List.mem_range'_1, Prod.mk.injEq]
  constructor
  · rintro ⟨a, ha, b, hb, rfl, rfl⟩; omega
  · intro h; exact ⟨x, by omega, y, by omega, rfl, rfl⟩

theorem nodup_range1 (k : Nat) : (List.range' 1 k).Nodup := List.nodup_range' (step := 1)

theorem nodup_flatMap_range {β : Type} (F : Nat → List β) (h1 : ∀ x, (F x).Nodup)
    (h2 : ∀ x x' b, b ∈ F x → b ∈ F x' → x = x') : ∀ k, ((List.range' 1 k).flatMap F).Nodup := by
  intro k
  induction k with
  | zero => exact List.Pairwise.nil
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, e]
    unfold List.Nodup
    rw [List.pairwise_append]
    refine ⟨ih, ?_, ?_⟩
    · have e2 : [k+1].flatMap F = F (k+1) := by simp
      rw [e2]; exact h1 (k+1)
    · intro a ha b hb hab
      rw [List.mem_flatMap] at ha hb
      obtain ⟨x, hx, hax⟩ := ha
      obtain ⟨x', hx', hbx'⟩ := hb
      rw [List.mem_range'_1] at hx
      have hx'' : x' = k + 1 := by simpa using hx'
      subst hab
      have := h2 x x' a hax hbx'
      omega

theorem nodup_schurPairs (n : Nat) : (schurPairs n).Nodup := by
  unfold schurPairs
  apply nodup_flatMap_range
  · intro x
    unfold List.Nodup
    rw [List.pairwise_map]
    have := nodup_range1 (n - x)
    unfold List.Nodup at this
    exact this.imp (fun h h' => h (by simpa using h'))
  · intro x x' b hb hb'
    rw [List.mem_map] at hb hb'
    obtain ⟨y, _, rfl⟩ := hb
    obtain ⟨y', _, h⟩ := hb'
    have := congrArg Prod.fst h
    simpa using this.symm

/-- Boolean rainbow test on a pair `(x, y)`, third element `x + y`. -/
def isRainbowPair (c : Nat → Nat) (p : Nat × Nat) : Bool :=
  decide (c p.1 ≠ c p.2 ∧ c p.1 ≠ c (p.1 + p.2) ∧ c p.2 ≠ c (p.1 + p.2))

theorem length_filter_flatMap_range {β : Type} (F : Nat → List β) (p : β → Bool) : ∀ k,
    (((List.range' 1 k).flatMap F).filter p).length = sumTo (fun x => ((F x).filter p).length) k := by
  intro k
  induction k with
  | zero => rfl
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, List.filter_append, List.length_append, ih, e]
    simp [sumTo]

theorem pairCount_eq_length (c : Nat → Nat) (n : Nat) :
    pairCount c n = ((schurPairs n).filter (isRainbowPair c)).length := by
  unfold schurPairs pairCount
  rw [length_filter_flatMap_range]
  apply sumTo_congr
  intro x _ _
  rw [List.filter_map, List.length_map]
  rw [← sumTo_ind_eq_length]
  apply sumTo_congr
  intro y _ _
  unfold rainbowInd isRainbowPair
  simp

/-- **The count is a cardinality**: `rainbowCount c n` is the number of rainbow members of the
duplicate-free list of all Schur pairs of `[n]`. -/
theorem rainbowCount_eq_length (c : Nat → Nat) (n : Nat) :
    rainbowCount c n = ((schurPairs n).filter (isRainbowPair c)).length := by
  rw [rainbowCount_eq_pairCount, pairCount_eq_length]

theorem length_flatMap_range {β : Type} (F : Nat → List β) : ∀ k,
    ((List.range' 1 k).flatMap F).length = sumTo (fun x => (F x).length) k := by
  intro k
  induction k with
  | zero => rfl
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, List.length_append, ih, e]
    simp [sumTo]

/-- The source's eq. (1) for the list: there are exactly `binom(n,2)` Schur pairs. -/
theorem schurPairs_length (n : Nat) : 2 * (schurPairs n).length = n * (n - 1) := by
  unfold schurPairs
  rw [length_flatMap_range]
  have h2 : ∀ x, 1 ≤ x → x ≤ n →
      ((List.range' 1 (n - x)).map fun y => (x, y)).length = sumTo (fun _ => 1) (n - x) := by
    intro x _ _
    rw [List.length_map, List.length_range', sumTo_const, Nat.mul_one]
  rw [sumTo_congr n h2]
  have h3 : sumTo (fun z => sumTo (fun _ => 1) (z - 1)) n
      = sumTo (fun x => sumTo (fun _ => 1) (n - x)) n := sum_swap (fun _ _ _ => 1) n
  rw [← h3]
  have h4 : ∀ z, 1 ≤ z → z ≤ n → sumTo (fun _ => 1) (z - 1) = z - 1 := by
    intro z _ _
    rw [sumTo_const, Nat.mul_one]
  rw [sumTo_congr n h4]
  exact schur_total n

#print axioms witness_count
#print axioms family_above
#print axioms everywhere_above
#print axioms not_tightnessConjecture
#print axioms not_tightnessConjectureLiminf
#print axioms schur_total
#print axioms rainbowCount_le
#print axioms rainbowCount_congr
#print axioms rainbowInd_fin
#print axioms check_m1
#print axioms check_m2
#print axioms check_c0
#print axioms sum_swap
#print axioms rainbowCount_eq_pairCount
#print axioms mem_schurPairs
#print axioms nodup_schurPairs
#print axioms rainbowCount_eq_length
#print axioms schurPairs_length
