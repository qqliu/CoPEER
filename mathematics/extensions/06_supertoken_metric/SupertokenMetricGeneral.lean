/-!
# Kernel certificate (PRIMARY): Conjecture 4.2 on the metric dimension of supertoken graphs is
# false; it fails at k = 2 for every n >= 8 (2026-09-19)

NEW dated artifact, outside the frozen 285-record release. Core Lean only: no Mathlib, no `sorry`,
no `native_decide`.

Source (journal page read 2026-09-19, quotes in BINDING.md): E. T. Baskoro, C. Dalfo, M. A. Fiol and
R. Simanjuntak, *On some metric properties of supertoken graphs*, Utilitas Mathematica 123 (2025)
19-33, DOI 10.61091/um123-02. Section 3: a vertex of the k-supertoken graph F_k(G) is a
nonnegative n-vector u = (u_1, ..., u_n) with sum k (k indistinguishable tokens on the n vertices
of G, repetitions allowed); u and v are adjacent if one token of u is moved along an edge of G to
another vertex, giving v. Section 1: C is a resolving set if every vertex u is uniquely determined
by the vector of graph distances (dist(u, z_1), ..., dist(u, z_c)); dim is the minimum cardinality
of a resolving set. Conjecture 4.2 (verbatim, with its misprint "metric distance"): "The metric
distance of the supertoken graph F_k(K_n) is dim(F_k(K_n)) = n - 1."

The first part of this file (definitions, walks, `comps`, `l1`, `halfL1`) is textually identical to
the same part of `SupertokenMetric.lean`, the independent finite route to the (8, 2) refutation.

Certified here, over the definitions and NOT assuming the source's distance formula:
* `dist_formula`, `dist_iff`   for ALL n and k: the shortest-path distance of the token-move graph
                         F_k(K_n) exists and equals (1/2) sum_i |x_i - y_i| (the source's
                         Proposition 3.1(i)); walks are defined inductively, existence and minimality
                         are proved by induction, nothing is evaluated;
* `dist_symm`, `adj_vertex`  for all n, k: the distance is symmetric; a token move from a vertex
                         lands on a vertex;
* `landmarks_resolving`, `resolving_set_of_size_six`  e1+e2, e1+e3, e1+e4, e5+e6, e5+e7, e5+e8 form
                         a resolving set of F_2(K_8) with 6 elements;
* `conjecture_4_2_fails_at_8_2`  `¬ IsMetricDim 8 2 (8 - 1)`;
* `conjecture_4_2_false` the universal statement over all integers n >= 1, k >= 1 is false;
* `family_resolving`, `conjecture_4_2_fails_k2`  for EVERY n >= 8: the six landmarks padded with
                         zeros together with 2e_9, ..., 2e_n resolve F_2(K_n), so
                         `¬ IsMetricDim n 2 (n - 1)`;
* `conjecture_4_2_not_eventually_true_k2`  no threshold n0 makes dim F_2(K_n) = n - 1 for all n >= n0.
The only kernel-evaluated facts are `landmarks_shape`, `landmarks_ok` and `prefix_separate` (the six
landmarks separate all 8-vectors of equal sum s <= 2: 1 + 8 + 36 vectors).
NOT certified: the exact value of any dimension (see the bonus file for n = 8), any k other than 2
beyond the general distance formula, or that the conjecture was open.
-/
set_option maxRecDepth 100000

namespace SupertokenMetric

/-! ## The graph F_k(K_n), its walks, its distance, resolving sets, metric dimension -/

/-- A vertex of F_k(K_n): a vector of n nonnegative integers with coordinate sum k. -/
def IsVertex (n k : Nat) (x : List Nat) : Prop := x.length = n ∧ x.sum = k

/-- Move one token from coordinate i to coordinate j. -/
def move (u : List Nat) (i j : Nat) : List Nat :=
  (u.set i (u.getD i 0 - 1)).set j (u.getD j 0 + 1)

/-- Adjacency: v is obtained from u by moving one token from a coordinate i that holds a token to
a different coordinate j (every two distinct coordinates are joined, the base graph being K_n). -/
def Adj (u v : List Nat) : Prop :=
  ∃ i j, i < u.length ∧ j < u.length ∧ i ≠ j ∧ 0 < u.getD i 0 ∧ v = move u i j

/-- `Walk n k x y m`: a walk with m edges from x to y all of whose vertices are vertices of
F_k(K_n). -/
inductive Walk (n k : Nat) : List Nat → List Nat → Nat → Prop
  | nil {x : List Nat} : IsVertex n k x → Walk n k x x 0
  | cons {x z y : List Nat} {m : Nat} :
      IsVertex n k x → Adj x z → Walk n k z y m → Walk n k x y (m + 1)

/-- d is the graph distance from x to y: some walk has d edges and no walk has fewer. -/
def IsDist (n k : Nat) (x y : List Nat) (d : Nat) : Prop :=
  Walk n k x y d ∧ ∀ m, Walk n k x y m → d ≤ m

/-- R is a resolving set: its members are vertices, and any two distinct vertices have different
graph distances to some member of R. -/
def Resolving (n k : Nat) (R : List (List Nat)) : Prop :=
  (∀ r, r ∈ R → IsVertex n k r) ∧
  ∀ x y, IsVertex n k x → IsVertex n k y → x ≠ y →
    ∃ r, r ∈ R ∧ ∃ dx dy, IsDist n k x r dx ∧ IsDist n k y r dy ∧ dx ≠ dy

/-- d is the metric dimension: the minimum cardinality of a resolving set. -/
def IsMetricDim (n k d : Nat) : Prop :=
  (∃ R : List (List Nat), R.Nodup ∧ R.length = d ∧ Resolving n k R) ∧
  ∀ R : List (List Nat), R.Nodup → Resolving n k R → d ≤ R.length

/-! ## General lemmas: a potential that is 1-Lipschitz along edges and can always be decreased
is the graph distance -/

theorem walk_target {n k : Nat} {x y : List Nat} {m : Nat} (w : Walk n k x y m) :
    IsVertex n k y := by
  induction w with
  | nil h => exact h
  | cons _ _ _ ih => exact ih

theorem walk_lower {n k : Nat} (f : List Nat → List Nat → Nat)
    (hdiag : ∀ y, IsVertex n k y → f y y = 0)
    (hlip : ∀ u v t, IsVertex n k u → Adj u v → IsVertex n k t → f u t ≤ f v t + 1)
    {x y : List Nat} {m : Nat} (w : Walk n k x y m) : f x y ≤ m := by
  induction w with
  | nil h => simp [hdiag _ h]
  | cons hx hadj w' ih =>
    have := hlip _ _ _ hx hadj (walk_target w')
    omega

theorem walk_exists {n k : Nat} (f : List Nat → List Nat → Nat)
    (hzero : ∀ x y, IsVertex n k x → IsVertex n k y → f x y = 0 → x = y)
    (hdesc : ∀ x y, IsVertex n k x → IsVertex n k y → f x y ≠ 0 →
      ∃ z, Adj x z ∧ IsVertex n k z ∧ f z y + 1 = f x y) :
    ∀ (d : Nat) (x y : List Nat), IsVertex n k x → IsVertex n k y → f x y = d → Walk n k x y d
  | 0, x, y, hx, hy, h => by
    have := hzero x y hx hy h
    subst this
    exact Walk.nil hx
  | d + 1, x, y, hx, hy, h => by
    obtain ⟨z, hadj, hz, hzd⟩ := hdesc x y hx hy (by omega)
    exact Walk.cons hx hadj (walk_exists f hzero hdesc d z y hz hy (by omega))

theorem isDist_unique {n k : Nat} {x y : List Nat} {d e : Nat}
    (h1 : IsDist n k x y d) (h2 : IsDist n k x y e) : d = e := by
  have := h1.2 e h2.1
  have := h2.2 d h1.1
  omega

/-! ## Enumeration of the vertex set, general in n and k -/

/-- All vectors of length n with sum k. -/
def comps : Nat → Nat → List (List Nat)
  | 0, 0 => [[]]
  | 0, _ + 1 => []
  | n + 1, k => (List.range (k + 1)).flatMap fun a => (comps n (k - a)).map (a :: ·)

theorem mem_comps : ∀ (n k : Nat) (x : List Nat), x ∈ comps n k ↔ IsVertex n k x
  | 0, 0, x => by
    cases x <;> simp [comps, IsVertex]
  | 0, k + 1, x => by
    cases x <;> simp [comps, IsVertex]
  | n + 1, k, x => by
    cases x with
    | nil => simp [comps, IsVertex]
    | cons a t =>
      simp only [comps, IsVertex, List.mem_flatMap, List.mem_range, List.mem_map,
        List.length_cons, List.sum_cons]
      constructor
      · rintro ⟨b, hb, s, hs, heq⟩
        have h1 := (mem_comps n (k - b) s).1 hs
        injection heq with e1 e2
        subst e1; subst e2
        unfold IsVertex at h1
        omega
      · rintro ⟨hl, hs⟩
        exact ⟨a, by omega, t, (mem_comps n (k - a) t).2 ⟨by omega, by omega⟩, rfl⟩

/-! ## The half-L1 potential of the source's Proposition 3.1(i) -/

/-- sum_i |x_i - y_i| -/
def l1 : List Nat → List Nat → Nat
  | a :: x, b :: y => ((a - b) + (b - a)) + l1 x y
  | _, _ => 0

/-- (1/2) sum_i |x_i - y_i| -/
def halfL1 (x y : List Nat) : Nat := l1 x y / 2


/-! ## Proposition 3.1(i) of the source for ALL n and k -/

/-- The excess sum_i max(x_i - y_i, 0). -/
def exc : List Nat → List Nat → Nat
  | a :: x, b :: y => (a - b) + exc x y
  | _, _ => 0

theorem l1_eq_exc : ∀ x y : List Nat, l1 x y = exc x y + exc y x
  | [], [] => rfl
  | [], _ :: _ => rfl
  | _ :: _, [] => rfl
  | a :: x, b :: y => by
    have ih := l1_eq_exc x y
    simp only [l1, exc, ih]
    omega

theorem exc_sum : ∀ x y : List Nat, x.length = y.length → exc x y + y.sum = exc y x + x.sum
  | [], [], _ => rfl
  | [], _ :: _, h => by simp at h
  | _ :: _, [], h => by simp at h
  | a :: x, b :: y, h => by
    have ih := exc_sum x y (by simpa using h)
    simp only [exc, List.sum_cons]
    omega

theorem exc_self : ∀ x : List Nat, exc x x = 0
  | [] => rfl
  | a :: x => by simp [exc, exc_self x]

theorem eq_of_exc_zero : ∀ x y : List Nat, x.length = y.length → exc x y = 0 → exc y x = 0 → x = y
  | [], [], _, _, _ => rfl
  | [], _ :: _, h, _, _ => by simp at h
  | _ :: _, [], h, _, _ => by simp at h
  | a :: x, b :: y, h, h1, h2 => by
    simp only [exc] at h1 h2
    have ih := eq_of_exc_zero x y (by simpa using h) (by omega) (by omega)
    have : a = b := by omega
    rw [this, ih]

theorem getD_set_ne : ∀ (u : List Nat) (i j a : Nat), i ≠ j → (u.set i a).getD j 0 = u.getD j 0
  | [], _, _, _, _ => by simp
  | c :: u, 0, 0, a, h => absurd rfl h
  | c :: u, 0, j + 1, a, _ => by simp
  | c :: u, i + 1, 0, a, _ => by simp
  | c :: u, i + 1, j + 1, a, h => by
    have ih := getD_set_ne u i j a (by omega)
    simpa using ih

theorem sum_set : ∀ (u : List Nat) (i a : Nat), i < u.length →
    (u.set i a).sum + u.getD i 0 = u.sum + a
  | [], _, _, h => by simp at h
  | c :: u, 0, a, _ => by simp; omega
  | c :: u, i + 1, a, h => by
    have ih := sum_set u i a (by simpa using h)
    simp only [List.set_cons_succ, List.sum_cons, List.getD_cons_succ]
    omega

theorem exc_set_le : ∀ (u t : List Nat) (i a : Nat),
    exc u t ≤ exc (u.set i a) t + (u.getD i 0 - a)
  | [], _, _, _ => by simp [exc]
  | _ :: _, [], _, _ => by simp [exc]
  | c :: u, b :: t, 0, a => by
    simp only [List.set_cons_zero, exc, List.getD_cons_zero]
    omega
  | c :: u, b :: t, i + 1, a => by
    have ih := exc_set_le u t i a
    simp only [List.set_cons_succ, exc, List.getD_cons_succ]
    omega

theorem exc_pos : ∀ x y : List Nat, exc x y ≠ 0 →
    ∃ i, i < x.length ∧ i < y.length ∧ y.getD i 0 < x.getD i 0
  | [], _, h => by simp [exc] at h
  | _ :: _, [], h => by simp [exc] at h
  | a :: x, b :: y, h => by
    by_cases hab : b < a
    · exact ⟨0, by simp, by simp, by simpa using hab⟩
    · have h' : exc x y ≠ 0 := by
        simp only [exc] at h
        omega
      obtain ⟨i, h1, h2, h3⟩ := exc_pos x y h'
      exact ⟨i + 1, by simpa using h1, by simpa using h2, by simpa using h3⟩

theorem exc_set_dec : ∀ (x y : List Nat) (i : Nat), i < x.length → i < y.length →
    y.getD i 0 < x.getD i 0 → exc (x.set i (x.getD i 0 - 1)) y + 1 = exc x y
  | [], _, _, h, _, _ => by simp at h
  | _ :: _, [], _, _, h, _ => by simp at h
  | a :: x, b :: y, 0, _, _, h => by
    simp only [List.getD_cons_zero] at h
    simp only [List.set_cons_zero, exc, List.getD_cons_zero]
    omega
  | a :: x, b :: y, i + 1, h1, h2, h => by
    simp only [List.getD_cons_succ] at h
    have ih := exc_set_dec x y i (by simpa using h1) (by simpa using h2) h
    simp only [List.set_cons_succ, exc, List.getD_cons_succ]
    omega

theorem exc_set_inc : ∀ (x y : List Nat) (j : Nat), x.getD j 0 < y.getD j 0 →
    exc (x.set j (x.getD j 0 + 1)) y = exc x y
  | [], _, _, _ => by simp [exc]
  | _ :: _, [], _, _ => by simp [exc]
  | a :: x, b :: y, 0, h => by
    simp only [List.getD_cons_zero] at h
    simp only [List.set_cons_zero, exc, List.getD_cons_zero]
    omega
  | a :: x, b :: y, j + 1, h => by
    simp only [List.getD_cons_succ] at h
    have ih := exc_set_inc x y j h
    simp only [List.set_cons_succ, exc, List.getD_cons_succ, ih]

theorem halfL1_eq_exc {n k : Nat} {x y : List Nat} (hx : IsVertex n k x) (hy : IsVertex n k y) :
    halfL1 x y = exc x y ∧ exc y x = exc x y := by
  have h1 := l1_eq_exc x y
  have h2 := exc_sum x y (by rw [hx.1, hy.1])
  rw [hx.2, hy.2] at h2
  unfold halfL1
  omega

/-- Proposition 3.1(i) of the source, for all n and k: the shortest-path distance of the
token-move graph F_k(K_n) is (1/2) sum_i |x_i - y_i|. -/
theorem dist_formula (n k : Nat) {x y : List Nat} (hx : IsVertex n k x) (hy : IsVertex n k y) :
    IsDist n k x y (halfL1 x y) := by
  have hdiag : ∀ y, IsVertex n k y → exc y y = 0 := fun y _ => exc_self y
  have hlip : ∀ u v t, IsVertex n k u → Adj u v → IsVertex n k t → exc u t ≤ exc v t + 1 := by
    intro u v t _ hadj _
    obtain ⟨i, j, _, _, hij, hpos, rfl⟩ := hadj
    have s1 := exc_set_le u t i (u.getD i 0 - 1)
    have s2 := exc_set_le (u.set i (u.getD i 0 - 1)) t j (u.getD j 0 + 1)
    rw [getD_set_ne u i j _ hij] at s2
    unfold move
    omega
  have hzero : ∀ x y, IsVertex n k x → IsVertex n k y → exc x y = 0 → x = y := by
    intro x y hx hy h
    have := (halfL1_eq_exc hx hy).2
    exact eq_of_exc_zero x y (by rw [hx.1, hy.1]) h (by omega)
  have hdesc : ∀ x y, IsVertex n k x → IsVertex n k y → exc x y ≠ 0 →
      ∃ z, Adj x z ∧ IsVertex n k z ∧ exc z y + 1 = exc x y := by
    intro x y hx hy hne
    have hsymm := (halfL1_eq_exc hx hy).2
    obtain ⟨i, hi, _, hgt⟩ := exc_pos x y hne
    obtain ⟨j, _, hj, hlt⟩ := exc_pos y x (by omega)
    have hij : i ≠ j := by
      intro e
      subst e
      omega
    have hjx : (x.set i (x.getD i 0 - 1)).getD j 0 = x.getD j 0 := getD_set_ne x i j _ hij
    refine ⟨move x i j, ⟨i, j, hi, hj, hij, by omega, rfl⟩, ⟨?_, ?_⟩, ?_⟩
    · simp [move, hx.1]
    · have s1 := sum_set x i (x.getD i 0 - 1) hi
      have s2 := sum_set (x.set i (x.getD i 0 - 1)) j (x.getD j 0 + 1) (by simpa using hj)
      rw [hjx] at s2
      have := hx.2
      unfold move
      omega
    · have d1 := exc_set_dec x y i hi (by rw [hy.1, ← hx.1]; exact hi) hgt
      have d2 := exc_set_inc (x.set i (x.getD i 0 - 1)) y j (by rw [hjx]; exact hlt)
      rw [hjx] at d2
      unfold move
      omega
  have key : IsDist n k x y (exc x y) :=
    ⟨walk_exists exc hzero hdesc _ x y hx hy rfl, fun m w => walk_lower exc hdiag hlip w⟩
  rw [(halfL1_eq_exc hx hy).1]
  exact key


/-- e1+e2, e1+e3, e1+e4, e5+e6, e5+e7, e5+e8. -/
def landmarks : List (List Nat) :=
  [[1, 1, 0, 0, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0, 0, 0],
   [0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 1, 0, 0, 1]]

/-- For all n and k: d is the graph distance from x to y iff 2 d = sum_i |x_i - y_i|. -/
theorem dist_iff (n k : Nat) {x y : List Nat} (hx : IsVertex n k x) (hy : IsVertex n k y)
    (d : Nat) : IsDist n k x y d ↔ 2 * d = l1 x y := by
  have h1 := l1_eq_exc x y
  have h2 := halfL1_eq_exc hx hy
  constructor
  · intro h
    have := isDist_unique h (dist_formula n k hx hy)
    omega
  · intro h
    have hd : d = halfL1 x y := by omega
    rw [hd]
    exact dist_formula n k hx hy

/-- For all n and k the graph distance is symmetric, so "distance from u to the landmark" and
"distance from the landmark to u" are the same number. -/
theorem dist_symm (n k : Nat) {x y : List Nat} (hx : IsVertex n k x) (hy : IsVertex n k y)
    (d : Nat) : IsDist n k x y d ↔ IsDist n k y x d := by
  have h1 := l1_eq_exc x y
  have h2 := l1_eq_exc y x
  rw [dist_iff n k hx hy, dist_iff n k hy hx]
  constructor <;> intro h <;> omega

/-- For all n and k: a token move from a vertex of F_k(K_n) lands on a vertex of F_k(K_n). -/
theorem adj_vertex {n k : Nat} {u v : List Nat} (hu : IsVertex n k u) (h : Adj u v) :
    IsVertex n k v := by
  obtain ⟨i, j, hi, hj, hij, hpos, rfl⟩ := h
  have hjx := getD_set_ne u i j (u.getD i 0 - 1) hij
  refine ⟨by simp [move, hu.1], ?_⟩
  have s1 := sum_set u i (u.getD i 0 - 1) hi
  have s2 := sum_set (u.set i (u.getD i 0 - 1)) j (u.getD j 0 + 1) (by simpa using hj)
  rw [hjx] at s2
  have := hu.2
  unfold move
  omega

/-- For all n, k: a list of vertices whose excess signatures separate all pairs of distinct
vertices is a resolving set (the graph distance to r is exc r x, by `dist_formula`). -/
theorem resolving_of_separates {n k : Nat} (R : List (List Nat))
    (hR : ∀ r, r ∈ R → IsVertex n k r)
    (hsep : ∀ x y, IsVertex n k x → IsVertex n k y → x ≠ y → ∃ r, r ∈ R ∧ exc r x ≠ exc r y) :
    Resolving n k R := by
  refine ⟨hR, ?_⟩
  intro x y hx hy hne
  obtain ⟨r, hr, hd⟩ := hsep x y hx hy hne
  have hrv := hR r hr
  refine ⟨r, hr, halfL1 x r, halfL1 y r, dist_formula n k hx hrv, dist_formula n k hy hrv, ?_⟩
  have e1 := halfL1_eq_exc hx hrv
  have e2 := halfL1_eq_exc hy hrv
  omega

/-! ### Removing repetitions from a resolving list -/

def dd : List (List Nat) → List (List Nat)
  | [] => []
  | r :: R => if r ∈ dd R then dd R else r :: dd R

theorem mem_dd : ∀ (R : List (List Nat)) (x : List Nat), x ∈ dd R ↔ x ∈ R
  | [], x => by simp [dd]
  | r :: R, x => by
    have ih := mem_dd R
    unfold dd
    split
    · rename_i h
      constructor
      · intro hx
        exact List.mem_cons_of_mem _ ((ih x).1 hx)
      · intro hx
        rcases List.mem_cons.mp hx with rfl | hx
        · exact h
        · exact (ih x).2 hx
    · simp only [List.mem_cons, ih]

theorem nodup_dd : ∀ R : List (List Nat), (dd R).Nodup
  | [] => by simp [dd]
  | r :: R => by
    have ih := nodup_dd R
    unfold dd
    split
    · exact ih
    · rename_i h
      exact List.nodup_cons.mpr ⟨h, ih⟩

theorem length_dd_le : ∀ R : List (List Nat), (dd R).length ≤ R.length
  | [] => by simp [dd]
  | r :: R => by
    have ih := length_dd_le R
    unfold dd
    split <;> simp only [List.length_cons] <;> omega

theorem resolving_dd {n k : Nat} {R : List (List Nat)} (h : Resolving n k R) :
    Resolving n k (dd R) := by
  refine ⟨fun r hr => h.1 r ((mem_dd R r).1 hr), ?_⟩
  intro x y hx hy hne
  obtain ⟨r, hr, rest⟩ := h.2 x y hx hy hne
  exact ⟨r, (mem_dd R r).2 hr, rest⟩

/-! ### List lemmas for the family k = 2, n = 8 + m -/

theorem exc_append : ∀ (L a Z b : List Nat), L.length = a.length →
    exc (L ++ Z) (a ++ b) = exc L a + exc Z b
  | [], [], Z, b, _ => by simp [exc]
  | [], _ :: _, _, _, h => by simp at h
  | _ :: _, [], _, _, h => by simp at h
  | c :: L, d :: a, Z, b, h => by
    have ih := exc_append L a Z b (by simpa using h)
    simp only [List.cons_append, exc, ih]
    omega

theorem exc_zeros : ∀ (m : Nat) (b : List Nat), exc (List.replicate m 0) b = 0
  | 0, b => by simp [exc]
  | m + 1, [] => by simp [List.replicate_succ, exc]
  | m + 1, c :: b => by
    have ih := exc_zeros m b
    simp only [List.replicate_succ, exc, ih]
    omega

theorem sum_zeros : ∀ m : Nat, (List.replicate m 0).sum = 0
  | 0 => rfl
  | m + 1 => by
    have ih := sum_zeros m
    simp only [List.replicate_succ, List.sum_cons, ih]

theorem getD_zeros : ∀ m t : Nat, (List.replicate m 0).getD t 0 = 0
  | 0, t => by simp
  | m + 1, 0 => by simp [List.replicate_succ]
  | m + 1, t + 1 => by
    have ih := getD_zeros m t
    simpa [List.replicate_succ] using ih

theorem exc_twoAt : ∀ (m t : Nat) (b : List Nat), t < m → b.length = m →
    exc ((List.replicate m 0).set t 2) b = 2 - b.getD t 0
  | 0, _, _, h, _ => by omega
  | m + 1, _, [], _, h => by simp at h
  | m + 1, 0, c :: b, _, _ => by
    have hz := exc_zeros m b
    simp only [List.replicate_succ, List.set_cons_zero, exc, List.getD_cons_zero, hz]
    omega
  | m + 1, t + 1, c :: b, ht, hb => by
    have ih := exc_twoAt m t b (by omega) (by simpa using hb)
    simp only [List.replicate_succ, List.set_cons_succ, exc, List.getD_cons_succ, ih]
    omega

theorem getD_le_sum : ∀ (b : List Nat) (t : Nat), b.getD t 0 ≤ b.sum
  | [], t => by simp
  | c :: b, 0 => by simp
  | c :: b, t + 1 => by
    have ih := getD_le_sum b t
    simp only [List.getD_cons_succ, List.sum_cons]
    omega

theorem exists_getD_ne : ∀ b b' : List Nat, b.length = b'.length → b ≠ b' →
    ∃ t, t < b.length ∧ b.getD t 0 ≠ b'.getD t 0
  | [], [], _, h => absurd rfl h
  | [], _ :: _, h, _ => by simp at h
  | _ :: _, [], h, _ => by simp at h
  | c :: b, d :: b', hl, hne => by
    by_cases hcd : c = d
    · subst hcd
      have hne' : b ≠ b' := fun e => hne (by rw [e])
      obtain ⟨t, ht, hd⟩ := exists_getD_ne b b' (by simpa using hl) hne'
      exact ⟨t + 1, by simpa using ht, by simpa using hd⟩
    · exact ⟨0, by simp, by simpa using hcd⟩

theorem sum_append_nat : ∀ a b : List Nat, (a ++ b).sum = a.sum + b.sum
  | [], b => by simp
  | c :: a, b => by
    have ih := sum_append_nat a b
    simp only [List.cons_append, List.sum_cons, ih]
    omega

/-! ### The family: n - 2 landmarks resolve F_2(K_n) for every n >= 8 -/

/-- The six landmarks padded with m zeros, then 2e_p for every coordinate p >= 9. -/
def familyLandmarks (m : Nat) : List (List Nat) :=
  (landmarks.map fun L => L ++ List.replicate m 0) ++
    (List.range m).map fun t => List.replicate 8 0 ++ (List.replicate m 0).set t 2

theorem landmarks_shape : ∀ L ∈ landmarks, L.length = 8 ∧ L.sum = 2 := by decide +kernel

/-- Prefixes of equal sum s <= 2 are separated by the six landmarks. -/
theorem prefix_separate : ∀ s, s < 3 → ∀ a ∈ comps 8 s, ∀ a' ∈ comps 8 s, a ≠ a' →
    ∃ L, L ∈ landmarks ∧ exc L a ≠ exc L a' := by decide +kernel

theorem family_resolving (m : Nat) : Resolving (8 + m) 2 (familyLandmarks m) := by
  apply resolving_of_separates
  · intro r hr
    rcases List.mem_append.mp hr with h | h
    · obtain ⟨L, hL, rfl⟩ := List.mem_map.mp h
      obtain ⟨h1, h2⟩ := landmarks_shape L hL
      exact ⟨by simp [h1], by rw [sum_append_nat, h2, sum_zeros]⟩
    · obtain ⟨t, ht, rfl⟩ := List.mem_map.mp h
      have htm : t < m := List.mem_range.mp ht
      refine ⟨by simp <;> omega, ?_⟩
      have s := sum_set (List.replicate m 0) t 2 (by simpa using htm)
      rw [getD_zeros, sum_zeros] at s
      rw [sum_append_nat, sum_zeros]
      omega
  · intro x y hx hy hne
    have hxs : x = x.take 8 ++ x.drop 8 := (List.take_append_drop 8 x).symm
    have hys : y = y.take 8 ++ y.drop 8 := (List.take_append_drop 8 y).symm
    have hxa : (x.take 8).length = 8 := by rw [List.length_take, hx.1]; omega
    have hya : (y.take 8).length = 8 := by rw [List.length_take, hy.1]; omega
    have hxb : (x.drop 8).length = m := by rw [List.length_drop, hx.1]; omega
    have hyb : (y.drop 8).length = m := by rw [List.length_drop, hy.1]; omega
    have hxsum : (x.take 8).sum + (x.drop 8).sum = 2 := by
      rw [← sum_append_nat, ← hxs]; exact hx.2
    have hysum : (y.take 8).sum + (y.drop 8).sum = 2 := by
      rw [← sum_append_nat, ← hys]; exact hy.2
    by_cases hb : x.drop 8 = y.drop 8
    · -- equal tails: the prefixes differ and have the same sum
      have hane : x.take 8 ≠ y.take 8 := by
        intro e
        apply hne
        rw [hxs, hys, e, hb]
      have hsum : (y.take 8).sum = (x.take 8).sum := by rw [hb] at hxsum; omega
      have hmx : x.take 8 ∈ comps 8 (x.take 8).sum := (mem_comps _ _ _).2 ⟨hxa, rfl⟩
      have hmy : y.take 8 ∈ comps 8 (x.take 8).sum := (mem_comps _ _ _).2 ⟨hya, hsum⟩
      obtain ⟨L, hL, hd⟩ := prefix_separate _ (by omega) _ hmx _ hmy hane
      refine ⟨L ++ List.replicate m 0, List.mem_append.mpr (Or.inl (List.mem_map.mpr ⟨L, hL, rfl⟩)), ?_⟩
      have hl8 := (landmarks_shape L hL).1
      rw [hxs, hys, exc_append L _ _ _ (by rw [hl8, hxa]), exc_append L _ _ _ (by rw [hl8, hya]),
        exc_zeros, exc_zeros]
      omega
    · -- tails differ at some coordinate t: 2e_(8+t) separates
      obtain ⟨t, ht, hd⟩ := exists_getD_ne _ _ (by rw [hxb, hyb]) hb
      rw [hxb] at ht
      refine ⟨List.replicate 8 0 ++ (List.replicate m 0).set t 2,
        List.mem_append.mpr (Or.inr (List.mem_map.mpr ⟨t, List.mem_range.mpr ht, rfl⟩)), ?_⟩
      have b1 := getD_le_sum (x.drop 8) t
      have b2 := getD_le_sum (y.drop 8) t
      rw [hxs, hys, exc_append _ _ _ _ (by simp [hxa]), exc_append _ _ _ _ (by simp [hya]),
        exc_zeros, exc_zeros, exc_twoAt m t _ ht hxb, exc_twoAt m t _ ht hyb]
      omega

/-! ### The instance n = 8, k = 2 -/

theorem landmarks_ok : landmarks.Nodup ∧ landmarks.length = 6 := by decide +kernel

/-- The six landmarks form a resolving set of F_2(K_8). -/
theorem landmarks_resolving : Resolving 8 2 landmarks := by
  apply resolving_of_separates
  · intro r hr
    exact landmarks_shape r hr
  · intro x y hx hy hne
    exact prefix_separate 2 (by omega) x ((mem_comps 8 2 x).2 hx) y ((mem_comps 8 2 y).2 hy) hne

/-- F_2(K_8) has a resolving set with six elements. -/
theorem resolving_set_of_size_six :
    ∃ R : List (List Nat), R.Nodup ∧ R.length = 6 ∧ Resolving 8 2 R :=
  ⟨landmarks, landmarks_ok.1, landmarks_ok.2, landmarks_resolving⟩

/-- Whatever the metric dimension of F_2(K_8) is, it is at most 6. -/
theorem metric_dim_le_six (d : Nat) (h : IsMetricDim 8 2 d) : d ≤ 6 := by
  have := h.2 landmarks landmarks_ok.1 landmarks_resolving
  have h6 := landmarks_ok.2
  omega

/-- Conjecture 4.2 fails at n = 8, k = 2: the metric dimension of F_2(K_8) is not n - 1 = 7. -/
theorem conjecture_4_2_fails_at_8_2 : ¬ IsMetricDim 8 2 (8 - 1) := fun h => by
  have := metric_dim_le_six _ h
  omega

/-- Conjecture 4.2, read as the universal statement over integers n >= 1 and k >= 1, is false. -/
theorem conjecture_4_2_false : ¬ ∀ n k : Nat, 1 ≤ n → 1 ≤ k → IsMetricDim n k (n - 1) :=
  fun h => conjecture_4_2_fails_at_8_2 (h 8 2 (by decide) (by decide))

/-- For every n >= 8 the graph F_2(K_n) has a duplicate-free resolving list with at most n - 2
elements. -/
theorem family_small_resolving (m : Nat) :
    ∃ R : List (List Nat), R.Nodup ∧ R.length ≤ 6 + m ∧ Resolving (8 + m) 2 R := by
  refine ⟨dd (familyLandmarks m), nodup_dd _, ?_, resolving_dd (family_resolving m)⟩
  have h1 := length_dd_le (familyLandmarks m)
  have h2 : (familyLandmarks m).length = 6 + m := by
    simp [familyLandmarks, landmarks] <;> omega
  omega

/-- Conjecture 4.2 fails at k = 2 for EVERY n >= 8. -/
theorem conjecture_4_2_fails_k2 (n : Nat) (hn : 8 ≤ n) : ¬ IsMetricDim n 2 (n - 1) := by
  intro h
  obtain ⟨m, rfl⟩ : ∃ m, n = 8 + m := ⟨n - 8, by omega⟩
  obtain ⟨R, hnd, hlen, hres⟩ := family_small_resolving m
  have := h.2 R hnd hres
  omega

/-- In particular no threshold n0 rescues the conjecture for k = 2. -/
theorem conjecture_4_2_not_eventually_true_k2 :
    ¬ ∃ n0 : Nat, ∀ n, n0 ≤ n → IsMetricDim n 2 (n - 1) := by
  rintro ⟨n0, h⟩
  exact conjecture_4_2_fails_k2 (n0 + 8) (by omega) (h (n0 + 8) (by omega))

end SupertokenMetric

#print axioms SupertokenMetric.mem_comps
#print axioms SupertokenMetric.dist_formula
#print axioms SupertokenMetric.dist_iff
#print axioms SupertokenMetric.dist_symm
#print axioms SupertokenMetric.adj_vertex
#print axioms SupertokenMetric.landmarks_resolving
#print axioms SupertokenMetric.resolving_set_of_size_six
#print axioms SupertokenMetric.conjecture_4_2_fails_at_8_2
#print axioms SupertokenMetric.conjecture_4_2_false
#print axioms SupertokenMetric.family_resolving
#print axioms SupertokenMetric.conjecture_4_2_fails_k2
#print axioms SupertokenMetric.conjecture_4_2_not_eventually_true_k2
